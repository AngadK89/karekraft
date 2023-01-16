/*
The code in this file deals with reading and sending the data required to add/delete a product to/from the customer's cart, 
or to update it's quantity.

This 'required data' is the ID of the product and an action (add/delete), which is stored in every product update button.
*/

var updateBtns = document.getElementsByClassName("update-cart")

for(var i = 0; i < updateBtns.length; i++){
    /* 
    When a button to add/update products in cart is clicked, this event listener is triggered, 
    which reads the button's data and runs the UpdateUserOrder function.  
    */

    updateBtns[i].addEventListener('click', function(){
        var productId = this.dataset.product
        var action = this.dataset.action
        console.log("product ID: ", productId, "Action: ", action, "User: ", user)

        //If customer tries to add product to cart but is not logged in, they are redirected to sign-up page 
        if (user === 'AnonymousUser') {
            window.location.href = "register"   
        }
        else {
            updateUserOrder(productId, action)
        }
    })
}


function updateUserOrder(productId, action){
    //Invokes the fetch API to trigger an HTTP request which sends the 
    //clicked button's data to the updateItem view in views.py
    
    console.log("User is logged in. Sending data...")
    var url = '/update_item/'

    fetch(url, {
        method: 'POST',
        headers: {
            'Content-type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify({'productId': productId, 'action': action}), 
    })

    .then((response) => {
        return response.json();
    })

    .then((data) => {
        console.log('Data: ', data)
        location.reload()
    });
}


