from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.db.models import Sum, F, DecimalField
from django.db.models.functions import Coalesce
from decimal import Decimal
from .models import Asset, CurrencyRate


@admin.register(CurrencyRate)
class CurrencyRateAdmin(admin.ModelAdmin):
    """货币汇率管理界面"""
    list_display = ('currency_display', 'currency', 'rate_to_usd', 'updated_at')
    list_display_links = ('currency_display', 'currency')
    readonly_fields = ('updated_at',)
    
    def currency_display(self, obj):
        """格式化显示货币名称"""
        flags = {
            'USD': '🇺🇸',
            'CNY': '🇨🇳',
            'EUR': '🇪🇺',
            'JPY': '🇯🇵',
            'KRW': '🇰🇷',
        }
        flag = flags.get(obj.currency, '')
        return f"{flag} {obj.get_currency_display()}"
    currency_display.short_description = _('货币')
    
    def has_delete_permission(self, request, obj=None):
        """限制删除权限，防止误删基础货币"""
        return False


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    """资产管理界面"""
    list_display = (
        'name', 'category_display', 'formatted_balance', 
        'formatted_balance_usd', 'currency_flag', 
        'include_in_total_icon', 'user_display', 'created_at'
    )
    list_filter = ('currency', 'include_in_total', 'category', 'created_at')
    search_fields = ('name', 'user_id', 'notes')
    readonly_fields = ('created_at', 'updated_at', 'balance_in_usd')
    autocomplete_fields = ['category']
    
    fieldsets = (
        (_('基本信息'), {
            'fields': ('name', 'category', 'user_id')
        }),
        (_('资产详情'), {
            'fields': ('currency', 'balance', 'balance_in_usd', 'include_in_total', 'notes')
        }),
        (_('时间信息'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def balance_in_usd(self, obj):
        """计算美元价值"""
        return obj.get_balance_in_usd()
    balance_in_usd.short_description = _('美元价值')
    
    def get_queryset(self, request):
        """优化查询，预加载分类"""
        return super().get_queryset(request).select_related('category')
    
    def formatted_balance(self, obj):
        """格式化显示资产余额"""
        # 根据余额大小使用不同颜色
        if obj.balance > 0:
            color = "green"
        elif obj.balance < 0:
            color = "red"
        else:
            color = "gray"
            
        return format_html(
            '<span style="color: {}; font-weight: bold;">{} {}</span>',
            color,
            obj.balance,
            obj.currency
        )
    formatted_balance.short_description = _('资产余额')
    formatted_balance.admin_order_field = 'balance'
    
    def formatted_balance_usd(self, obj):
        """格式化显示美元余额"""
        usd_value = obj.get_balance_in_usd()
        
        # 根据余额大小使用不同颜色
        if usd_value > 0:
            color = "green"
        elif usd_value < 0:
            color = "red"
        else:
            color = "gray"
            
        return format_html(
            '<span style="color: {};">${}</span>',
            color,
            usd_value.quantize(Decimal('0.01'))
        )
    formatted_balance_usd.short_description = _('美元价值')
    
    def currency_flag(self, obj):
        """显示货币旗帜图标"""
        flags = {
            'USD': '🇺🇸',
            'CNY': '🇨🇳',
            'EUR': '🇪🇺',
            'JPY': '🇯🇵',
            'KRW': '🇰🇷',
        }
        flag = flags.get(obj.currency, '')
        return format_html(
            '<span title="{}">{} {}</span>',
            obj.get_currency_display(),
            flag,
            obj.currency
        )
    currency_flag.short_description = _('货币')
    currency_flag.admin_order_field = 'currency'
    
    def include_in_total_icon(self, obj):
        """用图标表示是否计入总资产"""
        if obj.include_in_total:
            return format_html('<span style="color:green;">✓</span>')
        return format_html('<span style="color:gray;">✗</span>')
    include_in_total_icon.short_description = _('计入总资产')
    include_in_total_icon.admin_order_field = 'include_in_total'
    
    def category_display(self, obj):
        """格式化显示分类"""
        if not obj.category:
            return _('未分类')
        
        return format_html(
            '<span>{} ({})</span>',
            obj.category.name,
            obj.category.get_category_type_display()
        )
    category_display.short_description = _('资产分类')
    category_display.admin_order_field = 'category__name'
    
    def user_display(self, obj):
        """用户ID显示"""
        return format_html(
            '<span title="{}">{}</span>',
            _('点击查看该用户的所有资产'),
            obj.user_id
        )
    user_display.short_description = _('用户ID')
    user_display.admin_order_field = 'user_id'
    
    def changelist_view(self, request, extra_context=None):
        """添加资产统计信息到列表页面"""
        response = super().changelist_view(request, extra_context)
        
        try:
            # 当前筛选的查询集
            queryset = self.get_queryset(request)
            
            # 总资产统计(美元)
            total_usd = sum(asset.get_balance_in_usd() for asset in queryset)
            
            # 按货币分组
            currency_totals = {}
            for asset in queryset:
                if asset.currency not in currency_totals:
                    currency_totals[asset.currency] = Decimal('0')
                currency_totals[asset.currency] += asset.balance
            
            # 格式化货币统计
            formatted_totals = []
            for currency, total in currency_totals.items():
                flags = {
                    'USD': '🇺🇸',
                    'CNY': '🇨🇳',
                    'EUR': '🇪🇺',
                    'JPY': '🇯🇵',
                    'KRW': '🇰🇷',
                }
                flag = flags.get(currency, '')
                formatted_totals.append({
                    'currency': currency,
                    'display': dict(Asset.CURRENCY_CHOICES).get(currency),
                    'flag': flag,
                    'total': total.quantize(Decimal('0.01')),
                })
            
            # 排序: 先USD, 然后按金额降序
            def sort_key(item):
                if item['currency'] == 'USD':
                    return (0, 0)
                return (1, -float(item['total']))
            
            formatted_totals.sort(key=sort_key)
            
            # 添加到上下文
            if not extra_context:
                extra_context = {}
                
            extra_context.update({
                'total_assets_usd': total_usd.quantize(Decimal('0.01')),
                'currency_totals': formatted_totals,
                'asset_count': queryset.count(),
            })
            
            response.context_data.update(extra_context)
        except (AttributeError, TypeError):
            # 防止在其他视图出错
            pass
        
        return response
    
    class Media:
        """添加自定义CSS和JS"""
        css = {
            'all': ('admin/css/custom_asset_admin.css',)
        }
