from django.shortcuts import render
from django.db.models import Sum, Count, F, Q, DecimalField
from django.db.models.functions import Coalesce
from rest_framework import status, serializers
from rest_framework.decorators import action
from rest_framework.viewsets import GenericViewSet
from django.utils.translation import gettext_lazy as _
from decimal import Decimal

from utils.permissions import IsAuthenticatedExternal
from utils.mixins import *
from .models import Asset, CurrencyRate
from .serializers import (
    AssetSerializer, AssetCreateSerializer, CurrencyRateSerializer,
    AssetTotalByTypeSerializer
)
from categorization.models import AssetCategory


class CurrencyRateViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    """货币汇率视图集"""
    queryset = CurrencyRate.objects.all()
    serializer_class = CurrencyRateSerializer
    permission_classes = [IsAuthenticatedExternal]


class AssetViewSet(CreateModelMixin,
                   RetrieveModelMixin,
                   UpdateModelMixin,
                   PartialUpdateModelMixin,
                   DestroyModelMixin,
                   ListModelMixin,
                   GenericViewSet):
    """资产视图集"""
    queryset = Asset.objects.all()
    serializer_class = AssetSerializer
    permission_classes = [IsAuthenticatedExternal]
    
    def get_serializer_class(self):
        """根据操作返回不同的序列化器"""
        if self.action == 'create':
            return AssetCreateSerializer
        return AssetSerializer
    
    def get_queryset(self):
        """获取当前用户的资产"""
        queryset = super().get_queryset()
        
        # 从认证后的请求中获取用户ID
        user_id = None
        if hasattr(self.request, 'remote_user'):
            user_id = self.request.remote_user.get('id')
            
        if user_id:
            return queryset.filter(user_id=user_id)
        return queryset.none()
    
    def perform_create(self, serializer):
        """创建资产时自动添加用户ID"""
        user_id = self.request.remote_user.get('id')
            
        if not user_id:
            raise serializers.ValidationError(_('无法获取用户ID'))
            
        serializer.save(user_id=user_id)
    
    @action(detail=False, methods=['get'])
    def total_assets(self, request):
        """计算用户总资产数额（美元）"""
        queryset = self.get_queryset().filter(include_in_total=True)
        
        # 获取所有分类信息，用于判断正负资产
        categories = {cat.id: cat for cat in AssetCategory.objects.all()}
        
        # 获取所有货币汇率
        currency_rates = {rate.currency: rate.rate_to_usd for rate in CurrencyRate.objects.all()}
        
        # 初始化统计变量
        total_positive_usd = Decimal('0.00')  # 正资产总额
        total_negative_usd = Decimal('0.00')  # 负资产总额
        assets_by_currency = {}  # 按货币统计
        
        # 遍历所有资产计算总值
        for asset in queryset:
            # 判断资产是正是负
            is_positive = True
            if asset.category_id and asset.category_id in categories:
                is_positive = categories[asset.category_id].is_positive_asset
            
            # 计算美元价值
            amount = asset.balance
            if asset.currency == 'USD':
                usd_value = amount
            elif asset.currency in currency_rates:
                usd_value = amount * currency_rates[asset.currency]
            else:
                # 汇率不存在时，使用1:1汇率（保留原值）
                usd_value = amount
            
            # 分别累加正负资产
            if is_positive:
                total_positive_usd += usd_value
            else:
                total_negative_usd += usd_value
            
            # 累加按货币统计
            currency = asset.currency
            if currency not in assets_by_currency:
                assets_by_currency[currency] = {
                    'positive': Decimal('0.00'),
                    'negative': Decimal('0.00')
                }
                
            if is_positive:
                assets_by_currency[currency]['positive'] += amount
            else:
                assets_by_currency[currency]['negative'] += amount
        
        # 计算净资产
        net_asset_usd = total_positive_usd - total_negative_usd
        
        # 格式化货币金额
        formatted_by_currency = {}
        for currency, amounts in assets_by_currency.items():
            rate = currency_rates.get(currency, Decimal('1.0'))
            
            formatted_by_currency[currency] = {
                'currency_display': dict(Asset.CURRENCY_CHOICES).get(currency),
                'positive': {
                    'amount': str(amounts['positive'].quantize(Decimal('0.01'))),
                    'amount_in_usd': str((amounts['positive'] * rate).quantize(Decimal('0.01')))
                },
                'negative': {
                    'amount': str(amounts['negative'].quantize(Decimal('0.01'))),
                    'amount_in_usd': str((amounts['negative'] * rate).quantize(Decimal('0.01')))
                },
                'net': {
                    'amount': str((amounts['positive'] - amounts['negative']).quantize(Decimal('0.01'))),
                    'amount_in_usd': str(((amounts['positive'] - amounts['negative']) * rate).quantize(Decimal('0.01')))
                }
            }
        
        return self.get_success_response(
            data={
                'total_positive_usd': str(total_positive_usd.quantize(Decimal('0.01'))),
                'total_negative_usd': str(total_negative_usd.quantize(Decimal('0.01'))),
                'net_asset_usd': str(net_asset_usd.quantize(Decimal('0.01'))),
                'by_currency': formatted_by_currency,
                'asset_count': queryset.count(),
            },
            msg=_('获取成功')
        )
    
    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """列出用户每种资产分类的总额"""
        queryset = self.get_queryset().filter(include_in_total=True)
        print(queryset)
        
        # 获取所有分类
        categories = {cat.id: cat for cat in AssetCategory.objects.all()}
        
        # 准备结果数组
        result = []
        positive_total = Decimal('0.00')
        negative_total = Decimal('0.00')
        
        # 按分类统计
        for category_id, category in categories.items():
            category_assets = queryset.filter(category_id=category_id)
            
            if not category_assets.exists():
                continue
            
            # 手动计算该分类下所有资产的美元总值
            category_total_usd = Decimal('0.00')
            for asset in category_assets:
                # 获取美元价值
                asset_value = asset.get_balance_in_usd()
                category_total_usd += asset_value
            
            # 确定正负资产类型
            is_positive = category.is_positive_asset
            
            # 累加到总额
            if is_positive:
                positive_total += category_total_usd
            else:
                negative_total += category_total_usd
            
            # 添加到结果
            result.append({
                'category_id': category_id,
                'category_name': category.name,
                'category_type': category.category_type,
                'is_positive_asset': is_positive,
                'total_balance_usd': category_total_usd.quantize(Decimal('0.01')),
                'asset_count': category_assets.count(),
            })
        
        # 对结果按资产总额降序排序
        result.sort(key=lambda x: (not x['is_positive_asset'], -float(x['total_balance_usd'])))
        
        # 更新序列化器以包含是否正资产字段
        class EnhancedAssetTotalByTypeSerializer(AssetTotalByTypeSerializer):
            is_positive_asset = serializers.BooleanField()
        
        serializer = EnhancedAssetTotalByTypeSerializer(result, many=True)
        
        # 计算净资产
        net_asset_usd = positive_total - negative_total
        
        return self.get_success_response(
            data={
                'categories': serializer.data,
                'summary': {
                    'positive_total_usd': str(positive_total.quantize(Decimal('0.01'))),
                    'negative_total_usd': str(negative_total.quantize(Decimal('0.01'))),
                    'net_asset_usd': str(net_asset_usd.quantize(Decimal('0.01'))),
                }
            },
            msg=_('获取成功')
        )
