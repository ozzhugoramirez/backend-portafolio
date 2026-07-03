from django.urls import path
from .views import ProductoListCreateView, ProductoDetailByBarcodeView

urlpatterns = [
    # Ej: POST a /api/bazar/productos/ para crear un producto que no existía
    path('productos/', ProductoListCreateView.as_view(), name='producto-list-create'),
    
    # Ej: GET o PUT a /api/bazar/productos/barras/779123456789/
    path('productos/barras/<str:codigo_barras>/', ProductoDetailByBarcodeView.as_view(), name='producto-detail-barcode'),
]