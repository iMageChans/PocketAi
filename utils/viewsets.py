from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from django.utils.translation import gettext_lazy as _


class StandardResponseViewSet(GenericViewSet):
    """标准响应格式的视图集基类"""
    
    def get_standard_response(self, data=None, msg=None, code=200, status_code=status.HTTP_200_OK):
        """获取标准响应格式"""
        if msg is None:
            msg = _('获取成功') if code == 200 else _('操作失败')
            
        return Response({
            'code': code,
            'msg': msg,
            'data': data
        }, status=status_code)
    
    def list(self, request, *args, **kwargs):
        """重写列表方法，返回符合项目规范的响应格式"""
        queryset = self.filter_queryset(self.get_queryset())
        
        # 分页
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            paginated_response = self.get_paginated_response(serializer.data)
            # 直接返回分页响应，因为CustomPagination已经格式化了响应
            return paginated_response
        
        # 如果没有分页，手动格式化响应
        serializer = self.get_serializer(queryset, many=True)
        return self.get_standard_response(data=serializer.data)
    
    def retrieve(self, request, *args, **kwargs):
        """重写检索方法，返回符合项目规范的响应格式"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return self.get_standard_response(data=serializer.data)
    
    def create(self, request, *args, **kwargs):
        """重写创建方法，返回符合项目规范的响应格式"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return self.get_standard_response(
            data=serializer.data,
            msg=_('创建成功'),
            status_code=status.HTTP_201_CREATED
        )
    
    def update(self, request, *args, **kwargs):
        """重写更新方法，返回符合项目规范的响应格式"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return self.get_standard_response(data=serializer.data, msg=_('更新成功'))
    
    def destroy(self, request, *args, **kwargs):
        """重写删除方法，返回符合项目规范的响应格式"""
        instance = self.get_object()
        self.perform_destroy(instance)
        return self.get_standard_response(data=None, msg=_('删除成功')) 