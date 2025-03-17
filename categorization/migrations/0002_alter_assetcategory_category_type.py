# Generated by Django 3.2.25 on 2025-03-17 11:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('categorization', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assetcategory',
            name='category_type',
            field=models.CharField(choices=[('debit', '借记卡/现金'), ('credit', '信用卡'), ('borrow_lend', '借贷'), ('investment', '投资'), ('network', '网络')], max_length=20, verbose_name='资产大分类'),
        ),
    ]
