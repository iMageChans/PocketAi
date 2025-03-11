from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from utils.serializers_fields import TimestampField
from .models import MessageSession, Message
from transactions.models import Transaction
from transactions.serializers import TransactionSerializer


class MessageSerializer(serializers.ModelSerializer):
    """消息序列化器"""
    created_at = TimestampField(read_only=True)
    updated_at = TimestampField(read_only=True)
    transactions = serializers.SerializerMethodField()
    message_type_display = serializers.CharField(source='get_message_type_display', read_only=True)
    
    class Meta:
        model = Message
        fields = [
            'id', 'session', 'content', 'transaction_ids', 
            'random_seed', 'message_type', 'message_type_display', 'is_user',
            'transactions', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_user']
    
    def get_transactions(self, obj):
        """获取关联的交易记录详情"""
        transaction_ids = obj.get_transaction_ids_list()
        if not transaction_ids:
            return []
        
        transactions = Transaction.objects.filter(id__in=transaction_ids)
        return TransactionSerializer(transactions, many=True).data


class MessageCreateSerializer(serializers.ModelSerializer):
    """创建消息的序列化器"""
    transaction_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        help_text=_('关联的交易ID列表')
    )
    
    class Meta:
        model = Message
        fields = ['session', 'content', 'transaction_ids', 'message_type']
    
    def validate_transaction_ids(self, value):
        """验证交易ID列表"""
        if not value:
            return value
        
        # 检查交易记录是否存在
        existing_ids = set(Transaction.objects.filter(
            id__in=value
        ).values_list('id', flat=True))
        
        invalid_ids = set(value) - existing_ids
        if invalid_ids:
            raise serializers.ValidationError(
                _('以下交易ID不存在: %(ids)s') % {'ids': ', '.join(map(str, invalid_ids))}
            )
        
        return value
    
    def create(self, validated_data):
        """创建消息"""
        transaction_ids = validated_data.pop('transaction_ids', None)
        
        message = Message(**validated_data)
        
        # 设置交易ID列表
        if transaction_ids:
            message.set_transaction_ids_list(transaction_ids)
        
        message.save()
        return message


class MessageSessionSerializer(serializers.ModelSerializer):
    """消息会话序列化器"""
    created_at = TimestampField(read_only=True)
    updated_at = TimestampField(read_only=True)
    
    class Meta:
        model = MessageSession
        fields = [
            'id', 'user_id', 'model', 'assistant_name', 
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user_id', 'created_at', 'updated_at']


class MessageSessionCreateSerializer(serializers.ModelSerializer):
    """创建消息会话的序列化器"""
    class Meta:
        model = MessageSession
        fields = ['model', 'assistant_name']


class MessageSessionDetailSerializer(MessageSessionSerializer):
    """带消息列表的会话详情序列化器"""
    messages = MessageSerializer(many=True, read_only=True)
    
    class Meta(MessageSessionSerializer.Meta):
        fields = MessageSessionSerializer.Meta.fields + ['messages'] 