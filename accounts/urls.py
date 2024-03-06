from django.urls import path
from accounts.views import login_page,register_page , activate_email, success , add_to_cart, cart, remove_from_cart, remove_coupon
# from products.views import add_to_cart

urlpatterns = [
   path('login/' , login_page , name="login" ),
   path('register/' , register_page , name="register"),
   path('activate/<email_token>/' , activate_email , name="activate_email"),
   path('add-to-cart/<uid>/' , add_to_cart , name="add_to_cart"),
   path('remove-from-cart/<uid>/', remove_from_cart, name = "remove_from_cart"),
   path('remove-coupon/<cart_uid>/', remove_coupon, name="remove_coupon"),
   path('cart/', cart, name="cart"),
   path('success/', success, name="success")
]
