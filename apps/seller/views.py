from django.shortcuts import render, redirect, get_object_or_404
from .models import Product
from django.contrib.auth.decorators import login_required

@login_required
def product_list(request):
    products = Product.objects.all()
    return render(request, "seller/product_list.html", {"products": products})

@login_required
def product_create(request):
    # Только seller может создавать продукт
    if not hasattr(request.user, "seller"):
        return redirect("product_list")

    if request.method == "POST":
        title = request.POST["title"]
        price = request.POST["price"]
        seller = request.user.seller
        Product.objects.create(title=title, price=price, seller=seller)
        return redirect("product_list")

    return render(request, "seller/product_create.html")