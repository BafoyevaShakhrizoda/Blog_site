from django.contrib import admin
from .models import Category, Comment, Product, ProductImage

# Register your models here.

class ProductImageInLine(admin.TabularInline):
    model = ProductImage

class ProductAdmin(admin.ModelAdmin):
    list_display = ['title', 'id', 'created_at', 'category', 'seller']
    inlines = [ProductImageInLine]

admin.site.register(Product, ProductAdmin)
admin.site.register(ProductImage)
admin.site.register(Comment)
admin.site.register(Category)