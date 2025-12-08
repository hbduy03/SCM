from django.db import models, transaction
from django.db.models import CharField

from apps.catalog.models import Product, Supplier

from apps.sales.models import Order
from inventorySystem.settings import AUTH_USER_MODEL


class Inventory(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)
    min_quantity = models.IntegerField(default=10)
    max_quantity = models.IntegerField(default=1000)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.product.name} - Qty {self.quantity}'

    @property
    def is_low_stock(self):
        return self.quantity <= self.min_quantity


from django.db import models

class StockIn(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)
    updated_quantity = models.IntegerField(default=0)
    unit_price = models.DecimalField(max_digits=20, decimal_places=2)
    total_cost = models.DecimalField(max_digits=24, decimal_places=2, editable=False)
    note=models.TextField(blank=True, verbose_name='NOte')
    approved_by = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
                                    related_name='approved_stockins')
    created_by = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name='Created By')
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    is_disable = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.total_cost = self.quantity * self.unit_price
        super().save(*args, **kwargs)

    def __str__(self):
        return f'StockIn {self.product.name} - QT {self.quantity} - Date {self.created_at}'


class StockOut(models.Model):
    TYPE_CHOICES = [
        ('order', 'Sales Order'),
        ('damaged', 'Damaged'),
        ('return_supplier', 'Return to Supplier'),
        ('promotion', 'Promotion/Gift'),
        ('internal', 'Internal Use'),
        ('transfer', 'Stock Transfer'),
        ('adjustment', 'Inventory Adjustment'),
        ('other', 'Other'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True, blank=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='order')
    quantity = models.IntegerField(default=0)
    updated_quantity = models.IntegerField(default=0)
    reason = models.CharField(max_length=200, blank=True)
    note = models.TextField(blank=True)
    approved_by = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='approved_stockouts')
    created_by = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    is_disable = models.BooleanField(default=False)
    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Out {self.quantity} {self.product.unit} - {self.get_type_display()}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None

        if is_new:
            with transaction.atomic():
                inventory = Inventory.objects.select_for_update().get(product=self.product)
                if inventory.quantity < self.quantity:
                    raise ValueError(f"Insufficient stock! Current stock: {inventory.quantity}")

                inventory.quantity -= self.quantity
                inventory.save()

                self.updated_quantity = inventory.quantity
        super().save(*args, **kwargs)
