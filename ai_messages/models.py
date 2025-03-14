from django.db import models
from django.utils.translation import gettext_lazy as _
import uuid
import json


# Create your models here.

class MessageSession(models.Model):
    """消息会话模型"""
    # 保留原有的自增ID作为主键
    user_id = models.IntegerField(_('用户ID'), db_index=True)
    model = models.CharField(_('模型名称'), max_length=255)
    assistant_name = models.CharField(_('助手名称'), max_length=100, blank=True, null=True)

    # 元数据字段
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)

    class Meta:
        verbose_name = _('消息会话')
        verbose_name_plural = _('消息会话')
        ordering = ['-updated_at']

    def __str__(self):
        """字符串表示"""
        if self.assistant_name:
            return f"{self.assistant_name} - {self.user_id} ({self.uuid})"
        return f"{self.model} - {self.user_id} ({self.uuid})"

    @property
    def session_id(self):
        """
        兼容性属性，返回整数ID
        用于保持与旧代码的兼容性
        """
        return self.id


class Message(models.Model):
    """消息模型"""
    # 消息类型常量
    TYPE_USER = 'user'
    TYPE_ASSISTANT = 'assistant'
    TYPE_SYSTEM = 'system'

    MESSAGE_TYPE_CHOICES = (
        (TYPE_USER, _('用户')),
        (TYPE_ASSISTANT, _('助手')),
        (TYPE_SYSTEM, _('系统')),
    )

    session = models.ForeignKey(
        MessageSession,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name=_('所属会话')
    )

    session_uuid = models.UUIDField(
        _('会话UUID'),
        null=True,
        blank=True,
        db_index=True,
        help_text=_('会话的UUID标识符')
    )

    user_id = models.IntegerField(_('用户ID'), db_index=True, blank=True, null=True)

    content = models.TextField(_('消息内容'))

    # 存储交易记录ID数组，以逗号分隔的字符串形式
    transaction_ids = models.TextField(
        _('关联交易ID'),
        default="0",
        help_text=_('以逗号分隔的交易ID列表，默认为0表示无关联交易')
    )

    # 随机数字段
    random = models.IntegerField(
        _('随机种子'),
        default=0
    )

    # 消息类型字段 - 使用字符串类型支持多种消息类型
    message_type = models.CharField(
        _('消息类型'),
        max_length=20,
        choices=MESSAGE_TYPE_CHOICES,
        default=TYPE_USER,
        db_index=True
    )

    # 保留原有的is_user字段以保持兼容性，但将其设为只读属性
    is_user = models.BooleanField(
        _('是否用户消息'),
        default=True,
        help_text=_('已废弃，请使用message_type字段')
    )

    is_voice = models.BooleanField(
        _('是否语音消息'),
        default=False,
    )

    emoji = models.CharField(
        '表情字段',
        max_length=50,
        default='random',
    )

    file_path = models.CharField(
        '语音路径',
        max_length=255,
        null=True,
        blank=True
    )

    voice_date = models.CharField(
        '语音秒数',
        max_length=255,
        null=True,
        blank=True
    )

    # 元数据字段
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)

    class Meta:
        verbose_name = _('消息')
        verbose_name_plural = _('消息')
        ordering = ['created_at']

    def __str__(self):
        """字符串表示"""
        prefix = self.get_message_type_display()
        return f"{prefix}: {self.content[:30]}..."

    def save(self, *args, **kwargs):

        # 同步is_user和message_type
        self.is_user = (self.message_type == self.TYPE_USER)
        super().save(*args, **kwargs)

    def get_transaction_ids_list(self):
        """获取交易ID列表"""
        if not self.transaction_ids or self.transaction_ids == "0":
            return []
        return [int(id_str) for id_str in self.transaction_ids.split(',') if id_str.strip().isdigit()]

    def set_transaction_ids_list(self, id_list):
        """设置交易ID列表"""
        if not id_list:
            self.transaction_ids = "0"
        else:
            self.transaction_ids = ','.join(str(id) for id in id_list)
