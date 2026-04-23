from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.conf import settings
from google import genai
from google.genai import types
from datetime import datetime
import re
import traceback

# Importamos absolutamente todos los modelos que armamos
from .models import (
    ChatSession, ChatMessage, AIProfile, GlobalMemory, 
    CustomPrompt, Notebook, Project, NotebookMemory, ProjectMemory
)

client = genai.Client(api_key=settings.GEMINI_API_KEY)

def build_system_prompt(user, session):
    profile, _ = AIProfile.objects.get_or_create(user=user)
    
    memorias_globales = GlobalMemory.objects.filter(user=user).values_list('fact', flat=True)
    mem_global_str = "\n- ".join(memorias_globales) if memorias_globales else "Ninguna todavía."

    contexto_especifico = ""
    memoria_local_str = "Ninguna."
    ubicacion = "General"

    if getattr(session, 'notebook', None):
        ubicacion = f"Cuaderno: {session.notebook.title}"
        if session.notebook.system_prompt:
            contexto_especifico = session.notebook.system_prompt.prompt_text
        memorias_locales = session.notebook.memories.all().values_list('fact', flat=True)
        if memorias_locales: memoria_local_str = "\n- ".join(memorias_locales)
            
    elif getattr(session, 'project', None):
        ubicacion = f"Proyecto: {session.project.title}"
        if session.project.system_prompt:
            contexto_especifico = session.project.system_prompt.prompt_text
        memorias_locales = session.project.memories.all().values_list('fact', flat=True)
        if memorias_locales: memoria_local_str = "\n- ".join(memorias_locales)
            
    else:
        active_prompt = CustomPrompt.objects.filter(user=user, is_active=True).first()
        if active_prompt: contexto_especifico = active_prompt.prompt_text

    user_name = profile.user_name if hasattr(profile, 'user_name') else user.username
    
    base_prompt = f"""
Sos {profile.ai_name}, el asistente personal de {user_name}.
Entorno actual: [{ubicacion}].
Fecha actual: {datetime.now().strftime("%d/%m/%Y %H:%M")}.

=== TU CONTEXTO SOBRE EL USUARIO ===
{mem_global_str}

=== TU MEMORIA DE ESTE ENTORNO ===
{memoria_local_str}

=== INSTRUCCIONES DEL ENTORNO ===
{contexto_especifico if contexto_especifico else 'Compórtate como un asistente experto y directo.'}

=== REGLAS ESTRICTAS DE RESPUESTA (OBLIGATORIO) ===
1. Si el usuario te pide recordar algo local, usa: [GUARDAR_NOTA: dato]. Si es global, usa: [GUARDAR_GLOBAL: dato].
2. SUGERENCIAS DE RESPUESTA: Al final de TU respuesta, SIEMPRE debes dar 3 opciones cortas de lo que el usuario te podría responder o preguntar a continuación para avanzar. Usa estrictamente este formato al final del texto: [SUGERENCIAS: opcion 1 | opcion 2 | opcion 3]
3. YOUTUBE: Si el tema es complejo (medicina, ciencias, programación) y un video ayudaría, recomienda UNO usando estrictamente este formato: [YOUTUBE: https://www.youtube.com/watch?v=ID_DEL_VIDEO]
"""
    return base_prompt


# --- VISTAS DEL DASHBOARD (WORKSPACE) ---

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

class CustomPromptsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        prompts = CustomPrompt.objects.filter(user=request.user)
        # ACÁ ESTABA EL ERROR: Faltaba enviar el 'prompt_text' al frontend
        data = [
            {
                "id": str(p.id), 
                "title": p.title, 
                "prompt_text": p.prompt_text
            } 
            for p in prompts
        ]
        return Response(data)

class NotebookManagerView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        title = request.data.get('title', 'Nuevo Cuaderno')
        color = request.data.get('color', 'border-blue-400')
        prompt_id = request.data.get('prompt_id')
        
        notebook = Notebook.objects.create(
            user=request.user, 
            title=title, 
            color=color,
            system_prompt_id=prompt_id
        )
        return Response({"id": str(notebook.id), "title": notebook.title})

class ProjectManagerView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        title = request.data.get('title', 'Nuevo Proyecto')
        prompt_id = request.data.get('prompt_id')
        
        project = Project.objects.create(
            user=request.user, 
            title=title,
            system_prompt_id=prompt_id
        )
        return Response({"id": str(project.id), "title": project.title})


# --- VISTAS DEL CHAT ---

class SessionManagerView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
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
        
        # Extraemos los nombres para la cabecera del input
        notebook_name = session.notebook.title if getattr(session, 'notebook', None) else None
        prompt_name = None
        if getattr(session, 'notebook', None) and session.notebook.system_prompt:
            prompt_name = session.notebook.system_prompt.title
        elif getattr(session, 'project', None) and session.project.system_prompt:
            prompt_name = session.project.system_prompt.title
        else:
            active = CustomPrompt.objects.filter(user=request.user, is_active=True).first()
            if active:
                prompt_name = active.title

        return Response({
            "messages": messages_data,
            "meta": {
                "message_count": session.message_count,
                "limit": profile.context_warning_limit,
                "notebook_name": notebook_name,
                "prompt_name": prompt_name
            }
        })

    def post(self, request, session_id):
        session = get_object_or_404(ChatSession, id=session_id, user=request.user)
        profile, _ = AIProfile.objects.get_or_create(user=request.user)
        
        user_text = request.data.get('message')
        modelo_elegido = request.data.get('model', profile.default_model)

        if not user_text:
            return Response({"error": "Mensaje vacío"}, status=400)

        # --- MAGIA 1: LIMPIEZA DE INSTRUCCIÓN ---
        instruccion_extra = ""
        clean_user_text = user_text
        match_instruccion = re.search(r'\[INSTRUCCIÓN PARA ESTE MENSAJE:\s*(.*?)\]', user_text)
        
        if match_instruccion:
            instruccion_extra = f"\n\n[INSTRUCCIÓN INYECTADA DEL USUARIO SOLO PARA ESTE TURNO: {match_instruccion.group(1)}]"
            # Borramos la etiqueta para que la BD quede limpia
            clean_user_text = re.sub(r'\[INSTRUCCIÓN PARA ESTE MENSAJE:\s*(.*?)\]', '', user_text).strip()

        # Guardamos el texto LIMPIO en la base de datos
        ChatMessage.objects.create(session=session, role='user', content=clean_user_text)

        db_messages = session.messages.all().order_by('created_at')
        historial = [
            types.Content(role=msg.role, parts=[types.Part.from_text(text=msg.content)])
            for msg in db_messages
        ]

        system_instruction = build_system_prompt(request.user, session)
        # Sumamos la instrucción invisible al cerebro de Gemini
        if instruccion_extra:
            system_instruction += instruccion_extra
            
        config = types.GenerateContentConfig(system_instruction=system_instruction, temperature=0.7)

        try:
            response = client.models.generate_content(model=modelo_elegido, contents=historial, config=config)
            if not response.text: raise ValueError("Respuesta vacía.")
            model_text = response.text

            # --- MAGIA 2: INTERCEPTORES DE MEMORIA ---
            match_global = re.search(r'\[GUARDAR_GLOBAL:\s*(.*?)\]', model_text)
            if match_global:
                GlobalMemory.objects.create(user=request.user, fact=match_global.group(1).strip())
                model_text = re.sub(r'\[GUARDAR_GLOBAL:\s*(.*?)\]', '', model_text).strip()

            match_local = re.search(r'\[GUARDAR_NOTA:\s*(.*?)\]', model_text)
            if match_local:
                hecho_local = match_local.group(1).strip()
                if getattr(session, 'notebook', None): NotebookMemory.objects.create(notebook=session.notebook, fact=hecho_local)
                elif getattr(session, 'project', None): ProjectMemory.objects.create(project=session.project, fact=hecho_local)
                else: GlobalMemory.objects.create(user=request.user, fact=hecho_local)
                model_text = re.sub(r'\[GUARDAR_NOTA:\s*(.*?)\]', '', model_text).strip()

            if session.title == "Nueva conversación" and session.messages.count() <= 2:
                session.title = clean_user_text[:30] + "..."
                session.save()

            ChatMessage.objects.create(session=session, role='model', content=model_text)
            session.refresh_from_db()

            notebook_name = session.notebook.title if getattr(session, 'notebook', None) else None
            prompt_name = session.notebook.system_prompt.title if getattr(session, 'notebook', None) and session.notebook.system_prompt else None

            return Response({
                "role": "model", 
                "content": model_text, # Acá viaja con las [SUGERENCIAS] y el [YOUTUBE], lo limpiaremos en el front
                "meta": {
                    "message_count": session.message_count,
                    "limit": profile.context_warning_limit,
                    "notebook_name": notebook_name,
                    "prompt_name": prompt_name
                }
            })

        except Exception as e:
            traceback.print_exc() 
            return Response({"error": str(e)}, status=500)