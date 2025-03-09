from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class GoalsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'goals'
    verbose_name = _('梦想基金')
