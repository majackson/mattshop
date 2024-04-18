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

class CreateOrderItemSerializer(serializers.Serializer):
    product_id = serializers.IntegerField(required=True)
    quantity = serializers.IntegerField(required=True)

class CreateOrderSerializer(serializers.Serializer):
    """A serializer to manage the validation of incoming order creation requests."""
    items = CreateOrderItemSerializer(many=True)

    def validate(self, data):
        # check there is at least one thing being ordered
        if len(data['items']) == 0:
            raise serializers.ValidationError("At least one product should be in an order.")

        # check we aren't specifying the same product multiple times - this seems most likely a mistake
        product_ids = [order['product_id'] for order in data['items']]
        if len(product_ids) != len(set(product_ids)):
            raise serializers.ValidationError("Duplicate product specified in the same order.")

        return data
