from datetime import datetime

from mattshop.products.factories import ProductFactory, ProductPriceFactory

import pytest

@pytest.mark.django_db
def test_get_current_price():
    product = ProductFactory()
    ProductPriceFactory(product=product, price=100, effective_from=datetime(2021, 1, 1))

    assert product.get_current_price() == 100

@pytest.mark.django_db
def test_get_current_price_multiple_past_prices():
    product = ProductFactory()
    ProductPriceFactory(product=product, price=100, effective_from=datetime(2021, 1, 1))
    ProductPriceFactory(product=product, price=120, effective_from=datetime(2022, 1, 1))
    ProductPriceFactory(product=product, price=140, effective_from=datetime(2024, 1, 1))

    assert product.get_current_price() == 140

@pytest.mark.django_db
def test_get_current_price_with_future_price():
    product = ProductFactory()
    ProductPriceFactory(product=product, price=100, effective_from=datetime(2021, 1, 1))
    ProductPriceFactory(product=product, price=120, effective_from=datetime(2022, 1, 1))
    ProductPriceFactory(product=product, price=140, effective_from=datetime(2249, 1, 1))

    assert product.get_current_price() == 120