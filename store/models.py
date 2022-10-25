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
    category = models.CharField(
        "Category", max_length=10, choices=CATEGORIES, default=None
    )

    price = models.PositiveIntegerField("Price")
    stock = models.PositiveIntegerField("Stock", default=0)

    image = models.ImageField(null=True, blank=True)

    @property
    def ImageURL(self):
        try:
            url = self.image.url
        except:
            url = ""
        return url

    def __str__(self) -> str:
        return self.name


class ShippingAddress(models.Model):
    customer = models.ForeignKey(
        Customer, on_delete=models.SET_NULL, blank=True, null=True
    )
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
    razorpay_order = models.JSONField(null=True)

    METHODS = [
        ("Razorpay", "Razorpay"),
        ("COD", "COD"),
    ]
    payment_method = models.CharField(max_length=20, choices=METHODS, null=True, blank=False)
    paid = models.BooleanField(default=False)

    def razorpayOrder(self, amount):
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
        self.razorpay_order = {
            "order_id": order["id"],
            "status": order["status"],
        }
        self.save()

    def __str__(self) -> str:
        return str(self.id)

    @property
    def get_cart_total(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.get_total for item in orderitems])
        return total

    @property
    def get_cart_items(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.quantity for item in orderitems])
        return total


class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, blank=True, null=True)
    quantity = models.PositiveIntegerField(default=0, blank=True, null=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.product.name

    @property
    def get_total(self):
        total = self.product.price * self.quantity
        return total
