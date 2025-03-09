from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from .models import Asset, CurrencyRate
from categorization.serializers import AssetCategorySerializer
from utils.serializers_fields import TimestampField


class CurrencyRateSerializer(serializers.ModelSerializer):
    """货币汇率序列化器"""
    currency_display = serializers.CharField(source='get_currency_display', read_only=True)
    updated_at = TimestampField(read_only=True)
    
    class Meta:
        model = CurrencyRate
        fields = ['id', 'currency', 'currency_display', 'rate_to_usd', 'updated_at']
        read_only_fields = ['id', 'updated_at']


class AssetSerializer(serializers.ModelSerializer):
    """资产序列化器"""
    category_detail = AssetCategorySerializer(source='category', read_only=True)
    currency_display = serializers.CharField(source='get_currency_display', read_only=True)
    balance_in_usd = serializers.DecimalField(
        max_digits=17, 
        decimal_places=2, 
        read_only=True,
        source='get_balance_in_usd'
    )
    created_at = TimestampField(read_only=True)
    updated_at = TimestampField(read_only=True)

    class Meta:
        model = Asset
        fields = [
            'id', 'name', 'category', 'category_detail', 'currency', 'currency_display',
            'balance', 'balance_in_usd', 'notes', 'include_in_total', 'user_id',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user_id', 'created_at', 'updated_at', 'balance_in_usd']


class AssetCreateSerializer(serializers.ModelSerializer):
    """创建资产的序列化器"""
    class Meta:
        model = Asset
        fields = [
            'name', 'category', 'currency', 'balance', 
            'notes', 'include_in_total'
        ]


class AssetTotalByTypeSerializer(serializers.Serializer):
    """按类型统计资产总额的序列化器"""
    category_id = serializers.IntegerField()
    category_name = serializers.CharField()
    category_type = serializers.CharField()
    is_positive_asset = serializers.BooleanField(default=True)
    total_balance_usd = serializers.DecimalField(max_digits=20, decimal_places=2)
    asset_count = serializers.IntegerField() 