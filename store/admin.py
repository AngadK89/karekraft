from django.contrib import admin
from .models import *
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin


class CustomerAdmin(admin.ModelAdmin):
    'Class defining how customer records are displayed to admin'

    fields = ("user", "name", "email")  #All the fields displayed for each customer's record
    readonly_fields = ("user", "name", "email")
    list_display = ("user", "name", "email")
    search_fields = ["name", "email", "user__username"]


class ProductAdmin(admin.ModelAdmin):
    'Class defining how product data is displayed/can be updated by admin'

    #Defines the fields that will be displayed for each product & the headers they will be divided under
    fieldsets = [
        ("Product Details", {"fields": ["name", "desc", "category", "image"]}),
        (None, {"fields": ["price", "stock"]}),
    ]

    list_display = ("name", "category", "stock")    #The fields displayed in the table listing all the products
    list_filter = ["category"]  #Parameters basis which products can be filtered
    search_fields = ["name"]
    ordering = [
        "name",
    ]

class ProductInlineAdmin(admin.TabularInline):
    '''
    Allows products in customer's order to be displayed to the admin under the order summary.
    The admin cannot add/change/delete the details of the customer's order
    '''

    model = Order.products.through
    extra = 0
    can_delete = False

    def has_add_permission(self, request, obj):
        return False

    def has_change_permission(self, request, obj):
        return False


class OrderAdmin(admin.ModelAdmin):
    fieldsets = [
        ("Order Details", {'fields': ["customer", "date_ordered", "status", ]}),
        ("Shipping Details", {'fields': ['shipping_address', ]}),
        ("Payment Details", {'fields': ['payment_method', 'paid']}),
    ]
    readonly_fields = ["customer", "date_ordered", "payment_method", "shipping_address", ]
    list_display = ["id", "date_ordered", "status", "paid", ]
    list_filter = ["status", "paid", "payment_method"]
    ordering = ["-date_ordered"]
    inlines = (ProductInlineAdmin, )


class ShippingAddressAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {"fields": ("customer", "date_added")}),
        ("Shipping Details", {"fields": ("address", "city", "state", "zipcode")}),
    ]

    readonly_fields = [
        "customer",
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