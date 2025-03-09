from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from .models import Ledger


@admin.register(Ledger)
class LedgerAdmin(admin.ModelAdmin):
    """账本管理界面"""
    list_display = ('name', 'category_name', 'user_display', 'default_status', 'created_display')
    list_filter = ('is_default', 'category', 'created_at')
    search_fields = ('name', 'user_id')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        (_('基本信息'), {
            'fields': ('name', 'category', 'user_id')
        }),
        (_('账本设置'), {
            'fields': ('is_default',),
            'description': _('设置为默认账本后，该用户的其他账本将自动变为非默认')
        }),
        (_('时间信息'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def category_name(self, obj):
        """返回分类名称"""
        if obj.category:
            return obj.category.name
        return _('未分类')
    category_name.short_description = _('账本分类')
    category_name.admin_order_field = 'category__name'
    
    def user_display(self, obj):
        """显示用户ID"""
        return format_html('<span title="{}">{}</span>', 
                          _('点击查看该用户的所有账本'), 
                          obj.user_id)
    user_display.short_description = _('用户ID')
    user_display.admin_order_field = 'user_id'
    
    def default_status(self, obj):
        """高亮显示默认状态"""
        if obj.is_default:
            return format_html('<span style="color:green; font-weight:bold;">✓ {}</span>', 
                              _('默认'))
        return format_html('<span style="color:gray;">✗ {}</span>', 
                          _('非默认'))
    default_status.short_description = _('默认状态')
    default_status.admin_order_field = 'is_default'
    
    def created_display(self, obj):
        """格式化显示创建时间"""
        return obj.created_at.strftime('%Y-%m-%d %H:%M')
    created_display.short_description = _('创建时间')
    created_display.admin_order_field = 'created_at'
    
    def get_queryset(self, request):
        """优化查询性能"""
        return super().get_queryset(request).select_related('category')
    
    def save_model(self, request, obj, form, change):
        """保存模型时记录额外信息"""
        # 记录额外调试信息(可选)
        # print(f"保存账本: {obj.name}, 用户ID: {obj.user_id}")
        super().save_model(request, obj, form, change)
    
    actions = ['make_default']
    
    @admin.action(description=_('设为默认账本'))
    def make_default(self, request, queryset):
        """批量设置默认账本操作"""
        # 分组处理，确保每个用户只有一个默认账本
        user_ids = set()
        for ledger in queryset:
            user_ids.add(ledger.user_id)
        
        updated = 0
        for user_id in user_ids:
            # 找到该用户在选中集合中的第一个账本
            first_ledger = queryset.filter(user_id=user_id).first()
            if first_ledger:
                # 取消该用户的所有默认账本
                Ledger.objects.filter(user_id=user_id, is_default=True).update(is_default=False)
                # 设置新的默认账本
                first_ledger.is_default = True
                first_ledger.save()
                updated += 1
        
        self.message_user(
            request,
            _('成功将 %(count)d 个账本设为默认账本 (每个用户只处理第一个选中的账本)') % {'count': updated}
        )
    
    class Media:
        """添加自定义CSS美化界面"""
        css = {
            'all': ('admin/css/custom_ledger_admin.css',)
        }
        # 实际使用时，需要创建此CSS文件或移除此配置
