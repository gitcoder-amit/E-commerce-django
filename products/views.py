from django.shortcuts import render, redirect
from products.models import *


def get_product(request , slug):
    try:
        product = Product.objects.get(slug =slug)
        context = {'product':product}
        if request.GET.get('size'):
            size = request.GET.get('size')
            price = product.get_product_by_size(size)
            context['selected_size'] = size
            context['updated_price'] = price
            return render(request, 'product/product.html' , context)
        return render(request, 'product/product.html' , context)

    except Exception as e:
        print(e)

