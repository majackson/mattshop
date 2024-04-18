from django.urls import include, path
from rest_framework.authtoken import views

urlpatterns = [
    path('healthcheck/', include('mattshop.healthcheck.urls')),
    path('products/', include('mattshop.products.urls')),
    path('login/', views.obtain_auth_token),
]
