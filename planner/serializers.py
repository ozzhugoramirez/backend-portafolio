from rest_framework import serializers
from .models import WorkProject, WorkModule, WorkLog

class WorkLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkLog
        fields = '__all__'

class WorkModuleSerializer(serializers.ModelSerializer):
    logs = WorkLogSerializer(many=True, read_only=True)

    class Meta:
        model = WorkModule
        fields = '__all__'

class WorkProjectSerializer(serializers.ModelSerializer):
    modules = WorkModuleSerializer(many=True, read_only=True)

    class Meta:
        model = WorkProject
        fields = '__all__'