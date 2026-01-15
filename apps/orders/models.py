# from django.db import models
# from apps.users.models import CustomUser
# from apps.seller.models import Seller
# from apps.products.models import Product
#
# class Order(models.Model):
#     STATUS_CHOICES = [
#         ("cart", "Basket"),
#         ("pending", "Waiting for payment"),
#         ("paid", "Paid"),
#         ("completed", "Completed"),
#     ]
#     buyer = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
#     seller = models.ForeignKey(Seller, on_delete=models.CASCADE)
#
#     status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="cart")
#     created_at = models.DateTimeField(auto_now_add=True)
#
#     def __str__(self):
#         return f"Order #{self.id} - {self.status}"
#
# class UserCartItems(models.Model):
#     order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
#     product = models.ForeignKey(Product, on_delete=models.CASCADE)
#
#     quantity = models.PositiveIntegerField(default=1)
#     price = models.DecimalField(max_digits=10, decimal_places=2)
#
#     def __str__(self):
#         return f"{self.product.title} x {self.quantity}"
#
from django.db import models
from apps.users.models import CustomUser
from apps.seller.models import Seller
from apps.products.models import Product

STATUS_CHOICES = [
    ("cart", "Basket"),
    ("pending", "Waiting for payment"),
    ("paid", "Paid"),
    ("completed", "Completed"),
]
class Cart(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

from apps.products.models import Product

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="cart_items")
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

class Order(models.Model):
    buyer = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="cart")
    created_at = models.DateTimeField(auto_now_add=True)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="order_items")
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)