# core/forms.py - UPDATED

from django import forms
from django.forms import inlineformset_factory
from .models import Order, OrderItem
from apps.catalog.models import Product


# ==================== ORDER FORM ====================

class OrderForm(forms.ModelForm):

    class Meta:
        model = Order
        fields = ['customer_name', 'customer_phone', 'customer_email',
                  'customer_address', 'payment_method', 'note']
        widgets = {
            'customer_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter customer name'
            }),
            'customer_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '0901234567'
            }),
            'customer_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'email@example.com'
            }),
            'customer_address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Shipping address'
            }),
            'payment_method': forms.Select(attrs={
                'class': 'form-control'
            }),
            'note': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Special notes about this order...'
            }),
        }
        labels = {
            'customer_name': 'Customer Name',
            'customer_phone': 'Phone Number',
            'customer_email': 'Email',
            'customer_address': 'Shipping Address',
            'payment_method': 'Payment Method',
            'note': 'Note',
        }


# ==================== ORDER ITEM FORM ====================

class OrderItemForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(OrderItemForm, self).__init__(*args, **kwargs)
        self.fields['product'].queryset = Product.objects.filter(is_active=True)

    class Meta:
        model = OrderItem
        fields = ['product', 'quantity', 'unit_price']
        widgets = {
            'product': forms.Select(attrs={
                'class': 'form-control product-select',
                'onchange': 'updateProductInfo(this)',
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control quantity-input',
                'min': 1,
                'value': 1,
                'onchange': 'calculateTotal()',
            }),
            'unit_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'readonly': 'readonly',
                'step': '0.01',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['product'].queryset = Product.objects.filter(is_active=True)

        self.fields['product'].label_from_instance = lambda obj: \
            f"{obj.name} - {obj.code} (Available: {obj.inventory.quantity} {obj.unit})"


# ==================== ORDER ITEM FORMSET ====================

OrderItemFormSet = inlineformset_factory(
    Order,               # Parent model
    OrderItem,           # Child model
    form=OrderItemForm,  # Form for each item
    extra=0,
    can_delete=True,
    min_num=1,
    validate_min=True,
)
