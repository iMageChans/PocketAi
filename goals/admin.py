from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from .models import Goal, Deposit


class DepositInline(admin.TabularInline):
    """存款记录内联管理"""
    model = Deposit
    extra = 0
    readonly_fields = ('deposit_date',)
    fields = ('amount', 'notes', 'deposit_date')


@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    """梦想基金管理界面"""
    list_display = (
        'name', 'user_display', 'progress_display', 
        'deadline_display', 'status_display', 'created_at'
    )
    list_filter = ('is_completed', 'created_at')
    search_fields = ('name', 'user_id', 'description')
    readonly_fields = ('current_amount', 'is_completed', 'created_at', 'updated_at')
    inlines = [DepositInline]
    
    fieldsets = (
        (_('基本信息'), {
            'fields': ('name', 'user_id', 'description')
        }),
        (_('目标设置'), {
            'fields': ('target_amount', 'current_amount', 'deadline', 'is_completed')
        }),
        (_('时间信息'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def user_display(self, obj):
        """显示用户ID"""
        return format_html('<span title="{}">{}</span>', 
                          _('点击查看该用户的所有梦想基金'), 
                          obj.user_id)
    user_display.short_description = _('用户ID')
    user_display.admin_order_field = 'user_id'
    
    def progress_display(self, obj):
        """显示进度条"""
        if obj.target_amount <= 0:
            percentage = 100
        else:
            percentage = min(int((obj.current_amount / obj.target_amount) * 100), 100)
        
        # 根据进度使用不同颜色
        if percentage < 30:
            color = "red"
        elif percentage < 70:
            color = "orange"
        else:
            color = "green"
            
        return format_html(
            '<div style="width:100px; background-color:#f1f1f1; border-radius:4px;">'
            '<div style="width:{}px; height:10px; background-color:{}; border-radius:4px;"></div>'
            '</div>'
            '<span style="margin-left:5px;">{}/{} ({}%)</span>',
            percentage, color, obj.current_amount, obj.target_amount, percentage
        )
    progress_display.short_description = _('进度')
    
    def deadline_display(self, obj):
        """格式化显示截止日期"""
        return obj.deadline.strftime('%Y-%m-%d')
    deadline_display.short_description = _('截止日期')
    deadline_display.admin_order_field = 'deadline'
    
    def status_display(self, obj):
        """显示完成状态"""
        if obj.is_completed:
            return format_html('<span style="color:green; font-weight:bold;">✓ {}</span>', 
                              _('已完成'))
        return format_html('<span style="color:orange;">○ {}</span>', 
                          _('进行中'))
    status_display.short_description = _('状态')
    status_display.admin_order_field = 'is_completed'


@admin.register(Deposit)
class DepositAdmin(admin.ModelAdmin):
    """存款记录管理界面"""
    list_display = ('goal_name', 'amount', 'notes', 'deposit_date')
    list_filter = ('deposit_date', 'goal')
    search_fields = ('goal__name', 'notes')
    
    def goal_name(self, obj):
        """显示梦想基金名称"""
        return obj.goal.name
    goal_name.short_description = _('梦想基金')
    goal_name.admin_order_field = 'goal__name'
