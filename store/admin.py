from django.contrib import admin

from .models import Category, Order, OrderItem, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["name", "category", "price", "stock", "badge", "is_active"]
    list_editable = ["price", "stock", "badge", "is_active"]
    list_filter = ["category", "is_active"]
    search_fields = ["name"]
    prepopulated_fields = {"slug": ("name",)}


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    can_delete = False
    readonly_fields = ["product", "product_name", "price", "quantity"]

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "full_name", "total", "status", "created_at"]
    list_editable = ["status"]
    list_filter = ["status", "created_at"]
    search_fields = ["id", "email", "full_name"]
    readonly_fields = ["user", "full_name", "email", "phone", "address", "city",
                       "postal_code", "total", "created_at"]
    inlines = [OrderItemInline]
