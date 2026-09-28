from django.urls import path
from .views import OloChatView

urlpatterns = [
    # Puedes cambiar 'chat/' por la ruta que prefieras
    path('chat/', OloChatView.as_view(), name='olo_chat'),
]