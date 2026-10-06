from django.contrib import admin

from .models import (
    Category,
    Supplier,
    Product,
    StockMovement,
)


@admin.register(Category)
class CategoryAdmin(
    admin.ModelAdmin
):

    search_fields = [
        "name"
    ]


@admin.register(Supplier)
class SupplierAdmin(
    admin.ModelAdmin
):

    list_display = [
        "name",
        "email",
        "phone",
        "active",
    ]

    search_fields = [
        "name",
        "email",
    ]


@admin.register(Product)
class ProductAdmin(
    admin.ModelAdmin
):

    list_display = [
        "name",
        "barcode",
        "category",
        "stock",
        "price",
        "active",
    ]

    search_fields = [
        "name",
        "barcode",
        "brand",
    ]

    list_filter = [
        "active",
        "category",
    ]


@admin.register(StockMovement)
class StockMovementAdmin(
    admin.ModelAdmin
):

    list_display = [
        "product",
        "movement_type",
        "quantity",
        "previous_stock",
        "new_stock",
        "created_at",
    ]

    list_filter = [
        "movement_type"
    ]

    search_fields = [
        "product__name",
        "product__barcode",
    ]