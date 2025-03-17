from django.core.management.base import BaseCommand
from django.utils.translation import gettext_lazy as _
from categorization.models import TransactionCategory, LedgerCategory, AssetCategory


class Command(BaseCommand):
    help = '初始化默认分类数据'

    def handle(self, *args, **options):
        self.stdout.write('开始初始化默认分类...')

        # 初始化交易分类
        transaction_categories = [
            # 支出分类 (19大类)
            {'name': _('食品'), 'is_income': False, 'icon': '🍽️', 'sort_order': 1},
            {'name': _('服饰'), 'is_income': False, 'icon': '👕', 'sort_order': 2},
            {'name': _('出行'), 'is_income': False, 'icon': '🚌', 'sort_order': 3},
            {'name': _('蔬菜'), 'is_income': False, 'icon': '🥬', 'sort_order': 4},
            {'name': _('零食'), 'is_income': False, 'icon': '🍪', 'sort_order': 5},
            {'name': _('日用'), 'is_income': False, 'icon': '🛒', 'sort_order': 6},
            {'name': _('购物'), 'is_income': False, 'icon': '🛍️', 'sort_order': 7},
            {'name': _('水果'), 'is_income': False, 'icon': '🍎', 'sort_order': 8},
            {'name': _('体育'), 'is_income': False, 'icon': '⚽', 'sort_order': 9},
            {'name': _('通讯'), 'is_income': False, 'icon': '📱', 'sort_order': 10},
            {'name': _('学习'), 'is_income': False, 'icon': '📚', 'sort_order': 11},
            {'name': _('美容'), 'is_income': False, 'icon': '💄', 'sort_order': 12},
            {'name': _('宠物'), 'is_income': False, 'icon': '🐱', 'sort_order': 13},
            {'name': _('娱乐'), 'is_income': False, 'icon': '🎮', 'sort_order': 14},
            {'name': _('数码'), 'is_income': False, 'icon': '💻', 'sort_order': 15},
            {'name': _('礼物'), 'is_income': False, 'icon': '🎁', 'sort_order': 16},
            {'name': _('旅行'), 'is_income': False, 'icon': '✈️', 'sort_order': 17},
            {'name': _('居家'), 'is_income': False, 'icon': '🏠', 'sort_order': 18},
            {'name': _('其他'), 'is_income': False, 'icon': '📝', 'sort_order': 19},

            # 收入分类 (4大类)
            {'name': _('工资'), 'is_income': True, 'icon': '💰', 'sort_order': 1},
            {'name': _('兼职'), 'is_income': True, 'icon': '💼', 'sort_order': 2},
            {'name': _('投资'), 'is_income': True, 'icon': '📈', 'sort_order': 3},
            {'name': _('其他'), 'is_income': True, 'icon': '📝', 'sort_order': 4},
        ]

        # 初始化账本类型 (5类)
        ledger_categories = [
            {'name': _('日常账本'), 'icon': '📅', 'is_default': True, 'sort_order': 1},
            {'name': _('商务账本'), 'icon': '💼', 'is_default': False, 'sort_order': 2},
            {'name': _('旅行账本'), 'icon': '✈️', 'is_default': False, 'sort_order': 3},
            {'name': _('居家账本'), 'icon': '🏠', 'is_default': False, 'sort_order': 4},
            {'name': _('自定义账本'), 'icon': '⚙️', 'is_default': False, 'sort_order': 5},
        ]

        # 初始化资产分类
        asset_categories = [
            # Debit (借记卡/现金类)
            {'name': _('现金'), 'category_type': '借记卡/现金', 'icon': '💵', 'is_positive_asset': True, 'sort_order': 1},
            {'name': _('银行借记卡'), 'category_type': '借记卡/现金', 'icon': '💳', 'is_positive_asset': True, 'sort_order': 2},
            {'name': _('定期存款'), 'category_type': '借记卡/现金', 'icon': '📱', 'is_positive_asset': True, 'sort_order': 3},

            # Credit (信用卡类)
            {'name': _('信用卡'), 'category_type': '信用卡', 'icon': '💰', 'is_positive_asset': False,'sort_order': 4},
            {'name': _('花呗'), 'category_type': '信用卡', 'icon': '💳', 'is_positive_asset': False, 'sort_order': 5},
            {'name': _('京东白条'), 'category_type': '信用卡', 'icon': '💳', 'is_positive_asset': False, 'sort_order': 6},

            # Borrow/Lend (借贷类)
            {'name': _('微信钱包'), 'category_type': '网络', 'icon': '📤', 'is_positive_asset': True, 'sort_order': 7},
            {'name': _('支付宝'), 'category_type': '网络', 'icon': '📥', 'is_positive_asset': True, 'sort_order': 8},
            {'name': _('其他'), 'category_type': '网络', 'icon': '🏦', 'is_positive_asset': True, 'sort_order': 9},

        ]

        # 创建交易分类
        for category in transaction_categories:
            TransactionCategory.objects.get_or_create(
                name=category['name'],
                is_income=category['is_income'],
                defaults={
                    'icon': category['icon'],
                    'sort_order': category['sort_order']
                }
            )
            self.stdout.write(f"创建交易分类: {category['name']} ({'收入' if category['is_income'] else '支出'})")

        # 创建账本类型
        for category in ledger_categories:
            LedgerCategory.objects.get_or_create(
                name=category['name'],
                defaults={
                    'icon': category['icon'],
                    'is_default': category['is_default'],
                    'sort_order': category['sort_order']
                }
            )
            self.stdout.write(f"创建账本类型: {category['name']}")

        # 创建资产分类
        for category in asset_categories:
            AssetCategory.objects.get_or_create(
                name=category['name'],
                category_type=category['category_type'],
                defaults={
                    'icon': category['icon'],
                    'is_positive_asset': category['is_positive_asset'],
                    'sort_order': category['sort_order']
                }
            )
            self.stdout.write(f"创建资产分类: {category['name']} ({category['category_type']})")

        self.stdout.write(self.style.SUCCESS('成功初始化所有默认分类！'))