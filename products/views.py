from django.shortcuts import render, redirect
from products.models import *
from accounts.models import Cart, CartItems
from django.http import HttpResponseRedirect


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

def add_to_cart(request, uid):
    variant = request.GET.get("variant")
    product = Product.objects.get(uid =uid)
    user = request.user
    cart, _ = Cart.objects.get_or_create(user=user, is_paid=False)
    cart_item = CartItems.objects.create(cart=cart, product=product)
    if variant:
        sizeVariant = SizeVariant.objects.get(size_name=variant)
        cart_item.size_variant = sizeVariant
        cart_item.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
