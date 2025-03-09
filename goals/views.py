from django.shortcuts import render
from django.db import transaction
from django.db.models import Sum, F, Q
from rest_framework import status, serializers
from rest_framework.decorators import action
from rest_framework.viewsets import GenericViewSet
from django.utils.translation import gettext_lazy as _
from decimal import Decimal

from utils.permissions import IsAuthenticatedExternal
from utils.mixins import *
from .models import Goal, Deposit
from .serializers import (
    GoalSerializer, GoalCreateSerializer,
    DepositSerializer, DepositCreateSerializer
)


class GoalViewSet(CreateModelMixin,
                  RetrieveModelMixin,
                  UpdateModelMixin,
                  PartialUpdateModelMixin,
                  ListModelMixin,
                  GenericViewSet):
    """梦想基金视图集"""
    queryset = Goal.objects.all()
    serializer_class = GoalSerializer
    permission_classes = [IsAuthenticatedExternal]
    
    def get_serializer_class(self):
        """根据操作返回不同的序列化器"""
        if self.action == 'create':
            return GoalCreateSerializer
        return GoalSerializer
    
    def get_queryset(self):
        """获取当前用户的梦想基金"""
        queryset = super().get_queryset()
        
        # 从认证后的请求中获取用户ID
        user_id = None
        if hasattr(self.request, 'remote_user'):
            user_id = self.request.remote_user.get('id')
            
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        else:
            queryset = queryset.none()
            
        # 按状态筛选
        is_completed = self.request.GET.get('is_completed')
        if is_completed is not None:
            is_completed = is_completed.lower() in ('true', '1', 'yes')
            queryset = queryset.filter(is_completed=is_completed)
            
        # 搜索关键词
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search)
            )
            
        return queryset
    
    def perform_create(self, serializer):
        """创建梦想基金时自动添加用户ID"""
        user_id = self.request.remote_user.get('id')
            
        if not user_id:
            raise serializers.ValidationError(_('无法获取用户ID'))
            
        serializer.save(user_id=user_id)
    
    @action(detail=True, methods=['post'])
    def deposit(self, request, pk=None):
        """向梦想基金存款"""
        goal = self.get_object()
        
        # 使用专门的存款序列化器
        serializer = DepositCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # 验证存款目标是否匹配
        if serializer.validated_data.get('goal').id != goal.id:
            return Response({
                'code': 400,
                'msg': _('存款目标不匹配'),
                'data': {}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 如果已经完成目标，不允许继续存款
        if goal.is_completed:
            return Response({
                'code': 400,
                'msg': _('该梦想基金已达成目标，不能继续存款'),
                'data': {}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 获取存款金额
        deposit_amount = serializer.validated_data.get('amount')
        
        # 使用事务确保数据一致性
        with transaction.atomic():
            # 创建存款记录
            deposit = serializer.save()
            
            # 更新梦想基金当前金额
            goal.current_amount += deposit_amount
            
            # 如果当前金额达到或超过目标金额，标记为已完成
            if goal.current_amount >= goal.target_amount:
                goal.is_completed = True
            
            goal.save()
        
        # 返回更新后的梦想基金信息
        goal_serializer = self.get_serializer(goal)
        return Response({
            'code': 200,
            'msg': _('存款成功'),
            'data': {
                'goal': goal_serializer.data,
                'deposit': DepositSerializer(deposit).data
            }
        })
    
    @action(detail=True, methods=['get'])
    def deposits(self, request, pk=None):
        """获取梦想基金的存款记录"""
        goal = self.get_object()
        deposits = goal.deposits.all().order_by('-deposit_date')
        
        # 分页
        page = self.paginate_queryset(deposits)
        if page is not None:
            serializer = DepositSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = DepositSerializer(deposits, many=True)
        return Response({
            'code': 200,
            'msg': _('获取成功'),
            'data': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """获取用户梦想基金总览"""
        queryset = self.get_queryset()
        
        # 统计数据
        total_goals = queryset.count()
        completed_goals = queryset.filter(is_completed=True).count()
        in_progress_goals = total_goals - completed_goals
        
        # 计算总金额
        total_target = queryset.aggregate(
            total=Sum('target_amount')
        )['total'] or Decimal('0')
        
        total_current = queryset.aggregate(
            total=Sum('current_amount')
        )['total'] or Decimal('0')
        
        # 计算总体进度
        overall_progress = 0
        if total_target > 0:
            overall_progress = min(round((total_current / total_target) * 100, 2), 100)
        
        return Response({
            'code': 200,
            'msg': _('获取成功'),
            'data': {
                'total_goals': total_goals,
                'completed_goals': completed_goals,
                'in_progress_goals': in_progress_goals,
                'total_target_amount': total_target,
                'total_current_amount': total_current,
                'overall_progress': overall_progress
            }
        })
