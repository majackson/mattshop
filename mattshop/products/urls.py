from django.urls import path

from mattshop.products.views import ProductListView


urlpatterns = [
    path('list/', ProductListView.as_view(), name='product-list-view'),
]
