from django.contrib import admin

# Register your models here.
from .models import UserCartItems, Order


class OrderAdmin(admin.ModelAdmin):
    list_display = ['buyer', 'seller', 'status', 'created_at']

admin.site.register(Order, OrderAdmin)
admin.site.register(UserCartItems)
