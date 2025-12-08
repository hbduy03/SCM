
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import *

@admin.register(User)
class UserAdmin(BaseUserAdmin):

    list_display = ['username', 'email', 'get_avatar', 'role', 'phone', 'is_active', 'date_joined']
    list_filter = ['role', 'is_active', 'is_staff', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'phone']

    fieldsets = BaseUserAdmin.fieldsets + (
        ('Thông tin bổ sung', {
            'fields': ('role', 'phone',  'avatar')
        }),
    )

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Thông tin bổ sung', {
            'fields': ('role', 'phone',  'avatar', 'email')
        }),
    )

    def get_avatar(self, obj):
        """Hiển thị avatar trong admin list"""
        if obj.avatar:
            return format_html('<img src="{}" width="40" height="40" style="border-radius: 50%;" />', obj.avatar.url)
        return format_html(
            '<div style="width:40px;height:40px;background:#ddd;border-radius:50%;display:flex;align-items:center;justify-content:center;"><i class="fas fa-user"></i></div>')

    get_avatar.short_description = 'Avatar'