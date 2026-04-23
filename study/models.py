import uuid
from django.db import models
from django.contrib.auth.models import User

# --- PERFIL Y PROMPTS ---

class AIProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='ai_profile')
    ai_name = models.CharField(max_length=50, default="olo")
    user_name = models.CharField(max_length=50, default="Seba")
    default_model = models.CharField(max_length=50, default="gemini-2.5-flash")
    context_warning_limit = models.IntegerField(default=40)
    
    def __str__(self):
        return f"Perfil de {self.ai_name} para {self.user_name}"

class CustomPrompt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100, help_text="Ej: Contexto Enfermería, Contexto Programación")
    prompt_text = models.TextField()
    is_active = models.BooleanField(default=False, help_text="Si es true, se usa como prompt global por defecto.")

    def __str__(self):
        return self.title

# --- CUADERNOS Y PROYECTOS ---

class Notebook(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notebooks')
    title = models.CharField(max_length=255)
    color = models.CharField(max_length=50, default='border-blue-400')
    description = models.TextField(blank=True, null=True)
    
    # NUEVO: Prompt específico de este cuaderno
    system_prompt = models.ForeignKey(CustomPrompt, on_delete=models.SET_NULL, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class Project(models.Model):
    STATUS_CHOICES = [
        ('Planificación', 'Planificación'),
        ('Desarrollo', 'En desarrollo'),
        ('Testing', 'Testing'),
        ('Mantenimiento', 'Mantenimiento'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projects')
    title = models.CharField(max_length=255)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Desarrollo')
    progress = models.IntegerField(default=0)
    tags = models.JSONField(default=list, blank=True)
    
    # NUEVO: Prompt específico de este proyecto
    system_prompt = models.ForeignKey(CustomPrompt, on_delete=models.SET_NULL, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

# --- SESIONES Y MENSAJES ---

class ChatSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_sessions')
    title = models.CharField(max_length=255, default="Nueva Conversación")
    notebook = models.ForeignKey(Notebook, on_delete=models.SET_NULL, null=True, blank=True, related_name='chats')
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True, related_name='chats')
    message_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class ChatMessage(models.Model):
    ROLE_CHOICES = [('user', 'User'), ('model', 'Model')]
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            self.session.message_count += 1
            self.session.save(update_fields=['message_count'])

# --- SISTEMA DE MEMORIA NIVELES MULTIPLES ---

class GlobalMemory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    fact = models.TextField() # Ej: "Seba es autodidacta"
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Global: {self.fact[:30]}"

class NotebookMemory(models.Model):
    notebook = models.ForeignKey(Notebook, on_delete=models.CASCADE, related_name='memories')
    fact = models.TextField() # Ej: "La fórmula de la presión arterial es..."
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cuaderno ({self.notebook.title}): {self.fact[:30]}"

class ProjectMemory(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='memories')
    fact = models.TextField() # Ej: "Usamos Django 5.0 en este proyecto"
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Proyecto ({self.project.title}): {self.fact[:30]}"