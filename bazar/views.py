from django.shortcuts import render

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import Producto
from .serializers import ProductoSerializer

# 1. Para crear un producto nuevo (POST) o listar todos (GET)
class ProductoListCreateView(generics.ListCreateAPIView):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer

# 2. Para buscar (GET) o editar (PUT/PATCH) por Código de Barras
class ProductoDetailByBarcodeView(APIView):
    """
    Maneja las peticiones de un producto específico usando su código de barras.
    """
    def get(self, request, codigo_barras):
        try:
            producto = Producto.objects.get(codigo_barras=codigo_barras)
            serializer = ProductoSerializer(producto)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Producto.DoesNotExist:
            # Si no existe, devolvemos 404. Tu frontend leerá este 404 y abrirá el formulario de creación.
            return Response(
                {"detail": "Producto no encontrado."}, 
                status=status.HTTP_404_NOT_FOUND
            )

    def put(self, request, codigo_barras):
        # Actualiza el producto si se edita desde el frontend
        producto = get_object_or_404(Producto, codigo_barras=codigo_barras)
        # partial=True permite actualizar solo algunos campos si no envías todos
        serializer = ProductoSerializer(producto, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)