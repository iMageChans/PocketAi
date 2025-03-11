from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from .models import MessageSession, Message


class MessageInline(admin.TabularInline):
    """消息内联管理"""
    model = Message
    extra = 0
    readonly_fields = ('created_at',)
    fields = ('content', 'is_user', 'transaction_ids', 'created_at')


@admin.register(MessageSession)
class MessageSessionAdmin(admin.ModelAdmin):
    """消息会话管理界面"""
    list_display = ('assistant_display', 'model_display', 'user_display', 'message_count', 'updated_at')
    list_filter = ('model', 'created_at', 'updated_at')
    search_fields = ('assistant_name', 'model', 'user_id')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [MessageInline]
    
    fieldsets = (
        (_('基本信息'), {
            'fields': ('user_id', 'model', 'assistant_name')
        }),
        (_('时间信息'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def assistant_display(self, obj):
        """显示助手名称"""
        if obj.assistant_name:
            return format_html('<span style="font-weight:bold;">{}</span>', obj.assistant_name)
        return format_html('<span style="color:gray;">-</span>')
    assistant_display.short_description = _('助手名称')
    assistant_display.admin_order_field = 'assistant_name'
    
    def model_display(self, obj):
        """显示模型名称"""
        model_colors = {
            'gpt-4': 'green',
            'gpt-3.5': 'blue',
            'claude-3': 'purple',
            'claude-2': 'indigo',
        }
        
        color = 'black'
        for model_key, model_color in model_colors.items():
            if model_key in obj.model.lower():
                color = model_color
                break
                
        return format_html('<span style="color:{};">{}</span>', color, obj.model)
    model_display.short_description = _('模型')
    model_display.admin_order_field = 'model'
    
    def user_display(self, obj):
        """显示用户ID"""
        return format_html('<span title="{}">{}</span>', 
                          _('点击查看该用户的所有会话'), 
                          obj.user_id)
    user_display.short_description = _('用户ID')
    user_display.admin_order_field = 'user_id'
    
    def message_count(self, obj):
        """显示消息数量"""
        count = obj.messages.count()
        return format_html('<span title="{}">{}</span>', 
                          _('消息总数'), count)
    message_count.short_description = _('消息数')


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """消息管理界面"""
    list_display = ('message_type', 'content_preview', 'session_display', 'is_voice', 'has_transactions', 'created_at')
    list_filter = ('is_user', 'created_at', 'session__model')
    search_fields = ('content', 'session__assistant_name', 'session__user_id')
    readonly_fields = ('created_at', 'updated_at', 'random_seed')
    
    fieldsets = (
        (_('基本信息'), {
            'fields': ('session', 'is_user', 'is_voice', 'content')
        }),
        (_('关联信息'), {
            'fields': ('transaction_ids', 'random_seed')
        }),
        (_('时间信息'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def message_type(self, obj):
        """显示消息类型"""
        if obj.is_user:
            return format_html('<span style="color:blue;">👤 {}</span>', _('用户'))
        return format_html('<span style="color:green;">🤖 {}</span>', _('助手'))
    message_type.short_description = _('类型')
    message_type.admin_order_field = 'is_user'
    
    def content_preview(self, obj):
        """显示消息内容预览"""
        max_length = 50
        content = obj.content
        if len(content) > max_length:
            content = content[:max_length] + '...'
        return content
    content_preview.short_description = _('内容预览')
    
    def session_display(self, obj):
        """显示所属会话"""
        if obj.session.assistant_name:
            return format_html('{} ({})', 
                              obj.session.assistant_name,
                              obj.session.model)
        return obj.session.model
    session_display.short_description = _('所属会话')
    session_display.admin_order_field = 'session__assistant_name'
    
    def has_transactions(self, obj):
        """显示是否有关联交易"""
        transaction_ids = obj.get_transaction_ids_list()
        if transaction_ids:
            return format_html('<span style="color:green;">✓ {}</span>', len(transaction_ids))
        return format_html('<span style="color:gray;">✗</span>')
    has_transactions.short_description = _('关联交易')
    has_transactions.admin_order_field = 'transaction_ids'
