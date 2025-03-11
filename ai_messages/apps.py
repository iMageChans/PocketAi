from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AiMessagesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ai_messages'
    verbose_name = _('消息会话')
