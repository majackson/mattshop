import json

from django.contrib.auth import get_user_model
from django.test import Client

from rest_framework import status
from rest_framework.authtoken.models import Token

from mattshop.orders.factories import OrderFactory, OrderItemFactory

import pytest

@pytest.mark.django_db
def test_order_history_requires_authentication():
    resp = Client().get('/orders/history/')
    assert resp.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.django_db
@pytest.mark.parametrize(('verb', 'supported'), [
    ('GET', True),
    ('HEAD', True),
    ('POST', False),
    ('PUT', False),
    ('PATCH', False),
    ('DELETE', False),
])
def test_order_history_supported_http_verbs(verb, supported):
    client = Client()
    client_method = getattr(client, verb.lower())
    user = get_user_model().objects.create_user(username='test')
    token, _ = Token.objects.get_or_create(user=user)
    resp = client_method('/orders/history/', HTTP_AUTHORIZATION=f'Token {token.key}')
    expected = status.HTTP_200_OK if supported else status.HTTP_405_METHOD_NOT_ALLOWED
    assert resp.status_code == expected

@pytest.mark.django_db
def test_empty_order_history():
    user = get_user_model().objects.create_user(username='test')
    token, _ = Token.objects.get_or_create(user=user)
    resp = Client().get('/orders/history/', HTTP_AUTHORIZATION=f'Token {token.key}')
    assert resp.status_code == status.HTTP_200_OK
    assert json.loads(resp.content)['results'] == []

@pytest.mark.django_db
def test_order_history_one_order():
    user = get_user_model().objects.create_user(username='test')
    OrderFactory(
        user=user,
        total_price=50,
        items__product_price=25,
        items__quantity=2
    )
    token, _ = Token.objects.get_or_create(user=user)
    resp = Client().get('/orders/history/', HTTP_AUTHORIZATION=f'Token {token.key}')
    assert resp.status_code == status.HTTP_200_OK

    results = json.loads(resp.content)['results']
    assert len(results) == 1
    assert 'id' in results[0]
    assert 'created_at' in results[0]
    assert results[0]['total_price'] == '50.00'
    assert len(results[0]['items']) == 1
    assert results[0]['items'][0]['product_price'] == '25.00'
    assert results[0]['items'][0]['quantity'] == 2

@pytest.mark.django_db
def test_order_history_pages():
    user = get_user_model().objects.create_user(username='test')
    for _ in range(25):  # enough to trigger pagination
        OrderFactory(user=user)
    token, _ = Token.objects.get_or_create(user=user)
    resp = Client().get('/orders/history/', HTTP_AUTHORIZATION=f'Token {token.key}')
    assert resp.status_code == status.HTTP_200_OK

    results = json.loads(resp.content)['results']
    assert len(results) == 20

    resp = Client().get('/orders/history/?page=2', HTTP_AUTHORIZATION=f'Token {token.key}')
    assert resp.status_code == status.HTTP_200_OK

    results = json.loads(resp.content)['results']
    assert len(results) == 5
