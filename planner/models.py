from django.db import models

class WorkProject(models.Model):
    """El contenedor principal. Ej: Silo, Vexa."""
    STATUS_CHOICES = (
        ('active', 'Activo'),
        ('paused', 'Pausado'), # Siempre es bueno tener un estado de pausa
        ('completed', 'Completado'),
        ('cancelled', 'Cancelado'),
    )

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, help_text="Visión general del proyecto")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Útiles para tu control personal
    repository_url = models.URLField(blank=True, null=True)
    target_date = models.DateField(blank=True, null=True, help_text="Fecha estimada de finalización")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class WorkModule(models.Model):
    """Las partes o componentes del proyecto. Ej: Barra de tareas, Autenticación."""
    STATUS_CHOICES = (
        ('todo', 'Por hacer'),
        ('in_progress', 'En progreso'),
        ('testing', 'En pruebas'),
        ('done', 'Listo'),
    )
    PRIORITY_CHOICES = (
        ('low', 'Baja'),
        ('medium', 'Media'),
        ('high', 'Alta'),
    )

    # Relación fuerte: Si borrás el proyecto, se borran sus módulos (CASCADE)
    project = models.ForeignKey(WorkProject, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='todo')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.project.title} - {self.title}"

class WorkLog(models.Model):
    """El historial o registro de lo que vas haciendo en cada módulo."""
    LOG_TYPES = (
        ('feature', 'Nueva Función'),
        ('bugfix', 'Corrección de Error'),
        ('note', 'Nota / Idea'),
        ('refactor', 'Mejora de Código'),
    )

    module = models.ForeignKey(WorkModule, on_delete=models.CASCADE, related_name='logs')
    version_tag = models.CharField(max_length=50, blank=True, help_text="Ej: v1.0.1, opcional")
    log_type = models.CharField(max_length=20, choices=LOG_TYPES, default='note')
    content = models.TextField(help_text="Registro completo de lo que se hizo")
    
    # Tiempo invertido (opcional, pero excelente para medir tu productividad)
    hours_spent = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at'] # Siempre mostrar los más recientes primero

    def __str__(self):
        return f"Log: {self.module.title} ({self.created_at.strftime('%Y-%m-%d')})"