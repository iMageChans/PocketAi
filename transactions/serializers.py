from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from utils.serializers_fields import TimestampField
from .models import Transaction
from ledger.serializers import LedgerSerializer
from assets.serializers import AssetSerializer
from categorization.serializers import TransactionCategorySerializer


class TransactionSerializer(serializers.ModelSerializer):
    """交易记录序列化器"""
    ledger_detail = LedgerSerializer(source='ledger', read_only=True)
    asset_detail = AssetSerializer(source='asset', read_only=True)
    category_detail = TransactionCategorySerializer(source='category', read_only=True)
    transaction_date = TimestampField()
    created_at = TimestampField(read_only=True)
    updated_at = TimestampField(read_only=True)
    
    class Meta:
        model = Transaction
        fields = [
            'id', 'user_id', 'is_expense', 'ledger', 'ledger_detail',
            'asset', 'asset_detail', 'category', 'category_detail',
            'amount', 'transaction_date', 'notes', 'include_in_stats',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user_id', 'created_at', 'updated_at']
    
    def to_representation(self, instance):
        """
        重写序列化方法，确保当asset为null时，序列化后的JSON中asset的id为0而不是null
        """
        ret = super().to_representation(instance)
        
        # 处理asset为null的情况
        if ret['asset'] is None:
            ret['asset'] = 0
        
        # 处理asset_detail为null的情况
        if ret['asset_detail'] is None:
            ret['asset_detail'] = {
                'id': 0,
                'name': '',
                'balance': 0,
                'currency': 'USD',
                'currency_display': '美元'
            }
        
        # 处理category为null的情况
        if ret['category'] is None:
            ret['category'] = 0
            
        # 处理category_detail为null的情况
        if ret['category_detail'] is None:
            ret['category_detail'] = {
                'id': 0,
                'name': '',
                'is_income': not instance.is_expense
            }
            
        return ret


class TransactionCreateSerializer(serializers.ModelSerializer):
    """创建交易记录的序列化器"""
    transaction_date = TimestampField()
    
    class Meta:
        model = Transaction
        fields = [
            'is_expense', 'ledger', 'asset', 'category',
            'amount', 'transaction_date', 'notes', 'include_in_stats'
        ]
    
    def validate(self, attrs):
        """验证创建交易的数据"""
        # 验证交易分类与交易类型是否匹配
        category = attrs.get('category')
        is_expense = attrs.get('is_expense', True)
        
        if category and category.is_income != (not is_expense):
            # 如果不匹配，根据分类自动调整交易类型
            attrs['is_expense'] = not category.is_income
            
        return attrs


class TransactionSummarySerializer(serializers.Serializer):
    """交易汇总序列化器"""
    total_expense = serializers.DecimalField(max_digits=20, decimal_places=2)
    total_income = serializers.DecimalField(max_digits=20, decimal_places=2)
    net_amount = serializers.DecimalField(max_digits=20, decimal_places=2)
    transaction_count = serializers.IntegerField()
    period = serializers.CharField(required=False)  # 时间段标识


class CategorySummarySerializer(serializers.Serializer):
    """分类汇总序列化器"""
    category_id = serializers.IntegerField()
    category_name = serializers.CharField()
    total_amount = serializers.DecimalField(max_digits=20, decimal_places=2)
    transaction_count = serializers.IntegerField()
    is_income = serializers.BooleanField()


class CategoryMonthlyStatSerializer(serializers.Serializer):
    """分类月度统计序列化器"""
    category_id = serializers.IntegerField()
    category_name = serializers.CharField()
    is_income = serializers.BooleanField()
    total_amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    transaction_count = serializers.IntegerField()


class MonthlyStatSerializer(serializers.Serializer):
    """月度统计序列化器"""
    month = serializers.CharField()
    month_timestamp = serializers.IntegerField()
    categories = CategoryMonthlyStatSerializer(many=True)
    total_expense = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_income = serializers.DecimalField(max_digits=15, decimal_places=2)
    net_amount = serializers.DecimalField(max_digits=15, decimal_places=2) 