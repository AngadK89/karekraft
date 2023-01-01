from http.client import HTTPResponse
from telnetlib import STATUS
from django.shortcuts import render, redirect
from store.forms import SignUpForm
from .models import *
from django.http import JsonResponse
import datetime
import json
from .utils import querying_data
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from .forms import SignUpForm, UpdateUserForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordChangeView
from django.contrib.messages.views import SuccessMessageMixin
import pytz

def store(request):
    if request.user.is_authenticated:
        cart_data = querying_data(request)
        cartItems = cart_data["cartItems"]
    else:
        cartItems = 0
    products = Product.objects.all()
    context = {"products": products, "cartItems": cartItems}
    return render(request, "store/store.html", context)


def search_results(request):
    if request.method == "POST":
        searched = request.POST["searched"]
        products = Product.objects.filter(name__icontains=searched)
        if request.user.is_authenticated:
            cart_data = querying_data(request)
            cartItems = cart_data["cartItems"]
        else:
            cartItems = 0
        context = {"products": products, "cartItems": cartItems}
        return render(request, 'store/search-results.html', context)


def register(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            email = form.cleaned_data.get('email')
            user = authenticate(username=username, password=raw_password)
            messages.success(request, f'Your account has been created!')
            login(request, user)
            customer = Customer(user=user, name=username, email=email)
            customer.save()
            return redirect("store")
    
    else:
        form = SignUpForm()
    context = {'form': form}
    return render(request, 'store/register.html', context)


def login_request(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=raw_password)
            if user is not None:
                login(request, user)
                messages.success(request, f'You have been logged in!')
                return redirect("store")
            else:
                messages.error(request,"Invalid username or password.")
        else:
            messages.error(request,"Invalid username or password.")    
    form = AuthenticationForm()
    context = {'form': form}
    return render(request, 'store/login.html', context)


def logout_request(request):
    logout(request)
    messages.info(request, "You have successfully logged out.") 
    return redirect("store")

@login_required
def view_profile(request):
    customer = request.user.customer
    try:
        orders = Order.objects.filter(customer=customer, complete=True)
        full_order_details = []
        for order in orders:
            cart = OrderItem.objects.filter(order_id=order.id)
            full_order_details.append((order, cart))

    except Order.DoesNotExist:
        full_order_details = None
        # shipping_details = None
    context = {'customer': customer, 'full_order_details': full_order_details}
    return render(request, 'store/view-profile.html', context)


@login_required
def edit_profile(request):
    customer = request.user.customer
    if request.method == 'POST':
        user_form = UpdateUserForm(request.POST, instance=request.user)
        if user_form.is_valid():
            user_form.save()
            username = user_form.cleaned_data.get('username')
            email = user_form.cleaned_data.get('email')
            customer.name = username
            customer.email = email
            customer.save()
            messages.success(request, 'Your profile is updated successfully')
            return redirect("view-profile")
        
    else:
        user_form = UpdateUserForm(instance=request.user)
    context = {'user_form': user_form}
    return render(request, 'store/edit-profile.html', context)


class ChangePasswordView(SuccessMessageMixin, PasswordChangeView):
    template_name = 'store/change-password.html'
    success_message = "Successfully Changed Your Password"
    success_url = reverse_lazy('store')


@login_required
def cart(request):
    cart_data = querying_data(request)
    items, order, cartItems = (
        cart_data["items"],
        cart_data["order"],
        cart_data["cartItems"],
    )
    context = {"items": items, "order": order, "cartItems": cartItems}
    return render(request, "store/cart.html", context)


@login_required
def checkout(request):
    cart_data = querying_data(request)
    items, order, cartItems = (
        cart_data["items"],
        cart_data["order"],
        cart_data["cartItems"],
    )
    customer = request.user.customer
    shippingAddresses = ShippingAddress.objects.filter(customer=customer)
    context = {"items": items, "order": order, "cartItems": cartItems, "shippingAddresses": shippingAddresses}
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
    data = json.loads(request.body)
   
    customer = request.user.customer
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    total = int(data["form"]["total"])
    print(data)
    shipping_address = None 

    try:
        shipping_address = ShippingAddress.objects.get(id=data["shipping"]["id"])

    except KeyError:
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
    order.date_ordered = datetime.datetime.now(pytz.timezone('Asia/Calcutta'))
    order.complete = True
    order.save()

    items = order.orderitem_set.all()
    for item in items:
        product = item.product
        product.stock -= item.quantity
        if product.stock < 0:
            product.stock = 0 
        product.save()

    return JsonResponse("Your order has been placed!", safe=False)
