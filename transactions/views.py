from django.shortcuts import render
from django.db.models import Sum, Count, Case, When, F, Q, Value, CharField, DecimalField
from django.db.models.functions import TruncDay, TruncWeek, TruncMonth, TruncYear, Coalesce
from rest_framework import status, serializers
from rest_framework.decorators import action
from rest_framework.viewsets import GenericViewSet
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
import pytz

from utils.permissions import IsAuthenticatedExternal
from utils.mixins import *
from .models import Transaction
from .serializers import (
    TransactionSerializer, TransactionCreateSerializer,
    TransactionSummarySerializer, CategorySummarySerializer,
    MonthlyStatSerializer
)


class TransactionViewSet(CreateModelMixin,
                       RetrieveModelMixin,
                       UpdateModelMixin,
                       PartialUpdateModelMixin,
                       DestroyModelMixin,
                       ListModelMixin,
                       GenericViewSet):
    """交易记录视图集"""
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticatedExternal]
    
    def get_serializer_class(self):
        """根据操作返回不同的序列化器"""
        if self.action == 'create':
            return TransactionCreateSerializer
        return TransactionSerializer
    
    def get_queryset(self):
        """获取当前用户的交易记录"""
        queryset = super().get_queryset()
        
        # 从认证后的请求中获取用户ID
        user_id = None
        if hasattr(self.request, 'remote_user'):
            user_id = self.request.remote_user.get('id')
            
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        else:
            queryset = queryset.none()
            
        # 按账本筛选
        ledger_id = self.request.GET.get('ledger_id')
        if ledger_id:
            queryset = queryset.filter(ledger_id=ledger_id)
            
        # 按资产筛选
        asset_id = self.request.GET.get('asset_id')
        if asset_id:
            queryset = queryset.filter(asset_id=asset_id)
            
        # 按类别筛选
        category_id = self.request.GET.get('category_id')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
            
        # 按交易类型筛选
        is_expense = self.request.GET.get('is_expense')
        if is_expense is not None:
            is_expense = is_expense.lower() in ('true', '1', 'yes')
            queryset = queryset.filter(is_expense=is_expense)
            
        # 按日期范围筛选
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        if start_date:
            try:
                start_date = datetime.fromtimestamp(int(start_date), tz=pytz.UTC)
                queryset = queryset.filter(transaction_date__gte=start_date)
            except (ValueError, TypeError):
                pass
                
        if end_date:
            try:
                end_date = datetime.fromtimestamp(int(end_date), tz=pytz.UTC)
                queryset = queryset.filter(transaction_date__lte=end_date)
            except (ValueError, TypeError):
                pass
                
        # 按金额范围筛选
        min_amount = self.request.GET.get('min_amount')
        max_amount = self.request.GET.get('max_amount')
        if min_amount:
            try:
                queryset = queryset.filter(amount__gte=Decimal(min_amount))
            except (ValueError, TypeError):
                pass
                
        if max_amount:
            try:
                queryset = queryset.filter(amount__lte=Decimal(max_amount))
            except (ValueError, TypeError):
                pass
        
        # 按纳入统计筛选
        include_in_stats = self.request.GET.get('include_in_stats')
        if include_in_stats is not None:
            include_in_stats = include_in_stats.lower() in ('true', '1', 'yes')
            queryset = queryset.filter(include_in_stats=include_in_stats)
            
        # 搜索关键词
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(notes__icontains=search) |
                Q(category__name__icontains=search) |
                Q(asset__name__icontains=search) |
                Q(ledger__name__icontains=search)
            )
            
        return queryset.select_related('ledger', 'asset', 'category')
    
    def perform_create(self, serializer):
        """创建交易记录时自动添加用户ID"""
        user_id = self.request.remote_user.get('id')
            
        if not user_id:
            raise serializers.ValidationError(_('无法获取用户ID'))
            
        serializer.save(user_id=user_id)
    
    @action(detail=False, methods=['get'])
    def by_ledger(self, request):
        """根据账本ID列出交易记录，并计算统计数据"""
        ledger_id = request.query_params.get('ledger_id')
        if not ledger_id:
            return self.get_error_response(msg=_('缺少账本ID参数'), code=400)
        
        # 基础查询集
        queryset = self.get_queryset().filter(ledger_id=ledger_id, include_in_stats=True)
        
        # 获取时间周期和偏移参数
        period = request.query_params.get('period', 'month')
        offset = request.query_params.get('offset', '0')
        
        # 计算时间范围和获取导航信息
        start_datetime, end_datetime, period_trunc, date_format, navigation_info = self._get_time_period_params(period, offset)
        
        # 时间范围筛选
        period_queryset = queryset.filter(
            transaction_date__gte=start_datetime,
            transaction_date__lte=end_datetime
        )
        
        # 计算总统计数据
        summary = period_queryset.aggregate(
            total_expense=Coalesce(Sum(Case(
                When(is_expense=True, then='amount'),
                default=Value(Decimal('0')),
                output_field=DecimalField()
            )), Value(Decimal('0')), output_field=DecimalField()),
            total_income=Coalesce(Sum(Case(
                When(is_expense=False, then='amount'),
                default=Value(Decimal('0')),
                output_field=DecimalField()
            )), Value(Decimal('0')), output_field=DecimalField()),
            transaction_count=Count('id')
        )
        
        # 计算净额
        summary['net_amount'] = summary['total_income'] - summary['total_expense']
        
        # 按时间段分组统计 - 修复类型混合问题
        period_stats = period_queryset.annotate(
            period=period_trunc
        ).values('period').annotate(
            total_expense=Coalesce(Sum(Case(
                When(is_expense=True, then='amount'),
                default=Value(Decimal('0')),
                output_field=DecimalField()
            )), Value(Decimal('0')), output_field=DecimalField()),
            total_income=Coalesce(Sum(Case(
                When(is_expense=False, then='amount'),
                default=Value(Decimal('0')),
                output_field=DecimalField()
            )), Value(Decimal('0')), output_field=DecimalField()),
            transaction_count=Count('id')
        ).order_by('period')
        
        # 格式化时间并计算净额
        formatted_periods = []
        for stat in period_stats:
            if stat['period']:
                period_str = stat['period'].strftime(date_format)
                formatted_periods.append({
                    'period': period_str,
                    'total_expense': stat['total_expense'],
                    'total_income': stat['total_income'],
                    'net_amount': stat['total_income'] - stat['total_expense'],
                    'transaction_count': stat['transaction_count']
                })
        
        # 按分类统计
        category_stats = period_queryset.values(
            'category_id', 
            'category__name', 
            'category__is_income'
        ).annotate(
            total_amount=Sum('amount'),
            transaction_count=Count('id')
        ).order_by('-total_amount')
        
        # 格式化分类统计
        formatted_categories = []
        for stat in category_stats:
            if stat['category_id']:
                formatted_categories.append({
                    'category_id': stat['category_id'],
                    'category_name': stat['category__name'] or _('未分类'),
                    'is_income': stat['category__is_income'],
                    'total_amount': stat['total_amount'],
                    'transaction_count': stat['transaction_count']
                })
        
        # 序列化结果
        summary_serializer = TransactionSummarySerializer(summary)
        periods_serializer = TransactionSummarySerializer(formatted_periods, many=True)
        categories_serializer = CategorySummarySerializer(formatted_categories, many=True)
        
        # 在响应中添加导航信息
        return self.get_success_response(
            data={
                'summary': summary_serializer.data,
                'periods': periods_serializer.data,
                'categories': categories_serializer.data,
                'navigation': navigation_info
            },
            msg=_('获取成功')
        )
    
    @action(detail=False, methods=['get'])
    def by_asset(self, request):
        """根据资产获取交易记录的统计数据"""
        asset_id = request.query_params.get('asset_id')
        if not asset_id:
            return self.get_success_response(
                msg='缺少资产ID参数',
                status_code=status.HTTP_400_BAD_REQUEST
            )
            
        queryset = self.get_queryset().filter(asset_id=asset_id, include_in_stats=True)
        
        # 获取时间周期和偏移参数
        period = request.query_params.get('period', 'month')
        if period not in ['month', 'year']:
            period = 'month'  # 对于资产视图，只支持month和year
        
        offset = request.query_params.get('offset', '0')
        
        # 计算时间范围和获取导航信息
        start_datetime, end_datetime, period_trunc, date_format, navigation_info = self._get_time_period_params(period, offset)
        
        # 时间范围筛选
        period_queryset = queryset.filter(
            transaction_date__gte=start_datetime,
            transaction_date__lte=end_datetime
        )
        
        # 计算总收支情况 - 修复类型混合问题
        summary = period_queryset.aggregate(
            total_expense=Coalesce(Sum(Case(
                When(is_expense=True, then='amount'),
                default=Value(Decimal('0')),
                output_field=DecimalField()
            )), Value(Decimal('0')), output_field=DecimalField()),
            total_income=Coalesce(Sum(Case(
                When(is_expense=False, then='amount'),
                default=Value(Decimal('0')),
                output_field=DecimalField()
            )), Value(Decimal('0')), output_field=DecimalField()),
            transaction_count=Count('id')
        )
        
        # 计算净额
        summary['net_amount'] = summary['total_income'] - summary['total_expense']
        
        # 按时间段分组统计 - 修复类型混合问题
        period_stats = period_queryset.annotate(
            period=period_trunc
        ).values('period').annotate(
            total_expense=Coalesce(Sum(Case(
                When(is_expense=True, then='amount'),
                default=Value(Decimal('0')),
                output_field=DecimalField()
            )), Value(Decimal('0')), output_field=DecimalField()),
            total_income=Coalesce(Sum(Case(
                When(is_expense=False, then='amount'),
                default=Value(Decimal('0')),
                output_field=DecimalField()
            )), Value(Decimal('0')), output_field=DecimalField()),
            transaction_count=Count('id')
        ).order_by('period')
        
        # 格式化时间并计算净额
        formatted_periods = []
        for stat in period_stats:
            if stat['period']:
                period_str = stat['period'].strftime(date_format)
                formatted_periods.append({
                    'period': period_str,
                    'total_expense': stat['total_expense'],
                    'total_income': stat['total_income'],
                    'net_amount': stat['total_income'] - stat['total_expense'],
                    'transaction_count': stat['transaction_count']
                })
        
        # 按分类统计
        category_stats = period_queryset.values(
            'category_id', 
            'category__name', 
            'category__is_income'
        ).annotate(
            total_amount=Sum('amount'),
            transaction_count=Count('id')
        ).order_by('-total_amount')
        
        # 格式化分类统计
        formatted_categories = []
        for stat in category_stats:
            if stat['category_id']:
                formatted_categories.append({
                    'category_id': stat['category_id'],
                    'category_name': stat['category__name'] or 'Others',
                    'is_income': stat['category__is_income'],
                    'total_amount': stat['total_amount'],
                    'transaction_count': stat['transaction_count']
                })
        
        # 序列化结果
        summary_serializer = TransactionSummarySerializer(summary)
        periods_serializer = TransactionSummarySerializer(formatted_periods, many=True)
        categories_serializer = CategorySummarySerializer(formatted_categories, many=True)
        
        # 在响应中添加导航信息
        return self.get_success_response(
            data={
                'summary': summary_serializer.data,
                'periods': periods_serializer.data,
                'categories': categories_serializer.data,
                'navigation': navigation_info
            },
            msg='获取成功'
        )

    @action(detail=False, methods=['get'])
    def asset_monthly_categories(self, request):
        """根据资产ID查询每个月按分类统计的数据"""
        # 获取资产ID
        asset_id = request.query_params.get('asset_id')
        if not asset_id:
            return self.get_error_response(
                msg=_('缺少资产ID参数'),
                code=400,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # 获取用户ID
        user_id = None
        if hasattr(request, 'remote_user'):
            user_id = request.remote_user.get('id')
        
        if not user_id:
            return self.get_error_response(
                msg=_('无法获取用户ID'),
                code=401,
                status_code=status.HTTP_401_UNAUTHORIZED
            )
        
        # 基础查询集
        queryset = Transaction.objects.filter(
            user_id=user_id,
            asset_id=asset_id,
            include_in_stats=True
        )
        
        # 获取时间范围参数
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if start_date:
            try:
                start_date = datetime.fromtimestamp(int(start_date), tz=pytz.UTC)
                queryset = queryset.filter(transaction_date__gte=start_date)
            except (ValueError, TypeError):
                pass
        
        if end_date:
            try:
                end_date = datetime.fromtimestamp(int(end_date), tz=pytz.UTC)
                queryset = queryset.filter(transaction_date__lte=end_date)
            except (ValueError, TypeError):
                pass
        
        # 按月份分组
        monthly_data = {}
        
        # 按月份和分类分组统计
        monthly_stats = queryset.annotate(
            month=TruncMonth('transaction_date')
        ).values(
            'month', 
            'category_id', 
            'category__name', 
            'category__is_income',
            'is_expense'
        ).annotate(
            total_amount=Sum('amount'),
            transaction_count=Count('id')
        ).order_by('-month', 'category_id')
        
        # 组织数据按月份分组
        for stat in monthly_stats:
            month_date = stat['month']
            month_str = month_date.strftime('%Y-%m')
            
            if month_str not in monthly_data:
                monthly_data[month_str] = {
                    'month': month_str,
                    'month_timestamp': int(month_date.timestamp()),
                    'categories': [],
                    'total_expense': Decimal('0'),
                    'total_income': Decimal('0'),
                    'net_amount': Decimal('0')
                }
            
            # 添加分类数据
            category_data = {
                'category_id': stat['category_id'],
                'category_name': stat['category__name'] or 'Others',
                'is_income': stat['category__is_income'],
                'total_amount': stat['total_amount'],
                'transaction_count': stat['transaction_count']
            }
            
            # 更新月度总计
            if stat['is_expense']:
                monthly_data[month_str]['total_expense'] += stat['total_amount']
            else:
                monthly_data[month_str]['total_income'] += stat['total_amount']
            
            monthly_data[month_str]['categories'].append(category_data)
        
        # 计算净额并转换为列表
        formatted_results = []
        for month_str, data in monthly_data.items():
            data['net_amount'] = data['total_income'] - data['total_expense']
            formatted_results.append(data)
        
        # 按月份降序排序
        formatted_results.sort(key=lambda x: x['month'], reverse=True)
        
        # 使用序列化器
        serializer = MonthlyStatSerializer(formatted_results, many=True)
        
        # 使用分页器
        page = self.paginate_queryset(serializer.data)
        if page is not None:
            return self.get_paginated_response(page)
        
        # 如果没有分页，返回所有结果
        return self.get_success_response(
            data=serializer.data,
            msg=_('获取成功')
        )

    def _get_time_period_params(self, time_period, offset=0):
        """
        获取不同时间周期的查询参数，支持时间偏移
        
        参数:
            time_period: 时间周期类型（day, week, month, year）
            offset: 时间偏移，0表示当前，-1表示上一个周期，1表示下一个周期
        
        返回:
            (period_start, period_end, period_trunc_function, date_format, navigation_info)
        """
        today = timezone.now().date()
        offset = int(offset) if offset else 0
        
        # 记录导航信息用于返回给前端
        navigation_info = {
            'period': time_period,
            'current_offset': offset,
            'previous_offset': offset - 1,
            'next_offset': offset + 1
        }
        
        if time_period == 'day':
            # 每日视图，偏移日期
            target_date = today + timedelta(days=offset)
            start_date = target_date
            end_date = target_date
            trunc_func = TruncDay('transaction_date')  # 已实例化的截断函数
            date_format = '%Y-%m-%d'
            navigation_info['period_display'] = target_date.strftime('%Y-%m-%d')
            
        elif time_period == 'week':
            # 周视图，计算所在周的周一
            target_date = today + timedelta(weeks=offset)
            weekday = target_date.weekday()  # 0是周一，6是周日
            start_date = target_date - timedelta(days=weekday)  # 调整到周一
            end_date = start_date + timedelta(days=6)  # 周日
            trunc_func = TruncWeek('transaction_date')  # 已实例化的截断函数
            date_format = '%Y-%m-%d'
            navigation_info['period_display'] = f"{start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}"
            
        elif time_period == 'year':
            # 年视图，计算目标年份
            target_year = today.year + offset
            start_date = datetime(target_year, 1, 1).date()
            end_date = datetime(target_year, 12, 31).date()
            trunc_func = TruncYear('transaction_date')  # 已实例化的截断函数
            date_format = '%Y'
            navigation_info['period_display'] = str(target_year)
            
        else:  # 默认为month
            # 月视图，计算目标月份
            target_month = today.month + offset
            target_year = today.year
            
            # 处理月份溢出
            while target_month > 12:
                target_month -= 12
                target_year += 1
            while target_month < 1:
                target_month += 12
                target_year -= 1
            
            # 计算月初和月末
            start_date = datetime(target_year, target_month, 1).date()
            # 下月第一天减一天 = 本月最后一天
            if target_month == 12:
                end_date = datetime(target_year + 1, 1, 1).date() - timedelta(days=1)
            else:
                end_date = datetime(target_year, target_month + 1, 1).date() - timedelta(days=1)
            
            trunc_func = TruncMonth('transaction_date')  # 已实例化的截断函数
            date_format = '%Y-%m'
            month_name = start_date.strftime('%B')  # 月份的完整名称
            navigation_info['period_display'] = f"{month_name} {target_year}"
        
        # 将日期转为datetime并设置时区
        start_datetime = timezone.make_aware(
            datetime.combine(start_date, datetime.min.time())
        )
        end_datetime = timezone.make_aware(
            datetime.combine(end_date, datetime.max.time())
        )
        
        # 添加时间边界到导航信息
        navigation_info['start_date'] = int(start_datetime.timestamp())
        navigation_info['end_date'] = int(end_datetime.timestamp())
        
        return start_datetime, end_datetime, trunc_func, date_format, navigation_info
