from django.db import models
from apps.seller.models import Seller
from apps.users.models import CustomUser



class Category(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name
    

class Product(models.Model):
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    title = models.CharField(max_length=150)
    description = models.TextField()
    price = models.DecimalField(max_digits=10_000_000, decimal_places=2)
    in_stock = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.title)
    
    class Meta:
        ordering = ('-id',)

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='product_images')

class Comment(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    body = models.CharField(max_length=150)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return "Comment of " + str(self.author.username)