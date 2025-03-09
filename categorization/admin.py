from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import LedgerCategory, AssetCategory, TransactionCategory


@admin.register(LedgerCategory)
class LedgerCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'is_default', 'sort_order', 'created_at')
    list_display_links = ('name',)
    list_filter = ('is_default',)
    list_editable = ('sort_order',)
    search_fields = ('name', 'description')
    ordering = ('sort_order', 'name')
    
    fieldsets = (
        (_('基本信息'), {
            'fields': ('name', 'description', 'icon', 'is_default', 'sort_order')
        }),
    )
    
    def get_list_display(self, request):
        """返回经过翻译的列表显示字段"""
        return (
            'name', 
            'description', 
            'is_default', 
            'sort_order', 
            'created_at'
        )
    
    def get_ordering(self, request):
        return ('sort_order', 'name')


@admin.register(AssetCategory)
class AssetCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'category_type', 'is_positive_asset', 'sort_order', 'created_at')
    list_display_links = ('name',)
    list_filter = ('category_type', 'is_positive_asset')
    list_editable = ('sort_order',)
    search_fields = ('name',)
    ordering = ('sort_order', 'category_type', 'name')
    
    fieldsets = (
        (_('基本信息'), {
            'fields': ('name', 'icon')
        }),
        (_('分类设置'), {
            'fields': ('category_type', 'is_positive_asset', 'sort_order')
        }),
    )
    
    def get_list_display(self, request):
        return (
            'name', 
            'category_type', 
            'is_positive_asset', 
            'sort_order', 
            'created_at'
        )
    
    def get_ordering(self, request):
        return ('sort_order', 'category_type', 'name')


@admin.register(TransactionCategory)
class TransactionCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_income', 'sort_order', 'created_at')
    list_display_links = ('name',)
    list_filter = ('is_income',)
    list_editable = ('sort_order',)
    search_fields = ('name',)
    ordering = ('sort_order', '-is_income', 'name')
    
    fieldsets = (
        (_('基本信息'), {
            'fields': ('name', 'icon')
        }),
        (_('分类设置'), {
            'fields': ('is_income', 'sort_order')
        }),
    )
    
    def get_list_display(self, request):
        return (
            'name', 
            'is_income', 
            'sort_order', 
            'created_at'
        )
    
    def get_ordering(self, request):
        return ('sort_order', '-is_income', 'name')
