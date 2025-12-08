# apps/sales/admin.py
from django.contrib import admin
from .models import Order, OrderItem
from apps.inventory.models import StockOut  # Dùng để xem StockOut liên quan


# Inline cho Chi tiết đơn hàng (OrderItem)
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1  # Thêm 1 dòng trống
    readonly_fields = ('subtotal',)
    autocomplete_fields = ('product',)  # Tối ưu hóa việc tìm kiếm sản phẩm


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'customer_name', 'status', 'total_amount', 'created_at', 'created_by')
    list_filter = ('status', 'created_at')
    search_fields = ('order_id', 'customer_name', 'customer_phone')
    readonly_fields = ('total_amount',)
    inlines = [OrderItemInline]

    fieldsets = (
        ("Thông tin Đơn hàng", {
            'fields': ('order_id', 'status', 'total_amount', 'created_by'),
        }),
        ("Thông tin Khách hàng", {
            'fields': ('customer_name', 'customer_phone', 'customer_address'),
        }),
    )

    # Tự động gán order_id nếu chưa có
    def save_model(self, request, obj, form, change):
        if not obj.order_id:
            # Logic tạo mã đơn hàng: ví dụ: ORD-YYYYMMDD-ID
            today_date = obj.created_at.strftime("%Y%m%d")
            # Nếu chưa lưu, chưa có ID. Dùng một ID tạm, hoặc chỉ tạo sau khi save
            # Với Serializer tốt hơn: order_id được tạo trước khi save.
            # Tạm thời để trống và dùng logic bên ngoài Admin nếu cần mã hóa phức tạp hơn.
            # Ở đây, tôi sẽ để người dùng nhập hoặc dùng ID sau khi lưu.
            pass
        obj.created_by = request.user
        super().save_model(request, obj, form, change)


# Thêm chức năng xem Phiếu xuất kho liên quan đến đơn hàng
class StockOutInline(admin.TabularInline):
    model = StockOut
    extra = 0
    can_delete = False
    readonly_fields = ('product', 'quantity', 'created_at', 'created_by', 'note')
    verbose_name = "Phiếu xuất kho liên quan"


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'unit_price', 'subtotal')
    list_filter = ('order__status',)
    search_fields = ('order__order_id', 'product__name')
    list_select_related = ('order', 'product')