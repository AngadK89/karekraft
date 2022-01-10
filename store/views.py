from django.shortcuts import render
from .models import *
from django.http import JsonResponse
import datetime
import json
from .utils import querying_data, guestOrder

def store(request):
    cart_data = querying_data(request)
    cartItems = cart_data['cartItems']
    products = Product.objects.all()
    context = {'products': products, 'cartItems': cartItems}
    return render(request, 'store/store.html', context)


def cart(request):
    cart_data = querying_data(request)
    items, order, cartItems = cart_data['items'], cart_data['order'], cart_data['cartItems']
    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'store/cart.html', context)


def checkout(request):
    cart_data = querying_data(request)
    items, order, cartItems = cart_data['items'], cart_data['order'], cart_data['cartItems']
    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'store/checkout.html', context)


def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']

    print(f'Product ID: {productId}')
    print(f'Action: {action}')

    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == 'add':
        orderItem.quantity += 1
    elif action == 'remove':
        orderItem.quantity -= 1
    
    orderItem.save()
    
    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse('Item was added', safe=False)


def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)

    else:
        customer, order = guestOrder(request, data)

    total = int(data['form']['total'])
    order.transaction_id = transaction_id

    if total == int(order.get_cart_total):
        order.complete = True
    order.save()

    ShippingAddress.objects.create(
    customer=customer,
    order=order,
    address=data['shipping']['address'],
    city=data['shipping']['city'],
    state=data['shipping']['state'],
    zipcode=data['shipping']['zipcode'],
    )

    return JsonResponse('Payment complete!', safe=False)