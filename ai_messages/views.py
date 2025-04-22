from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.viewsets import GenericViewSet
from django.utils.translation import gettext_lazy as _
from django.http import Http404

from datetime import datetime
from django.utils import timezone
from decimal import Decimal, InvalidOperation

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
        # 1. 验证请求数据
        serializer = MessageProcessSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'code': 400,
                'msg': _('请求参数错误'),
                'data': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        # 2. 获取验证后的数据
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

        # 3. 获取用户ID并验证
        user_id = self._get_user_id(request)
        if not user_id:
            return Response({
                'code': 401,
                'msg': _('无法获取用户ID'),
                'data': None
            }, status=status.HTTP_401_UNAUTHORIZED)

        # 4. 验证会话归属
        session_validation_result = self._validate_session(session_id, user_id)
        if isinstance(session_validation_result, Response):
            return session_validation_result
        session = session_validation_result

        # 5. 使用事务确保数据一致性
        with db_transaction.atomic():
            # 5.1 保存用户消息
            user_message = self._create_user_message(user_id, session, content, is_voice, file_path, voice_date)
            
            # 5.2 获取AI回复
            auth_header = request.META.get('HTTP_AUTHORIZATION', '')
            model_name = self._get_model_name(session.model)
            
            bot_response = creat_ai_chat(content, auth_header, model_name=model_name)
            if bot_response is None:
                return Response({
                    'code': 400,
                    'msg': _('bot is None'),
                    'data': None
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 5.3 处理交易数据
            transactions = self._extract_transactions(bot_response)
            transaction_ids = self._process_transactions(transactions, user_id, ledger_id, asset_id)
            
            # 5.4 提取AI回复内容
            ai_content = self._extract_ai_content(bot_response)
            
            # 5.5 获取随机值和表情
            random_value, emoji_value = self._extract_random_emoji(bot_response)
            
            # 5.6 创建AI回复消息
            ai_message = self._create_ai_message(
                user_id, session, ai_content, random_value, emoji_value, transaction_ids
            )

        # 6. 更新会话的最后更新时间
        session.save()  # 触发auto_now字段更新

        # 7. 返回成功响应
        return Response({
            'code': 200,
            'msg': _('发送成功'),
            'data': {
                'results': [MessageSerializer(user_message).data, MessageSerializer(ai_message).data]
            }
        })

    def _get_user_id(self, request):
        """从请求中获取用户ID"""
        if hasattr(request, 'remote_user'):
            return request.remote_user.get('id')
        return None

    def _validate_session(self, session_id, user_id):
        """验证会话归属"""
        try:
            session = MessageSession.objects.get(id=session_id)
            if session.user_id != user_id:
                return Response({
                    'code': 403,
                    'msg': _('无法在其他用户的会话中发送消息'),
                    'data': None
                }, status=status.HTTP_403_FORBIDDEN)
            return session
        except MessageSession.DoesNotExist:
            return Response({
                'code': 404,
                'msg': _('指定的会话不存在'),
                'data': None
            }, status=status.HTTP_404_NOT_FOUND)

    def _create_user_message(self, user_id, session, content, is_voice, file_path, voice_date):
        """创建用户消息"""
        return Message.objects.create(
            user_id=user_id,
            session=session,
            content=content,
            message_type=Message.TYPE_USER,
            is_user=True,
            is_voice=is_voice,
            file_path=file_path,
            voice_date=voice_date,
        )

    def _get_model_name(self, model):
        """获取模型名称"""
        if model == 'ChatGPT':
            return 'gpt-3.5-turbo'
        elif model == 'DeepSeek':
            return 'deepseek-chat'
        else:
            return 'qwen-max'

    def _extract_transactions(self, bot_response):
        """从AI响应中提取交易数据"""
        transactions = []
        
        # 记录日志，帮助调试
        logger.debug(f"AI响应原始数据: {bot_response}")
        
        if not isinstance(bot_response, dict):
            return []
        
        # 提取content字段
        bot_content = bot_response.get('content', bot_response)
        
        # 从不同可能的位置提取transactions
        if isinstance(bot_content, dict):
            if "transactions" in bot_content:
                transactions = bot_content["transactions"]
            elif "content" in bot_content and isinstance(bot_content["content"], dict):
                if "transactions" in bot_content["content"]:
                    transactions = bot_content["content"]["transactions"]
        elif "transactions" in bot_response:
            transactions = bot_response["transactions"]
        
        # 确保transactions是列表
        if not isinstance(transactions, list):
            transactions = []
        
        logger.debug(f"提取的交易数据: {transactions}")
        return transactions

    def _process_transactions(self, transactions, user_id, ledger_id, asset_id):
        """处理交易数据并创建交易记录"""
        transaction_ids = []
        
        if not transactions:
            return transaction_ids
        
        for transaction in transactions:
            try:
                # 确定交易类型
                is_expense = transaction.get('type') == 'expense'
                is_income = not is_expense
                
                # 解析交易日期
                transaction_date = self._parse_transaction_date(transaction)
                
                # 解析交易金额
                amount = self._parse_transaction_amount(transaction)
                
                # 获取分类ID
                category_id = get_category_id(transaction.get('category'), is_income)
                
                # 创建交易记录
                new_transaction = Transaction.objects.create(
                    user_id=user_id,
                    ledger_id=ledger_id,
                    asset_id=asset_id,
                    category_id=category_id,
                    amount=amount,
                    transaction_date=transaction_date,
                    notes=transaction.get('note', ''),
                    is_expense=is_expense,
                )
                transaction_ids.append(new_transaction.id)
                logger.debug(f"成功创建交易记录: ID={new_transaction.id}")
            except Exception as e:
                logger.error(f"创建交易记录失败: {str(e)}, 交易数据: {transaction}")
        
        return transaction_ids

    def _parse_transaction_date(self, transaction):
        """解析交易日期"""
        try:
            return datetime.strptime(transaction['date'], "%Y-%m-%d %H:%M:%S")
        except (ValueError, KeyError):
            try:
                return datetime.strptime(transaction.get('date', ''), "%Y-%m-%d")
            except (ValueError, KeyError):
                logger.warning(f"无法解析交易日期，使用当前时间: {transaction}")
                return timezone.now()

    def _parse_transaction_amount(self, transaction):
        """解析交易金额"""
        try:
            return Decimal(str(transaction.get('amount', 0)))
        except (ValueError, TypeError, InvalidOperation):
            logger.warning(f"无效的交易金额: {transaction.get('amount')}")
            return Decimal('0')

    def _extract_ai_content(self, bot_response):
        """从AI响应中提取内容"""
        default_content = "The server is busy. Please try again later."
        
        if not isinstance(bot_response, dict):
            return default_content
        
        # 按优先级尝试不同的内容位置
        if "ai_output" in bot_response:
            return bot_response['ai_output']
        
        if "content" in bot_response:
            content = bot_response['content']
            if isinstance(content, dict):
                if "ai_output" in content:
                    return content['ai_output']
                if "en" in content:
                    return content['en']
            if isinstance(content, str):
                return content
        
        if "en" in bot_response:
            en_content = bot_response['en']
            if isinstance(en_content, dict) and "ai_output" in en_content:
                return en_content['ai_output']
            if isinstance(en_content, str):
                return en_content
        
        return default_content

    def _extract_random_emoji(self, bot_response):
        """从AI响应中提取随机值和表情"""
        if isinstance(bot_response, dict):
            return bot_response.get('random', 0), bot_response.get('emoji', '')
        return 0, ''

    def _create_ai_message(self, user_id, session, content, random_value, emoji_value, transaction_ids):
        """创建AI回复消息"""
        ai_message = Message.objects.create(
            user_id=user_id,
            session=session,
            content=content,
            message_type=Message.TYPE_ASSISTANT,
            is_user=False,
            random=random_value,
            emoji=emoji_value,
        )
        
        # 如果有交易ID，设置到消息中
        if transaction_ids:
            ai_message.set_transaction_ids_list(transaction_ids)
            ai_message.save()
            logger.debug(f"设置AI消息的交易IDs: {ai_message.transaction_ids}")
        
        return ai_message

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
