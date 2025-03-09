from rest_framework import serializers

from utils.serializers_fields import TimestampField
from .models import Ledger
from categorization.serializers import LedgerCategorySerializer


class LedgerSerializer(serializers.ModelSerializer):
    """账本序列化器"""
    category_detail = LedgerCategorySerializer(source='category', read_only=True)

    created_at = TimestampField(read_only=True)
    updated_at = TimestampField(read_only=True)
    
    class Meta:
        model = Ledger
        fields = [
            'id', 'name', 'category', 'category_detail', 
            'user_id', 'is_default', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        

class LedgerCreateSerializer(serializers.ModelSerializer):

    """创建账本的序列化器"""
    class Meta:
        model = Ledger
        fields = ['name', 'category', 'is_default'] 