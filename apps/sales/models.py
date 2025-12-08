from django.db import models

from inventorySystem.settings import AUTH_USER_MODEL


# Create your models here.
class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('transfer', 'Transfer'),
        ('cod', 'COD'),
    ]
    order_id = models.CharField(unique=True,max_length=20)
    customer_name = models.CharField(max_length=200)
    customer_email = models.EmailField(max_length=50)
    customer_phone = models.CharField(max_length=20)
    customer_address = models.TextField(max_length=200)
    note = models.TextField(blank=True)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='pending')
    total_amount = models.DecimalField(max_digits=30, decimal_places=2, default=0)
    created_by = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Status")

    def __str__(self):
        return f'Mã: {self.order_id} - KH: {self.customer_name}'

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name="Order")
    product = models.ForeignKey('catalog.Product', on_delete=models.PROTECT, verbose_name="Product")
    quantity = models.IntegerField(verbose_name="Quantity")
    unit_price = models.DecimalField(max_digits=20, decimal_places=2, verbose_name="Unit Price")
    subtotal = models.DecimalField(max_digits=24, decimal_places=2, editable=False, verbose_name="Subtotal")

    class Meta:
        unique_together = ('order', 'product')

    def save(self, *args, **kwargs):
        self.subtotal = self.quantity * self.unit_price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"


