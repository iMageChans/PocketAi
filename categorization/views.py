from rest_framework.decorators import action
from django.utils.translation import gettext_lazy as _
from rest_framework.viewsets import GenericViewSet

from utils.permissions import IsAuthenticatedExternal
from utils.mixins import *
from .models import LedgerCategory, AssetCategory, TransactionCategory
from .serializers import (
    LedgerCategorySerializer,
    AssetCategorySerializer,
    TransactionCategorySerializer
)


# Create your views here.

class LedgerCategoryViewSet(ListModelMixin,
                            RetrieveModelMixin,
                            GenericViewSet):
    """账本分类视图集"""
    queryset = LedgerCategory.objects.all()
    serializer_class = LedgerCategorySerializer
    permission_classes = [IsAuthenticatedExternal]

    @action(detail=False, methods=['get'])
    def default(self, request):
        """获取默认账本分类"""
        instance = self.get_queryset().filter(is_default=True).first()
        if not instance:
            return Response({
                'code': 404,
                'msg': _('未找到默认账本'),
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(instance)
        return Response({
            'code': 200,
            'msg': _('获取成功'),
            'data': serializer.data
        })


class AssetCategoryViewSet(ListModelMixin,
                           RetrieveModelMixin,
                           GenericViewSet):
    """资产分类视图集"""
    queryset = AssetCategory.objects.all()
    serializer_class = AssetCategorySerializer
    permission_classes = [IsAuthenticatedExternal]

    @action(detail=False, methods=['get'])
    def types(self, request):
        """获取资产分类类型列表"""
        types = [
            {'key': key, 'value': str(value)}
            for key, value in AssetCategory.CATEGORY_TYPE_CHOICES
        ]
        return Response({
            'code': 200,
            'msg': _('获取成功'),
            'data': types
        })


class TransactionCategoryViewSet(ListModelMixin,
                           RetrieveModelMixin,
                           GenericViewSet):
    """交易分类视图集"""
    queryset = TransactionCategory.objects.all()
    serializer_class = TransactionCategorySerializer
    permission_classes = [IsAuthenticatedExternal]
