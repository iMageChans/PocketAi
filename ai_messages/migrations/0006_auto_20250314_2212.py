# Generated by Django 3.2.25 on 2025-03-14 14:12

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('ai_messages', '0005_auto_20250312_1848'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='session_uuid',
            field=models.UUIDField(blank=True, db_index=True, help_text='会话的UUID标识符', null=True, verbose_name='会话UUID'),
        ),
        migrations.AddField(
            model_name='messagesession',
            name='uuid',
            field=models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, help_text='会话的唯一标识符', unique=True, verbose_name='UUID'),
        ),
    ]
