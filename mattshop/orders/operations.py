from django.db import transaction

from mattshop.orders import exceptions
from mattshop.orders.models import Order, OrderItem
from mattshop.products.models import Product


def create_order(user, order_contents):
    """Creates an order with given content.

    Args:
        user (User): User who created the order.
        order_contents (list): The contents of a desired order from the given user. A list of dicts
            with keys 'product_id' and 'quantity'.

    Returns:
        The instance of the newly-created order.

    The tricky part of this task is ensuring the stock deduction happens atomically with the order creation.
    We must ensure that when we check that we have adequate stock to fulfil this order, that further orders for these
    products are blocked until the order has been created, and the stock items have been deducted from the product.
    We do this with django's `select_for_update` queryset method (which maps to a DB row-level locking capability).
    Without this row-level lock, it might be possible for two concurrently-placed orders for the same product to result
    in the same stock being allocated to two separate orders, and an impossible negative stock level being recorded.
    """
    products = Product.objects.select_for_update().filter(
        id__in=[order_item['product_id'] for order_item in order_contents]
    )
    with transaction.atomic():

        # check stock matches order requirements
        for order_item_request in order_contents:
            product = products.get(id=order_item_request['product_id'])
            if order_item_request['quantity'] > product.quantity_in_stock:
                raise exceptions.OutOfStockOrderError(
                    "Insufficient stock level of {} ({}): requested {}, have {}".format(
                        product.name, product.id, order_item_request['quantity'], product.quantity_in_stock
                    )
                )

        # make the order
        order = Order.objects.create(user=user, total_price=0)
        for order_item_request in order_contents:
            product = products.get(id=order_item_request['product_id'])
            order_item = OrderItem.objects.create(
                order=order,
                product=product,
                product_price=product.get_current_price(),
                quantity=order_item_request['quantity']
            )
        order.total_price = sum(item.product_price * item.quantity for item in order.items.all())
        order.save()

        # deduct stock levels from product
        for order_item in order.items.all():
            order_item.product.quantity_in_stock -= order_item.quantity
            order_item.product.save()

    return order