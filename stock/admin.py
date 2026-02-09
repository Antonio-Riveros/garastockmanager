from django.contrib import admin
from .models import Category, Item
from django.utils.html import format_html

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')
    search_fields = ('name', 'code')

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'category', 'status', 'quantity', 'created_at', 'qr_code_preview')
    list_filter = ('category', 'status', 'created_at')
    search_fields = ('code', 'name', 'description')
    readonly_fields = ('code', 'qr_code', 'created_at')
    
    def qr_code_preview(self, obj):
        if obj.qr_code:
            return format_html('<img src="{}" width="50" height="50" />', obj.qr_code.url)
        return "-"
    qr_code_preview.short_description = "QR Code"
