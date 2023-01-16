from django.urls import path
from . import views

urlpatterns = [
    path("", views.store, name="store"),
    path("cart/", views.cart, name="cart"),
    path("checkout/", views.checkout, name="checkout"),
    path("update_item/", views.updateItem, name="update_item"),
    path("process_order/", views.processOrder, name="process_order"),
    path("post_process/", views.postProcess, name='post_process'),
    path('register/', views.register, name='register'),
    path('login/', views.loginRequest, name='login'),
    path('logout/', views.logoutRequest, name='logout'),
    path('view-profile/', views.viewProfile, name='view-profile'),
    path('edit-profile/', views.editProfile, name='edit-profile'),
    path('change-password/', views.ChangePasswordView.as_view(), name='change-password'),
    path('search-results/', views.searchResults, name='search-results'),
]
