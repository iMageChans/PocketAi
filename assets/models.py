from django.db import models
from django.utils.translation import gettext_lazy as _
from categorization.models import AssetCategory
from decimal import Decimal


class CurrencyRate(models.Model):
    """货币汇率模型"""
    CURRENCY_CHOICES = (
        ('USD', _('美元')),
        ('CNY', _('人民币')),
        ('EUR', _('欧元')),
        ('JPY', _('日元')),
        ('KRW', _('韩元')),
    )
    
    currency = models.CharField(
        _('货币代码'), 
        max_length=3, 
        choices=CURRENCY_CHOICES,
        unique=True
    )
    rate_to_usd = models.DecimalField(
        _('兑美元汇率'), 
        max_digits=15, 
        decimal_places=6,
        help_text=_('1单位该货币等于多少美元')
    )
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)
    
    class Meta:
        verbose_name = _('货币汇率')
        verbose_name_plural = _('货币汇率')
    
    def __str__(self):
        return f"{self.get_currency_display()} ({self.currency}): {self.rate_to_usd} USD"


class Asset(models.Model):
    """资产模型"""
    CURRENCY_CHOICES = (
        ('USD', _('美元')),
        ('CNY', _('人民币')),
        ('EUR', _('欧元')),
        ('JPY', _('日元')),
        ('KRW', _('韩元')),
    )
    
    name = models.CharField(_('资产名称'), max_length=100)
    category = models.ForeignKey(
        AssetCategory,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_('资产分类'),
        related_name='assets'
    )
    currency = models.CharField(
        _('货币类型'), 
        max_length=3, 
        choices=CURRENCY_CHOICES,
        default='USD'
    )
    balance = models.DecimalField(_('资产余额'), max_digits=17, decimal_places=2)
    notes = models.TextField(_('备注'), blank=True)
    include_in_total = models.BooleanField(
        _('列入总资产计算'), 
        default=True,
        help_text=_('是否将此资产计入总资产')
    )
    user_id = models.CharField(_('用户ID'), max_length=50, db_index=True)
    
    # 元数据字段
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)
    
    class Meta:
        verbose_name = _('资产')
        verbose_name_plural = _('资产')
        ordering = ['-balance', 'name']
    
    def __str__(self):
        return f"{self.name} - {self.balance} {self.currency} ({self.user_id})"
    
    def get_balance_in_usd(self):
        """获取资产的美元价值"""
        # 获取分类的正负属性
        is_positive = True
        if self.category and not self.category.is_positive_asset:
            is_positive = False
        
        # 计算基础金额
        amount = self.balance
        
        # 只有正资产需要转负号
        if not is_positive:
            amount = -amount
        
        # 货币转换
        if self.currency == 'USD':
            return amount
        
        try:
            rate = CurrencyRate.objects.get(currency=self.currency)
            return amount * rate.rate_to_usd
        except CurrencyRate.DoesNotExist:
            # 如果汇率不存在，仍然返回原始金额（默认1:1比例）
            # 这样可以避免完全丢失该资产的统计
            return amount
