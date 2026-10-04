import re
from google import genai
from google.genai import types
from django.conf import settings
from .models import GlobalMemory, ChatMessage

client = genai.Client(api_key=settings.GEMINI_API_KEY)

def get_olo_response(chat_session, new_message_text):
    # 1. Recuperar la Memoria Global
    memorias = GlobalMemory.objects.all()
    memoria_texto = "\n".join([f"- {m.fact}" for m in memorias])

    # 2. Construir la Instrucción del Sistema
    sys_inst = chat_session.prompt.system_instruction if chat_session.prompt else "Sos Olo, mi asistente personal."
    
    if memoria_texto:
        sys_inst += f"\n\nMEMORIA GLOBAL SOBRE EL USUARIO:\n{memoria_texto}"
        
    sys_inst += (
        "\n\nREGLA CRÍTICA: Si el usuario te pide explícitamente que recuerdes algo "
        "o que guardes un dato para el futuro, incluí al final de tu respuesta la etiqueta exacta "
        "[MEMORIA: el dato a recordar]."
    )

    # 3. Construir el historial (Memoria a corto plazo)
    history_qs = chat_session.messages.all().order_by('created_at')
    contents = []
    
    for msg in history_qs:
        contents.append(types.Content(role=msg.role, parts=[types.Part.from_text(text=msg.text)]))

    # Agregar el nuevo mensaje del usuario
    contents.append(types.Content(role="user", parts=[types.Part.from_text(text=new_message_text)]))

    try:
        # 4. Llamar a Gemini
        response = client.models.generate_content(
            model='gemini-2.5-flash', # o gemini-1.5-flash
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=sys_inst,
            ),
        )
        
        reply = response.text

        # 5. Interceptar si Olo decidió guardar algo en la memoria
        memoria_match = re.search(r'\[MEMORIA:\s*(.*?)\]', reply, re.IGNORECASE)
        if memoria_match:
            nuevo_dato = memoria_match.group(1)
            GlobalMemory.objects.create(fact=nuevo_dato)
            # Limpiamos la respuesta para no mostrarle la etiqueta al usuario
            reply = re.sub(r'\[MEMORIA:\s*(.*?)\]', '', reply, flags=re.IGNORECASE).strip()

        return reply

    except Exception as e:
        return f"Error interno en Olo: {str(e)}"