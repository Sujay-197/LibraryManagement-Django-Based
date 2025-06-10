from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing, name='landing'),
    path('books/', views.book_list, name='book_list'),
    path('books/<int:pk>/', views.book_detail, name='book_detail'),
    path('books/create/', views.book_create, name='book_create'),
    path('books/<int:pk>/edit/', views.book_update, name='book_update'),
    path('books/<int:pk>/delete/', views.book_delete, name='book_delete'),
    path('cart/action/', views.cart_action, name='cart_action'),
    path('cart/add/<int:book_id>/', views.cart_action, name='add_to_cart'),
    path('cart/remove/<int:cart_item_id>/', views.cart_action, name='remove_from_cart'),
    path('cart/', views.view_cart, name='view_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('orders/', views.order_list, name='order_list'),
    path('orders/<int:order_id>/approve/', views.order_approve, name='order_approve'),
]
