from django.contrib import admin
from .models import *


class CustomerAdmin(admin.ModelAdmin):
    fields = ("user", "name", "email")
    readonly_fields = ("user", "name", "email")
    list_display = ("user", "name", "email")
    search_fields = ["name", "email", "user__username"]


class ProductAdmin(admin.ModelAdmin):
    fieldsets = [
        ("Product Details", {"fields": ["name", "desc", "category", "image"]}),
        (None, {"fields": ["price", "stock"]}),
    ]

    list_display = ("name", "category", "stock")
    list_filter = ["category"]
    search_fields = ["name"]
    ordering = [
        "name",
    ]


class OrderAdmin(admin.ModelAdmin):
    fieldsets = [
        ("Order Details", {'fields': ["customer", "transaction_id", "date_ordered", "status"]}),
        ("Payment Details", {'fields': ['payment_method', 'paid']}),
    ]
    readonly_fields = ["customer", "transaction_id", "date_ordered", "payment_method"]
    list_display = ["transaction_id", "date_ordered", "status", "paid"]
    list_filter = ["status", "paid", "payment_method"]
    ordering = ["-date_ordered"]


class ShippingAddressAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {"fields": ("customer", "order", "date_added")}),
        ("Shipping Details", {"fields": ("address", "city", "state", "zipcode")}),
    ]

    readonly_fields = [
        "customer",
        "order",
        "address",
        "city",
        "state",
        "zipcode",
        "date_added",
    ]
    list_display = ["address", "customer", "date_added"]
    search_fields = ["address", "city", "state", "zipcode", "customer__name"]


admin.site.register(Customer, CustomerAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem)
admin.site.register(ShippingAddress, ShippingAddressAdmin)
