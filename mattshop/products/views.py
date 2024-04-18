from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny

from mattshop.products.models import Product
from mattshop.products.serializers import ProductSerializer


class ProductListView(ListAPIView):
    queryset = Product.objects.filter(enabled=True, quantity_in_stock__gt=0)
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]