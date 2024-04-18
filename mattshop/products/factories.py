from datetime import datetime

import factory
from factory.django import DjangoModelFactory


from mattshop.products.models import Product, ProductPrice

class ProductPriceFactory(DjangoModelFactory):
    price = factory.Faker("pydecimal", min_value=0.01, max_value=1000, right_digits=2)
    effective_from = datetime(2020, 1, 1)

    class Meta:
        model = ProductPrice


class ProductFactory(DjangoModelFactory):
    name = factory.Faker("street_name")  # looks sort of like a product name?
    quantity_in_stock = factory.Faker("pyint", min_value=0, max_value=10)
    enabled = True
    prices = factory.RelatedFactory(ProductPriceFactory, factory_related_name='product')

    class Meta:
        model = Product
        skip_postgeneration_save = True
