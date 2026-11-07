from django.conf import settings

from .cart import Cart


def cart_summary(request):
    cart = Cart(request)
    return {"cart_count": len(cart), "show_demo_login": settings.DEBUG}
