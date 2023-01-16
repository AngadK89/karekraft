from http.client import HTTPResponse
from telnetlib import STATUS
from django.shortcuts import render, redirect
from store.forms import SignUpForm
from .models import *
from django.http import JsonResponse
import datetime
import json
from .utils import queryingData
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
    '''Loading up the homepage of the website, 
       including navigation bar and product listing'''

    if request.user.is_authenticated:   #is_authenticated checks if user is logged in
        cart_data = queryingData(request)  #Retrieves customer's open cart (refer to utils.py for queryingData() code)
        cartItems = cart_data["cartItems"]  #Retrieves all items/products in customer's cart
    else:
        cartItems = 0
    products = Product.objects.all()    #Retrieves all products
    context = {"products": products, "cartItems": cartItems}
    return render(request, "store/store.html", context)


def searchResults(request):
    'Searching for products by name basis text input entered by customer'
    if request.method == "POST":
        searched = request.POST["searched"] #Text entered by customer
        products = Product.objects.filter(name__icontains=searched)
        if request.user.is_authenticated:
            cart_data = queryingData(request)
            cartItems = cart_data["cartItems"]
        else:
            cartItems = 0
        context = {"products": products, "cartItems": cartItems}
        return render(request, 'store/search-results.html', context)


def register(request):
    '''
    Registration page of the website. Deals with:
        - Validation of entered registration data
        - Creation of new customer record
        - Subsequent logging in of customer
    '''

    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            email = form.cleaned_data.get('email')
            user = authenticate(username=username, password=raw_password)   #Verifies entered data
            messages.success(request, f'Your account has been created!')
            login(request, user)
            customer = Customer(user=user, name=username, email=email)  
            customer.save() #Saves customer record in database
            return redirect("store")
    
    else:
        #If form validation fails, customer is redirected to sign up again
        form = SignUpForm()
    context = {'form': form}
    return render(request, 'store/register.html', context)


def loginRequest(request):
    '''
    Login page of the website. Deals with:
        - Validation and authentication of entered login data
        - Subsequent logging in of customer
    '''

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)   #Reading login form data
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
    form = AuthenticationForm() #If form validation fails, customer is redirected to login again
    context = {'form': form}
    return render(request, 'store/login.html', context)


def logoutRequest(request):
    'Logging customer out of their account'

    logout(request)
    messages.info(request, "You have successfully logged out.") 
    return redirect("store")

@login_required #Customer must be logged in to access the functionality 
def viewProfile(request):
    'Returns customer account details and all their past orders to display on profile page'

    customer = request.user.customer
    try:
        orders = Order.objects.filter(customer=customer, complete=True) #Returns successfully placed orders
        full_order_details = []
        for order in orders:
            cart = OrderItem.objects.filter(order_id=order.id)
            full_order_details.append((order, cart))    #Every order & its details (products ordered) 
                                                        #stored as a tuple element in a list

    except Order.DoesNotExist:  #Handles exception where customer has no past orders
        full_order_details = None
    context = {'customer': customer, 'full_order_details': full_order_details}
    return render(request, 'store/view-profile.html', context)


@login_required
def editProfile(request):
    'Updating customer information basis data entered into UpdateUserForm'

    customer = request.user.customer
    if request.method == 'POST':
        user_form = UpdateUserForm(request.POST, instance=request.user)
        if user_form.is_valid():
            user_form.save()
            username = user_form.cleaned_data.get('username')
            email = user_form.cleaned_data.get('email')
            customer.name = username    #Updates customer record
            customer.email = email
            customer.save() #Saves updates to record in database
            messages.success(request, 'Your profile is updated successfully')
            return redirect("view-profile")
        
    else:
        #Redirects customer to re-enter data in case form validation fails (invalid data entered)
        user_form = UpdateUserForm(instance=request.user)
    context = {'user_form': user_form}
    return render(request, 'store/edit-profile.html', context)


class ChangePasswordView(SuccessMessageMixin, PasswordChangeView):
    '''Inherits from Django's built-in password change class to provide
       functionality of changing customer's password'''

    template_name = 'store/change-password.html'
    success_message = "Successfully Changed Your Password"
    success_url = reverse_lazy('store')


@login_required
def cart(request):
    '''
    Retrieves all data displayed on cart page: 
        - Products ordered
        - Product quantities
        - Product totals
        - Cart total 
    '''
    
    cart_data = queryingData(request)  #Refer to utils.py for queryingData() code
    items, order, cartItems = (
        cart_data["items"],
        cart_data["order"],
        cart_data["cartItems"],
    )
    context = {"items": items, "order": order, "cartItems": cartItems}
    return render(request, "store/cart.html", context)


@login_required
def checkout(request):
    '''
    Retrieves all data required for checkout page:
        - Order summary data (same data as cart function)
        - Customer's saved shipping addresses
    '''

    cart_data = queryingData(request)
    items, order, cartItems = (
        cart_data["items"],
        cart_data["order"],
        cart_data["cartItems"],
    )
    customer = request.user.customer
    shippingAddresses = ShippingAddress.objects.filter(customer=customer)   #Returns customer's saved shipping addresses
    context = {"items": items, "order": order, "cartItems": cartItems, "shippingAddresses": shippingAddresses}
    return render(request, "store/checkout.html", context)


def updateItem(request):
    '''Adding/Deleting products, or updating product quantities in the customer's cart'''

    data = json.loads(request.body)
    productId = data["productId"]
    action = data["action"] #Tells us what action to perform, i.e., add or remove product to/from cart

    print(f"Product ID: {productId}")
    print(f"Action: {action}")

    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)  
    #Adds orderitem record if product not already in cart, else retrieves orderitem record associated with product

    if action == "add":
        orderItem.quantity += 1
    elif action == "remove":
        orderItem.quantity -= 1

    orderItem.save()    #Saves updates to orderitem record in database

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse("Item was added", safe=False)


def processOrder(request):
    '''
    Processing final data inputs by customer, such as shipping information, 
    and sending required payment data such as the razorpay order in case online payment is selected.
    However, the order is not yet successfully placed.
    '''

    data = json.loads(request.body)
    customer = request.user.customer
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    total = int(data["form"]["total"])
    print(data)
    shipping_address = None 

    try:
        shipping_address = ShippingAddress.objects.get(id=data["shipping"]["id"])

    #If saved address not selected, exception is raised, indicating new address is entered & must be read 
    except KeyError:    
        shipping_address = ShippingAddress(
            customer=customer,
            address=data["shipping"]["address"],
            city=data["shipping"]["city"],
            state=data["shipping"]["state"],
            zipcode=data["shipping"]["zipcode"],
        )
        shipping_address.save() #Saves new shipping address record in database

    order.shipping_address = shipping_address
    order.save()    #Updates order record in database with shipping address foreign key

    if not data['COD']: #Sends razorpay order details if Razorpay selected as payment method
        order.razorpayOrder(total*100)
        return JsonResponse({'razorpay_order': order.razorpay_order})
    else:
        return JsonResponse('', safe=False)



def postProcess(request):
    '''
    Verifies payment & successfully places order by updating required fields such as payment_method, paid, and complete.
    Also ensures that product stocks are decremented according to quantity ordered by customer. 
    '''

    data = json.loads(request.body)

    if not data['COD']:
        order = Order.objects.get(razorpay_order__icontains=data['order_id'])
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
    order.save()    #Updates order data in database

    #Decrements each product's available stock basis quantity ordered by customer
    items = order.orderitem_set.all()
    for item in items:
        product = item.product
        product.stock -= item.quantity
        if product.stock < 0:
            product.stock = 0 
        product.save()
    messages.success(request, "Your order has been placed!")
    return JsonResponse("Your order has been placed!", safe=False)
