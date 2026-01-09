from django.db import models
from apps.users.models import CustomUser
from apps.orders.models import Order


class UserCard(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="cards")

    card_number = models.CharField(max_length=20)
    cardholder_name = models.CharField(max_length=150)
    exp_month = models.PositiveIntegerField()
    exp_year = models.PositiveIntegerField()

    is_default = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.cardholder_name} - {self.card_number[-4:]}"

class Payment(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    card = models.ForeignKey(UserCard, on_delete=models.SET_NULL, null=True)

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    STATUS_CHOICES = [
        ("success", "Success"),
        ("failed", "Failed"),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Payment #{self.id} - {self.status}"

    