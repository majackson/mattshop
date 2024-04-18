from datetime import datetime

from rest_framework import serializers

from mattshop.products.models import Product


class ProductSerializer(serializers.ModelSerializer):
    price = serializers.SerializerMethodField()

    def get_price(self, obj: Product):
        latest_price = obj.prices.filter(effective_from__lte=datetime.now()).order_by('-effective_from').first()
        return "{:.2f}".format(latest_price.price)

    class Meta:
        model = Product
        fields = ['id', 'name', 'quantity_in_stock', 'price']