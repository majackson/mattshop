from django.views import View
from rest_framework.generics import ListAPIView, CreateAPIView

from mattshop.orders.models import Order
from mattshop.orders.serializers import OrderSerializer


class OrderListView(ListAPIView):
    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


class OrderCreateView(View):
    pass