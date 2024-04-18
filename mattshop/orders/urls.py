from django.urls import path

from mattshop.orders.views import OrderListView, OrderCreateView


urlpatterns = [
    path('history/', OrderListView.as_view(), name='order-list-view'),
    path('create/', OrderCreateView.as_view(), name='order-create-view'),
]
