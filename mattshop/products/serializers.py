from datetime import datetime

from rest_framework import serializers

from mattshop.products.models import Product


class ProductSerializer(serializers.ModelSerializer):
    price = serializers.SerializerMethodField()

    def get_price(self, obj: Product):
        return "{:.2f}".format(obj.get_current_price())

    class Meta:
        model = Product
        fields = ['id', 'name', 'quantity_in_stock', 'price']