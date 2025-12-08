
from django.contrib import admin
from .models import Inventory, StockIn, StockOut


@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ('product__product_id','product', 'quantity', 'min_quantity', 'max_quantity', 'is_low_stock', 'last_updated')
    list_filter = ('last_updated', 'min_quantity')
    search_fields = ('product__name', 'product__code')
    readonly_fields = ('quantity', 'last_updated')  # Không cho phép sửa quantity trực tiếp
    # Dùng list_select_related để tối ưu truy vấn ForeignKey
    list_select_related = ('product',)

    # Hiển thị trạng thái tồn kho thấp (Low Stock)
    def is_low_stock(self, obj):
        return obj.is_low_stock

    is_low_stock.boolean = True
    is_low_stock.short_description = "Tồn kho thấp"


@admin.register(StockIn)
class StockInAdmin(admin.ModelAdmin):
    list_display = ('product__product_id','product', 'supplier', 'quantity', 'unit_price', 'total_cost', 'created_by', 'created_at')
    search_fields = ('product__name', 'supplier__name')
    list_filter = ('supplier', 'created_at')
    list_select_related = ('product', 'supplier', 'created_by')
    readonly_fields = ('total_cost',)


@admin.register(StockOut)
class StockOutAdmin(admin.ModelAdmin):
    list_display = ('product', 'quantity', 'order', 'created_by', 'created_at')
    search_fields = ('product__name', 'order__order_code')
    list_filter = ('created_at',)
    list_select_related = ('product', 'order', 'created_by')