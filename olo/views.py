import traceback
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.conf import settings
from django.utils import timezone
from google import genai
from google.genai import types

from .models import DailyMemory

# Inicializamos el cliente una sola vez
client = genai.Client(api_key=settings.GEMINI_API_KEY)

class OloChatView(APIView):
    # AllowAny permite que la app móvil consuma la API sin token de login
    permission_classes = [AllowAny]

    def post(self, request):
        prompt = request.data.get('prompt')
        device_id = request.data.get('device_id') 

        if not prompt:
            return Response({"error": "El prompt es obligatorio."}, status=400)

        today = timezone.localdate()

        # 1. Buscar o crear la memoria correcta (Web o Móvil)
        if request.user.is_authenticated:
            memory, created = DailyMemory.objects.get_or_create(
                user=request.user,
                date=today
            )
        elif device_id:
            memory, created = DailyMemory.objects.get_or_create(
                user=None,
                device_id=device_id,
                date=today
            )
        else:
            return Response({"error": "Falta autenticación o un device_id."}, status=401)

        # 2. Configurar la identidad y el tiempo de OLO
        now = timezone.localtime()
        fecha_hora_actual = now.strftime("%A, %d de %B de %Y a las %H:%M:%S")
        
        system_instruction = (
            "Tu nombre es OLO. Eres un amigo y asistente personal súper cercano, cálido y natural. Cero robótico.\n\n"
            "REGLAS ESTRICTAS DE FORMATO:\n"
            "1. Tus respuestas deben ser MUY breves, pensadas para leerse de un vistazo en la pantalla de un celular sin hacer scroll.\n"
            "2. NUNCA uses listas largas, viñetas interminables ni bloques gigantes de texto.\n"
            "3. Habla como en un chat uno a uno (estilo WhatsApp): respuestas cortas, directas y al pie.\n"
            "4. Explica las cosas de forma increíble, fácil de entender, con ejemplos simples de la vida real.\n"
            "5. Termina tus respuestas manteniendo la conversación viva, haciendo una pregunta corta si es necesario.\n\n"
            f"Contexto temporal: {fecha_hora_actual}."
        )

        # 3. Reconstruir el historial usando diccionarios (A prueba de fallos)
        contents = []
        for msg in memory.history:
            contents.append({
                "role": msg['role'], 
                "parts": [{"text": str(msg['text'])}]
            })
        
        # Agregamos el mensaje nuevo del usuario
        contents.append({
            "role": "user", 
            "parts": [{"text": str(prompt)}]
        })

        try:
            # 4. Llamar a la API de Gemini
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                )
            )
            
            olo_respuesta = response.text

            # 5. Guardar la nueva interacción en la base de datos
            memory.history.append({"role": "user", "text": str(prompt)})
            memory.history.append({"role": "model", "text": olo_respuesta})
            memory.save()

            return Response({
                "respuesta": olo_respuesta,
                "fecha_memoria": today
            })

        except Exception as e:
            # Si falla algo, esto te devuelve el traceback completo en formato JSON
            return Response({
                "error_gemini": str(e), 
                "traceback": traceback.format_exc()
            }, status=500)