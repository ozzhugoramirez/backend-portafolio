from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid


class DailyMemory(models.Model):
    # Ahora el usuario puede ser nulo (para la app móvil)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='olo_memories', null=True, blank=True)
    
    # Identificador único para el celular (ej: un UUID que generás en la app móvil)
    device_id = models.CharField(max_length=255, null=True, blank=True)
    
    date = models.DateField(default=timezone.localdate)
    history = models.JSONField(default=list) 

    def __str__(self):
        if self.user:
            return f"Memoria OLO - Web: {self.user.username} ({self.date})"
        return f"Memoria OLO - Móvil: {self.device_id} ({self.date})"






# 1. Comportamientos predefinidos (Tus Prompts)
class OloPrompt(models.Model):
    name = models.CharField(max_length=50, help_text="Ej: Tutor, Examen, General")
    system_instruction = models.TextField(help_text="El prompt de cómo debe actuar.")

    def __str__(self):
        return self.name

# 2. Memoria Global (Lo que Olo recuerda de vos)
class GlobalMemory(models.Model):
    fact = models.TextField(help_text="Dato a recordar. Ej: 'A Seba le gusta Rust'.")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.fact

# 3. La Sesión de Chat Única
class ChatSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    prompt = models.ForeignKey(OloPrompt, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chat {self.id}"

# 4. Los mensajes dentro del chat
class ChatMessage(models.Model):
    session = models.ForeignKey(ChatSession, related_name='messages', on_delete=models.CASCADE)
    role = models.CharField(max_length=10) # 'user' o 'model'
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.role} - {self.created_at.strftime('%H:%M')}"