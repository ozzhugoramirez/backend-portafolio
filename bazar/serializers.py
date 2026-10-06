from rest_framework import serializers

from .models import (
    Category,
    Supplier,
    Product,
    StockMovement,
)


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = [
            "id",
            "name",
        ]


class SupplierSerializer(serializers.ModelSerializer):

    class Meta:
        model = Supplier
        fields = [
            "id",
            "name",
            "email",
            "phone",
            "city",
            "country",
            "active",
        ]


class ProductSerializer(serializers.ModelSerializer):

    category = serializers.CharField()

    supplier = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True
    )

    price = serializers.FloatField(
        min_value=0
    )

    cost = serializers.FloatField(
        min_value=0
    )

    class Meta:
        model = Product

        fields = [
            "id",
            "barcode",
            "name",
            "brand",
            "category",
            "supplier",
            "description",
            "measure",
            "location",
            "price",
            "cost",
            "stock",
            "minimum_stock",
            "active",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]


    def validate_barcode(self, value):

        barcode = value.strip()

        if not barcode:
            raise serializers.ValidationError(
                "El código de barras es obligatorio."
            )

        queryset = Product.objects.filter(
            barcode=barcode
        )

        if self.instance:
            queryset = queryset.exclude(
                pk=self.instance.pk
            )

        if queryset.exists():
            raise serializers.ValidationError(
                "Ya existe un producto con este código."
            )

        return barcode


    def validate_name(self, value):

        name = value.strip()

        if not name:
            raise serializers.ValidationError(
                "El nombre es obligatorio."
            )

        return name


    def validate_category(self, value):

        category = value.strip()

        if not category:
            raise serializers.ValidationError(
                "La categoría es obligatoria."
            )

        return category


    def _get_category(
        self,
        name
    ):

        category = (
            Category.objects
            .filter(
                name__iexact=name
            )
            .first()
        )

        if category:
            return category

        return Category.objects.create(
            name=name.strip()
        )


    def _get_supplier(
        self,
        name
    ):

        if not name:
            return None

        clean_name = name.strip()

        if not clean_name:
            return None

        supplier = (
            Supplier.objects
            .filter(
                name__iexact=clean_name
            )
            .first()
        )

        if supplier:
            return supplier

        return Supplier.objects.create(
            name=clean_name
        )


    def create(
        self,
        validated_data
    ):

        category_name = (
            validated_data.pop(
                "category"
            )
        )

        supplier_name = (
            validated_data.pop(
                "supplier",
                None
            )
        )

        category = self._get_category(
            category_name
        )

        supplier = self._get_supplier(
            supplier_name
        )

        return Product.objects.create(
            category=category,
            supplier=supplier,
            **validated_data
        )


    def update(
        self,
        instance,
        validated_data
    ):

        if "category" in validated_data:

            category_name = (
                validated_data.pop(
                    "category"
                )
            )

            instance.category = (
                self._get_category(
                    category_name
                )
            )


        if "supplier" in validated_data:

            supplier_name = (
                validated_data.pop(
                    "supplier"
                )
            )

            instance.supplier = (
                self._get_supplier(
                    supplier_name
                )
            )


        for attribute, value in validated_data.items():

            setattr(
                instance,
                attribute,
                value
            )


        instance.save()

        return instance


class StockMovementSerializer(
    serializers.ModelSerializer
):

    product_name = serializers.CharField(
        source="product.name",
        read_only=True
    )

    barcode = serializers.CharField(
        source="product.barcode",
        read_only=True
    )

    class Meta:
        model = StockMovement

        fields = [
            "id",
            "product",
            "product_name",
            "barcode",
            "movement_type",
            "quantity",
            "previous_stock",
            "new_stock",
            "note",
            "created_at",
        ]