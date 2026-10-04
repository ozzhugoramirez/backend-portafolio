from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.views import View
from .models import *
from .services import get_olo_response

class OloView(View):
    def get(self, request, session_id=None):
        if not session_id:
            nueva_sesion = ChatSession.objects.create()
            return redirect('olo_chat_detail', session_id=nueva_sesion.id)

        session = get_object_or_404(ChatSession, id=session_id)
        mensajes = list(session.messages.all().order_by('created_at'))
        prompts = OloPrompt.objects.all() # Traemos todos tus prompts

        context = {
            'session': session,
            'mensajes': mensajes,
            'prompts': prompts, # Los pasamos al HTML
        }
        return render(request, "pages/OLO/index.html", context)

    def post(self, request, session_id):
        session = get_object_or_404(ChatSession, id=session_id)
        user_text = request.POST.get('message', '').strip()
        
        # ⚠️ IMPORTANTE: Capturamos el prompt seleccionado y lo guardamos en la sesión
        prompt_id = request.POST.get('prompt_id')
        if prompt_id:
            try:
                session.prompt = OloPrompt.objects.get(id=prompt_id)
                session.save()
            except OloPrompt.DoesNotExist:
                pass

        if user_text:
            ChatMessage.objects.create(session=session, role='user', text=user_text)
            ai_reply = get_olo_response(session, user_text)
            ChatMessage.objects.create(session=session, role='model', text=ai_reply)

        return redirect('olo_chat_detail', session_id=session.id)


# ==========================================
# VISTAS DEL ADMINISTRADOR DE PROMPTS
# ==========================================
class PromptListView(ListView):
    model = OloPrompt
    template_name = 'pages/OLO/prompt_list.html'
    context_object_name = 'prompts'

class PromptCreateView(CreateView):
    model = OloPrompt
    fields = ['name', 'system_instruction']
    template_name = 'pages/OLO/prompt_form.html'
    success_url = reverse_lazy('olo_prompt_list')

class PromptUpdateView(UpdateView):
    model = OloPrompt
    fields = ['name', 'system_instruction']
    template_name = 'pages/OLO/prompt_form.html'
    success_url = reverse_lazy('olo_prompt_list')