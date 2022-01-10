import json
from .models import *

def querying_data(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        try:
            cart =  json.loads(request.COOKIES['cart']) #json.loads() makes it a python dictionary
        except KeyError:
            cart = {}
        print("Cart: ", cart)

        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0}
        cartItems = order['get_cart_items']

        for i in cart:
            try: 
                cartItems += cart[i]['quantity']

                product = Product.objects.get(id=i)
                total = (product.price * cart[i]['quantity'])

                order['get_cart_total'] += total
                order['get_cart_items'] += cart[i]['quantity']

                item = {
                    'product': product,
                    'quantity': cart[i]['quantity'],
                    'get_total': total,
                }
                items.append(item)
                
            except:
                pass

    return {'items': items, 'order': order, 'cartItems': cartItems}


def guestOrder(request, data):
    print("User is not logged in.")

    print("Cookies: ", request.COOKIES)

    name = data['form']['name']
    email = data['form']['email']

    cart_data = querying_data(request)
    items = cart_data['items']

    customer, created = Customer.objects.get_or_create(email=email)
    customer.name = name
    customer.save()

    order = Order.objects.create(
        customer=customer,
        complete=False,
    )

    for item in items:
        product = Product.objects.get(id=item['product'].id)

        orderItem = OrderItem.objects.create(
            product=product,
            order=order,
            quantity = item['quantity' ]
        )
    
    return customer, order