'''
This file maintains all the classes used to manage the relational database in Python. 
Within this file:
 - Each class is a table in the relational database of the website
 - An attribute of a defined class is a field of the associated database table
 - Each attribute is defined as an instance of a Django pre-defined class, which relates to the data type of the database field  
 - The constraints on each field are passed as attributes of the defined instance

E.g., the Customer class refers to the Customer table in the relational database.
The 'name' attribute refers to the 'name' field of the Customer table in the database.
This 'name' attribute is an instance of Django's CharField class, indicating it is a character data type field.
The constraints on this field are a length constraint of 200 characters, defined using the attribute max_length of CharField.
'''

from django.db import models
from django.contrib.auth.models import User
from django.db.models.fields import BooleanField
import razorpay


class Customer(models.Model):
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, null=True)
    email = models.EmailField(null=True)

    def __str__(self) -> str:
        return self.name


class Product(models.Model):
    name = models.CharField("Name", max_length=200, null=True)
    desc = models.TextField("Description", null=True)
    CATEGORIES = [
        ("Oil", "Oil"),
        ("Mist", "Mist"),
        ("Serum", "Serum"),
        ("Scrub", "Scrub"),
        ("Mask", "Mask"),
    ]
    #Gives a pre-defined list of choices for the product category
    category = models.CharField("Category", max_length=10, choices=CATEGORIES, default=None) 
    price = models.PositiveIntegerField("Price")
    stock = models.PositiveIntegerField("Stock", default=0)
    image = models.ImageField(null=True, blank=True)

    @property
    def ImageURL(self):
        try:
            url = self.image.url
        except:
            url = ""    #Displays blank image in case there is no product image uploaded by user
        return url

    def __str__(self) -> str:
        return self.name


class ShippingAddress(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, blank=True, null=True)
    address = models.CharField(max_length=200, null=False)
    city = models.CharField(max_length=200, null=False)
    state = models.CharField(max_length=200, null=False)
    zipcode = models.CharField(max_length=200, null=False)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return "{address}, {city}, {state}, {zipcode}".format(address=self.address, city=self.city, state=self.state, zipcode=self.zipcode)


class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, blank=True, null=True)
    shipping_address = models.ForeignKey(ShippingAddress, on_delete=models.SET_NULL, blank=False, null=True)
    products = models.ManyToManyField(Product, through="OrderItem")
    date_ordered = models.DateTimeField(blank=False, null=True)
    STATUS = [
        ("Received", "Received"),
        ("Dispatched", "Dispatched"),
        ("Delivered", "Delivered"),
        ("Returned Requested", "Returned Requested"),
        ("Returned", "Returned"),
        ("Cancelled", "Cancelled"),
    ]
    status = models.CharField(max_length=20, choices=STATUS, default="Received", null=True, blank=False)
    complete = models.BooleanField(default=False)
    razorpay_order = models.JSONField(null=True)    #Stores data of razorpay order as JSON if customer chooses to pay through razorpay. 
                                                    #Necessaary to store razorpay order data for payment verification

    METHODS = [
        ("Razorpay", "Razorpay"),
        ("COD", "COD"),
    ]
    payment_method = models.CharField(max_length=20, choices=METHODS, null=True, blank=False)
    paid = models.BooleanField(default=False)

    def razorpayOrder(self, amount):
        '''Uses Razorpay API to create order to be sent to Razorpay as part of payment request, 
           and stores order ID in Order record for payment verification'''

        secret = "A3Qj0BehTIFJAgnoVquqQRee"
        client = razorpay.Client(
            auth=("rzp_test_95n7g5IxLaQMGz", secret)
        )

        DATA = {
            "amount": amount,
            "currency": "INR",
            "receipt": str(self.id),
        }
        order = client.order.create(data=DATA)
        self.razorpay_order = {         #Data stored in key:value pairs as it is a JSON field
            "order_id": order["id"],
            "status": order["status"],
        }
        self.save() #Stores razorpay order ID and payment status in database

    def __str__(self) -> str:
        return str(self.id)

    @property
    def get_cart_total(self):
        'Getter method used to return cart total'

        orderitems = self.orderitem_set.all()
        total = sum([item.get_total for item in orderitems])
        return total

    @property
    def get_cart_items(self):
        '''Getter method used to return total number of items in customer's cart'''

        orderitems = self.orderitem_set.all()
        total = sum([item.quantity for item in orderitems])
        return total


class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, blank=True, null=True)
    quantity = models.PositiveIntegerField(default=0, blank=True, null=True)
    date_added = models.DateTimeField(auto_now_add=True)    #Automatically assigned datetime when record created

    def __str__(self) -> str:
        return self.product.name

    @property
    def get_total(self):
        'Returns the total price of each product added, basis quantity of each product added to cart'
        total = self.product.price * self.quantity
        return total
