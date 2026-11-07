from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .cart import Cart
from .forms import CheckoutForm
from .models import Category, Order, OrderItem, Product

PRODUCTS_PER_PAGE = 12


def product_list(request, slug=None):
    products = Product.objects.filter(is_active=True).select_related("category")
    current_category = None

    if slug:
        current_category = get_object_or_404(Category, slug=slug)
        products = products.filter(category=current_category)

    paginator = Paginator(products, PRODUCTS_PER_PAGE)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(
        request,
        "store/product_list.html",
        {
            "page_obj": page_obj,
            "categories": Category.objects.all(),
            "current_category": current_category,
        },
    )


def product_detail(request, slug):
    product = get_object_or_404(
        Product.objects.select_related("category"), slug=slug, is_active=True
    )
    related_products = (
        Product.objects.filter(is_active=True, category=product.category)
        .exclude(pk=product.pk)
        .select_related("category")[:4]
    )
    return render(
        request,
        "store/product_detail.html",
        {"product": product, "related_products": related_products},
    )


def cart_detail(request):
    cart = Cart(request)
    return render(
        request,
        "store/cart.html",
        {"cart_items": list(cart), "cart_total": cart.total()},
    )


@require_POST
def cart_add(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)

    if not product.in_stock:
        messages.error(request, f"{product.name} is out of stock.")
        return redirect(product.get_absolute_url())

    quantity = parse_quantity(request.POST.get("quantity"), fallback=1)
    cart = Cart(request)
    added = cart.add(product, quantity=quantity)

    if added < quantity:
        messages.error(
            request,
            f"Only {added} of {product.name} left in stock, so that is what we added.",
        )
    else:
        messages.success(request, f"{product.name} added to your cart.")

    return redirect("store:cart_detail")


@require_POST
def cart_update(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    quantity = parse_quantity(request.POST.get("quantity"), fallback=1)

    cart = Cart(request)
    if quantity < 1 or not product.in_stock:
        cart.remove(product)
        applied = 0
    else:
        applied = cart.add(product, quantity=quantity, replace=True)

    if is_ajax(request):
        return JsonResponse(
            {
                "quantity": applied,
                "line_total": f"{product.price * applied:.2f}",
                "cart_total": f"{cart.total():.2f}",
                "cart_count": len(cart),
                "stock": product.stock,
                "removed": applied == 0,
            }
        )

    return redirect("store:cart_detail")


@require_POST
def cart_remove(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = Cart(request)
    cart.remove(product)

    if is_ajax(request):
        return JsonResponse(
            {
                "removed": True,
                "cart_total": f"{cart.total():.2f}",
                "cart_count": len(cart),
            }
        )

    messages.success(request, f"{product.name} removed from your cart.")
    return redirect("store:cart_detail")


def parse_quantity(raw, fallback=1):
    try:
        return int(raw)
    except (TypeError, ValueError):
        return fallback


def is_ajax(request):
    return request.headers.get("X-Requested-With") == "XMLHttpRequest"


@login_required
def checkout(request):
    cart = Cart(request)
    cart_items = list(cart)

    if not cart_items:
        messages.error(request, "Your cart is empty.")
        return redirect("store:product_list")

    if request.method == "POST":
        form = CheckoutForm(request.POST)
        if form.is_valid():
            try:
                order = place_order(request, form)
            except OutOfStock as problem:
                messages.error(request, str(problem))
                return redirect("store:cart_detail")

            cart.clear()
            messages.success(request, f"Order #{order.pk} placed. Thank you.")
            return redirect(order.get_absolute_url())
    else:
        form = CheckoutForm(
            initial={
                "full_name": request.user.get_full_name(),
                "email": request.user.email,
            }
        )

    return render(
        request,
        "store/checkout.html",
        {"form": form, "cart_items": cart_items, "cart_total": cart.total()},
    )


class OutOfStock(Exception):
    pass


@transaction.atomic
def place_order(request, form):
    cart = Cart(request)
    quantities = {int(key): value["quantity"] for key, value in cart.cart.items()}

    products = Product.objects.select_for_update().filter(id__in=quantities.keys())
    products_by_id = {product.id: product for product in products}

    if len(products_by_id) != len(quantities):
        raise OutOfStock("A product in your cart is no longer available.")

    for product_id, quantity in quantities.items():
        product = products_by_id[product_id]
        if quantity > product.stock:
            raise OutOfStock(
                f"Only {product.stock} of {product.name} left in stock. "
                "Please update your cart."
            )

    total = sum(
        products_by_id[product_id].price * quantity
        for product_id, quantity in quantities.items()
    )

    order = form.save(commit=False)
    order.user = request.user
    order.total = total
    order.save()

    for product_id, quantity in quantities.items():
        product = products_by_id[product_id]
        OrderItem.objects.create(
            order=order,
            product=product,
            product_name=product.name,
            price=product.price,
            quantity=quantity,
        )
        product.stock -= quantity
        product.save(update_fields=["stock"])

    return order


@login_required
def order_detail(request, pk):
    order = get_object_or_404(
        Order.objects.prefetch_related("items"), pk=pk, user=request.user
    )
    return render(request, "store/order_detail.html", {"order": order})


@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user).prefetch_related("items")
    return render(request, "store/order_list.html", {"orders": orders})
