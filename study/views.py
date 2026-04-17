from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.conf import settings
from .models import ChatSession, ChatMessage, AIProfile, GlobalMemory, CustomPrompt, Notebook, Project
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
Sos {profile.ai_name}, el asistente personal de {profile.user_name if hasattr(profile, 'user_name') else user.username}.
Fecha actual: {datetime.now().strftime("%d/%m/%Y %H:%M")}.

HECHOS IMPORTANTES QUE DEBES RECORDAR SIEMPRE:
- {memoria_str}

REGLA DE MEMORIA: Si el usuario te pide explícitamente que recuerdes algo o guardes algo en memoria, DEBES incluir al final de tu respuesta la etiqueta exacta: [GUARDAR_MEMORIA: lo que debo recordar].
"""
    if active_prompt:
        base_prompt += f"\n\nINSTRUCCIONES ADICIONALES:\n{active_prompt.prompt_text}"

    return base_prompt


# --- NUEVAS VISTAS PARA EL DASHBOARD ---

class WorkspaceDataView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile, _ = AIProfile.objects.get_or_create(user=request.user)
        notebooks = Notebook.objects.filter(user=request.user).order_by('-updated_at')
        projects = Project.objects.filter(user=request.user).order_by('-updated_at')
        
        return Response({
            "ai_limit": profile.context_warning_limit,
            "notebooks": [{"id": str(n.id), "title": n.title, "color": n.color, "pages": n.chats.count()} for n in notebooks],
            "projects": [{"id": str(p.id), "title": p.title, "status": p.status, "progress": p.progress, "tags": p.tags} for p in projects]
        })

class NotebookManagerView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        title = request.data.get('title', 'Nuevo Cuaderno')
        color = request.data.get('color', 'border-blue-400')
        notebook = Notebook.objects.create(user=request.user, title=title, color=color)
        return Response({"id": str(notebook.id), "title": notebook.title})

class ProjectManagerView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        title = request.data.get('title', 'Nuevo Proyecto')
        project = Project.objects.create(user=request.user, title=title)
        return Response({"id": str(project.id), "title": project.title})


# --- VISTAS DE CHAT ACTUALIZADAS ---

class SessionManagerView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Ahora podemos filtrar si queremos ver solo los chats de un proyecto o cuaderno
        notebook_id = request.query_params.get('notebook_id')
        project_id = request.query_params.get('project_id')
        
        sessions = ChatSession.objects.filter(user=request.user).order_by('-created_at')
        
        if notebook_id:
            sessions = sessions.filter(notebook_id=notebook_id)
        if project_id:
            sessions = sessions.filter(project_id=project_id)
            
        data = [{"id": str(s.id), "title": s.title or "Chat sin título"} for s in sessions]
        return Response(data)

    def post(self, request):
        notebook_id = request.data.get('notebook_id')
        project_id = request.data.get('project_id')
        
        session = ChatSession.objects.create(
            user=request.user, 
            title="Nueva conversación",
            notebook_id=notebook_id,
            project_id=project_id
        )
        return Response({"id": str(session.id), "title": session.title})

class SessionChatView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, session_id):
        session = get_object_or_404(ChatSession, id=session_id, user=request.user)
        profile, _ = AIProfile.objects.get_or_create(user=request.user)
        
        messages = session.messages.all().order_by('created_at')
        messages_data = [{"role": msg.role, "content": msg.content} for msg in messages]
        
        # OJO ACÁ: Ya no devolvemos una lista plana, devolvemos un diccionario con metadata
        return Response({
            "messages": messages_data,
            "meta": {
                "message_count": session.message_count,
                "limit": profile.context_warning_limit
            }
        })

    def post(self, request, session_id):
        session = get_object_or_404(ChatSession, id=session_id, user=request.user)
        profile, _ = AIProfile.objects.get_or_create(user=request.user)
        
        user_text = request.data.get('message')
        modelo_elegido = request.data.get('model', 'gemini-2.5-flash')

        if not user_text:
            return Response({"error": "Mensaje vacío"}, status=400)

        # Al guardar, el modelo suma +1 automático
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
                 raise ValueError("La API devolvió una respuesta vacía o bloqueada.")
                 
            model_text = response.text

            match = re.search(r'\[GUARDAR_MEMORIA:\s*(.*?)\]', model_text)
            if match:
                hecho_a_guardar = match.group(1).strip()
                GlobalMemory.objects.create(user=request.user, fact=hecho_a_guardar)
                model_text = re.sub(r'\[GUARDAR_MEMORIA:\s*(.*?)\]', '', model_text).strip()

            if session.title == "Nueva conversación" and session.messages.count() <= 2:
                session.title = user_text[:30] + "..."
                session.save()

            # Al guardar, suma +1 automático
            ChatMessage.objects.create(session=session, role='model', content=model_text)
            
            # Refrescamos para traer el contador actualizado de la DB
            session.refresh_from_db()

            return Response({
                "role": "model", 
                "content": model_text,
                "meta": {
                    "message_count": session.message_count,
                    "limit": profile.context_warning_limit
                }
            })

        except Exception as e:
            print("🔥" * 20)
            print(f"🔥 ERROR EN ENTITY: {str(e)}")
            traceback.print_exc() 
            print("🔥" * 20)
            return Response({"error": str(e)}, status=500)