from django.test import Client

from rest_framework import status


def test_heartbeat():
    resp = Client().get('/healthcheck/heartbeat/')
    assert resp.status_code == status.HTTP_200_OK
