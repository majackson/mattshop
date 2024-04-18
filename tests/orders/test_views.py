import json

from django.contrib.auth import get_user_model
from django.test import Client

from rest_framework import status
from rest_framework.authtoken.models import Token

from mattshop.orders.models import Order
from mattshop.orders.factories import OrderFactory

import pytest

from mattshop.products.factories import ProductFactory


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


@pytest.mark.django_db
def test_order_create_view():
    user = get_user_model().objects.create_user(username='test')
    token, _ = Token.objects.get_or_create(user=user)
    product = ProductFactory(quantity_in_stock=12, prices__price=50)
    resp = Client().put('/orders/create/', json.dumps({
        'items': [{'product_id': product.id, 'quantity': 3}]
    }), content_type='application/json', HTTP_AUTHORIZATION=f'Token {token.key}')

    assert resp.status_code == status.HTTP_201_CREATED

    orders = Order.objects.filter(user=user)
    assert orders.count() == 1


@pytest.mark.django_db
@pytest.mark.parametrize(('verb', 'supported'), [
    ('GET', False),
    ('HEAD', False),
    ('POST', False),
    ('PUT', True),
    ('PATCH', False),
    ('DELETE', False),
])
def test_order_view_supported_http_verbs(verb, supported):
    client = Client()
    client_method = getattr(client, verb.lower())
    user = get_user_model().objects.create_user(username='test')
    token, _ = Token.objects.get_or_create(user=user)
    resp = client_method('/orders/create/', content_type='application/json', HTTP_AUTHORIZATION=f'Token {token.key}')
    expected = status.HTTP_400_BAD_REQUEST if supported else status.HTTP_405_METHOD_NOT_ALLOWED
    assert resp.status_code == expected


@pytest.mark.django_db
def test_order_view_out_of_stock():
    user = get_user_model().objects.create_user(username='test')
    token, _ = Token.objects.get_or_create(user=user)
    product = ProductFactory(quantity_in_stock=1)
    resp = Client().put('/orders/create/', json.dumps({
        'items': [{'product_id': product.id, 'quantity': 3}]
    }), content_type='application/json', HTTP_AUTHORIZATION=f'Token {token.key}')

    assert resp.status_code == status.HTTP_400_BAD_REQUEST

    orders = Order.objects.filter(user=user)
    assert orders.count() == 0
