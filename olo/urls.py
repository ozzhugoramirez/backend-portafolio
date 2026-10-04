from django.urls import path
from .views import OloView, PromptListView, PromptCreateView, PromptUpdateView

urlpatterns = [
    # Rutas del Chat
    path('', OloView.as_view(), name='olo_inicio'),
    path('chat/<uuid:session_id>/', OloView.as_view(), name='olo_chat_detail'),
    
    # Rutas del Administrador de Prompts
    path('prompts/', PromptListView.as_view(), name='olo_prompt_list'),
    path('prompts/nuevo/', PromptCreateView.as_view(), name='olo_prompt_create'),
    path('prompts/<int:pk>/editar/', PromptUpdateView.as_view(), name='olo_prompt_update'),
]