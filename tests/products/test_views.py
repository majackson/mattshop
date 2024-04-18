import json

from django.test import Client

from rest_framework import status

from mattshop.products.factories import ProductFactory

import pytest

@pytest.mark.django_db
def test_product_list_empty_list_view():
    resp = Client().get('/products/list/')
    assert resp.status_code == status.HTTP_200_OK
    assert json.loads(resp.content)['results'] == []


@pytest.mark.django_db
@pytest.mark.parametrize(('verb', 'supported'), [
    ('GET', True),
    ('HEAD', True),
    ('POST', False),
    ('PUT', False),
    ('PATCH', False),
    ('DELETE', False),
])
def test_product_list_supported_http_verbs(verb, supported):
    client = Client()
    client_method = getattr(client, verb.lower())
    resp = client_method('/products/list/')
    expected = status.HTTP_200_OK if supported else status.HTTP_405_METHOD_NOT_ALLOWED
    assert resp.status_code == expected

@pytest.mark.django_db
def test_product_list_view_unpaginated():
    ProductFactory(enabled=True, name='rice (kgs)', quantity_in_stock=5, prices__price='10.00')
    resp = Client().get('/products/list/')
    assert resp.status_code == status.HTTP_200_OK
    product_data = json.loads(resp.content)['results']
    assert len(product_data) == 1
    product = product_data[0]

    assert product['name'] == 'rice (kgs)'
    assert product['quantity_in_stock'] == 5
    assert product['price'] == 10.00


@pytest.mark.django_db
def test_product_list_view_unpaginated():
    ProductFactory(name='rice (kgs)', quantity_in_stock=5, prices__price='10.00')
    resp = Client().get('/products/list/')
    assert resp.status_code == status.HTTP_200_OK
    product_data = json.loads(resp.content)['results']
    assert len(product_data) == 1
    product = product_data[0]

    assert 'id' in product
    assert product['name'] == 'rice (kgs)'
    assert product['quantity_in_stock'] == 5
    assert product['price'] == '10.00'


@pytest.mark.django_db
def test_product_list_view_pages():
    for _ in range(25):  # enough to cause paging
        ProductFactory()

    resp = Client().get('/products/list/')
    assert resp.status_code == status.HTTP_200_OK
    product_data = json.loads(resp.content)['results']
    assert len(product_data) == 20

    resp = Client().get('/products/list/?page=2')
    assert resp.status_code == status.HTTP_200_OK
    product_data = json.loads(resp.content)['results']
    assert len(product_data) == 5