#portafolio/core/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


from django.conf import settings
from .views import *
from django.conf.urls import  handler404
from django.contrib.auth.views import LogoutView


#handler404 = page_not_found

urlpatterns = [
    path('admin/', admin.site.urls),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('login/', LoginView.as_view(), name='login'),
    path("logout/",LogoutView.as_view(next_page="/login/"),name="logout"),
    
 
   # Rutas para el Login
    path('api/auth/passkey/login/options/', PasskeyLoginOptionsAPIView.as_view(), name='passkey_login_options'),
    path('api/auth/passkey/login/verify/', PasskeyLoginVerifyAPIView.as_view(), name='passkey_login_verify'),

    # Rutas para el Registro
    path('api/auth/passkey/register/options/', PasskeyRegisterOptionsAPIView.as_view(), name='passkey_register_options'),
    path('api/auth/passkey/register/verify/', PasskeyRegisterVerifyAPIView.as_view(), name='passkey_register_verify'),
    path('api/', include('api.urls')),
    path("", HomeView.as_view(), name="home"),
   
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


