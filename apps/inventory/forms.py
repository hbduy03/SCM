from django import forms
from .models import *

class StockInForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(StockInForm, self).__init__(*args, **kwargs)
        self.fields['supplier'].queryset = Supplier.objects.filter(is_active=True)
        self.fields['product'].queryset = Product.objects.filter(is_active=True)

    class Meta:
        model = StockIn
        fields = ['product', 'supplier', 'quantity', 'unit_price', 'note']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-control'}),
            'supplier': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'note': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'product': 'Product',
            'supplier': 'Supplier',
            'quantity': 'Quantity',
            'unit_price': 'Unit Price',
            'note': 'Detailed Note',
        }


class StockOutForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(StockOutForm, self).__init__(*args, **kwargs)
        self.fields['product'].queryset = Product.objects.filter(is_active=True)

    class Meta:
        model = StockOut
        fields = ['product', 'type', 'quantity', 'reason', 'note']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-control'}),
            'type': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'reason': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Reason for stock-out'
            }),
            'note': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'product': 'Product',
            'type': 'Stock-out Type',
            'quantity': 'Quantity',
            'reason': 'Reason',
            'note': 'Detailed Note',
        }
