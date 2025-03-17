from django.db import models
from django.utils.translation import gettext_lazy as _


class LedgerCategory(models.Model):
    """账本分类模型"""
    name = models.CharField(_('名称'), max_length=50)
    description = models.TextField(_('描述'), blank=True, null=True)
    icon = models.CharField(_('图标'), max_length=100, blank=True)
    is_default = models.BooleanField(_('是否默认账本'), default=False)
    sort_order = models.IntegerField(_('排序'), default=0, help_text=_('数字越小排序越靠前'))
    
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)
    
    class Meta:
        verbose_name = _('账本分类')
        verbose_name_plural = _('账本分类')
        ordering = ['sort_order', 'name']
    
    def __str__(self):
        return self.name


class AssetCategory(models.Model):
    """资产分类模型"""
    CATEGORY_TYPE_CHOICES = (
        ('借记卡/现金', _('借记卡/现金')),
        ('信用卡', _('信用卡')),
        ('借贷', _('借贷')),
        ('投资', _('投资')),
        ('网络', _('网络')),
    )
    
    name = models.CharField(_('名称'), max_length=50)
    icon = models.CharField(_('图标'), max_length=100, blank=True)
    category_type = models.CharField(
        _('资产大分类'), 
        max_length=20, 
        choices=CATEGORY_TYPE_CHOICES
    )
    is_positive_asset = models.BooleanField(_('是否正资产'), default=True)
    sort_order = models.IntegerField(_('排序'), default=0, help_text=_('数字越小排序越靠前'))
    
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)
    
    class Meta:
        verbose_name = _('资产分类')
        verbose_name_plural = _('资产分类')
        ordering = ['sort_order', 'category_type', 'name']
    
    def __str__(self):
        return f"{self.get_category_type_display()}-{self.name}"


class TransactionCategory(models.Model):
    """交易分类模型"""
    name = models.CharField(_('名称'), max_length=50)
    is_income = models.BooleanField(_('是否收入'), default=False, help_text=_('默认为支出'))
    icon = models.CharField(_('图标'), max_length=100, blank=True)
    sort_order = models.IntegerField(_('排序'), default=0, help_text=_('数字越小排序越靠前'))
    
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)
    
    class Meta:
        verbose_name = _('交易分类')
        verbose_name_plural = _('交易分类')
        ordering = ['sort_order', '-is_income', 'name']
    
    def __str__(self):
        category_type = _('收入') if self.is_income else _('支出')
        return f"{category_type}-{self.name}"
