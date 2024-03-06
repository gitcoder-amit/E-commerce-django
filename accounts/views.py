from cmath import log
from tkinter import E
from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate , login , logout
from django.http import HttpResponseRedirect,HttpResponse
# Create your views here.
from .models import Profile
from products.models import *
from accounts.models import Cart, CartItems
from django.http import HttpResponseRedirect
from django.contrib import messages
import razorpay
from django.conf import settings




def login_page(request):
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user_obj = User.objects.filter(username = email)

        if not user_obj.exists():
            messages.warning(request, 'Account not found.')
            return HttpResponseRedirect(request.path_info)


        if not user_obj[0].profile.is_email_verified:
            messages.warning(request, 'Your account is not verified.')
            return HttpResponseRedirect(request.path_info)

        user_obj = authenticate(username = email , password= password)
        if user_obj:
            login(request , user_obj)
            return redirect('/')

        

        messages.warning(request, 'Invalid credentials')
        return HttpResponseRedirect(request.path_info)


    return render(request ,'accounts/login.html')


def register_page(request):

    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        user_obj = User.objects.filter(username = email)

        if user_obj.exists():
            messages.warning(request, 'Email is already taken.')
            return HttpResponseRedirect(request.path_info)

        print(email)

        user_obj = User.objects.create(first_name = first_name , last_name= last_name , email = email , username = email)
        user_obj.set_password(password)
        user_obj.save()

        messages.success(request, 'An email has been sent on your mail.')
        return HttpResponseRedirect(request.path_info)


    return render(request ,'accounts/register.html')




def activate_email(request , email_token):
    try:
        user = Profile.objects.get(email_token= email_token)
        user.is_email_verified = True
        user.save()
        return redirect('/accounts/login')
    except Exception as e:
        return HttpResponse('Invalid Email token')


def cart(request):
    cart_obj = None
    try:
        cart_obj = Cart.objects.get(is_paid = False, user = request.user)
    except Exception as e:
        print(e)

    # context['cart_items'] = Cart.objects.filter(is_paid = False, user = request.user).first().cart_items.all()
    if request.method == 'POST':
        coupon = request.POST.get('coupon')
        coupon_obj = Coupon.objects.filter(coupon_code__icontains = coupon)
        if not coupon_obj.exists():
            messages.warning(request, 'Invalid Coupon Code')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        if cart_obj.coupon:
            messages.warning(request, 'Coupon already exists')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        
        if cart_obj.get_cart_total() < coupon_obj[0].minimum_amount:
            messages.warning(request, 'total price should be greater than {}'.format(coupon_obj[0].minimum_amount))
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


        cart_obj.coupon = coupon_obj[0]
        cart_obj.save()

        
        context['payment'] = payment

        messages.success(request, 'Coupon added successfully')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    if cart_obj:
        client = razorpay.Client(auth = (settings.KEY, settings.SECRET))
        payment = client.order.create({'amount': cart_obj.get_cart_total()*100, 'currency': 'INR', 'payment_capture': 1})
        cart_obj.razor_pay_order_id = payment['id']
        cart_obj.save()
        context = {'cart': cart_obj, 'cart_items': cart_obj.cart_items.all(), 'payment':payment}

        return render(request, 'accounts/cart.html', context)
    else:
        return HttpResponse("cart is empty")

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

def remove_from_cart(request, uid):
    try:
        cart_item = CartItems.objects.get(uid =uid)
        cart_item.delete()
    except Exception as e:
        print(e)
        
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def remove_coupon(request, cart_uid):
    cart_obj = Cart.objects.get(uid = cart_uid)
    cart_obj.coupon = None
    cart_obj.save()
    messages.success(request, 'Coupon removed successfully')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))



def success(request):
    order_id = request.GET.get('order_id')
    cart = Cart.objects.get(razor_pay_order_id = order_id)
    cart.is_paid = True
    cart.save()
    return HttpResponse('Payment Success')