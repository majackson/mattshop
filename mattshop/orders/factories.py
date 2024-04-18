import factory

from django.contrib.auth import get_user_model
from factory.django import DjangoModelFactory


from mattshop.orders.models import Order, OrderItem
from mattshop.products.factories import ProductFactory

class OrderItemFactory(DjangoModelFactory):
    product = factory.SubFactory(ProductFactory)
    product_price = factory.Faker("pydecimal", min_value=0.01, max_value=1000, right_digits=2)
    quantity = factory.Faker('random_int')

    class Meta:
        model = OrderItem


class OrderFactory(DjangoModelFactory):
    user = factory.SubFactory(get_user_model())
    total_price = factory.Faker("pydecimal", min_value=0.01, max_value=1000, right_digits=2)
    items = factory.RelatedFactory(OrderItemFactory, factory_related_name='order')

    class Meta:
        model = Order
        skip_postgeneration_save = True
