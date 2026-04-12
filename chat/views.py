from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from .models import ChatSession, ChatMessage
from google import genai
from google.genai import types

# Importamos la configuración dinámica de Entity
from .entity_config import get_entity_config 

client = genai.Client(api_key=settings.GEMINI_API_KEY)

class EntityChatView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        session, _ = ChatSession.objects.get_or_create(user=request.user)
        messages = session.messages.all().order_by('created_at')
        
        data = [
            {"id": msg.id, "role": msg.role, "content": msg.content, "created_at": msg.created_at}
            for msg in messages
        ]
        return Response(data)

    def post(self, request):
        user_text = request.data.get('message')
        if not user_text:
            return Response({"error": "El mensaje no puede estar vacío"}, status=400)

        session, _ = ChatSession.objects.get_or_create(user=request.user)

        # Fix Anticrash
        last_msg = session.messages.last()
        if last_msg and last_msg.role == 'user':
            last_msg.delete()

        nuevo_mensaje = ChatMessage.objects.create(session=session, role='user', content=user_text)

        db_messages = session.messages.all().order_by('created_at')
        historial_formateado = []
        
        for msg in db_messages:
            historial_formateado.append(
                types.Content(role=msg.role, parts=[types.Part.from_text(text=msg.content)])
            )

        try:
            # Llamamos al modelo pasándole el historial Y LA CONFIGURACIÓN de personalidad
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=historial_formateado,
                config=get_entity_config() # <--- Acá inyectamos a Entity
            )
            model_text = response.text

            ChatMessage.objects.create(session=session, role='model', content=model_text)

            return Response({"role": "model", "content": model_text})
            
        except Exception as e:
            nuevo_mensaje.delete()
            print(f"🔥 ERROR EN ENTITY: {str(e)}") 
            return Response({"error": str(e)}, status=500)