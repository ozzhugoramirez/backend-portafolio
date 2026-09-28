from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

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