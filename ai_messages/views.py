from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.viewsets import GenericViewSet
from django.utils.translation import gettext_lazy as _
from django.http import Http404

from datetime import datetime

from transactions.models import Transaction
from utils.permissions import IsAuthenticatedExternal
from utils.mixins import *
from .models import MessageSession, Message
from .serializers import (
    MessageSessionSerializer, MessageSessionCreateSerializer,
    MessageSerializer, MessageCreateSerializer,
    MessageSessionDetailSerializer, MessageProcessSerializer
)
from .services import creat_ai_chat, get_assistant_list
from django.db import transaction as db_transaction
from utils.viewsets import StandardResponseViewSet
from utils.pagination import CustomPagination
from decimal import Decimal

# 配置日志
logger = logging.getLogger(__name__)


class MessageSessionViewSet(CreateModelMixin,
                            RetrieveModelMixin,
                            UpdateModelMixin,
                            DestroyModelMixin,
                            ListModelMixin,
                            StandardResponseViewSet):
    """消息会话视图集"""
    queryset = MessageSession.objects.all()
    serializer_class = MessageSessionSerializer
    permission_classes = [IsAuthenticatedExternal]
    pagination_class = CustomPagination


    # 添加一个额外的路由，支持通过整数ID查找会话
    @action(detail=True, methods=['get'], url_path='by-id/(?P<id>\d+)')
    def get_by_id(self, request, id=None):
        """通过整数ID获取会话"""
        try:
            session = MessageSession.objects.get(id=id)

            # 检查权限
            user_id = request.remote_user.get('id')
            if session.user_id != user_id:
                raise Http404(_("没有找到符合条件的会话"))

            serializer = self.get_serializer(session)
            return self.get_success_response(data=serializer.data)
        except MessageSession.DoesNotExist:
            raise Http404(_("没有找到符合条件的会话"))

    @action(detail=False, methods=['delete'])
    def delete_all(self, request):
        """删除用户的所有消息和会话"""
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

        try:
            with db_transaction.atomic():
                # 获取用户的所有会话ID
                session_ids = MessageSession.objects.filter(user_id=user_id).values_list('id', flat=True)
                
                # 删除用户的所有消息
                deleted_messages_count = Message.objects.filter(session_id__in=session_ids).delete()[0]
                
                # 删除用户的所有会话
                deleted_sessions_count = MessageSession.objects.filter(user_id=user_id).delete()[0]
                
                return Response({
                    'code': 200,
                    'msg': _('删除成功'),
                    'data': {
                        'deleted_messages_count': deleted_messages_count,
                        'deleted_sessions_count': deleted_sessions_count
                    }
                })
        except Exception as e:
            logger.error(f"删除用户消息和会话时出错: {str(e)}")
            return Response({
                'code': 500,
                'msg': _('服务器内部错误'),
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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

        # 确保分页器已初始化
        paginator = self.pagination_class()
        paginator.page_size = self.pagination_class.page_size

        # 分页
        page = paginator.paginate_queryset(messages, request)
        if page is not None:
            serializer = MessageSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = MessageSerializer(messages, many=True)
        return Response({
            'code': 200,
            'msg': _('获取成功'),
            'data': serializer.data
        })

    @action(detail=True, methods=['get'])
    def sync_history(self, request, pk=None):
        """同步历史消息

        通过传入一个message_id，返回该会话中在这个消息之前的所有消息
        """
        session = self.get_object()
        message_id = request.query_params.get('message_id')

        if not message_id:
            return Response({
                'code': 400,
                'msg': _('缺少message_id参数'),
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # 获取指定的消息
            reference_message = Message.objects.get(id=message_id, session=session)

            # 获取该消息之前的所有消息
            messages = session.messages.filter(
                created_at__lt=reference_message.created_at
            ).order_by('created_at')

            # 确保分页器已初始化
            paginator = self.pagination_class()
            paginator.page_size = self.pagination_class.page_size

            # 分页
            page = paginator.paginate_queryset(messages, request)
            if page is not None:
                serializer = MessageSerializer(page, many=True)
                return paginator.get_paginated_response(serializer.data)

            serializer = MessageSerializer(messages, many=True)
            return Response({
                'code': 200,
                'msg': _('获取成功'),
                'data': serializer.data
            })

        except Message.DoesNotExist:
            return Response({
                'code': 404,
                'msg': _('指定的消息不存在'),
                'data': None
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"同步历史消息时出错: {str(e)}")
            return Response({
                'code': 500,
                'msg': _('服务器内部错误'),
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def list(self, request, *args, **kwargs):
        """重写列表方法，返回符合项目规范的响应格式"""
        queryset = self.filter_queryset(self.get_queryset())

        # 分页
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            # 手动构造符合项目规范的响应格式
            return Response({
                'code': 200,
                'msg': _('获取成功'),
                'data': {
                    'count': self.paginator.page.paginator.count,
                    'next': self.paginator.get_next_link(),
                    'previous': self.paginator.get_previous_link(),
                    'results': serializer.data
                }
            })

        # 如果没有分页，手动格式化响应
        serializer = self.get_serializer(queryset, many=True)
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
    pagination_class = CustomPagination

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

    def _check_message_limit(self, request):
        """Check message limit for non-premium users

        Returns:
            Response or None: Response object if limit reached, otherwise None
        """
        # Check if user is premium
        is_premium = request.remote_user.get('is_premium')

        # No limit for premium users
        if is_premium:
            return None

        # Get user ID
        user_id = request.remote_user.get('id')
        if not user_id:
            return Response({
                'code': 401,
                'msg': _('Unable to get user ID'),
                'data': None
            }, status=status.HTTP_401_UNAUTHORIZED)

        # Count user messages
        message_count = Message.objects.filter(
            user_id=user_id,
            is_user=True  # Only count user messages
        ).count()

        # If message count exceeds 50, return upgrade prompt
        if message_count >= 50:
            return Response({
                'code': 598,
                'msg': _('Unlock unlimited voice & text chat'),
                'data': {
                    'message_count': message_count,
                    'message_limit': 50
                }
            }, status=598)

        # Limit not reached
        return None

    @action(detail=False, methods=['post'])
    def text_message(self, request):
        """处理文字消息"""
        # 检查用户是否为付费用户
        is_premium = request.remote_user.get('is_premium')

        # 如果不是付费用户，检查消息数量限制
        limit_response = self._check_message_limit(request)
        if limit_response:
            return limit_response

        return self._process_message(request, is_voice=False)

    @action(detail=False, methods=['post'])
    def voice_message(self, request):
        """Process voice message (converted to text)"""
        # Check message limit
        limit_response = self._check_message_limit(request)
        if limit_response:
            return limit_response

        return self._process_message(request, is_voice=True)

    def _process_message(self, request, is_voice=False):
        """处理消息的通用方法"""
        # 使用序列化器验证请求数据
        serializer = MessageProcessSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'code': 400,
                'msg': _('请求参数错误'),
                'data': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        # 获取验证后的数据
        validated_data = serializer.validated_data
        session_id = validated_data['session_id']
        content = validated_data['content']
        ledger_id = validated_data['ledger_id']
        asset_id = validated_data.get('asset_id')
        language = validated_data.get('language', self.DEFAULT_LANGUAGE)
        assistant_name = validated_data.get('assistant_name', 'Alice')
        file_path = validated_data.get('file_path')
        voice_date = validated_data.get('voice_date')
        user_template_id = validated_data.get('user_template_id', None)

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

        # 使用事务确保数据一致性
        with db_transaction.atomic():
            # 保存用户消息
            user_message = Message.objects.create(
                user_id=user_id,
                session=session,
                content=content,
                message_type=Message.TYPE_USER,
                is_user=True,
                is_voice=is_voice,
                file_path=file_path,
                voice_date=voice_date,
            )

            auth_header = request.META.get('HTTP_AUTHORIZATION', '')

            model_name = session.model

            if model_name == 'ChatGPT':
                model_name = 'gpt-3.5-turbo'
            elif model_name == 'DeepSeek':
                model_name = 'deepseek-chat'
            else:
                model_name = 'qwen-max'

            bot = creat_ai_chat(content, auth_header, model_name=model_name)
            if bot is None:
                return Response({
                'code': 400,
                'msg': _('bot is None'),
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)

            if 'content' in bot:
                bot = bot['content']
            else:
                bot = bot

            if "transactions" in bot:
                transactions = bot['transactions']
            elif "transactions" in bot['content']:
                transactions = bot['content']['transactions']
            else:
                transactions = []

            transaction_ids = []

            # 处理交易
            if transactions:
                for transaction in transactions:
                    try:
                        # 创建交易记录，使用正确的字段名
                        if transaction.get('type') == 'expense':
                            is_expense = True
                            is_income = False
                        else:
                            is_expense = False
                            is_income = True
                        transaction_date = datetime.strptime(transaction['date'], "%Y-%m-%d %H:%M:%S")
                        new_transaction = Transaction.objects.create(
                            user_id=user_id,
                            ledger_id=ledger_id,
                            asset_id=asset_id,
                            category_id=get_category_id(transaction.get('category'), is_income),
                            amount=Decimal(str(transaction.get('amount', 0))),
                            transaction_date=transaction_date,
                            notes=transaction['note'],
                            is_expense=is_expense,
                        )
                        transaction_ids.append(new_transaction.id)
                    except Exception as e:
                        logger.error(f"创建交易记录失败: {str(e)}")

            if "ai_output" in bot:
                content = bot['ai_output']
            elif "content" in bot:
                if "ai_output" in bot['content']:
                    content = bot['content']['ai_output']
                else:
                    content = bot['content']['en']
            elif "en" in bot:
                if "ai_output" in bot['en']:
                    content = bot['en']['ai_output']
                else:
                    content = bot['en']
            else:
                content = "The server is busy. Please try again later."

            # 创建AI回复消息
            ai_message = Message.objects.create(
                user_id=user_id,
                session=session,
                content=content,
                message_type=Message.TYPE_ASSISTANT,
                is_user=False,
                random=bot['random'],
                emoji=bot['emoji'],
            )

            # 如果有交易ID，设置到消息中
            if transaction_ids:
                ai_message.transaction_ids = ','.join(str(id) for id in transaction_ids)
                ai_message.save()

        # 更新会话的最后更新时间
        session.save()  # 触发auto_now字段更新

        return Response({
            'code': 200,
            'msg': _('发送成功'),
            'data': {
                'results': [MessageSerializer(user_message).data, MessageSerializer(ai_message).data]
            }
        })

    @action(detail=False, methods=['get'])
    def message_usage(self, request):
        """Get user's message usage information"""
        # Get user ID
        user_id = request.remote_user.get('id')
        if not user_id:
            return Response({
                'code': 401,
                'msg': _('Unable to get user ID'),
                'data': None
            }, status=status.HTTP_401_UNAUTHORIZED)

        # Check if user is premium
        is_premium = request.remote_user.get('is_premium')

        # Count user messages
        message_count = Message.objects.filter(
            user_id=user_id,
            is_user=True  # Only count user messages
        ).count()

        return Response({
            'code': 200,
            'msg': _('Success'),
            'data': {
                'message_count': message_count,
                'message_limit': None if is_premium else 50,  # No limit for premium users
                'is_premium': is_premium
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
