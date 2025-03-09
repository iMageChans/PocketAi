from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from decimal import Decimal


class Goal(models.Model):
    """梦想基金模型"""
    name = models.CharField(_('基金名称'), max_length=100)
    user_id = models.CharField(_('用户ID'), max_length=50, db_index=True)
    target_amount = models.DecimalField(
        _('目标金额'), 
        max_digits=15, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    current_amount = models.DecimalField(
        _('当前金额'), 
        max_digits=15, 
        decimal_places=2,
        default=Decimal('0.00')
    )
    deadline = models.DateTimeField(_('截止日期'))
    description = models.TextField(_('描述'), blank=True)
    is_completed = models.BooleanField(_('是否完成'), default=False)
    
    # 元数据字段
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)
    
    class Meta:
        verbose_name = _('梦想基金')
        verbose_name_plural = _('梦想基金')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.current_amount}/{self.target_amount}"
    
    def save(self, *args, **kwargs):
        """重写保存方法，检查是否达成目标"""
        if self.current_amount >= self.target_amount and not self.is_completed:
            self.is_completed = True
        super().save(*args, **kwargs)


class Deposit(models.Model):
    """存款记录模型"""
    goal = models.ForeignKey(
        Goal, 
        on_delete=models.CASCADE,
        related_name='deposits',
        verbose_name=_('梦想基金')
    )
    amount = models.DecimalField(
        _('存款金额'), 
        max_digits=15, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    notes = models.CharField(_('备注'), max_length=255, blank=True)
    deposit_date = models.DateTimeField(_('存款日期'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('存款记录')
        verbose_name_plural = _('存款记录')
        ordering = ['-deposit_date']
    
    def __str__(self):
        return f"{self.goal.name} - {self.amount}"
