from django.urls import path
from . import views

urlpatterns = [
    path("cart/", views.cart_list, name="cart_list"),
    path("cart/add/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
    path("orders/", views.order_list, name="order_list"),
    path("orders/<int:pk>/", views.order_detail, name="order_detail"),
]