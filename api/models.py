from django.db import models

def default_work_philosophy():
    return [
        {
            "icon": "shield", 
            "title": "Seguridad por Diseño", 
            "desc": "La integridad de los datos es mi prioridad desde la primera línea de código."
        },
        {
            "icon": "zap", 
            "title": "Performance Extrema", 
            "desc": "Optimización constante para lograr la máxima velocidad con el menor consumo de recursos."
        },
        {
            "icon": "heart", 
            "title": "Mente Analítica", 
            "desc": "Resolución de problemas complejos mediante diagnóstico preciso y soluciones escalables."
        }
    ]

def default_education():
    return [
        {
            "date": "2024 - Presente", 
            "title": "Título de la Carrera", 
            "institution": "Nombre de la Institución", 
            "desc": "Breve descripción de los logros o enfoque de la formación."
        }
    ]

def default_arsenal():
    return [
        {
            "category": "Backend & Infra", 
            "skills": ["Python", "Django", "Linux", "Docker"]
        },
        {
            "category": "Frontend", 
            "skills": ["Next.js", "React", "Tailwind CSS"]
        }
    ]

def default_social_links():
    return {
        "github": "https://github.com/",
        "linkedin": "https://linkedin.com/",
        "youtube": "https://youtube.com/",
        "tiktok": "https://tiktok.com/",
        "email": "mailto:correo@ejemplo.com"
    }

def default_certifications():
    return [
        {
            "title": "Google Cybersecurity Certificate",
            "issuer": "Google / Coursera",
            "date": "En progreso (2026)",
            "link": "https://coursera.org/..."
        },
        {
            "title": "AWS Certified Cloud Practitioner",
            "issuer": "Amazon Web Services",
            "date": "Planificado",
            "link": "#"
        }
    ]



class Profile(models.Model):
    
    name = models.CharField(max_length=100, default="Sebastian Villalba")
    hero_title = models.CharField(max_length=200, help_text="Ej: Ingeniería con propósito.")
    bio_p1 = models.TextField(help_text="Primer párrafo (Ej: Camino desde Enfermería...)")
    bio_p2 = models.TextField(help_text="Segundo párrafo (Ej: Rigurosidad aplicada a Software...)")
    
    location = models.CharField(max_length=100, default="Buenos Aires, ARG")
    origin = models.CharField(max_length=100, default="Paraguay")
    languages = models.CharField(max_length=100, default="ES / EN / KR (Basic)")

    social_links = models.JSONField(default=default_social_links, blank=True)
    certifications = models.JSONField(default=default_certifications, blank=True)
    
    profile_photo = models.ImageField(upload_to='profile/', blank=True, null=True)
    cv_file = models.FileField(upload_to='cv/', blank=True, null=True)
    
    work_philosophy = models.JSONField(default=default_work_philosophy, blank=True)
    education = models.JSONField(default=default_education, blank=True)
    arsenal = models.JSONField(default=default_arsenal, blank=True)
    
    is_available = models.BooleanField(default=True, help_text="Punto verde en el footer")
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Perfil Principal - {self.name}"





def default_links():
    return {"github": "https://github.com/tu-usuario/proyecto", "live": "https://proyecto.com"}

def default_metrics():
    return [
        {"label": "Tiempo de Boot", "value": "1.2s", "trend": "-40% vs Default"},
        {"label": "RAM en Idle", "value": "85 MB", "trend": "Ultra ligero"}
    ]

def default_structure():
    return [
        {"type": "folder", "name": "/etc/vexa-core/", "desc": "Configuraciones base"},
        {"type": "file", "name": "security.conf", "desc": "Reglas de firewall"}
    ]

def default_install_steps():
    return [
        {"step": "1. Hacer ejecutable", "code": "chmod +x install.sh"},
        {"step": "2. Ejecutar script", "code": "sudo ./install.sh"}
    ]

def default_changelog():
    return [
        {"version": "v1.0.4", "date": "10 Mar 2026", "updates": ["Mejora A", "Fix B"]}
    ]




class Project(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, help_text="Ej: vexa-os")
    version = models.CharField(max_length=50, blank=True, null=True)
    category = models.CharField(max_length=100)
    type = models.CharField(max_length=100)
    short_description = models.TextField()
    
    icon_name = models.CharField(max_length=50, default="server")
    gradient_class = models.CharField(max_length=100, default="from-zinc-800 via-zinc-900 to-black")
    image_main = models.ImageField(upload_to='projects/main/', blank=True, null=True)
    
   
    youtube_url = models.URLField(blank=True, null=True, help_text="Ej: https://www.youtube.com/watch?v=dQw4w9WgXcQ")

    tech_stack = models.JSONField(default=list, blank=True)
    highlights = models.JSONField(default=list, blank=True)
    prerequisites = models.JSONField(default=list, blank=True)
    links = models.JSONField(default=default_links, blank=True)
    clone_cmd = models.CharField(max_length=255, blank=True, null=True)
  
    metrics = models.JSONField(default=default_metrics, blank=True)
    structure = models.JSONField(default=default_structure, blank=True)
    install_steps = models.JSONField(default=default_install_steps, blank=True)
    changelog = models.JSONField(default=default_changelog, blank=True)

    analysis_text = models.TextField(blank=True)
    core_code = models.TextField(blank=True)
    
    

    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order', '-created_at']

    def __str__(self):
        return f"{self.title} ({self.category})"



class ProjectGalleryImage(models.Model):
    project = models.ForeignKey(Project, related_name='gallery', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='projects/gallery/')
    caption = models.CharField(max_length=150, blank=True)
    description = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"Imagen de galería para {self.project.title}"
    






class LabSnippet(models.Model):
    title = models.CharField(max_length=200, help_text="Ej: Hardening básico en Debian")
    category = models.CharField(max_length=100, help_text="Para filtrar en el sidebar (Ej: Ciberseguridad, Cloud, Scripts)")
    description = models.TextField(help_text="Descripción de para qué sirve este fragmento.")
    
    
    code = models.TextField(help_text="El fragmento de código, script o prompt.")
    language = models.CharField(max_length=50, default="bash", help_text="Lenguaje para el syntax (Ej: bash, json, text, python)")
    icon_name = models.CharField(max_length=50, default="terminal", help_text="Ícono Lucide (Ej: shield, cloud, terminal, sparkles)")
    
   
    tags = models.JSONField(default=list, blank=True, help_text='Ej: ["linux", "ufw", "security"]')
    is_public = models.BooleanField(default=True, help_text="Si es False, se oculta del Lab público")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.category}] {self.title}"






class TelemetryEvent(models.Model):
    
    action = models.CharField(max_length=50, help_text="Ej: view, click, download")
    target = models.CharField(max_length=100, help_text="Ej: home, cv, github, silo-ecommerce")
    
   
    ip_address = models.GenericIPAddressField(null=True, blank=True, help_text="Para evitar spam de F5")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.action}] {self.target} - IP: {self.ip_address} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"


class ContactMessage(models.Model):
    name = models.CharField("Nombre / Entidad", max_length=100)
    email = models.EmailField("Email de Retorno")
    subject = models.CharField("Asunto", max_length=200)
    message = models.TextField("Mensaje")
    created_at = models.DateTimeField("Fecha de Envío", auto_now_add=True)
    is_read = models.BooleanField("Leído", default=False)

    class Meta:
        verbose_name = "Mensaje de Contacto"
        verbose_name_plural = "Mensajes de Contacto"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.subject}"