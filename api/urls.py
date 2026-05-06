from django.urls import include, path
from .views import *

# Importamos las vistas de passkeys que están en tu app study
from study.views import (
    PasskeyLoginOptionsAPIView,
    PasskeyLoginVerifyAPIView,
    PasskeyRegisterOptionsAPIView,
    PasskeyRegisterVerifyAPIView,
    PasskeyListView 
)




urlpatterns = [
    path('study/', include('study.urls')),

    path('token/', CustomLoginAPIView.as_view(), name='token_obtain_pair'),

    path('profile/', ProfileAPIView.as_view(), name='api-profile'),
    
    path('projects/', ProjectListAPIView.as_view(), name='api-project-list'),
    path('projects/<slug:slug>/', ProjectDetailAPIView.as_view(), name='api-project-detail'),

    path('lab/', LabSnippetListAPIView.as_view(), name='api-lab-list'),
    path('lab/<int:pk>/', LabSnippetDetailAPIView.as_view(), name='api-lab-detail'),

    path('track/', TrackEventAPIView.as_view(), name='api-track-event'),
    path('dashboard/stats/', DashboardStatsAPIView.as_view(), name='api-dashboard-stats'),
    path('dashboard/stats/clear/', ClearTelemetryAPIView.as_view(), name='api-clear-telemetry'),

    path('contact/', ContactAPIView.as_view(), name='contact-api'),
    path('admin/messages/', AdminMessageAPIView.as_view(), name='admin-messages'), 
    path('admin/messages/<int:pk>/read/', MarkMessageReadAPIView.as_view(), name='mark-message-read'),

  
    path('auth/passkey/login/options/', PasskeyLoginOptionsAPIView.as_view(), name='passkey_login_options'),
    path('auth/passkey/login/verify/', PasskeyLoginVerifyAPIView.as_view(), name='passkey_login_verify'),
    path('auth/passkey/register/options/', PasskeyRegisterOptionsAPIView.as_view(), name='passkey_register_options'),
    path('auth/passkey/register/verify/', PasskeyRegisterVerifyAPIView.as_view(), name='passkey_register_verify'),
 
    path('auth/passkey/list/', PasskeyListView.as_view(), name='passkey_list'),
]