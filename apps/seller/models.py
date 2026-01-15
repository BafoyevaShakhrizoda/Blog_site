from django.db import models
from django.contrib.auth.models import AbstractUser
from apps.users.models import CustomUser


class Seller(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)

    shop_name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    seller_rating = models.FloatField(default=0)
    joined_at = models.DateTimeField(auto_now_add=True)
    shop_balance = models.DecimalField(max_digits=40, decimal_places=2)

    def __str__(self):
        return self.shop_name

    
    

    