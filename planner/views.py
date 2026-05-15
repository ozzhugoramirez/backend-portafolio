from rest_framework import generics
from rest_framework.permissions import IsAdminUser
from .models import WorkProject, WorkModule, WorkLog
from .serializers import *


class WorkProjectListCreateAPIView(generics.ListCreateAPIView):
    queryset = WorkProject.objects.all().order_by('-updated_at')
    serializer_class = WorkProjectSerializer
    permission_classes = [IsAdminUser] 

class WorkProjectDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = WorkProject.objects.all()
    serializer_class = WorkProjectSerializer
    permission_classes = [IsAdminUser]

# --- MÓDULOS ---
class WorkModuleListCreateAPIView(generics.ListCreateAPIView):
    queryset = WorkModule.objects.all()
    serializer_class = WorkModuleSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        queryset = super().get_queryset()
        project_id = self.request.query_params.get('project_id')
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        return queryset

class WorkModuleDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = WorkModule.objects.all()
    serializer_class = WorkModuleSerializer
    permission_classes = [IsAdminUser]

# --- REGISTROS (LOGS) ---
class WorkLogListCreateAPIView(generics.ListCreateAPIView):
    queryset = WorkLog.objects.all()
    serializer_class = WorkLogSerializer
    permission_classes = [IsAdminUser]

class WorkLogDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = WorkLog.objects.all()
    serializer_class = WorkLogSerializer
    permission_classes = [IsAdminUser]