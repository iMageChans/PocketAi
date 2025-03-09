from rest_framework import serializers
from rest_framework.decorators import action
from django.utils.translation import gettext_lazy as _
from rest_framework.viewsets import GenericViewSet

from utils.permissions import IsAuthenticatedExternal
from utils.mixins import *
from .models import Ledger
from .serializers import LedgerSerializer, LedgerCreateSerializer


class LedgerViewSet(CreateModelMixin,
                    UpdateModelMixin,
                    PartialUpdateModelMixin,
                    RetrieveModelMixin,
                    DestroyModelMixin,
                    ListModelMixin,
                    GenericViewSet):
    """账本视图集"""
    queryset = Ledger.objects.all()
    serializer_class = LedgerSerializer
    permission_classes = [IsAuthenticatedExternal]
    
    def get_serializer_class(self):
        """根据操作返回不同的序列化器"""
        if self.action == 'create':
            return LedgerCreateSerializer
        return LedgerSerializer
    
    def perform_create(self, serializer):
        """创建账本时自动添加用户ID"""
        user_id = self.request.remote_user.get('id')
            
        if not user_id:
            raise serializers.ValidationError(_('无法获取用户ID'))
            
        serializer.save(user_id=user_id)
    
    @action(detail=False, methods=['get'])
    def default(self, request):
        """获取当前用户的默认账本"""
        queryset = self.get_queryset().filter(is_default=True)
        if not queryset.exists():
            return Response({
                'code': status.HTTP_404_NOT_FOUND,
                'msg': _('未找到默认账本'),
                'data': {}
            }, status=status.HTTP_404_NOT_FOUND)
        
        instance = queryset.first()
        serializer = self.get_serializer(instance)
        return Response({
            'code': 200,
            'msg': _('获取成功'),
            'data': serializer.data
        })
    
    @action(detail=True, methods=['post'])
    def set_default(self, request, pk=None):
        """将指定账本设为默认账本"""
        instance = self.get_object()
        instance.is_default = True
        instance.save()
        
        serializer = self.get_serializer(instance)
        return Response({
            'code': status.HTTP_200_OK,
            'msg': _('设置成功'),
            'data': serializer.data
        })
