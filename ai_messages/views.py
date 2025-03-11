import random
import json

from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.viewsets import GenericViewSet
from django.utils.translation import gettext_lazy as _
from django.http import Http404

import pytz
from django.utils import timezone

from transactions.models import Transaction
from utils.permissions import IsAuthenticatedExternal
from utils.mixins import *
from .models import MessageSession, Message
from .serializers import (
    MessageSessionSerializer, MessageSessionCreateSerializer,
    MessageSerializer, MessageCreateSerializer,
    MessageSessionDetailSerializer
)
from .services import create_ai_analyst, creat_ai_chat, get_assistant_list

# 配置日志
logger = logging.getLogger(__name__)


class MessageSessionViewSet(CreateModelMixin,
                            RetrieveModelMixin,
                            UpdateModelMixin,
                            DestroyModelMixin,
                            ListModelMixin,
                            GenericViewSet):
    """消息会话视图集"""
    queryset = MessageSession.objects.all()
    serializer_class = MessageSessionSerializer
    permission_classes = [IsAuthenticatedExternal]

    def get_serializer_class(self):
        """根据操作返回不同的序列化器"""
        if self.action == 'create':
            return MessageSessionCreateSerializer
        elif self.action == 'retrieve':
            return MessageSessionDetailSerializer
        return MessageSessionSerializer

    def get_queryset(self):
        """获取当前用户的消息会话"""
        queryset = super().get_queryset()

        # 从认证后的请求中获取用户ID
        user_id = None
        if hasattr(self.request, 'remote_user'):
            user_id = self.request.remote_user.get('id')

        if user_id:
            queryset = queryset.filter(user_id=user_id)
        else:
            queryset = queryset.none()

        # 按模型名称筛选
        model = self.request.GET.get('model')
        if model:
            queryset = queryset.filter(model=model)

        # 按助手名称搜索
        assistant_name = self.request.GET.get('assistant_name')
        if assistant_name:
            queryset = queryset.filter(assistant_name__icontains=assistant_name)

        return queryset

    def get_object(self):
        """重写获取单个对象的方法，确保只能访问自己的数据"""
        obj = super().get_object()

        # 检查对象是否属于当前用户
        user_id = None
        if hasattr(self.request, 'remote_user'):
            user_id = self.request.remote_user.get('id')

        if user_id and obj.user_id != user_id:
            raise Http404(_("没有找到符合条件的会话"))

        return obj

    def perform_create(self, serializer):
        """创建消息会话时自动添加用户ID"""
        user_id = self.request.remote_user.get('id')

        if not user_id:
            raise serializers.ValidationError(_('无法获取用户ID'))

        serializer.save(user_id=user_id)

    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        """获取会话的所有消息"""
        session = self.get_object()
        messages = session.messages.all()

        # 分页
        page = self.paginate_queryset(messages)
        if page is not None:
            serializer = MessageSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = MessageSerializer(messages, many=True)
        return Response({
            'code': 200,
            'msg': _('获取成功'),
            'data': serializer.data
        })


class MessageViewSet(CreateModelMixin,
                     RetrieveModelMixin,
                     UpdateModelMixin,
                     DestroyModelMixin,
                     ListModelMixin,
                     GenericViewSet):
    """消息视图集"""
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticatedExternal]

    # 远程AI服务的URL
    AI_SERVICE_URL = 'https://api.example.com/ai/chat'  # 替换为实际的AI服务URL

    # 默认语言
    DEFAULT_LANGUAGE = 'en'

    def get_serializer_class(self):
        """根据操作返回不同的序列化器"""
        if self.action == 'create':
            return MessageCreateSerializer
        return MessageSerializer

    def get_queryset(self):
        """获取当前用户的消息"""
        queryset = super().get_queryset()

        # 从认证后的请求中获取用户ID
        user_id = None
        if hasattr(self.request, 'remote_user'):
            user_id = self.request.remote_user.get('id')

        if user_id:
            queryset = queryset.filter(session__user_id=user_id)
        else:
            queryset = queryset.none()

        # 按会话ID筛选
        session_id = self.request.GET.get('session_id')
        if session_id:
            queryset = queryset.filter(session_id=session_id)

        # 按消息类型筛选
        message_type = self.request.GET.get('message_type')
        if message_type:
            queryset = queryset.filter(message_type=message_type)

        # 保留原有的is_user筛选以保持兼容性
        is_user = self.request.GET.get('is_user')
        if is_user is not None:
            is_user = is_user.lower() in ('true', '1', 'yes')
            queryset = queryset.filter(is_user=is_user)

        return queryset

    def get_object(self):
        """重写获取单个对象的方法，确保只能访问自己的数据"""
        obj = super().get_object()

        # 检查对象是否属于当前用户
        user_id = None
        if hasattr(self.request, 'remote_user'):
            user_id = self.request.remote_user.get('id')

        if user_id and obj.session.user_id != user_id:
            raise Http404(_("没有找到符合条件的消息"))

        return obj

    def perform_create(self, serializer):
        """创建消息时验证会话归属"""
        session_id = serializer.validated_data.get('session').id
        user_id = self.request.remote_user.get('id')

        # 验证会话是否属于当前用户
        try:
            session = MessageSession.objects.get(id=session_id)
            if session.user_id != user_id:
                raise serializers.ValidationError(_('无法在其他用户的会话中创建消息'))
        except MessageSession.DoesNotExist:
            raise serializers.ValidationError(_('指定的会话不存在'))

        serializer.save()

    @action(detail=False, methods=['get'])
    def assistant(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        rsp = get_assistant_list(auth_header)
        return Response({
            'code': 200,
            'msg': "获取成功",
            'data': rsp['data']
        })

    @action(detail=False, methods=['post'])
    def text_message(self, request):
        """处理文字消息"""
        return self._process_message(request, is_voice=False)

    @action(detail=False, methods=['post'])
    def voice_message(self, request):
        """处理语音消息（已转为文字）"""
        return self._process_message(request, is_voice=True)

    def _process_message(self, request, is_voice=False):
        """处理消息的通用方法"""
        # 验证请求数据
        session_id = request.data.get('session_id')
        content = request.data.get('content')
        ledger_id = request.data.get('ledger_id')
        asset_id = request.data.get('asset_id', None)
        language = request.data.get('language', self.DEFAULT_LANGUAGE)
        assistant_name = request.data.get('assistant_name', None)

        if not session_id:
            return Response({
                'code': 400,
                'msg': _('缺少会话ID'),
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)

        if not ledger_id:
            return Response({
                'code': 400,
                'msg': _('账本不能为空'),
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)

        if not content:
            return Response({
                'code': 400,
                'msg': _('消息内容不能为空'),
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)

        # 获取用户ID
        user_id = None
        if hasattr(request, 'remote_user'):
            user_id = request.remote_user.get('id')

        if not user_id:
            return Response({
                'code': 401,
                'msg': _('无法获取用户ID'),
                'data': None
            }, status=status.HTTP_401_UNAUTHORIZED)

        # 验证会话归属
        try:
            session = MessageSession.objects.get(id=session_id)
            if session.user_id != user_id:
                return Response({
                    'code': 403,
                    'msg': _('无法在其他用户的会话中发送消息'),
                    'data': None
                }, status=status.HTTP_403_FORBIDDEN)
        except MessageSession.DoesNotExist:
            return Response({
                'code': 404,
                'msg': _('指定的会话不存在'),
                'data': None
            }, status=status.HTTP_404_NOT_FOUND)

        # 保存用户消息
        user_message = Message.objects.create(
            user_id=user_id,
            session=session,
            content=content,
            message_type=Message.TYPE_USER,
            is_user=True,
            is_voice=is_voice,
        )

        auth_header = request.META.get('HTTP_AUTHORIZATION', '')

        model_name = session.model

        if model_name == 'ChatGPT':
            model_name = 'gpt-3.5-turbo'
        elif model_name == 'DeepSeek':
            model_name = 'deepseek-chat'
        else:
            model_name = 'qwen-max'

        # 调用AI分析服务
        analyst = create_ai_analyst(content, auth_header, model_name=model_name)
        transactions = analyst.get('transactions', [])

        utc_now = timezone.now()
        local_tz = pytz.timezone(self.request.remote_user.get('timezone', 'UTC'))

        transaction_ids = []

        # 检查analyst的结构并安全地访问transactions
        try:
            # 处理交易
            if len(transactions) > 0:
                for transaction in transactions:
                    try:
                        # 创建交易记录，使用正确的字段名
                        if transaction.get('type') == 'expense':
                            is_expense = True
                            is_income = False
                        else:
                            is_expense = False
                            is_income = True
                        new_transaction = Transaction.objects.create(
                            user_id=user_id,
                            ledger_id=ledger_id,
                            asset_id=asset_id,
                            # 根据Transaction模型的实际字段选择以下之一:
                            # 如果Transaction模型有category字段(ForeignKey):
                            # category_id=get_category_id(transaction.get('category'), transaction.get('type')),
                            # 如果Transaction模型直接存储分类名称:
                            category_id=get_category_id(transaction.get('category'), is_income),
                            amount=transaction.get('amount', 0),
                            transaction_date=utc_now.astimezone(local_tz),
                            notes=transaction.get('notes', transaction.get('note', '')),
                            is_expense=is_expense,
                        )
                        transaction_ids.append(new_transaction.id)
                    except Exception as e:
                        # 记录具体的错误
                        print(f"创建交易记录失败: {str(e)}")
                        logger.error(f"创建交易记录失败: {str(e)}")
        except Exception as e:
            # 记录错误但继续执行
            print(f"处理交易时出错: {str(e)}")
            logger.error(f"处理交易时出错: {str(e)}")

        # 调用AI聊天服务
        chat = creat_ai_chat(content, auth_header, assistant_name, model_name=model_name, language=language)
        print(chat)

        # 确保chat不为空
        if not chat:
            chat = _('error')

        # 创建AI回复消息
        ai_message = Message.objects.create(
            user_id=user_id,
            session=session,
            content=chat,
            message_type=Message.TYPE_ASSISTANT,
            is_user=False,
            random=random.randint(1, 90),
        )

        # 如果有交易ID，设置到消息中
        if transaction_ids:
            ai_message.transaction_ids = ','.join(str(id) for id in transaction_ids)
            ai_message.save()

        return Response({
            'code': 200,
            'msg': '发送成功',
            'data': {
                'results': [MessageSerializer(user_message).data, MessageSerializer(ai_message).data]
            }
        })

def get_category_id(category_name, transaction_type):
    """根据分类名称和交易类型获取分类ID"""
    from categorization.models import TransactionCategory
    
    is_income = transaction_type
    
    try:
        # 尝试查找匹配的分类
        category = TransactionCategory.objects.filter(
            name__icontains=category_name,
            is_income=is_income
        ).first()
        
        if category:
            return category.id
        
        # 如果找不到匹配的分类，使用默认分类
        default_category = TransactionCategory.objects.filter(
            is_income=is_income,
            name='Others'
        ).first()
        
        if default_category:
            return default_category.id
        
        # 如果没有默认分类，使用第一个分类
        first_category = TransactionCategory.objects.filter(
            is_income=is_income
        ).first()
        
        if first_category:
            return first_category.id
        
        # 如果没有找到任何分类，返回None
        return None
    except Exception as e:
        logger.error(f"获取分类ID失败: {str(e)}")
        return None
