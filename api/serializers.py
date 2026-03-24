from rest_framework import serializers
from .models import *

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__'


class LabSnippetSerializer(serializers.ModelSerializer):
    class Meta:
        model = LabSnippet
        fields = '__all__'


class ProjectGalleryImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectGalleryImage
        fields = ['id', 'image', 'caption', 'description']


class ProjectSerializer(serializers.ModelSerializer):
    gallery = ProjectGalleryImageSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = '__all__'


class ContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        # Agregamos id, created_at e is_read
        fields = ['id', 'name', 'email', 'subject', 'message', 'created_at', 'is_read']