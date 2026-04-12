from django.urls import path
from .views import EntityChatView

urlpatterns = [
    path('session/', EntityChatView.as_view(), name='chat_session'),
]