from django.db import models

class Producto(models.Model):
    codigo_barras = models.CharField(max_length=100, unique=True)
    numero_item = models.CharField(max_length=50, blank=True, null=True)
    nombre = models.CharField(max_length=200)
    proveedor = models.CharField(max_length=150, blank=True, null=True)
    marca = models.CharField(max_length=100, blank=True, null=True)
    stock = models.IntegerField(default=0)
    categorias = models.CharField(max_length=200, blank=True, null=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    descripcion = models.TextField(blank=True, null=True)
    
    # Timestamps para control interno
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nombre} - {self.codigo_barras}"