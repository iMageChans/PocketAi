from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from utils.serializers_fields import TimestampField
from .models import Goal, Deposit


class DepositSerializer(serializers.ModelSerializer):
    """存款记录序列化器"""
    deposit_date = TimestampField(read_only=True)
    
    class Meta:
        model = Deposit
        fields = ['id', 'goal', 'amount', 'notes', 'deposit_date']
        read_only_fields = ['id', 'deposit_date']


class GoalSerializer(serializers.ModelSerializer):
    """梦想基金序列化器"""
    deadline = TimestampField()
    created_at = TimestampField(read_only=True)
    updated_at = TimestampField(read_only=True)
    progress_percentage = serializers.SerializerMethodField()
    remaining_amount = serializers.SerializerMethodField()
    
    class Meta:
        model = Goal
        fields = [
            'id', 'name', 'user_id', 'target_amount', 'current_amount',
            'deadline', 'description', 'is_completed', 'progress_percentage',
            'remaining_amount', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user_id', 'current_amount', 'is_completed', 
                           'created_at', 'updated_at']
    
    def get_progress_percentage(self, obj):
        """计算完成进度百分比"""
        if obj.target_amount <= 0:
            return 100
        percentage = (obj.current_amount / obj.target_amount) * 100
        return min(round(percentage, 2), 100)
    
    def get_remaining_amount(self, obj):
        """计算剩余需要存储的金额"""
        remaining = obj.target_amount - obj.current_amount
        return max(remaining, 0)


class GoalCreateSerializer(serializers.ModelSerializer):
    """创建梦想基金的序列化器"""
    deadline = TimestampField()
    
    class Meta:
        model = Goal
        fields = ['id','name', 'target_amount', 'deadline', 'description']
    
    def validate_target_amount(self, value):
        """验证目标金额必须大于0"""
        if value <= 0:
            raise serializers.ValidationError(_("目标金额必须大于0"))
        return value


class DepositCreateSerializer(serializers.ModelSerializer):
    """创建存款记录的序列化器"""
    class Meta:
        model = Deposit
        fields = ['id','goal', 'amount', 'notes']
    
    def validate(self, attrs):
        """验证存款操作"""
        goal = attrs.get('goal')
        
        # 只检查梦想基金是否已完成，不再检查存款金额是否超过目标
        if goal.is_completed:
            raise serializers.ValidationError(_("该梦想基金已达成目标，不能继续存款"))
        
        return attrs 