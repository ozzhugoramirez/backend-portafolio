from django.urls import path
from .views import *

urlpatterns = [
    # Rutas del Workspace
    path('workspace/', WorkspaceDataView.as_view(), name='workspace_data'),
    path('notebooks/', NotebookManagerView.as_view(), name='notebooks_create'),
    path('projects/', ProjectManagerView.as_view(), name='projects_create'),
    
    # --- LA RUTA QUE FALTABA ---
    path('prompts/', CustomPromptsView.as_view(), name='custom_prompts'), 
    
    # Rutas del Chat
    path('sessions/', SessionManagerView.as_view(), name='sessions_list_create'),
    path('sessions/<uuid:session_id>/', SessionChatView.as_view(), name='session_chat'),
]