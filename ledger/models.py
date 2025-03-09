from django.db import models
from django.utils.translation import gettext_lazy as _
from categorization.models import LedgerCategory


class Ledger(models.Model):
    """账本模型"""
    name = models.CharField(_('账本名称'), max_length=100)
    category = models.ForeignKey(
        LedgerCategory, 
        on_delete=models.SET_NULL, 
        null=True,
        verbose_name=_('账本分类'),
        related_name='ledgers'
    )
    user_id = models.IntegerField(_('用户ID'), db_index=True, help_text=_('UserCenter的用户ID'))
    is_default = models.BooleanField(_('是否默认账本'), default=False)
    
    # 元数据字段
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)
    
    class Meta:
        verbose_name = _('账本')
        verbose_name_plural = _('账本')
        ordering = ['-is_default', 'name']
        # 确保用户ID和账本名称的组合唯一
        unique_together = [('user_id', 'name')]
    
    def __str__(self):
        return f"{self.name} ({self.user_id})"
    
    def save(self, *args, **kwargs):
        """重写保存方法，确保每个用户只有一个默认账本"""
        # 如果当前账本是默认的，将该用户的其他所有账本设为非默认
        if self.is_default:
            Ledger.objects.filter(
                user_id=self.user_id, 
                is_default=True
            ).exclude(pk=self.pk).update(is_default=False)
        
        # 如果用户没有默认账本，则将当前账本设为默认
        if not Ledger.objects.filter(user_id=self.user_id, is_default=True).exists():
            self.is_default = True
            
        super().save(*args, **kwargs)
