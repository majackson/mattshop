from rest_framework import status
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from mattshop.orders import exceptions
from mattshop.orders.operations import create_order
from mattshop.orders.models import Order
from mattshop.orders.serializers import OrderSerializer, CreateOrderSerializer


class OrderListView(ListAPIView):
    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


class OrderCreateView(APIView):
    def put(self, request, *args, **kwargs):
        order_data = CreateOrderSerializer(data=request.data)
        if not order_data.is_valid():
            return Response(order_data.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            new_order = create_order(request.user, order_data.validated_data['items'])
            return Response({
                'order_id': new_order.id,
                'message': "Successfully created order"
            }, status=status.HTTP_201_CREATED)
        except exceptions.OutOfStockOrderError:
            return Response({
                'message': "One or more items were out of stock in the quantities you requested - order not created."
            }, status=status.HTTP_400_BAD_REQUEST)
