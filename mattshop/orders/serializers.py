from rest_framework import serializers

from mattshop.orders.models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrderItem
        fields = ['product', 'product_price', 'quantity']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ['id', 'created_at', 'total_price', 'items']


class CreateOrderSerializer(serializers.Serializer):
    """A serializer to manage the validation of incoming order creation requests."""
    product_id = serializers.IntegerField(required=True)
    quantity = serializers.IntegerField(required=True)
