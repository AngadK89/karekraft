import json
from .models import *


def querying_data(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    
    return {"items": items, "order": order, "cartItems": cartItems}


def guestOrder(request, data):
    print("User is not logged in.")

    print("Cookies: ", request.COOKIES)

    name = data["form"]["name"]
    email = data["form"]["email"]

    cart_data = querying_data(request)
    items = cart_data["items"]

    customer, created = Customer.objects.get_or_create(email=email)
    customer.name = name
    customer.save()

    order = Order.objects.create(
        customer=customer,
        complete=False,
    )

    for item in items:
        product = Product.objects.get(id=item["product"].id)

        orderItem = OrderItem.objects.create(
            product=product, order=order, quantity=item["quantity"]
        )

    return customer, order
