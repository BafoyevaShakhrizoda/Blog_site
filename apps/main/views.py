from django.shortcuts import render
from django.views import View
from apps.products.models import Product

# Create your views here.

class HomeView(View):
    def get(self, request):
        products = Product.objects.all()
        return render(request, "index.html", {'products':products})
