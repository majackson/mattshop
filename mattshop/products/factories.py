from datetime import datetime, timezone

import factory
from factory.django import DjangoModelFactory
from faker import Faker


from mattshop.products.models import Product, ProductPrice

faker = Faker()

class ProductPriceFactory(DjangoModelFactory):
    price = faker.pydecimal(min_value=0.01, max_value=1000, right_digits=2)
    effective_from = datetime(2020, 1, 1)

    class Meta:
        model = ProductPrice


class ProductFactory(DjangoModelFactory):
    name = "{}s".format(faker.street_name())  # looks sort of like a product name?
    quantity_in_stock = faker.pyint(min_value=0, max_value=10)
    enabled = True
    prices = factory.RelatedFactory(ProductPriceFactory, factory_related_name='product')

    class Meta:
        model = Product
        skip_postgeneration_save = True
