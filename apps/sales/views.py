from datetime import datetime
import uuid

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from .forms import OrderItemFormSet, OrderForm
from .models import Order
from ..authentication.views import user_role
from ..catalog.models import Product
from ..inventory.models import Inventory, StockOut


@login_required
def order_list(request):
    status = request.GET.get('status', '')
    orders = Order.objects.all().order_by('-created_at')

    if status:
        orders = orders.filter(status=status)

    context = {
        'orders': orders,
        'status_choices': Order.STATUS_CHOICES,
    }
    return render(request, 'sales/order-list.html', context)


@user_role(['admin', 'sales'])
@login_required
def order_detail(request, id):
    order = get_object_or_404(Order.objects.select_related('created_by'), id=id)
    order_items = order.items.select_related('product', 'product__category').all()

    context = {
        'order': order,
        'order_items': order_items,
    }
    return render(request, 'sales/order-detail.html', context)


@login_required
@user_role(['admin', 'warehouse'])
def confirm_order(request, id):
    order = get_object_or_404(Order, id=id)

    if order.status != 'pending':
        messages.warning(request, 'This order has already been processed!')
        return redirect('order_detail', id=id)

    try:
        with transaction.atomic():
            for item in order.items.all():
                StockOut.objects.create(
                    product=item.product,
                    order=order,
                    quantity=item.quantity,
                    approved_by=request.user,
                    created_by=request.user,
                    note=f'Stock out for order {order.order_id}',
                )

            order.status = 'processing'
            order.save()

            messages.success(request, 'Order confirmed and stock deducted successfully!')
    except Exception as e:
        messages.error(request, f'Error: {str(e)}')

    return redirect('order_detail', id=id)


@login_required
@user_role(['admin'])
def cancel_order(request, id):
    order = get_object_or_404(Order, id=id)

    if order.status == 'completed':
        messages.error(request, 'Cannot cancel a completed order!')
        return redirect('order_detail', id=id)

    try:
        with transaction.atomic():
            stock_out = StockOut.objects.filter(order=order).first()
            if stock_out:
                if not stock_out.is_disable:
                    if hasattr(stock_out, 'note'):
                        stock_out.note = f"Auto-cancelled because Order #{order.id} was cancelled by Admin."
                    stock_out.is_disable = True
                    stock_out.save()
            if order.status in ['processing', 'shipping']:
                for item in order.items.all():
                    inventory = Inventory.objects.get(product=item.product)
                    inventory.quantity += item.quantity
                    inventory.save()

            order.status = 'cancelled'
            order.save()

            messages.success(request, 'Order cancelled successfully!')
    except Exception as e:
        messages.error(request, f'Error: {str(e)}')

    return redirect('order_detail', id=id)


@login_required
@user_role(['admin', 'sales'])
def order_update_status(request, id):
    order = get_object_or_404(Order, id=id)

    if request.method == 'POST':
        new_status = request.POST.get('status')

        valid_transitions = {
            'pending': ['processing', 'cancelled'],
            'processing': ['shipping', 'cancelled'],
            'shipping': ['delivered', 'cancelled'],
        }

        if order.status in valid_transitions and new_status in valid_transitions[order.status]:
            order.status = new_status
            order.save()
            messages.success(request, f'Order status updated to "{order.get_status_display()}"!')
        else:
            messages.error(request, 'Invalid status transition!')

    return redirect('order_detail', id=id)


@login_required
@user_role(['admin', 'sales'])
def add_order(request):
    if request.method == 'POST':
        order_form = OrderForm(request.POST)
        order_item_formset = OrderItemFormSet(request.POST)

        if order_form.is_valid() and order_item_formset.is_valid():
            try:
                with transaction.atomic():
                    order = order_form.save(commit=False)
                    order.order_id = f"DH{datetime.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:6].upper()}"
                    order.created_by = request.user

                    total_amount = 0
                    for item_form in order_item_formset:
                        if item_form.cleaned_data and not item_form.cleaned_data.get('DELETE'):
                            quantity = item_form.cleaned_data['quantity']
                            unit_price = item_form.cleaned_data['unit_price']
                            total_amount += quantity * unit_price

                            product = item_form.cleaned_data['product']
                            inventory = Inventory.objects.get(product=product)

                            if inventory.quantity < quantity:
                                raise ValueError(f'Product {product.name} does not have enough stock! (Remaining: {inventory.quantity})')

                    order.total_amount = total_amount
                    order.save()

                    order_item_formset.instance = order
                    order_items = order_item_formset.save(commit=False)

                    for item in order_items:
                        item.subtotal = item.quantity * item.unit_price
                        item.save()

                    messages.success(request, f'Order {order.order_id} created successfully!')
                    return redirect('order_detail', id=order.id)

            except ValueError as e:
                messages.error(request, str(e))
            except Exception as e:
                messages.error(request, f'Error: {str(e)}')
        else:
            messages.error(request, 'Please check all information again!')

    else:
        order_form = OrderForm()
        order_item_formset = OrderItemFormSet()

    products = Product.objects.filter(is_active=True).select_related('category', 'inventory')
    products_data = []

    for product in products:
        try:
            stock = product.inventory.quantity
        except Inventory.DoesNotExist:
            stock = 0

        products_data.append({
            'id': product.id,
            'name': product.name,
            'product_id': product.product_id,
            'price': float(product.price),
            'unit': product.unit,
            'stock': stock,
        })

    context = {
        'order_form': order_form,
        'order_item_formset': order_item_formset,
        'products_data': products_data,
        'title': 'Create New Order',
    }

    return render(request, 'sales/order-form.html', context)


@login_required
@user_role(['admin', 'sales'])
def edit_order(request, id):
    order = get_object_or_404(Order, id=id)

    if order.status != 'pending':
        messages.error(request, 'Only pending orders can be edited!')
        return redirect('order_detail', id=id)

    if request.method == 'POST':
        order_form = OrderForm(request.POST, instance=order)
        order_item_formset = OrderItemFormSet(request.POST, instance=order)

        if order_form.is_valid() and order_item_formset.is_valid():
            try:
                with transaction.atomic():
                    order = order_form.save(commit=False)

                    total_amount = 0
                    for item_form in order_item_formset:
                        if item_form.cleaned_data and not item_form.cleaned_data.get('DELETE'):
                            quantity = item_form.cleaned_data['quantity']
                            unit_price = item_form.cleaned_data['unit_price']
                            total_amount += quantity * unit_price

                            product = item_form.cleaned_data['product']
                            inventory = Inventory.objects.get(product=product)

                            if inventory.quantity < quantity:
                                raise ValueError(f'Product {product.name} does not have enough stock!')

                    order.total_amount = total_amount
                    order.save()

                    order_items = order_item_formset.save(commit=False)

                    for item in order_item_formset.deleted_objects:
                        item.delete()

                    for item in order_items:
                        item.subtotal = item.quantity * item.unit_price
                        item.save()

                    messages.success(request, 'Order updated successfully!')
                    return redirect('order_detail', id=id)
            except ValueError as e:
                messages.error(request, str(e))
            except Exception as e:
                messages.error(request, f'Error: {str(e)}')
        else:
            messages.error(request, 'Please check all information again!')
    else:
        order_form = OrderForm(instance=order)
        order_item_formset = OrderItemFormSet(instance=order)

    products = Product.objects.filter(is_active=True).select_related('category')
    products_data = []

    for product in products:
        try:
            stock = product.inventory.quantity
        except:
            stock = 0

        products_data.append({
            'id': product.id,
            'name': product.name,
            'price': float(product.price),
            'unit': product.unit,
            'stock': stock,
        })

    context = {
        'order': order,
        'order_form': order_form,
        'order_item_formset': order_item_formset,
        'products_data': products_data,
        'title': f'Edit Order {order.order_id}',
    }
    return render(request, 'sales/order-form.html', context)


@login_required
def print_order(request, id):
    order = get_object_or_404(Order, id=id)
    order_items = order.items.select_related('product').all()

    context = {
        'order': order,
        'order_items': order_items,
        'print_date': datetime.now(),
    }
    return render(request, 'sales/order-print.html', context)
