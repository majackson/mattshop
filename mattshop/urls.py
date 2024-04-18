from django.urls import include, path

urlpatterns = [
    path('healthcheck/', include('mattshop.healthcheck.urls')),
    path('products/', include('mattshop.products.urls')),
    path('auth/', include('mattshop.authentication.urls')),
    path('orders/', include('mattshop.orders.urls')),
]
