from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import Profile, Project, LabSnippet, ProjectGalleryImage, TelemetryEvent
from .serializers import *
from django.core.mail import send_mail
from django.conf import settings




from django.db.models import Count
from rest_framework.permissions import AllowAny, IsAuthenticated

class ProfileAPIView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get(self, request):
        profile = Profile.objects.first()
        if not profile:
            return Response({})
        serializer = ProfileSerializer(profile)
        return Response(serializer.data)

    def put(self, request):
        profile = Profile.objects.first()
        if not profile:
            profile = Profile()
            
        serializer = ProfileSerializer(profile, data=request.data, partial=True) 
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        print("Errores en Profile PUT:", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)





class ProjectListAPIView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get(self, request):
        show_all = request.query_params.get('all', 'false').lower() == 'true'
        if show_all:
            projects = Project.objects.all()
        else:
            projects = Project.objects.filter(is_public=True)
            
        serializer = ProjectSerializer(projects, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ProjectSerializer(data=request.data)
        if serializer.is_valid():
            # 1. Guardamos el proyecto primero
            project = serializer.save()
            
            # 👉 2. ATRAPAMOS LAS FOTOS DE LA GALERÍA Y LAS GUARDAMOS
            gallery_files = request.FILES.getlist('gallery_images')
            for file in gallery_files:
                ProjectGalleryImage.objects.create(project=project, image=file)

            # Volvemos a serializar para devolver la data actualizada con la galería
            updated_serializer = ProjectSerializer(project)
            return Response(updated_serializer.data, status=status.HTTP_201_CREATED)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ==========================================
# 3. DETALLE, EDICIÓN Y BORRADO DE PROYECTOS 
# ==========================================
class ProjectDetailAPIView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_object(self, slug):
        return get_object_or_404(Project, slug=slug)

    def get(self, request, slug):
        project = self.get_object(slug)
        serializer = ProjectSerializer(project)
        return Response(serializer.data)

    def put(self, request, slug):
        project = self.get_object(slug)
        serializer = ProjectSerializer(project, data=request.data, partial=True)
        if serializer.is_valid():
            # 1. Guardamos los cambios de texto/cover
            project = serializer.save()
            
            # 👉 2. ATRAPAMOS LAS NUEVAS FOTOS DE LA GALERÍA
            # Nota: Esto AGREGA nuevas fotos a las que ya existen.
            gallery_files = request.FILES.getlist('gallery_images')
            for file in gallery_files:
                ProjectGalleryImage.objects.create(project=project, image=file)

            updated_serializer = ProjectSerializer(project)
            return Response(updated_serializer.data)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, slug):
        project = self.get_object(slug)
        project.delete()
        return Response({"message": "Proyecto eliminado"}, status=status.HTTP_204_NO_CONTENT)




class LabSnippetListAPIView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get(self, request):
        show_all = request.query_params.get('all', 'false').lower() == 'true'
        if show_all:
            snippets = LabSnippet.objects.all()
        else:
            snippets = LabSnippet.objects.filter(is_public=True)
            
        serializer = LabSnippetSerializer(snippets, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = LabSnippetSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LabSnippetDetailAPIView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_object(self, pk):
        return get_object_or_404(LabSnippet, pk=pk)

    def get(self, request, pk):
        snippet = self.get_object(pk)
        serializer = LabSnippetSerializer(snippet)
        return Response(serializer.data)

    def put(self, request, pk):
        snippet = self.get_object(pk)
        # partial=True para poder actualizar solo el código o el título si queremos
        serializer = LabSnippetSerializer(snippet, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        snippet = self.get_object(pk)
        snippet.delete()
        return Response({"message": "Snippet eliminado"}, status=status.HTTP_204_NO_CONTENT)
    



class TrackEventAPIView(APIView):
    """ Ruta PÚBLICA: La web le pega a esta ruta silenciosamente para registrar acciones """
    permission_classes = [AllowAny] 

    def post(self, request):
        action = request.data.get('action')
        target = request.data.get('target')
        
        if action and target:
            TelemetryEvent.objects.create(action=action, target=target)
            return Response({"status": "tracked"}, status=status.HTTP_201_CREATED)
            
        return Response({"error": "Faltan datos"}, status=status.HTTP_400_BAD_REQUEST)


class DashboardStatsAPIView(APIView):
    """ Ruta PRIVADA: Tu panel de admin consume esto para armar los gráficos """
    permission_classes = [IsAuthenticated] 

    def get(self, request):
        # 1. Visitas al Home
        total_views = TelemetryEvent.objects.filter(action='view', target='home').count()
        
        # 2. Descargas del CV
        cv_downloads = TelemetryEvent.objects.filter(action='download', target='cv').count()
        
        # 3. Clicks en Redes Sociales (Agrupados por red)
        # Esto te devuelve algo como: [{'target': 'github', 'total': 15}, {'target': 'linkedin', 'total': 8}]
        social_clicks = TelemetryEvent.objects.filter(action='click').values('target').annotate(total=Count('target')).order_by('-total')
        
        # 4. Vistas de Proyectos (Agrupados por proyecto)
        project_views = TelemetryEvent.objects.filter(action='view').exclude(target='home').values('target').annotate(total=Count('target')).order_by('-total')

        return Response({
            "overview": {
                "total_views": total_views,
                "cv_downloads": cv_downloads,
            },
            "social_clicks": list(social_clicks),
            "project_views": list(project_views)
        })
    

class AdminMessageAPIView(APIView):
    permission_classes = [IsAuthenticated] # 🔒 Solo vos podés entrar

    def get(self, request, *args, **kwargs):
        # Traemos todos los mensajes ordenados por el más nuevo primero
        mensajes = ContactMessage.objects.all().order_by('-created_at')
        serializer = ContactMessageSerializer(mensajes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class MarkMessageReadAPIView(APIView):
    permission_classes = [IsAuthenticated] # Solo el admin

    def patch(self, request, pk, *args, **kwargs):
        try:
            mensaje = ContactMessage.objects.get(pk=pk)
            mensaje.is_read = True
            mensaje.save()
            return Response({"status": "Mensaje marcado como leído"}, status=status.HTTP_200_OK)
        except ContactMessage.DoesNotExist:
            return Response({"error": "Mensaje no encontrado"}, status=status.HTTP_404_NOT_FOUND)


class ContactAPIView(APIView):
    permission_classes = [] 

    def post(self, request, *args, **kwargs):
        serializer = ContactMessageSerializer(data=request.data)
        
        if serializer.is_valid():
            mensaje = serializer.save()

            # 1. Asunto
            asunto = f"[SYSTEM_ALERT] Nuevo Payload de: {mensaje.name}"
            
            # 2. Texto plano (por si el correo del receptor no soporta HTML)
            cuerpo_texto = f"Nuevo mensaje de {mensaje.name} ({mensaje.email})\n\n{mensaje.message}"
            
            # 3. Diseño HTML (El diseño hacker para tu Gmail)
            cuerpo_html = f"""
            <div style="font-family: monospace; background-color: #050506; color: #a1a1aa; padding: 30px; border: 1px solid #27272a; border-radius: 8px; max-width: 600px;">
                <h2 style="color: #10b981; margin-top: 0;">[SECURE_PAYLOAD_RECEIVED]</h2>
                <p><strong>Identidad:</strong> <span style="color: #818cf8;">{mensaje.name}</span></p>
                <p><strong>Punto de Retorno:</strong> <a href="mailto:{mensaje.email}" style="color: #818cf8;">{mensaje.email}</a></p>
                <p><strong>Asunto:</strong> {mensaje.subject}</p>
                <hr style="border-color: #27272a; margin: 20px 0;">
                <p style="color: #e4e4e7; white-space: pre-wrap; font-size: 14px;">{mensaje.message}</p>
                <hr style="border-color: #27272a; margin: 20px 0;">
                <p style="font-size: 10px; color: #52525b; text-transform: uppercase;">Generado automáticamente por Command_Center_API</p>
            </div>
            """
            
            try:
                send_mail(
                    subject=asunto,
                    message=cuerpo_texto, # Fallback
                    from_email=settings.EMAIL_HOST_USER, 
                    recipient_list=[settings.DESTINATION_EMAIL], 
                    fail_silently=False,
                    html_message=cuerpo_html # <--- ACÁ LE PASAMOS EL DISEÑO
                )
            except Exception as e:
                print(f"Error enviando correo: {e}")
            
            return Response({"message": "Mensaje enviado y guardado exitosamente."}, status=status.HTTP_201_CREATED)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)