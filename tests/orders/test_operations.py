from django.contrib.auth import get_user_model

from mattshop.products.factories import ProductFactory
from mattshop.orders import exceptions
from mattshop.orders.models import Order
from mattshop.orders.operations import create_order

import pytest


@pytest.mark.django_db
def test_order_create_view():
    user = get_user_model().objects.create_user(username='test')
    product = ProductFactory(quantity_in_stock=12, prices__price=50)

    order = create_order(user, [{'product_id': product.id, 'quantity': 3}])

    orders = Order.objects.filter(user=user)
    assert orders.count() == 1
    assert orders.first().id == order.id

    order = orders[0]
    assert order.items.count() == 1
    assert order.total_price == 150

    order_item = order.items.first()
    assert order_item.product.id == product.id
    assert order_item.quantity == 3

    product.refresh_from_db()
    assert product.quantity_in_stock == 9

@pytest.mark.django_db
def test_order_create_view_multiple_products():
    user = get_user_model().objects.create_user(username='test')
    product1 = ProductFactory(quantity_in_stock=12, prices__price=12)
    product2 = ProductFactory(quantity_in_stock=7, prices__price=15)

    order = create_order(user, [
        {'product_id': product1.id, 'quantity': 2},
        {'product_id': product2.id, 'quantity': 1},
    ])

    orders = Order.objects.filter(user=user)
    assert orders.count() == 1
    assert orders.first().id == order.id

    order = orders[0]
    assert order.items.count() == 2
    assert order.total_price == 39

    product1.refresh_from_db()
    assert product1.quantity_in_stock == 10

    product2.refresh_from_db()
    assert product2.quantity_in_stock == 6

@pytest.mark.django_db
def test_order_create_view_out_of_stock():
    user = get_user_model().objects.create_user(username='test')
    product = ProductFactory(quantity_in_stock=2)

    with pytest.raises(exceptions.OutOfStockOrderError):
        create_order(user, [{'product_id': product.id, 'quantity': 3}])

    orders = Order.objects.filter(user=user)
    assert orders.count() == 0

@pytest.mark.django_db
def test_order_create_view_some_out_of_stock():
    """Test when we order multiple products, but just one of them is out of stock."""
    user = get_user_model().objects.create_user(username='test')
    product1 = ProductFactory(quantity_in_stock=1)
    product2 = ProductFactory(quantity_in_stock=20)

    with pytest.raises(exceptions.OutOfStockOrderError):
        create_order(user, [
            {'product_id': product1.id, 'quantity': 2},
            {'product_id': product2.id, 'quantity': 1}
        ])

    orders = Order.objects.filter(user=user)
    assert orders.count() == 0
