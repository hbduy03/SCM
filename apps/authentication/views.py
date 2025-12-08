import json
import random
from datetime import datetime, timedelta
from functools import wraps

import numpy as np
from django.db.models import Sum, F
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.shortcuts import render, redirect, get_object_or_404

from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib import messages
from django.utils import timezone

from apps.authentication.forms import UserProfileForm, CustomPasswordChangeForm, LoginForm
from .models import User
from inventorySystem import settings
from ..ai_models.forecasting import ai_engine
from ..catalog.models import Product
from ..inventory.models import StockIn, StockOut, Inventory
from ..sales.models import Order, OrderItem


def user_login(request):
    form = LoginForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('dashboard')
            else:
                messages.error(request, 'Username or password is incorrect!')
        else:
            messages.error(request, 'Please check your information and Captcha again!')

    return render(request, 'authentication/login.html', {'form': form})


def user_logout(request):
    logout(request)
    return redirect('user_login')


def user_role(allowed_roles=[]):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('user_login')
            user_role = request.user.role
            if user_role not in allowed_roles and not request.user.is_superuser:
                messages.error(request, 'You do not have permission to access this feature!')
                return redirect('dashboard')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


@login_required
def user_profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Information updated successfully!')
            return redirect('user_profile')
    else:
        form = UserProfileForm(instance=request.user)

    context = {
        'form': form,
    }
    return render(request, 'authentication/user-profile.html', context)


@login_required
def change_password(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            try:
                send_mail(
                    subject='Notification: Password has been changed',
                    message=f'''
                Hello {user.get_full_name() or user.username},

                Your account password has just been successfully changed.

                Details:
                - Username: {user.username}
                - Email: {user.email}
                - Time: {timezone.now().strftime("%d/%m/%Y %H:%M:%S")}

                If this was not you, please contact the administrator immediately.

                Dream Pos Supply Chain Management System
                    ''',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email] if user.email else [],
                    fail_silently=False,
                )

                messages.success(request,
                                 'Password changed successfully! A notification email has been sent.')

            except Exception as e:
                messages.warning(request,
                                 f'Password changed successfully! However, the email could not be sent: {str(e)}')

            return redirect('change_password')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{error}')
    else:
        form = CustomPasswordChangeForm(user=request.user)

    context = {
        'form': form,
    }
    return render(request, 'authentication/change-password.html', context)


@login_required
@user_role(['admin'])
def user_list(request):
    users = User.objects.filter(is_superuser=False)

    total_users = users.count()
    active_users = users.filter(is_active=True).count()
    inactive_users = users.filter(is_active=False).count()

    context = {
        'users': users,
        'total_users': total_users,
        'active_users': active_users,
        'inactive_users': inactive_users,
        'role_choices': User.role_choices,
    }
    return render(request, 'authentication/user-list.html', context)


@login_required
@user_role(['admin'])
def user_detail(request, pk):
    user = get_object_or_404(User, pk=pk, is_superuser=False)
    stats = {}

    if user.role == 'sales':
        orders = Order.objects.filter(created_by=user)

        stats = {
            'total_orders': orders.count(),
            'completed_orders': orders.filter(status='delivered').count(),
            'pending_orders': orders.filter(status='pending').count(),
            'cancelled_orders': orders.filter(status='cancelled').count(),
            'total_revenue': orders.filter(status='delivered').aggregate(
                total=Sum('total_amount')
            )['total'] or 0,
            'recent_orders': orders.order_by('-created_at')[:5],
        }

    elif user.role == 'warehouse':
        stock_ins = StockIn.objects.filter(created_by=user)
        stock_outs = StockOut.objects.filter(created_by=user)

        stats = {
            'total_stock_ins': stock_ins.count(),
            'total_stock_outs': stock_outs.count(),
            'total_stock_in_value': stock_ins.aggregate(
                total=Sum('total_cost')
            )['total'] or 0,
            'recent_stock_ins': stock_ins.order_by('-created_at')[:5],
            'recent_stock_outs': stock_outs.order_by('-created_at')[:5],
        }

    context = {
        'employee': user,
        'stats': stats,
    }
    return render(request, 'authentication/user-detail.html', context)

@login_required
@user_role(['admin'])
def user_deactivate(request, pk):

    user = get_object_or_404(User, pk=pk, is_superuser=False)

    if user == request.user:
        messages.error(request, 'You cannot disable your own account!')
        return redirect('user_list')

    if user.role == 'admin':
        messages.error(request, 'You cannot disable an admin account!')
        return redirect('user_list')

    user.is_active = False
    user.save()

    messages.success(request, f'Account {user.username} has been disabled!')

    return redirect('user_list')

@login_required
@user_role(['admin'])
def user_activate(request, pk):
    user = get_object_or_404(User, pk=pk, is_superuser=False)

    user.is_active = True
    user.save()

    messages.success(request, f'Account {user.username} has been active!')

    return redirect('user_list')


@login_required
def dashboard(request):
    user_role = request.user.role
    today = datetime.now().date()

    if user_role == 'admin':
        stats = {
            'total_products': Product.objects.filter(is_active=True).count(),
            'total_orders': Order.objects.count(),
            'pending_orders': Order.objects.filter(status='pending').count(),
            'low_stock_items': Inventory.objects.filter(quantity__lte=F('min_quantity'),product__is_active=True).count(),
            'total_revenue': Order.objects.filter(status='delivered').aggregate(total=Sum('total_amount'))[
                                 'total'] or 0,
            'total_customers': Order.objects.values('customer_phone').distinct().count(),
        }

        last_7_days = today - timedelta(days=6)
        revenue_by_day = []
        for i in range(7):
            date = last_7_days + timedelta(days=i)
            revenue = Order.objects.filter(
                status='delivered',
                created_at__date=date
            ).aggregate(total=Sum('total_amount'))['total'] or 0

            revenue_by_day.append({
                'date': date.strftime('%d/%m'),
                'revenue': float(revenue)
            })

        order_status_data = []
        for status_code, status_name in Order.STATUS_CHOICES:
            count = Order.objects.filter(status=status_code).count()
            order_status_data.append({
                'status': status_name,
                'count': count
            })

        recent_orders = Order.objects.select_related('created_by').order_by('-created_at')[:5]

        low_stock_products = Inventory.objects.filter(
            quantity__lte=F('min_quantity'),
            product__is_active=True
        ).select_related('product')[:5]

        ai_forecast = []
        ai_available = False

        if ai_engine.load_model():
            ai_available = True

            # Get 5 products (Priority: Low stock -> High stock)
            target_products = Inventory.objects.select_related('product').filter(product__is_active=True).order_by('quantity')[:5]

            for inv in target_products:
                # Direct prediction using Product ID string
                product_forecast = ai_engine.predict_product_demand(str(inv.product.product_id))

                shortage = product_forecast - inv.quantity

                if inv.quantity == 0:
                    urgency = 'Critical'
                elif shortage > 0:
                    urgency = 'High'
                else:
                    urgency = 'Normal'
                    shortage = 0

                ai_forecast.append({
                    'product_name': inv.product.name,
                    'current_stock': inv.quantity,
                    'forecast': product_forecast,
                    'shortage': shortage,
                    'urgency': urgency
                })

            # Sort critical items to top
            urgency_order = {'Critical': 0, 'High': 1, 'Normal': 2}
            ai_forecast.sort(key=lambda x: urgency_order.get(x['urgency'], 2))

        context = {
            'user_role': user_role,
            'stats': stats,
            'revenue_by_day': json.dumps(revenue_by_day),
            'order_status_data': json.dumps(order_status_data),
            'recent_orders': recent_orders,
            'low_stock_products': low_stock_products,
            'ai_forecast': ai_forecast,
            'ai_available': ai_available,
        }
        return render(request, 'dashboard/dashboard-admin.html', context)


    elif user_role == 'warehouse':
        stats = {
            'total_products': Product.objects.filter(is_active=True).count(),
            'low_stock_items': Inventory.objects.filter(quantity__lte=F('min_quantity')).count(),
            'pending_orders': Order.objects.filter(status='pending').count(),
            'stock_in_today': StockIn.objects.filter(created_at__date=today).count(),
            'stock_out_today': StockOut.objects.filter(created_at__date=today).count(),
            'total_inventory_value': Inventory.objects.aggregate(total=Sum(F('quantity') * F('product__price')))[
                                         'total'] or 0,
        }

        last_7_days = today - timedelta(days=6)
        stock_movement = []
        for i in range(7):
            date = last_7_days + timedelta(days=i)
            stock_in = StockIn.objects.filter(created_at__date=date).aggregate(total=Sum('quantity'))['total'] or 0
            stock_out = StockOut.objects.filter(created_at__date=date).aggregate(total=Sum('quantity'))['total'] or 0

            stock_movement.append({
                'date': date.strftime('%d/%m'),
                'stock_in': float(stock_in),
                'stock_out': float(stock_out)
            })

        inventory_status = {
            'low_stock': Inventory.objects.filter(quantity__lte=F('min_quantity')).count(),
            'normal': Inventory.objects.filter(quantity__gt=F('min_quantity'), quantity__lt=F('max_quantity')).count(),
            'overstock': Inventory.objects.filter(quantity__gte=F('max_quantity')).count(),
        }

        pending_orders = Order.objects.filter(status='pending').select_related('created_by')[:10]

        low_stock_products = Inventory.objects.filter(
            quantity__lte=F('min_quantity')
        ).select_related('product').order_by('quantity')[:10]

        recent_stock_in = StockIn.objects.select_related('product', 'supplier').order_by('-created_at')[:5]
        recent_stock_out = StockOut.objects.select_related('product').order_by('-created_at')[:5]

        context = {
            'user_role': user_role,
            'stats': stats,
            'stock_movement': json.dumps(stock_movement),
            'inventory_status': inventory_status,
            'pending_orders': pending_orders,
            'low_stock_products': low_stock_products,
            'recent_stock_in': recent_stock_in,
            'recent_stock_out': recent_stock_out,
        }
        return render(request, 'dashboard/dashboard-warehouse.html', context)

    elif user_role == 'sales':
        stats = {
            'my_orders_today': Order.objects.filter(created_by=request.user, created_at__date=today).count(),
            'my_orders_month': Order.objects.filter(created_by=request.user, created_at__month=today.month,
                                                    created_at__year=today.year).count(),
            'my_revenue_month': Order.objects.filter(created_by=request.user, created_at__month=today.month,
                                                     created_at__year=today.year, status='delivered').aggregate(
                total=Sum('total_amount'))['total'] or 0,
            'my_pending_orders': Order.objects.filter(created_by=request.user, status='pending').count(),
        }

        last_7_days = today - timedelta(days=6)
        my_sales_by_day = []
        for i in range(7):
            date = last_7_days + timedelta(days=i)
            revenue = Order.objects.filter(
                created_by=request.user,
                status='delivered',
                created_at__date=date
            ).aggregate(total=Sum('total_amount'))['total'] or 0

            my_sales_by_day.append({
                'date': date.strftime('%d/%m'),
                'revenue': float(revenue)
            })

        my_order_status = []
        for status_code, status_name in Order.STATUS_CHOICES:
            count = Order.objects.filter(created_by=request.user, status=status_code).count()
            my_order_status.append({
                'status': status_name,
                'count': count
            })

        my_recent_orders = Order.objects.filter(created_by=request.user).order_by('-created_at')[:10]

        my_top_products_qs = OrderItem.objects.filter(
            order__created_by=request.user,
            order__status='delivered'
        ).values('product__name').annotate(total_sold=Sum('quantity')).order_by('-total_sold')[:5]


        my_top_products_list = list(my_top_products_qs)
        for item in my_top_products_list:
            item['total_sold'] = float(item['total_sold']) if item['total_sold'] else 0

        low_stock_products = Inventory.objects.filter(
            quantity__lte=F('min_quantity')
        ).select_related('product')[:5]

        context = {
            'user_role': user_role,
            'stats': stats,
            'my_sales_by_day': json.dumps(my_sales_by_day),
            'my_order_status': json.dumps(my_order_status),
            'my_recent_orders': my_recent_orders,
            'my_top_products': json.dumps(my_top_products_list),
            'low_stock_products': low_stock_products,
        }
        return render(request, 'dashboard/dashboard-sales.html', context)

    else:
        return render(request, 'dashboard/dashboar-default.html')