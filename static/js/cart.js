var updateBtns = document.getElementsByClassName("update-cart")

for(var i = 0; i < updateBtns.length; i++){
    updateBtns[i].addEventListener('click', function(){
        var productId = this.dataset.product
        var action = this.dataset.action
        console.log("product ID: ", productId, "Action: ", action)

        console.log("User: ", user)
        if (user == 'AnonymousUser') {
            console.log("Not logged in")
        }
        else {
            console.log("User is logged in. Sending data...")
        }
    })
}