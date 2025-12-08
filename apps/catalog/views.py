from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from apps.inventory.models import Inventory, StockIn
from .models import Product, Category, Supplier
from .forms import ProductForm, CategoryForm, SupplierForm

from ..authentication.views import user_role
from ..sales.models import OrderItem

# ========== PRODUCT ========== #
@login_required
def product_list(request):
    products = Product.objects.filter(is_active=True).select_related('category')
    context = {
        'products': products,
        'view_type': 'active',
    }
    return render(request, 'catalog/product-list.html', context)

@login_required
def deactive_product_list(request):
    products = Product.objects.filter(is_active=False).select_related('category')
    context = {
        'products': products,
        'view_type': 'deactive',
    }
    return render(request, 'catalog/product-list.html', context)

@login_required
def product_detail(request, id):
    product = get_object_or_404(Product, id=id)
    context = {
        'product': product,
    }
    return render(request, 'catalog/product-detail.html', context)

@login_required
@user_role(['admin'])
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            Inventory.objects.create(product=product, quantity=0)
            messages.success(request, 'Added Product!')
            return redirect('add_product')
    else:
        form = ProductForm()
    return render(request, 'catalog/product-form.html', {'form': form, 'title': 'Add Product'})

@login_required
@user_role(['admin'])
def edit_product(request, id):
    product = get_object_or_404(Product, id=id)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Updated Product successfully!')
            return redirect('edit_product', id=id)
    else:
        form = ProductForm(instance=product)
    return render(request, 'catalog/product-form.html', {'form': form, 'title': 'Edit Product'})

def delete_product(request, id):
    product = get_object_or_404(Product, id=id)
    is_used = OrderItem.objects.filter(product=product).exists()

    if is_used:
        try:
            with transaction.atomic():
                if product.is_active:
                    product.is_active = False
                    product.save(update_fields=['is_active'])
                    messages.info(request, "Product has been deactivated because it is referenced in orders.")
                else:
                    messages.info(request, "This product is already deactivated.")
                return redirect('product_detail', id=id)
        except ValueError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
    else:
        try:
            if product.image:
                product.image.delete(save=False)
            product.delete()
            messages.success(request, "Product and its image have been permanently deleted.")
        except Exception as e:
            messages.error(request, f"Error deleting product: {str(e)}")
    messages.success(request, "Product has been permanently deleted.")
    return redirect('product_list')

# ================================================== #

# ========== Category ========== #
@login_required
def category_list(request):
    categories = Category.objects.all()
    context = {
        'categories': categories,
    }
    return render(request, 'catalog/category-list.html', context)

@login_required
@user_role(['admin'])
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category added successfully!')
            return redirect('category_list')
    else:
        form = CategoryForm()
    return render(request, 'catalog/category-form.html', {
        'form': form,
        'title': 'Add Category'
    })

@login_required
@user_role(['admin'])
def edit_category(request, id):
    category = get_object_or_404(Category, id=id)
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Updated Category successfully!')
            return redirect('category_list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'catalog/category-form.html', {
        'form': form,
        'category': category,
        'title': 'Edit Category'
    })

@login_required
@user_role(['admin'])
def delete_category(request, id):
    category = get_object_or_404(Category, id=id)
    has_products = Product.objects.filter(category=category).exists()

    if has_products:
        category.is_active = False
        category.save(update_fields=['is_active'])
        messages.error(request, "Cannot delete this category because there are products referencing it.")
        return redirect('category_list')

    category.delete()
    messages.success(request, "Category has been deleted successfully.")
    return redirect('category_list')

 # ======================================== #

# ========== Supplier ========== #
@login_required
def supplier_list(request):
    suppliers = Supplier.objects.all()
    context = {
        'suppliers': suppliers,
    }
    return render(request, 'catalog/supplier-list.html', context)

@login_required
@user_role(['admin'])
def add_supplier(request):
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Supplier added successfully!')
            return redirect('supplier_list')
    else:
        form = SupplierForm()
    return render(request, 'catalog/supplier-form.html', {
        'form': form,
        'title': 'Add Supplier'
    })

@login_required
@user_role(['admin'])
def edit_supplier(request, id):
    supplier = get_object_or_404(Supplier, id=id)
    if request.method == 'POST':
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            messages.success(request, 'Supplier updated successfully!')
            return redirect('supplier_list')
    else:
        form = SupplierForm(instance=supplier)
    return render(request, 'catalog/supplier-form.html', {
        'form': form,
        'title': 'Edit Supplier'
    })

@login_required
@user_role(['admin'])
def delete_supplier(request, id):
    supplier = get_object_or_404(Supplier, id=id)
    has_stockin = StockIn.objects.filter(supplier=supplier).exists()

    if has_stockin:
        messages.error(request, "Cannot delete supplier because it has stock-in records. Please deactivate instead.")
        supplier.is_active = False
        supplier.save(update_fields=['is_active'])
        return redirect('supplier_list')
    else:
        supplier.delete()
        messages.success(request, "Supplier deleted successfully.")
        return redirect('supplier_list')