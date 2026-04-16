from django.urls import path, include
from .views import *


urlpatterns = [
    path('sessions/', SessionManagerView.as_view(), name='sessions_list_create'),
    path('sessions/<uuid:session_id>/', SessionChatView.as_view(), name='session_chat'),
]