from django.db import models
from django.contrib.auth.models import User
from django.db.models.fields import BooleanField

class Customer(models.Model):
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, null=True)
    email = models.EmailField(null=True)

    def __str__(self) -> str:
        return self.name

class Product(models.Model):
    name = models.CharField('Name', max_length=200, null=True)
    desc = models.TextField('Description', null=True)
    CATEGORIES = [
        ('Oil', 'Oil'),
        ('Mist', 'Mist'),
        ('Serum', 'Serum'),
        ('Scrub', 'Scrub'),
        ('Mask', 'Mask'),
    ]
    category = models.CharField('Category', max_length=10, choices=CATEGORIES, default=None)

    price = models.PositiveIntegerField('Price')
    stock = models.PositiveIntegerField('Stock', default=0)

    image = models.ImageField(null=True, blank=True)

    @property
    def ImageURL(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url
        


    def __str__(self) -> str:
        return self.name

class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, blank=True, null=True)
    date_ordered = models.DateTimeField(auto_now_add=True)
    STATUS = [
        ('Received', 'Received'),
        ('Dispatched', 'Dispatched'),
        ('Delivered', 'Delivered'),
        ('Returned Requested', 'Returned Requested'),
        ('Returned', 'Returned'),
        ('Cancelled', 'Cancelled'),
    ]
    status = models.CharField(max_length=20, choices=STATUS, default='Received', null=True, blank=False)
    transaction_id = models.CharField(max_length=200, null=True)

    def __str__(self) -> str:
        return str(self.id)

class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, blank=True, null=True)
    quantity = models.PositiveIntegerField(default=0, blank=True, null=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.product.name

class ShippingAddress(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, blank=True, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, blank=True, null=True)
    address = models.CharField(max_length=200, null=False)
    city = models.CharField(max_length=200, null=False)
    state = models.CharField(max_length=200, null=False)
    zipcode = models.CharField(max_length=200, null=False)
    ate_added = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.address
