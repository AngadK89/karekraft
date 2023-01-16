import json
from .models import *


def queryingData(request):
    'Queries open order/cart and cart item associated with customer'

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False) #Retrieves customer's open cart
        items = order.orderitem_set.all()   #Returns list of all orderitem records associated with customer's order record 
                                            #i.e., list of all products in customer's open cart

        cartItems = order.get_cart_items    #Uses getter method of Order class to return total number of items in cart
    
    return {"items": items, "order": order, "cartItems": cartItems}

