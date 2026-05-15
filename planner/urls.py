from django.urls import path
from .views import *
urlpatterns = [
    # Proyectos
    path('projects/', WorkProjectListCreateAPIView.as_view(), name='work-project-list'),
    path('projects/<int:pk>/', WorkProjectDetailAPIView.as_view(), name='work-project-detail'),
    
    # Módulos
    path('modules/', WorkModuleListCreateAPIView.as_view(), name='work-module-list'),
    path('modules/<int:pk>/', WorkModuleDetailAPIView.as_view(), name='work-module-detail'),
    
    # Logs
    path('logs/', WorkLogListCreateAPIView.as_view(), name='work-log-list'),
    path('logs/<int:pk>/', WorkLogDetailAPIView.as_view(), name='work-log-detail'),
]