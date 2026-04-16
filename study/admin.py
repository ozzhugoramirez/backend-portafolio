from django.contrib import admin
from .models import *


admin.site.register(AIProfile)
admin.site.register(CustomPrompt)
admin.site.register(ChatMessage)
admin.site.register(ChatSession)
admin.site.register(GlobalMemory)
