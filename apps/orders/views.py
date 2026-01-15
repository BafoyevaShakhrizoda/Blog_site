from django.shortcuts import render, get_object_or_404, redirect
from .models import Cart, CartItem, Order, OrderItem
from apps.products.models import Product
from django.contrib.auth.decorators import login_required


@login_required
def cart_list(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    return render(request, "orders/cart_list.html", {"cart": cart})

@login_required
def add_to_cart(request, product_id):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    product = get_object_or_404(Product, id=product_id)
    CartItem.objects.create(cart=cart, product=product, quantity=1, price=product.price)
    return redirect("cart_list")


@login_required
def order_list(request):
    orders = Order.objects.filter(buyer=request.user)
    return render(request, "orders/order_list.html", {"orders": orders})

@login_required
def order_detail(request, pk):
    order = get_object_or_404(Order, id=pk, buyer=request.user)
    return render(request, "orders/order_detail.html", {"order": order})