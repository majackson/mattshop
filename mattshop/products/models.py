from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=100)
    enabled = models.BooleanField(default=True)
    quantity_in_stock = models.IntegerField()

    class Meta:
        ordering = ['name']

class ProductPrice(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='prices')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    effective_from = models.DateTimeField(db_index=True)