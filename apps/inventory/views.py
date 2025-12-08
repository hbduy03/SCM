from django.contrib.auth.decorators import login_required
from apps.sales.models import Order
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from apps.catalog.models import Product, Supplier
from .forms import StockInForm, StockOutForm
from django.db import transaction, models
from .models import Inventory, StockIn, StockOut
from datetime import datetime
from ..authentication.views import user_role


@login_required
def dashboard(request):
    total_products = Product.objects.count()
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(status='pending').count()
    low_stock_items = Inventory.objects.filter(quantity__lte=models.F('min_quantity')).count()

    recent_orders = Order.objects.all().order_by('-created_at')[:5]

    low_stock_products = Inventory.objects.filter(
        quantity__lte=models.F('min_quantity')
    ).select_related('product')[:5]

    context = {
        'total_products': total_products,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'low_stock_items': low_stock_items,
        'recent_orders': recent_orders,
        'low_stock_products': low_stock_products,
    }
    return render(request, 'inventory/index.html', context)


def inventory_list(request):
    inventories = Inventory.objects.filter(product__is_active=True).select_related('product', 'product__category')
    return render(request, 'inventory/inventory-list.html', {'inventories': inventories})


@login_required
@user_role(['admin', 'warehouse'])
def add_stock_in(request):
    if request.method == 'POST':
        form = StockInForm(request.POST)
        if form.is_valid():
            stock_in = form.save(commit=False)
            stock_in.created_by = request.user
            stock_in.save()
            messages.success(request, 'Stock in successfully!')
            return redirect('add_stock_in')
    else:
        form = StockInForm()
    return render(request, 'inventory/stock-in-form.html', {'form': form})


@login_required
@user_role(['admin', 'warehouse'])
def stock_in_list(request):
    stock_ins = StockIn.objects.select_related(
        'product', 'supplier', 'created_by'
    ).order_by('-created_at')
    suppliers = Supplier.objects.all()
    return render(request, 'inventory/stock-in-list.html', {
        'stock_ins': stock_ins,
        'suppliers': suppliers,
    })


@login_required
@user_role(['admin', 'warehouse'])
def stock_in_detail(request, id):
    stock_in = get_object_or_404(
        StockIn.objects.select_related(
            'product', 'product__category', 'supplier', 'created_by'
        ),
        id=id
    )

    try:
        current_inventory = Inventory.objects.get(product=stock_in.product)
    except Inventory.DoesNotExist:
        current_inventory = None

    return render(request, 'inventory/stock-in-detail.html', {
        'stock_in': stock_in,
        'current_inventory': current_inventory,
    })

@login_required
@user_role(['admin'])
def cancel_stock_in(request, id):
    try:
        with transaction.atomic():
            stock_in = StockIn.objects.select_for_update().get(id=id)

            if stock_in.is_disable:
                messages.warning(request, 'Stock in is cancelled!')
                return redirect('stock_in_detail', id=id)

            if stock_in.approved_by:
                inventory = Inventory.objects.select_for_update().get(product=stock_in.product)

                if inventory.quantity < stock_in.quantity:
                    messages.error(request, 'Cannot cancel! The items were already stocked in but have since been sold.')
                    return redirect('stock_in_detail', id=id)

                inventory.quantity -= stock_in.quantity
                inventory.save()
                msg = f'The stock-in record has been cancelled and {stock_in.quantity} items have been withdrawn from inventory.'

            else:
                msg =' Draft stock-in record cancelled (Inventory not affected).'

            # Cập nhật trạng thái
            stock_in.is_disable = True
            stock_in.save(update_fields=['is_disable'])

            messages.success(request, msg)

    except Exception as e:
        messages.error(request, f'Lỗi: {str(e)}')

    return redirect('stock_in_detail', id=id)


@login_required
@user_role(['admin'])
def confirm_stock_in(request, id):
    with transaction.atomic():

        stock_in = StockIn.objects.select_for_update().get(id=id)

        if stock_in.approved_by or stock_in.is_disable:
            return redirect('stock_in_detail', id=id)

        inventory, _ = Inventory.objects.select_for_update().get_or_create(
            product=stock_in.product,
            defaults={'quantity': 0}
        )
        inventory.quantity += stock_in.quantity
        inventory.save()

        stock_in.approved_by = request.user
        stock_in.updated_quantity = inventory.quantity
        stock_in.save()

    messages.success(request, 'Added Stock in successfully!')
    return redirect('stock_in_detail', id=id)

@login_required
@user_role(['admin', 'warehouse'])
def print_stock_in(request, id):
    stock_in = get_object_or_404(
        StockIn.objects.select_related(
            'product', 'product__category', 'supplier', 'created_by'
        ),
        id=id
    )

    context = {
        'stock_in': stock_in,
        'old_qty': stock_in.updated_quantity - stock_in.quantity,
        'print_date': datetime.now(),
        'company_name': 'DREAM POS COMPANY',
        'company_address': 'An Phu Dong 10, District 12, Ho Chi Minh City, Vietnam',
        'company_phone': '090123123',
    }

    return render(request, 'inventory/stock-in-print.html', context)


@login_required
@user_role(['admin', 'warehouse'])
def print_stock_out(request, id):
    stock_out = get_object_or_404(
        StockOut.objects.select_related(
            'product', 'product__category', 'order', 'created_by', 'approved_by'
        ),
        id=id
    )

    context = {
        'stock_out': stock_out,
        'old_qty': stock_out.updated_quantity + stock_out.quantity,
        'print_date': datetime.now(),
        'company_name': 'DREAM POS COMPANY',
        'company_address': 'An Phu Dong 10, District 12, Ho Chi Minh City, Vietnam',
        'company_phone': '090123123',
    }

    return render(request, 'inventory/stock-out-print.html', context)


@login_required
@user_role(['admin', 'warehouse'])
def stock_out_list(request):
    stock_outs = StockOut.objects.select_related('product', 'created_by', 'order')
    return render(request, 'inventory/stock-out-list.html', {
        'stock_outs': stock_outs,
        'type_choices': StockOut.TYPE_CHOICES,
    })


@login_required
@user_role(['admin', 'warehouse'])
def add_stock_out(request):
    if request.method == 'POST':
        form = StockOutForm(request.POST)
        if form.is_valid():
            try:
                stock_out = form.save(commit=False)
                stock_out.created_by = request.user

                if stock_out.type in ['damaged', 'adjustment']:
                    if request.user.role not in ['admin']:
                        messages.warning(request, 'This stock out type requires admin approval!')
                        return redirect('add_stock_out')
                    stock_out.approved_by = request.user

                stock_out.save()
                messages.success(request, 'Stock out created successfully!')
                return redirect('add_stock_out')
            except ValueError as e:
                messages.error(request, str(e))
        else:
            messages.error(request, 'Invalid information! Please review!')
    else:
        form = StockOutForm()

    products_stock = {inv.product.id: inv.quantity for inv in Inventory.objects.select_related('product')}

    return render(request, 'inventory/stock-out-form.html', {
        'form': form,
        'products_stock': products_stock,
    })


@login_required
@user_role(['admin', 'warehouse'])
def stock_out_detail(request, id):
    stock_out = get_object_or_404(
        StockOut.objects.select_related('product', 'created_by', 'approved_by', 'order'),
        id=id
    )
    return render(request, 'inventory/stock-out-detail.html', {'stock_out': stock_out})


@login_required
@user_role(['admin'])
def cancel_stock_out(request, id):
    stock_out = get_object_or_404(StockOut, id=id)

    if stock_out.order and stock_out.order.status != 'cancelled':
        messages.error(request, 'Cannot cancel stock out for an active order!')
        return redirect('stock_out_detail', id=id)

    try:
        with transaction.atomic():
            inventory = Inventory.objects.get(product=stock_out.product)
            inventory.quantity += stock_out.quantity
            inventory.save()

            stock_out.is_disable = True
            stock_out.save(update_fields=['is_disable'])

            messages.success(request, f'Stock out cancelled! Returned {stock_out.quantity} {stock_out.product.unit} {stock_out.product.name} to inventory!')

    except Exception as e:
        messages.error(request, f'Error: {str(e)}')

    return redirect('stock_out_detail', id=id)


@login_required
@user_role(['admin'])
def confirm_stock_out(request, id):
    stock_out = get_object_or_404(StockOut, id=id)
    if not stock_out.approved_by and not stock_out.is_disable:
        stock_out.approved_by = request.user
        stock_out.save()  #
        messages.success(request, 'Stock out is approved!')

    return redirect('stock_out_detail', id=id)