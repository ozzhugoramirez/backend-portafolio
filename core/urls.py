from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


from django.conf import settings
from .views import *
from django.conf.urls import  handler404


#handler404 = page_not_found

urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('api/', include('api.urls')),
    path("", HomeView.as_view(), name="home"),
   
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)