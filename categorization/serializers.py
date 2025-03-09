from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from .models import LedgerCategory, AssetCategory, TransactionCategory
from utils.serializers_fields import TimestampField


class LedgerCategorySerializer(serializers.ModelSerializer):
    """账本分类序列化器"""
    created_at = TimestampField(read_only=True)
    updated_at = TimestampField(read_only=True)
    
    class Meta:
        model = LedgerCategory
        fields = ['id', 'name', 'description', 'icon', 'is_default', 'sort_order', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
        extra_kwargs = {
            'name': {'error_messages': {'blank': _('账本名称不能为空')}},
            'icon': {'required': False},
            'description': {'required': False},
        }


class AssetCategorySerializer(serializers.ModelSerializer):
    """资产分类序列化器"""
    category_type_display = serializers.CharField(source='get_category_type_display', read_only=True, label=_('资产分类显示名称'))
    created_at = TimestampField(read_only=True)
    updated_at = TimestampField(read_only=True)
    
    class Meta:
        model = AssetCategory
        fields = ['id', 'name', 'icon', 'category_type', 'category_type_display', 'is_positive_asset', 'sort_order', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at', 'category_type_display']
        extra_kwargs = {
            'name': {'error_messages': {'blank': _('资产分类名称不能为空')}},
            'icon': {'required': False},
        }


class TransactionCategorySerializer(serializers.ModelSerializer):
    """交易分类序列化器"""
    type_display = serializers.SerializerMethodField(label=_('交易类型显示名称'))
    created_at = TimestampField(read_only=True)
    updated_at = TimestampField(read_only=True)
    
    class Meta:
        model = TransactionCategory
        fields = ['id', 'name', 'is_income', 'type_display', 'icon', 'sort_order', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at', 'type_display']
        extra_kwargs = {
            'name': {'error_messages': {'blank': _('交易分类名称不能为空')}},
            'icon': {'required': False},
        }
    
    def get_type_display(self, obj):
        """获取交易类型显示名称"""
        return _('收入') if obj.is_income else _('支出') 