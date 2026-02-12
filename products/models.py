from django.db import models
from django.contrib.auth.models import User

class Product(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=200)
    condition = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)

    EXCHANGE_CHOICES = [
        ('money', 'Money Only'),
        ('barter', 'Barter Only'),
        ('both', 'Money or Barter'),
    ]

    exchange_type = models.CharField(max_length=10, choices=EXCHANGE_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    barter_description = models.TextField(null=True, blank=True)

    image = models.ImageField(upload_to='products/')

    def __str__(self):
        return self.name
