from django.db import transaction
from django.db.models import Q

from rest_framework import generics, status

from rest_framework.permissions import AllowAny

from rest_framework.response import Response

from rest_framework.views import APIView


from .models import (
    Product,
    Supplier,
    Category,
    StockMovement,
)

from .serializers import (
    ProductSerializer,
    SupplierSerializer,
    CategorySerializer,
    StockMovementSerializer,
)


# ============================================================
# CONFIGURACIÓN PÚBLICA PARA EL SCANNER
# ============================================================

class PublicScannerMixin:

    authentication_classes = []

    permission_classes = [
        AllowAny
    ]


# ============================================================
# LISTAR / CREAR PRODUCTOS
# ============================================================

class ProductListCreateView(
    PublicScannerMixin,
    generics.ListCreateAPIView
):

    serializer_class = ProductSerializer

    queryset = (
        Product.objects
        .filter(
            active=True
        )
        .select_related(
            "category",
            "supplier"
        )
    )


    def create(
        self,
        request,
        *args,
        **kwargs
    ):

        serializer = self.get_serializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )


        with transaction.atomic():

            product = serializer.save()

            # Si el producto se crea
            # inicialmente con stock,
            # guardamos el movimiento.

            if product.stock > 0:

                StockMovement.objects.create(
                    product=product,
                    movement_type=(
                        StockMovement
                        .MovementType
                        .ENTRY
                    ),
                    quantity=product.stock,
                    previous_stock=0,
                    new_stock=product.stock,
                    note=(
                        "Stock inicial "
                        "al crear el producto."
                    )
                )


        response_serializer = (
            ProductSerializer(
                product
            )
        )


        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED
        )


# ============================================================
# BUSCAR PRODUCTO POR CÓDIGO
# ============================================================

class ProductByBarcodeView(
    PublicScannerMixin,
    APIView
):

    def get(
        self,
        request,
        barcode
    ):

        barcode = barcode.strip()


        product = (
            Product.objects
            .filter(
                barcode=barcode,
                active=True
            )
            .select_related(
                "category",
                "supplier"
            )
            .first()
        )


        if not product:

            return Response(
                {
                    "error": {
                        "code": (
                            "product_not_found"
                        ),
                        "message": (
                            "El producto no "
                            "está registrado."
                        ),
                        "barcode": barcode,
                    }
                },
                status=(
                    status
                    .HTTP_404_NOT_FOUND
                )
            )


        serializer = ProductSerializer(
            product
        )


        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


# ============================================================
# BUSCAR POR NOMBRE / MARCA / CÓDIGO / CATEGORÍA / PROVEEDOR
# ============================================================


class ProductSearchView(
    PublicScannerMixin,
    generics.ListAPIView
):

    serializer_class = ProductSerializer

    # IMPORTANTE:
    # queremos devolver un array JSON directo,
    # no una respuesta paginada.
    pagination_class = None


    def get_queryset(self):

        query = (
            self.request
            .query_params
            .get(
                "q",
                ""
            )
            .strip()
        )


        products = (
            Product.objects
            .filter(
                active=True
            )
            .select_related(
                "category",
                "supplier"
            )
        )


        if query:

            products = products.filter(

                Q(
                    name__icontains=query
                )

                |

                Q(
                    barcode__icontains=query
                )

                |

                Q(
                    brand__icontains=query
                )

                |

                Q(
                    category__name__icontains=query
                )

                |

                Q(
                    supplier__name__icontains=query
                )
            )


        return products[:30]


        

# ============================================================
# VER / ACTUALIZAR PRODUCTO
# ============================================================

class ProductDetailView(
    PublicScannerMixin,
    generics.RetrieveUpdateAPIView
):

    serializer_class = ProductSerializer

    queryset = (
        Product.objects
        .select_related(
            "category",
            "supplier"
        )
    )


# ============================================================
# REPONER STOCK
# ============================================================

class ProductRestockView(
    PublicScannerMixin,
    APIView
):

    def post(
        self,
        request,
        pk
    ):

        quantity = request.data.get(
            "quantity"
        )

        note = (
            request.data
            .get(
                "note",
                ""
            )
            .strip()
        )


        try:
            quantity = int(
                quantity
            )

        except (
            TypeError,
            ValueError
        ):

            return Response(
                {
                    "error": {
                        "code": (
                            "invalid_quantity"
                        ),
                        "message": (
                            "La cantidad debe "
                            "ser un número entero."
                        )
                    }
                },
                status=(
                    status
                    .HTTP_400_BAD_REQUEST
                )
            )


        if quantity <= 0:

            return Response(
                {
                    "error": {
                        "code": (
                            "invalid_quantity"
                        ),
                        "message": (
                            "La cantidad debe "
                            "ser mayor que cero."
                        )
                    }
                },
                status=(
                    status
                    .HTTP_400_BAD_REQUEST
                )
            )


        with transaction.atomic():

            try:

                product = (
                    Product.objects
                    .select_for_update()
                    .select_related(
                        "category",
                        "supplier"
                    )
                    .get(
                        pk=pk,
                        active=True
                    )
                )

            except Product.DoesNotExist:

                return Response(
                    {
                        "error": {
                            "code": (
                                "product_not_found"
                            ),
                            "message": (
                                "Producto no encontrado."
                            )
                        }
                    },
                    status=(
                        status
                        .HTTP_404_NOT_FOUND
                    )
                )


            previous_stock = (
                product.stock
            )


            product.stock += quantity

            product.save(
                update_fields=[
                    "stock",
                    "updated_at",
                ]
            )


            StockMovement.objects.create(
                product=product,
                movement_type=(
                    StockMovement
                    .MovementType
                    .RESTOCK
                ),
                quantity=quantity,
                previous_stock=(
                    previous_stock
                ),
                new_stock=(
                    product.stock
                ),
                note=note
            )


        serializer = ProductSerializer(
            product
        )


        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


# ============================================================
# MOVIMIENTOS
# ============================================================

class StockMovementListView(
    PublicScannerMixin,
    generics.ListAPIView
):

    serializer_class = (
        StockMovementSerializer
    )


    def get_queryset(self):

        queryset = (
            StockMovement.objects
            .select_related(
                "product"
            )
            .all()
        )


        barcode = (
            self.request
            .query_params
            .get(
                "barcode"
            )
        )


        if barcode:

            queryset = queryset.filter(
                product__barcode=barcode
            )


        return queryset[:100]


# ============================================================
# PROVEEDORES
# ============================================================

class SupplierListCreateView(
    PublicScannerMixin,
    generics.ListCreateAPIView
):

    serializer_class = (
        SupplierSerializer
    )

    queryset = (
        Supplier.objects
        .filter(
            active=True
        )
    )


# ============================================================
# CATEGORÍAS
# ============================================================

class CategoryListCreateView(
    PublicScannerMixin,
    generics.ListCreateAPIView
):

    serializer_class = (
        CategorySerializer
    )

    queryset = (
        Category.objects
        .all()
    )