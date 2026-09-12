#portafolio/api/urls.py

from django.urls import include, path
from .views import *





urlpatterns = [
    path('study/', include('study.urls')),
    path('bazar/', include('bazar.urls')),
   
    path('planner/', include('planner.urls')),

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

  


    path('timeline/', TimelineListCreateAPIView.as_view(), name='timeline-list-create'),
    path('timeline/<slug:slug>/', TimelineDetailAPIView.as_view(), name='timeline-detail'),
    path('timeline/media/<int:pk>/', TimelineMediaDeleteAPIView.as_view(), name='timeline-media-delete'),
]