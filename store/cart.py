from decimal import Decimal

from .models import Product

CART_SESSION_KEY = "cart"


class Cart:
    def __init__(self, request):
        self.session = request.session
        self.cart = self.session.setdefault(CART_SESSION_KEY, {})

    def __iter__(self):
        products = Product.objects.filter(id__in=self.cart.keys())
        for product in products:
            quantity = self.cart[str(product.id)]["quantity"]
            yield {
                "product": product,
                "quantity": quantity,
                "line_total": product.price * quantity,
            }

    def __len__(self):
        return sum(item["quantity"] for item in self.cart.values())

    def add(self, product, quantity=1, replace=False):
        key = str(product.id)
        current = self.cart.get(key, {"quantity": 0})["quantity"]
        new_quantity = quantity if replace else current + quantity
        new_quantity = max(1, min(new_quantity, product.stock))
        self.cart[key] = {"quantity": new_quantity}
        self.save()
        return new_quantity

    def remove(self, product):
        self.cart.pop(str(product.id), None)
        self.save()

    def clear(self):
        self.session[CART_SESSION_KEY] = {}
        self.cart = self.session[CART_SESSION_KEY]
        self.save()

    def total(self):
        return sum((item["line_total"] for item in self), Decimal("0.00"))

    def save(self):
        self.session[CART_SESSION_KEY] = self.cart
        self.session.modified = True
