from django.urls import path
from . import views

urlpatterns = [
    path('inventory/', views.inventory_list, name='inventory_list'),
    path('stock-in/add/', views.add_stock_in, name='add_stock_in'),
    path('stock-in/', views.stock_in_list, name='stock_in_list'),
    path('stock-in/<int:id>/cancel/', views.cancel_stock_in, name='cancel_stock_in'),
    path('stock-in/<int:id>/', views.stock_in_detail, name='stock_in_detail'),
    path('stock-in/<int:id>/confirm/', views.confirm_stock_in, name='confirm_stock_in'),
    path('stock-in/<int:id>/print/', views.print_stock_in, name='print_stock_in'),

    path('stock-out/', views.stock_out_list, name='stock_out_list'),
    path('stock-out/add/', views.add_stock_out, name='add_stock_out'),
    path('stock-out/<int:id>/', views.stock_out_detail, name='stock_out_detail'),
    path('stock-out/<int:id>/cancel/', views.cancel_stock_out, name='cancel_stock_out'),
    path('stock-out/<int:id>/confirm/', views.confirm_stock_out, name='confirm_stock_out'),
    path('stock-out/<int:id>/print/', views.print_stock_out, name='print_stock_out'),
]