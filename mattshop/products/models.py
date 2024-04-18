from django.db import models
from datetime import datetime

class Product(models.Model):
    name = models.CharField(max_length=100)
    enabled = models.BooleanField(default=True)
    quantity_in_stock = models.IntegerField()

    def __str__(self):
        return self.name

    def get_current_price(self):
        current_price = self.prices.filter(effective_from__lte=datetime.now()).order_by('-effective_from').first()
        return current_price.price

    class Meta:
        ordering = ['name']

class ProductPrice(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='prices')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    effective_from = models.DateTimeField(db_index=True)