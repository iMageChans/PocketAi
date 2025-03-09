from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.db.models import Sum, Count, Case, When, Value, DecimalField
from django.db.models.functions import Coalesce
from decimal import Decimal
from .models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    """交易记录管理界面"""
    list_display = (
        'transaction_type_icon', 'formatted_amount', 'category_display', 
        'asset_display', 'ledger_display', 'formatted_date', 
        'include_in_stats_icon', 'user_display'
    )
    list_filter = (
        'is_expense', 'include_in_stats', 'transaction_date',
        'ledger', 'asset', 'category'
    )
    search_fields = ('notes', 'user_id', 'amount')
    date_hierarchy = 'transaction_date'
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        (_('基本信息'), {
            'fields': ('user_id', 'is_expense', 'amount')
        }),
        (_('关联信息'), {
            'fields': ('ledger', 'asset', 'category')
        }),
        (_('交易详情'), {
            'fields': ('transaction_date', 'notes', 'include_in_stats')
        }),
        (_('时间信息'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """优化查询，预加载关联对象"""
        return super().get_queryset(request).select_related(
            'ledger', 'asset', 'category'
        )
    
    def transaction_type_icon(self, obj):
        """交易类型图标"""
        if obj.is_expense:
            return format_html(
                '<span style="color:red; font-weight:bold;">{} {}</span>',
                '↓', _('支出')
            )
        return format_html(
            '<span style="color:green; font-weight:bold;">{} {}</span>',
            '↑', _('收入')
        )
    transaction_type_icon.short_description = _('交易类型')
    transaction_type_icon.admin_order_field = 'is_expense'
    
    def formatted_amount(self, obj):
        """格式化金额显示"""
        color = "red" if obj.is_expense else "green"
        prefix = "-" if obj.is_expense else "+"
        
        # 获取资产的货币类型
        currency = 'USD'  # 默认货币
        if obj.asset and hasattr(obj.asset, 'currency'):
            currency = obj.asset.currency
            
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}{} {}</span>',
            color, prefix, obj.amount, currency
        )
    formatted_amount.short_description = _('金额')
    formatted_amount.admin_order_field = 'amount'
    
    def category_display(self, obj):
        """显示交易分类"""
        if not obj.category:
            return _('未分类')
        
        category_type = _('收入') if obj.category.is_income else _('支出')
        return format_html(
            '<span>{} ({})</span>',
            obj.category.name,
            category_type
        )
    category_display.short_description = _('交易分类')
    category_display.admin_order_field = 'category__name'
    
    def asset_display(self, obj):
        """显示关联资产"""
        if not obj.asset:
            return _('未关联资产')
        
        return format_html(
            '<span title="{}">{}</span>',
            _('查看资产详情'),
            obj.asset.name
        )
    asset_display.short_description = _('关联资产')
    asset_display.admin_order_field = 'asset__name'
    
    def ledger_display(self, obj):
        """显示关联账本"""
        if not obj.ledger:
            return _('未关联账本')
        
        return format_html(
            '<span title="{}">{}</span>',
            _('查看账本详情'),
            obj.ledger.name
        )
    ledger_display.short_description = _('所属账本')
    ledger_display.admin_order_field = 'ledger__name'
    
    def formatted_date(self, obj):
        """格式化显示交易日期"""
        return obj.transaction_date.strftime('%Y-%m-%d %H:%M')
    formatted_date.short_description = _('交易日期')
    formatted_date.admin_order_field = 'transaction_date'
    
    def include_in_stats_icon(self, obj):
        """用图标表示是否纳入统计"""
        if obj.include_in_stats:
            return format_html('<span style="color:green;">✓</span>')
        return format_html('<span style="color:gray;">✗</span>')
    include_in_stats_icon.short_description = _('纳入统计')
    include_in_stats_icon.admin_order_field = 'include_in_stats'
    
    def user_display(self, obj):
        """用户ID显示"""
        return format_html(
            '<span title="{}">{}</span>',
            _('点击查看该用户的所有交易'),
            obj.user_id
        )
    user_display.short_description = _('用户ID')
    user_display.admin_order_field = 'user_id'
    
    def changelist_view(self, request, extra_context=None):
        """添加交易统计信息到列表页面"""
        response = super().changelist_view(request, extra_context)
        
        try:
            # 获取当前筛选的查询集
            cl = response.context_data['cl']
            queryset = cl.queryset
            
            # 计算总收支情况
            summary = queryset.aggregate(
                total_expense=Coalesce(Sum(Case(
                    When(is_expense=True, then='amount'),
                    default=Value(Decimal('0')),
                    output_field=DecimalField()
                )), Value(Decimal('0')), output_field=DecimalField()),
                total_income=Coalesce(Sum(Case(
                    When(is_expense=False, then='amount'),
                    default=Value(Decimal('0')),
                    output_field=DecimalField()
                )), Value(Decimal('0')), output_field=DecimalField()),
                transaction_count=Count('id')
            )
            
            # 计算净额
            net_amount = summary['total_income'] - summary['total_expense']
            
            # 添加到上下文
            if not extra_context:
                extra_context = {}
                
            extra_context.update({
                'total_expense': summary['total_expense'].quantize(Decimal('0.01')),
                'total_income': summary['total_income'].quantize(Decimal('0.01')),
                'net_amount': net_amount.quantize(Decimal('0.01')),
                'transaction_count': summary['transaction_count'],
            })
            
            response.context_data.update(extra_context)
        except (AttributeError, KeyError):
            # 防止在其他视图出错
            pass
        
        return response
    
    class Media:
        """添加自定义CSS"""
        css = {
            'all': ('admin/css/custom_transaction_admin.css',)
        }
        js = ('admin/js/transaction_admin.js',)
