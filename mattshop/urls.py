from django.urls import include, path

urlpatterns = [
    path('healthcheck/', include('mattshop.healthcheck.urls')),
]
