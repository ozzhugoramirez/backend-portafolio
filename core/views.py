from django.shortcuts import render
from django.views import View
from api.models import Profile, Project
import json
import hashlib
import uuid
from rest_framework.authentication import SessionAuthentication
from django.conf import settings
from django.core.cache import cache
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from webauthn import generate_authentication_options, verify_authentication_response, options_to_json
from webauthn.helpers.structs import UserVerificationRequirement
from webauthn.helpers import base64url_to_bytes
from api.models import Passkey
from webauthn import generate_registration_options, verify_registration_response
from webauthn.helpers.structs import AuthenticatorSelectionCriteria, ResidentKeyRequirement
from webauthn.helpers import bytes_to_base64url

class HomeView(View):
    def get(self, request):
        
        profile = Profile.objects.first()
        
       
        projects = Project.objects.filter(is_public=True)

        context = {
            'profile': profile,
            'projects': projects,
        }

        return render(request, "pages/index.html", context)



# --- VISTA DEL DASHBOARD ---
class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'pages/dashboard.html'
    login_url = '/login/' # Si no está logueado, lo manda acá

class LoginView(TemplateView):
    template_name = 'account/login.html'





class PasskeyRegisterOptionsAPIView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        authenticator_selection = AuthenticatorSelectionCriteria(
            user_verification=UserVerificationRequirement.PREFERRED,
            resident_key=ResidentKeyRequirement.REQUIRED,
        )

        register_options = generate_registration_options(
            rp_id=settings.WEBAUTHN_RP_ID,
            rp_name=settings.WEBAUTHN_RP_NAME,
            user_id=str(user.id).encode("utf-8"),
            user_name=user.username,
            user_display_name=user.username,
            authenticator_selection=authenticator_selection,
        )

        challenge_id = str(uuid.uuid4())

        cache.set(
            f"webauthn_register_{challenge_id}",
            register_options.challenge,
            300,
        )

        res_dict = json.loads(options_to_json(register_options))
        res_dict["challenge_id"] = challenge_id

        return Response(
            res_dict,
            status=status.HTTP_200_OK
        )


class PasskeyRegisterVerifyAPIView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        attestation_response = request.data.get("attestation")
        challenge_id = request.data.get("challenge_id")
        device_name = request.data.get(
            "name",
            "Dispositivo"
        )

        expected_challenge = cache.get(
            f"webauthn_register_{challenge_id}"
        )

        if not expected_challenge:
            return Response(
                {"detail": "El tiempo de espera se agotó."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            verification = verify_registration_response(
                credential=attestation_response,
                expected_challenge=expected_challenge,
                expected_origin=settings.WEBAUTHN_EXPECTED_ORIGIN,
                expected_rp_id=settings.WEBAUTHN_RP_ID,
            )

            Passkey.objects.create(
                user=user,
                name=device_name,
                credential_id=attestation_response.get("id"),
                public_key=bytes_to_base64url(
                    verification.credential_public_key
                ),
                sign_count=verification.sign_count,
            )

            cache.delete(
                f"webauthn_register_{challenge_id}"
            )

            return Response(
                {"detail": "Dispositivo registrado exitosamente."},
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            return Response(
                {"detail": f"Error en el registro: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

            
# --- API DE PASSKEYS ---
class PasskeyLoginOptionsAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        auth_options = generate_authentication_options(
            rp_id=settings.WEBAUTHN_RP_ID,
            user_verification=UserVerificationRequirement.PREFERRED, 
        )
        challenge_id = str(uuid.uuid4())
        cache.set(f"webauthn_login_{challenge_id}", auth_options.challenge, 300)

        res_dict = json.loads(options_to_json(auth_options))
        res_dict['challenge_id'] = challenge_id 
        return Response(res_dict, status=status.HTTP_200_OK)

class PasskeyLoginVerifyAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        assertion_response = request.data.get('assertion')
        challenge_id = request.data.get('challenge_id')
        
        expected_challenge = cache.get(f"webauthn_login_{challenge_id}")
        if not expected_challenge:
            return Response({'detail': 'El tiempo de espera se agotó.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            credential_id = assertion_response.get('id')
            passkey = Passkey.objects.get(credential_id=credential_id)
            user = passkey.user 

            verification = verify_authentication_response(
                credential=assertion_response,
                expected_challenge=expected_challenge,
                expected_rp_id=settings.WEBAUTHN_RP_ID,
                expected_origin=settings.WEBAUTHN_EXPECTED_ORIGIN,
                credential_public_key=base64url_to_bytes(passkey.public_key),
                credential_current_sign_count=passkey.sign_count,
            )

            passkey.sign_count = verification.new_sign_count
            passkey.save()
            cache.delete(f"webauthn_login_{challenge_id}")

            # MAGIA NUEVA: Iniciamos sesión en Django directamente
            login(request, user)

            # Devolvemos la URL del dashboard para que el JS haga la redirección
            return Response({
                'detail': 'Login exitoso',
                'redirect_url': '/dashboard/'
            }, status=status.HTTP_200_OK)

        except Passkey.DoesNotExist:
            return Response({'detail': 'Este dispositivo no está registrado.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'detail': f'Error verificando passkey: {str(e)}'}, status=status.HTTP_401_UNAUTHORIZED)