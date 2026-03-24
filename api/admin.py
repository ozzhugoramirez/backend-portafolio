from django.contrib import admin
from .models import *

admin.site.register(Profile)
admin.site.register(Project) 
admin.site.register(LabSnippet)
admin.site.register(ProjectGalleryImage)
admin.site.register(TelemetryEvent)
admin.site.register(ContactMessage)
