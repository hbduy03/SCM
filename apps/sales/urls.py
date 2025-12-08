from django.urls import path
from . import views

urlpatterns = [
    path('orders/', views.order_list, name='order_list'),
    path('order/add/', views.add_order, name='add_order'),
    path('order/<int:id>/', views.order_detail, name='order_detail'),
    path('order/<int:id>/confirm/', views.confirm_order, name='confirm_order'),
    path('order/<int:id>/update-status/', views.order_update_status, name='order_update_status'),
    path('order/<int:id>/cancel/', views.cancel_order, name='cancel_order'),
    path('order/<int:id>/edit/', views.edit_order, name='edit_order'),
    path('order/<int:id>/print/', views.print_order, name='print_order')
]