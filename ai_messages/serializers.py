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
            'random', 'emoji', 'file_path', 'voice_date', 'message_type', 'message_type_display', 'is_user',
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
        fields = ['id', 'session', 'content', 'transaction_ids', 'message_type']

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
        fields = ['id', 'model', 'assistant_name']


class MessageSessionDetailSerializer(MessageSessionSerializer):
    """带消息列表的会话详情序列化器"""
    messages = MessageSerializer(many=True, read_only=True)

    class Meta(MessageSessionSerializer.Meta):
        fields = MessageSessionSerializer.Meta.fields + ['messages']


class MessageProcessSerializer(serializers.Serializer):
    """消息处理序列化器"""
    session_id = serializers.IntegerField(required=False)
    content = serializers.CharField(required=True)
    ledger_id = serializers.IntegerField(required=True)
    asset_id = serializers.IntegerField(required=False, allow_null=True)
    language = serializers.CharField(required=False, default='en')
    assistant_name = serializers.CharField(required=False, default='Alice')
    file_path = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    voice_date = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    user_template_id = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text="模板id")

    def validate(self, data):
        """验证至少提供了session_id或session_uuid之一"""
        if 'session_id' not in data:
            raise serializers.ValidationError(_("必须提供会话ID或会话ID"))
        return data

    def validate_session_id(self, value):
        """验证会话ID"""
        if value and value <= 0:
            raise serializers.ValidationError(_("会话ID必须是正整数"))
        return value

    def validate_content(self, value):
        """验证消息内容"""
        if not value.strip():
            raise serializers.ValidationError(_("消息内容不能为空"))
        return value

    def validate_ledger_id(self, value):
        """验证账本ID"""
        if value <= 0:
            raise serializers.ValidationError(_("账本ID必须是正整数"))
        return value 