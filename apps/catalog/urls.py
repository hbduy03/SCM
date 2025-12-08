from django.urls import path
from . import views

urlpatterns = [
    # URLS PRODUCT MODULE
    path('product/', views.product_list, name='product_list'),
    path('products/', views.deactive_product_list, name='deactive_product_list'),
    path('product/add/', views.add_product, name='add_product'),
    path('product/<int:id>/', views.product_detail, name='product_detail'),
    path('product/<int:id>/edit', views.edit_product, name='edit_product'),
    path('product/<int:id>/delete', views.delete_product, name='delete_product'),

    # URLS CATEGORY MODULE
    path('category/add/', views.add_category, name='add_category'),
    path('category/', views.category_list, name='category_list'),
    path('category/<int:id>/edit', views.edit_category, name='edit_category'),
    path('category/<int:id>/delete', views.delete_category, name='delete_category'),

    # URLS SUPPLIER MODULE
    path('supplier/add/', views.add_supplier, name='add_supplier'),
    path('supplier/', views.supplier_list, name='supplier_list'),
    path('supplier/<int:id>/edit', views.edit_supplier, name='edit_supplier'),
    path('supplier/<int:id>/delete', views.delete_supplier, name='delete_supplier'),
]