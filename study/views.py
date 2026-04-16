from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.conf import settings
from .models import ChatSession, ChatMessage, AIProfile, GlobalMemory, CustomPrompt
from google import genai
from google.genai import types
from datetime import datetime
import re
import traceback

client = genai.Client(api_key=settings.GEMINI_API_KEY)

def build_system_prompt(user):
    profile, _ = AIProfile.objects.get_or_create(user=user)
    active_prompt = CustomPrompt.objects.filter(user=user, is_active=True).first()
    memorias = GlobalMemory.objects.filter(user=user).values_list('fact', flat=True)
    
    memoria_str = "\n- ".join(memorias) if memorias else "Ninguna todavía."
    
    base_prompt = f"""
Sos {profile.ai_name}, el asistente personal de {profile.user_name}.
Fecha actual: {datetime.now().strftime("%d/%m/%Y %H:%M")}.

HECHOS IMPORTANTES QUE DEBES RECORDAR SIEMPRE:
- {memoria_str}

REGLA DE MEMORIA: Si el usuario te pide explícitamente que recuerdes algo o guardes algo en memoria, DEBES incluir al final de tu respuesta la etiqueta exacta: [GUARDAR_MEMORIA: lo que debo recordar].
"""
    if active_prompt:
        base_prompt += f"\n\nINSTRUCCIONES ADICIONALES:\n{active_prompt.prompt_text}"

    return base_prompt

class SessionManagerView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        sessions = ChatSession.objects.filter(user=request.user).order_by('-created_at')
        data = [{"id": str(s.id), "title": s.title or "Chat sin título"} for s in sessions]
        return Response(data)

    def post(self, request):
        session = ChatSession.objects.create(user=request.user, title="Nueva conversación")
        return Response({"id": str(session.id), "title": session.title})

class SessionChatView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, session_id):
        session = get_object_or_404(ChatSession, id=session_id, user=request.user)
        messages = session.messages.all().order_by('created_at')
        data = [{"role": msg.role, "content": msg.content} for msg in messages]
        return Response(data)

    def post(self, request, session_id):
        session = get_object_or_404(ChatSession, id=session_id, user=request.user)
        user_text = request.data.get('message')
        modelo_elegido = request.data.get('model', 'gemini-2.5-flash')

        if not user_text:
            return Response({"error": "Mensaje vacío"}, status=400)

        ChatMessage.objects.create(session=session, role='user', content=user_text)

        db_messages = session.messages.all().order_by('created_at')
        historial = [
            types.Content(role=msg.role, parts=[types.Part.from_text(text=msg.content)])
            for msg in db_messages
        ]

        system_instruction = build_system_prompt(request.user)
        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.7,
        )

        try:
            response = client.models.generate_content(
                model=modelo_elegido,
                contents=historial,
                config=config
            )
            
            if not response.text:
                 raise ValueError("La API de Gemini devolvió una respuesta vacía o bloqueada.")
                 
            model_text = response.text

            # Interceptar memoria
            match = re.search(r'\[GUARDAR_MEMORIA:\s*(.*?)\]', model_text)
            if match:
                hecho_a_guardar = match.group(1).strip()
                GlobalMemory.objects.create(user=request.user, fact=hecho_a_guardar)
                model_text = re.sub(r'\[GUARDAR_MEMORIA:\s*(.*?)\]', '', model_text).strip()

            if session.title == "Nueva conversación" and session.messages.count() <= 2:
                session.title = user_text[:30] + "..."
                session.save()

            ChatMessage.objects.create(session=session, role='model', content=model_text)
            return Response({"role": "model", "content": model_text})

        except Exception as e:
            print("🔥" * 20)
            print(f"🔥 ERROR EN ENTITY: {str(e)}")
            traceback.print_exc() 
            print("🔥" * 20)
            return Response({"error": str(e)}, status=500)