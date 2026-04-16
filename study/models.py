import uuid
from django.db import models
from django.contrib.auth.models import User

# 1. Configuración global y datos fijos
class AIProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='ai_profile')
    ai_name = models.CharField(max_length=50, default="Entity")
    user_name = models.CharField(max_length=50, default="Seba")
    default_model = models.CharField(max_length=50, default="gemini-2.5-flash")
    
    def __str__(self):
        return f"Perfil de {self.ai_name} para {self.user_name}"

# 2. Prompts Personalizados
class CustomPrompt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    prompt_text = models.TextField()
    is_active = models.BooleanField(default=False) # Para saber cuál usar

    def __str__(self):
        return self.title

# 3. Sesiones de Chat (Ahora con UUID y Título)
class ChatSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100, blank=True) # Para mostrar en la lista
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.title or 'Nueva Sesión'} - {self.id}"

# 4. Mensajes (Memoria de Sesión)
class ChatMessage(models.Model):
    ROLE_CHOICES = (('user', 'User'), ('model', 'Model'))
    session = models.ForeignKey(ChatSession, related_name='messages', on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

# 5. Memoria Global (Lo que le decís explícitamente que recuerde)
class GlobalMemory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    fact = models.TextField() # Ej: "Seba está desarrollando la app Halo"
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.fact