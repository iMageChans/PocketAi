from django.db import models
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import pre_save, post_save, pre_delete
from django.dispatch import receiver
from decimal import Decimal

from ledger.models import Ledger
from assets.models import Asset
from categorization.models import TransactionCategory


class Transaction(models.Model):
    """交易记录模型"""
    user_id = models.CharField(_('用户ID'), max_length=50, db_index=True)
    is_expense = models.BooleanField(_('是否支出'), default=True, help_text=_('默认为支出，否则为收入'))
    
    # 关联字段
    ledger = models.ForeignKey(
        Ledger, 
        on_delete=models.CASCADE,
        verbose_name=_('所属账本'),
        related_name='transactions'
    )
    asset = models.ForeignKey(
        Asset,
        on_delete=models.CASCADE, 
        verbose_name=_('关联资产'),
        related_name='transactions',
        null=True,
        blank=True
    )
    category = models.ForeignKey(
        TransactionCategory,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_('交易分类'),
        related_name='transactions'
    )
    
    # 交易详情
    amount = models.DecimalField(_('交易金额'), max_digits=17, decimal_places=2)
    transaction_date = models.DateTimeField(_('交易时间'), db_index=True)
    notes = models.TextField(_('备注'), blank=True)
    include_in_stats = models.BooleanField(_('纳入统计'), default=True)
    
    # 用于余额变更追踪
    _original_asset_id = None
    _original_amount = None
    _original_is_expense = None
    
    # 元数据字段
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)
    
    class Meta:
        verbose_name = _('交易记录')
        verbose_name_plural = _('交易记录')
        ordering = ['-transaction_date']
        indexes = [
            models.Index(fields=['user_id', 'transaction_date']),
            models.Index(fields=['ledger', 'transaction_date']),
            models.Index(fields=['asset', 'transaction_date']),
        ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 保存原始值用于后续比较
        self._original_asset_id = self.asset_id if self.asset_id else None
        self._original_amount = self.amount if self.amount else Decimal('0.00')
        self._original_is_expense = self.is_expense
    
    def __str__(self):
        tx_type = _('支出') if self.is_expense else _('收入')
        return f"{tx_type}: {self.amount} - {self.category.name if self.category else ''} ({self.transaction_date.strftime('%Y-%m-%d')})"
    
    def save(self, *args, **kwargs):
        # 检查交易分类与交易类型是否匹配
        if self.category and self.category.is_income != (not self.is_expense):
            # 如果不匹配，则更新交易类型以匹配分类
            self.is_expense = not self.category.is_income
        
        super().save(*args, **kwargs)
    
    def update_asset_balance(self):
        """更新关联资产的余额"""
        if not self.asset:
            return
        
        # 计算变动金额
        change_amount = self.amount
        if self.is_expense:
            change_amount = -change_amount
        
        # 更新资产余额
        self.asset.balance += change_amount
        self.asset.save(update_fields=['balance', 'updated_at'])
    
    def restore_original_balance(self):
        """还原修改前对资产余额的影响"""
        if not self._original_asset_id:
            return
        
        try:
            original_asset = Asset.objects.get(pk=self._original_asset_id)
            
            # 计算原始交易对余额的影响
            original_change = self._original_amount
            if self._original_is_expense:
                original_change = -original_change
            
            # 还原余额（反向操作）
            original_asset.balance -= original_change
            original_asset.save(update_fields=['balance', 'updated_at'])
            
        except Asset.DoesNotExist:
            pass


# 信号处理器用于管理资产余额变更
@receiver(pre_save, sender=Transaction)
def transaction_pre_save(sender, instance, **kwargs):
    """交易记录保存前的处理，用于还原对原始资产的影响"""
    if instance.pk:  # 仅对更新操作处理
        try:
            # 获取数据库中的原始记录
            old_instance = Transaction.objects.get(pk=instance.pk)
            
            # 如果资产、金额或交易类型变化，则需要还原原始资产的余额
            if (old_instance.asset_id != instance.asset_id or 
                old_instance.amount != instance.amount or
                old_instance.is_expense != instance.is_expense):
                
                # 保存原始值
                instance._original_asset_id = old_instance.asset_id
                instance._original_amount = old_instance.amount
                instance._original_is_expense = old_instance.is_expense
                
                # 只有当原始资产存在时才还原余额
                if old_instance.asset_id:
                    # 还原原始资产余额
                    old_change = old_instance.amount
                    if old_instance.is_expense:
                        old_change = -old_change
                    
                    if old_instance.asset:
                        old_instance.asset.balance -= old_change
                        old_instance.asset.save(update_fields=['balance', 'updated_at'])
            
        except Transaction.DoesNotExist:
            pass

@receiver(post_save, sender=Transaction)
def transaction_post_save(sender, instance, created, **kwargs):
    """交易记录保存后的处理，用于更新当前资产的余额"""
    # 只有当资产存在时才更新余额
    if not instance.asset:
        return
        
    # 计算变动金额
    change_amount = instance.amount
    if instance.is_expense:
        change_amount = -change_amount
    
    # 更新当前资产余额
    instance.asset.balance += change_amount
    instance.asset.save(update_fields=['balance', 'updated_at'])

@receiver(pre_delete, sender=Transaction)
def transaction_pre_delete(sender, instance, **kwargs):
    """交易记录删除前，还原对资产余额的影响"""
    if not instance.asset:
        return
        
    # 计算该交易对资产余额的影响
    change_amount = instance.amount
    if instance.is_expense:
        change_amount = -change_amount
    
    # 还原余额（反向操作）
    instance.asset.balance -= change_amount
    instance.asset.save(update_fields=['balance', 'updated_at'])
