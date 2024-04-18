from django.urls import path

from mattshop.healthcheck.views import heartbeat


urlpatterns = [
    path('heartbeat/', heartbeat, name='heartbeat'),
]
