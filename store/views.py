from http.client import HTTPResponse
from telnetlib import STATUS
from django.shortcuts import render, redirect
from .models import *
from django.http import JsonResponse
import datetime
import json
from .utils import querying_data, guestOrder


def store(request):
    cart_data = querying_data(request)
    cartItems = cart_data["cartItems"]
    products = Product.objects.all()
    context = {"products": products, "cartItems": cartItems}
    return render(request, "store/store.html", context)


def cart(request):
    cart_data = querying_data(request)
    items, order, cartItems = (
        cart_data["items"],
        cart_data["order"],
        cart_data["cartItems"],
    )
    context = {"items": items, "order": order, "cartItems": cartItems}
    return render(request, "store/cart.html", context)


def checkout(request):
    cart_data = querying_data(request)
    items, order, cartItems = (
        cart_data["items"],
        cart_data["order"],
        cart_data["cartItems"],
    )
    context = {"items": items, "order": order, "cartItems": cartItems}
    return render(request, "store/checkout.html", context)


def updateItem(request):
    data = json.loads(request.body)
    productId = data["productId"]
    action = data["action"]

    print(f"Product ID: {productId}")
    print(f"Action: {action}")

    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == "add":
        orderItem.quantity += 1
    elif action == "remove":
        orderItem.quantity -= 1

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse("Item was added", safe=False)


def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)

    else:
        customer, order = guestOrder(request, data)

    total = int(data["form"]["total"])
    order.transaction_id = transaction_id

    shipping_address = ShippingAddress(
        customer=customer,
        address=data["shipping"]["address"],
        city=data["shipping"]["city"],
        state=data["shipping"]["state"],
        zipcode=data["shipping"]["zipcode"],
    )
    shipping_address.save()
    order.shipping_address = shipping_address
    order.save()

    if not data['COD']:
        order.razorpayOrder(total*100)
        return JsonResponse({'razorpay_order': order.razorpay_order})
    else:
        return JsonResponse('', safe=False)



def postProcess(request):
    data = json.loads(request.body)

    if not data['COD']:
        order = Order.objects.get(razorpay_order__contains={'order_id': data['order_id']})
        order.razorpay_order['payment_id'] = data['payment_id']
        order.razorpay_order['signature'] = data['signature']
        order.payment_method = 'Razorpay'
        order.paid = True
    else:
        order = Order.objects.get(customer=request.user.customer, complete=False)
        order.payment_method = 'COD'
        order.paid = False

    order.complete = True
    order.save()

    return JsonResponse("Your order has been placed!", safe=False)
