import json
from .models import *


def querying_data(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    
    return {"items": items, "order": order, "cartItems": cartItems}
