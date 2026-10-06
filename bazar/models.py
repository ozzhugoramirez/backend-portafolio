import uuid

from django.core.validators import MinValueValidator
from django.db import models


class Category(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    name = models.CharField(
        max_length=120,
        unique=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"

    def __str__(self):
        return self.name


class Supplier(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    name = models.CharField(
        max_length=180,
        unique=True
    )

    email = models.EmailField(
        blank=True
    )

    phone = models.CharField(
        max_length=50,
        blank=True
    )

    city = models.CharField(
        max_length=120,
        blank=True
    )

    country = models.CharField(
        max_length=120,
        blank=True
    )

    active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Proveedor"
        verbose_name_plural = "Proveedores"

    def __str__(self):
        return self.name


class Product(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    barcode = models.CharField(
        max_length=80,
        unique=True,
        db_index=True
    )

    name = models.CharField(
        max_length=200,
        db_index=True
    )

    brand = models.CharField(
        max_length=120,
        blank=True
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="products"
    )

    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.SET_NULL,
        related_name="products",
        null=True,
        blank=True
    )

    description = models.TextField(
        blank=True
    )

    measure = models.CharField(
        max_length=100,
        blank=True
    )

    location = models.CharField(
        max_length=150,
        blank=True
    )

    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[
            MinValueValidator(0)
        ]
    )

    cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[
            MinValueValidator(0)
        ]
    )

    stock = models.PositiveIntegerField(
        default=0
    )

    minimum_stock = models.PositiveIntegerField(
        default=0
    )

    active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Producto"
        verbose_name_plural = "Productos"

    def __str__(self):
        return f"{self.name} - {self.barcode}"


class StockMovement(models.Model):

    class MovementType(models.TextChoices):
        ENTRY = "ENTRY", "Entrada"
        RESTOCK = "RESTOCK", "Reposición"
        SALE = "SALE", "Venta"
        EXIT = "EXIT", "Salida"
        ADJUSTMENT = "ADJUSTMENT", "Ajuste"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="movements"
    )

    movement_type = models.CharField(
        max_length=20,
        choices=MovementType.choices
    )

    quantity = models.PositiveIntegerField()

    previous_stock = models.PositiveIntegerField()

    new_stock = models.PositiveIntegerField()

    note = models.CharField(
        max_length=250,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return (
            f"{self.product.name} "
            f"{self.movement_type} "
            f"{self.quantity}"
        )