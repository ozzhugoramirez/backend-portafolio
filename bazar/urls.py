from django.urls import path

from .views import (
    ProductListCreateView,
    ProductByBarcodeView,
    ProductSearchView,
    ProductDetailView,
    ProductRestockView,
    StockMovementListView,
    SupplierListCreateView,
    CategoryListCreateView,
)


app_name = "bazar"


urlpatterns = [

    # Productos
    path(
        "products/",
        ProductListCreateView.as_view(),
        name="products"
    ),

    # Buscar
    path(
        "products/search/",
        ProductSearchView.as_view(),
        name="product-search"
    ),

    # Buscar por código
    path(
        "products/barcode/<str:barcode>/",
        ProductByBarcodeView.as_view(),
        name="product-barcode"
    ),

    # Producto individual
    path(
        "products/<uuid:pk>/",
        ProductDetailView.as_view(),
        name="product-detail"
    ),

    # Reponer
    path(
        "products/<uuid:pk>/restock/",
        ProductRestockView.as_view(),
        name="product-restock"
    ),

    # Movimientos
    path(
        "movements/",
        StockMovementListView.as_view(),
        name="movements"
    ),

    # Proveedores
    path(
        "suppliers/",
        SupplierListCreateView.as_view(),
        name="suppliers"
    ),

    # Categorías
    path(
        "categories/",
        CategoryListCreateView.as_view(),
        name="categories"
    ),
]