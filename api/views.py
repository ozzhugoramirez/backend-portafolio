from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import *
from .serializers import *
from django.core.mail import send_mail
from django.conf import settings
from rest_framework.throttling import AnonRateThrottle
import requests
from django.db.models import Count
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from django.utils import timezone
import logging
from datetime import timedelta
from django.db.models.functions import TruncWeek
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)



class CustomLoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        usuario_input = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(username=usuario_input, password=password)

        if user is not None:
            refresh = RefreshToken.for_user(user)
            
            user_agent = request.META.get('HTTP_USER_AGENT', 'Dispositivo desconocido')
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip_address = x_forwarded_for.split(',')[0]
            else:
                ip_address = request.META.get('REMOTE_ADDR', 'IP desconocida')

            fecha_hora = timezone.localtime(timezone.now()).strftime("%d/%m/%Y %H:%M:%S")

            asunto = f"Alerta de Seguridad: Nuevo inicio de sesión en devsebastian.com"
            cuerpo_texto = f"Se detectó un nuevo inicio de sesión.\nUsuario: {usuario_input}\nFecha: {fecha_hora}\nIP: {ip_address}\nDispositivo: {user_agent}"
            
            cuerpo_html = f"""
            <div style="background-color: #f5f5f7; padding: 40px 20px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;">
                <div style="max-width: 560px; margin: 0 auto; background-color: #ffffff; border-radius: 18px; padding: 40px; border: 1px solid #d2d2d7; box-shadow: 0 4px 12px rgba(0,0,0,0.05);">
                    <div style="text-align: center; margin-bottom: 24px;">
                        <h1 style="color: #1d1d1f; font-size: 24px; font-weight: 600; margin-bottom: 8px; letter-spacing: -0.022em;">
                            Alerta de Seguridad
                        </h1>
                        <p style="color: #86868b; font-size: 14px;">
                            Se detectó un nuevo acceso a tu panel de administración.
                        </p>
                    </div>

                    <div style="background-color: #f5f5f7; border-radius: 12px; padding: 20px; margin-bottom: 24px;">
                        <p style="margin: 0 0 12px 0; font-size: 14px;">
                            <strong style="color: #1d1d1f; display: block; margin-bottom: 2px;">Usuario</strong>
                            <span style="color: #515154;">{usuario_input}</span>
                        </p>
                        <p style="margin: 0 0 12px 0; font-size: 14px;">
                            <strong style="color: #1d1d1f; display: block; margin-bottom: 2px;">Fecha y Hora</strong>
                            <span style="color: #515154;">{fecha_hora}</span>
                        </p>
                        <p style="margin: 0 0 12px 0; font-size: 14px;">
                            <strong style="color: #1d1d1f; display: block; margin-bottom: 2px;">Dirección IP</strong>
                            <span style="color: #515154;">{ip_address}</span>
                        </p>
                        <p style="margin: 0; font-size: 14px;">
                            <strong style="color: #1d1d1f; display: block; margin-bottom: 2px;">Dispositivo / Navegador</strong>
                            <span style="color: #515154; word-break: break-all;">{user_agent}</span>
                        </p>
                    </div>

                    <p style="color: #1d1d1f; font-size: 14px; line-height: 1.5; margin-bottom: 0;">
                        Si fuiste vos, podés ignorar este mensaje. Si no reconocés esta actividad, alguien podría tener tu contraseña. Te recomendamos cambiarla inmediatamente y revisar los logs de tu servidor.
                    </p>

                    <hr style="border: 0; border-top: 1px solid #d2d2d7; margin: 32px 0 20px 0;">
                    <p style="color: #86868b; font-size: 12px; text-align: center; margin: 0;">
                        Sistema de Seguridad &bull; devsebastian.com
                    </p>
                </div>
            </div>
            """

            try:
                send_mail(
                    subject=asunto,
                    message=cuerpo_texto,
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[settings.DESTINATION_EMAIL],
                    fail_silently=False,
                    html_message=cuerpo_html
                )
            except Exception as e:
                logger.error(f"Error enviando alerta de seguridad: {e}")

            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'username': user.username
            }, status=status.HTTP_200_OK)
            
        return Response({'detail': 'Credenciales inválidas'}, status=status.HTTP_401_UNAUTHORIZED)

class ProfileAPIView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get(self, request):
        profile = Profile.objects.first()
        if not profile:
            return Response({})
        serializer = ProfileSerializer(profile)
        return Response(serializer.data)

    def put(self, request):
        profile = Profile.objects.first()
        if not profile:
            profile = Profile()
            
        serializer = ProfileSerializer(profile, data=request.data, partial=True) 
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        print("Errores en Profile PUT:", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)





class ProjectListAPIView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get(self, request):
        show_all = request.query_params.get('all', 'false').lower() == 'true'
        if show_all:
            projects = Project.objects.all()
        else:
            projects = Project.objects.filter(is_public=True)
            
        serializer = ProjectSerializer(projects, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ProjectSerializer(data=request.data)
        if serializer.is_valid():
            project = serializer.save()
            
           
            gallery_files = request.FILES.getlist('gallery_images')
            for file in gallery_files:
                ProjectGalleryImage.objects.create(project=project, image=file)

            
            updated_serializer = ProjectSerializer(project)
            return Response(updated_serializer.data, status=status.HTTP_201_CREATED)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class ProjectDetailAPIView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_object(self, slug):
        return get_object_or_404(Project, slug=slug)

    def get(self, request, slug):
        project = self.get_object(slug)
        serializer = ProjectSerializer(project)
        return Response(serializer.data)

    def put(self, request, slug):
        project = self.get_object(slug)
        serializer = ProjectSerializer(project, data=request.data, partial=True)
        if serializer.is_valid():
            project = serializer.save()
            
            
            gallery_files = request.FILES.getlist('gallery_images')
            for file in gallery_files:
                ProjectGalleryImage.objects.create(project=project, image=file)

            updated_serializer = ProjectSerializer(project)
            return Response(updated_serializer.data)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, slug):
        project = self.get_object(slug)
        project.delete()
        return Response({"message": "Proyecto eliminado"}, status=status.HTTP_204_NO_CONTENT)




class LabSnippetListAPIView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get(self, request):
        show_all = request.query_params.get('all', 'false').lower() == 'true'
        if show_all:
            snippets = LabSnippet.objects.all()
        else:
            snippets = LabSnippet.objects.filter(is_public=True)
            
        serializer = LabSnippetSerializer(snippets, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = LabSnippetSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LabSnippetDetailAPIView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_object(self, pk):
        return get_object_or_404(LabSnippet, pk=pk)

    def get(self, request, pk):
        snippet = self.get_object(pk)
        serializer = LabSnippetSerializer(snippet)
        return Response(serializer.data)

    def put(self, request, pk):
        snippet = self.get_object(pk)
        
        serializer = LabSnippetSerializer(snippet, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        snippet = self.get_object(pk)
        snippet.delete()
        return Response({"message": "Snippet eliminado"}, status=status.HTTP_204_NO_CONTENT)
    





def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

class TrackEventAPIView(APIView):
    
    permission_classes = [AllowAny] 

    def post(self, request):
        action = request.data.get('action')
        target = request.data.get('target')
        ip_address = get_client_ip(request)
        
        if action and target:
            
            if action == 'view':
                hace_3_horas = timezone.now() - timedelta(hours=3)
                
               
                evento_reciente = TelemetryEvent.objects.filter(
                    action=action,
                    target=target,
                    ip_address=ip_address,
                    created_at__gte=hace_3_horas
                ).exists()

                if evento_reciente:
                   
                    return Response({"status": "ignored_cooldown"}, status=status.HTTP_200_OK)

            
            TelemetryEvent.objects.create(action=action, target=target, ip_address=ip_address)
            return Response({"status": "tracked"}, status=status.HTTP_201_CREATED)
            
        return Response({"error": "Faltan datos"}, status=status.HTTP_400_BAD_REQUEST)


class DashboardStatsAPIView(APIView):
    
    permission_classes = [IsAuthenticated] 

    def get(self, request):
        hoy = timezone.now()
        inicio_semana = hoy - timedelta(days=hoy.weekday())
        inicio_semana = inicio_semana.replace(hour=0, minute=0, second=0, microsecond=0)

        
        eventos_semana = TelemetryEvent.objects.filter(created_at__gte=inicio_semana)

        total_views = eventos_semana.filter(action='view', target='home').count()
        cv_downloads = eventos_semana.filter(action='download', target='cv').count()
        
        social_clicks = eventos_semana.filter(action='click').values('target').annotate(total=Count('target')).order_by('-total')
        project_views = eventos_semana.filter(action='view').exclude(target='home').values('target').annotate(total=Count('target')).order_by('-total')

        
        historial = TelemetryEvent.objects.filter(action='view', target='home') \
            .annotate(semana=TruncWeek('created_at')) \
            .values('semana') \
            .annotate(total=Count('id')) \
            .order_by('-semana')

        return Response({
            "overview": {
                "total_views": total_views,
                "cv_downloads": cv_downloads,
                "current_week_start": inicio_semana.strftime('%d/%m/%Y')
            },
            "social_clicks": list(social_clicks),
            "project_views": list(project_views),
            "weekly_history": list(historial)
        })

class ClearTelemetryAPIView(APIView):
   
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        TelemetryEvent.objects.all().delete()
        return Response({"message": "Telemetría reseteada con éxito."}, status=status.HTTP_200_OK)
    

class AdminMessageAPIView(APIView):
    permission_classes = [IsAuthenticated] 

    def get(self, request, *args, **kwargs):
       
        mensajes = ContactMessage.objects.all().order_by('-created_at')
        serializer = ContactMessageSerializer(mensajes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class MarkMessageReadAPIView(APIView):
    permission_classes = [IsAuthenticated] 

    def patch(self, request, pk, *args, **kwargs):
        try:
            mensaje = ContactMessage.objects.get(pk=pk)
            mensaje.is_read = True
            mensaje.save()
            return Response({"status": "Mensaje marcado como leído"}, status=status.HTTP_200_OK)
        except ContactMessage.DoesNotExist:
            return Response({"error": "Mensaje no encontrado"}, status=status.HTTP_404_NOT_FOUND)

class ContactRateThrottle(AnonRateThrottle):
    rate = '3/hour' 

class ContactAPIView(APIView):
    permission_classes = [] 
    throttle_classes = [ContactRateThrottle] 

    def post(self, request, *args, **kwargs):
       
        recaptcha_token = request.data.get('recaptchaToken')
        
        if not recaptcha_token:
            return Response({"error": "Falta validación de seguridad."}, status=status.HTTP_400_BAD_REQUEST)

       
        verify_url = "https://www.google.com/recaptcha/api/siteverify"
        payload = {
            'secret': settings.RECAPTCHA_SECRET_KEY,
            'response': recaptcha_token
        }
        
        try:
            google_response = requests.post(verify_url, data=payload).json()
          
            if not google_response.get('success') or google_response.get('score', 0) < 0.5:
                return Response({"error": "Tráfico sospechoso bloqueado."}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({"error": "Error interno de validación."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        
        serializer = ContactMessageSerializer(data=request.data)
        
        if serializer.is_valid():
            mensaje = serializer.save()

            
            asunto = f"Nuevo mensaje de contacto: {mensaje.name}"
            cuerpo_texto = f"Mensaje de {mensaje.name} ({mensaje.email})\n\nAsunto: {mensaje.subject}\n\n{mensaje.message}"

           
            cuerpo_html = f"""
            <div style="background-color: #f5f5f7; padding: 40px 20px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;">
                <div style="max-width: 560px; margin: 0 auto; background-color: #ffffff; border-radius: 18px; padding: 40px; border: 1px solid #d2d2d7; box-shadow: 0 4px 12px rgba(0,0,0,0.05);">
                    
                    <h1 style="color: #1d1d1f; font-size: 24px; font-weight: 600; margin-bottom: 8px; letter-spacing: -0.022em;">
                        Nuevo mensaje
                    </h1>
                    <p style="color: #86868b; font-size: 14px; margin-bottom: 32px;">
                        Recibiste una nueva comunicación a través de tu portafolio.
                    </p>

                    <div style="margin-bottom: 24px;">
                        <p style="text-transform: uppercase; font-size: 11px; font-weight: 600; color: #86868b; letter-spacing: 0.05em; margin-bottom: 4px;">
                            Remitente
                        </p>
                        <p style="color: #1d1d1f; font-size: 16px; margin: 0;">
                            <strong>{mensaje.name}</strong> 
                            <span style="color: #86868b;">&bull;</span> 
                            <a href="mailto:{mensaje.email}" style="color: #0066cc; text-decoration: none;">{mensaje.email}</a>
                        </p>
                    </div>

                    <div style="margin-bottom: 24px;">
                        <p style="text-transform: uppercase; font-size: 11px; font-weight: 600; color: #86868b; letter-spacing: 0.05em; margin-bottom: 4px;">
                            Asunto del mensaje
                        </p>
                        <p style="color: #1d1d1f; font-size: 16px; margin: 0;">
                            {mensaje.subject}
                        </p>
                    </div>

                    <div style="background-color: #f5f5f7; border-radius: 12px; padding: 20px; margin-top: 32px;">
                        <p style="color: #1d1d1f; font-size: 15px; line-height: 1.5; margin: 0; white-space: pre-wrap;">
                            {mensaje.message}
                        </p>
                    </div>

                    <hr style="border: 0; border-top: 1px solid #d2d2d7; margin: 40px 0 20px 0;">
                    
                    <p style="color: #86868b; font-size: 12px; text-align: center; margin: 0;">
                        Enviado desde devsebastian.com
                    </p>
                </div>
            </div>
            """
            
            try:
                send_mail(
                    subject=asunto,
                    message=cuerpo_texto,
                    from_email=settings.EMAIL_HOST_USER, 
                    recipient_list=[settings.DESTINATION_EMAIL], 
                    fail_silently=False,
                    html_message=cuerpo_html
                )
            except Exception as e:
               
                print(f"Error enviando correo: {e}")
            
            return Response({"message": "Mensaje enviado exitosamente."}, status=status.HTTP_201_CREATED)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)










class TimelineListCreateAPIView(APIView):
    # Cualquiera puede leer (GET), pero solo vos (logueado) podés crear (POST)
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        # Como definimos ordering=['-event_date'] en el modelo, ya vienen ordenados perfectos.
        events = TimelineEvent.objects.all()
        serializer = TimelineEventSerializer(events, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = TimelineEventSerializer(data=request.data)
        if serializer.is_valid():
            event = serializer.save()
            
            # Lógica para manejar múltiples archivos si se envían en el POST
            # Se espera que los archivos vengan en la request.FILES con la clave 'files'
            files = request.FILES.getlist('files')
            for f in files:
                TimelineMedia.objects.create(event=event, file=f)
                
            # Devolvemos el evento ya creado con sus medias
            response_serializer = TimelineEventSerializer(event)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TimelineDetailAPIView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, slug):
        event = get_object_or_404(TimelineEvent, slug=slug)
        serializer = TimelineEventSerializer(event)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, slug):
        event = get_object_or_404(TimelineEvent, slug=slug)
        serializer = TimelineEventSerializer(event, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            
            # Podrías agregar lógica acá si querés sumar más fotos al editar
            files = request.FILES.getlist('files')
            for f in files:
                TimelineMedia.objects.create(event=event, file=f)
                
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, slug):
        event = get_object_or_404(TimelineEvent, slug=slug)
        event.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)




class TimelineMediaDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated] 

    def delete(self, request, pk):
        media = get_object_or_404(TimelineMedia, pk=pk)
        media.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)