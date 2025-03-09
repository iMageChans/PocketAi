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
            {'name': _('Food'), 'is_income': False, 'icon': '🍽️', 'sort_order': 1},
            {'name': _('Clothes'), 'is_income': False, 'icon': '👕', 'sort_order': 2},
            {'name': _('Transport'), 'is_income': False, 'icon': '🚌', 'sort_order': 3},
            {'name': _('Vegetables'), 'is_income': False, 'icon': '🥬', 'sort_order': 4},
            {'name': _('Snacks'), 'is_income': False, 'icon': '🍪', 'sort_order': 5},
            {'name': _('Groceries'), 'is_income': False, 'icon': '🛒', 'sort_order': 6},
            {'name': _('Shopping'), 'is_income': False, 'icon': '🛍️', 'sort_order': 7},
            {'name': _('Fruits'), 'is_income': False, 'icon': '🍎', 'sort_order': 8},
            {'name': _('Sports'), 'is_income': False, 'icon': '⚽', 'sort_order': 9},
            {'name': _('Communication'), 'is_income': False, 'icon': '📱', 'sort_order': 10},
            {'name': _('Study'), 'is_income': False, 'icon': '📚', 'sort_order': 11},
            {'name': _('Beauty'), 'is_income': False, 'icon': '💄', 'sort_order': 12},
            {'name': _('Pets'), 'is_income': False, 'icon': '🐱', 'sort_order': 13},
            {'name': _('Entertainment'), 'is_income': False, 'icon': '🎮', 'sort_order': 14},
            {'name': _('Digital'), 'is_income': False, 'icon': '💻', 'sort_order': 15},
            {'name': _('Gifts'), 'is_income': False, 'icon': '🎁', 'sort_order': 16},
            {'name': _('Travel'), 'is_income': False, 'icon': '✈️', 'sort_order': 17},
            {'name': _('Household'), 'is_income': False, 'icon': '🏠', 'sort_order': 18},
            {'name': _('Others'), 'is_income': False, 'icon': '📝', 'sort_order': 19},

            # 收入分类 (4大类)
            {'name': _('Salary'), 'is_income': True, 'icon': '💰', 'sort_order': 1},
            {'name': _('Part-time Job'), 'is_income': True, 'icon': '💼', 'sort_order': 2},
            {'name': _('Investments'), 'is_income': True, 'icon': '📈', 'sort_order': 3},
            {'name': _('Others'), 'is_income': True, 'icon': '📝', 'sort_order': 4},
        ]

        # 初始化账本类型 (5类)
        ledger_categories = [
            {'name': _('Daily Ledger'), 'icon': '📅', 'is_default': True, 'sort_order': 1},
            {'name': _('Business Ledger'), 'icon': '💼', 'is_default': False, 'sort_order': 2},
            {'name': _('Travel Ledger'), 'icon': '✈️', 'is_default': False, 'sort_order': 3},
            {'name': _('Housing Ledger'), 'icon': '🏠', 'is_default': False, 'sort_order': 4},
            {'name': _('Customization'), 'icon': '⚙️', 'is_default': False, 'sort_order': 5},
        ]

        # 初始化资产分类
        asset_categories = [
            # Debit (借记卡/现金类)
            {'name': _('Cash'), 'category_type': 'debit', 'icon': '💵', 'is_positive_asset': True, 'sort_order': 1},
            {'name': _('Debit Card'), 'category_type': 'debit', 'icon': '💳', 'is_positive_asset': True, 'sort_order': 2},
            {'name': _('PayPal'), 'category_type': 'debit', 'icon': '📱', 'is_positive_asset': True, 'sort_order': 3},
            {'name': _('Others Debit Account'), 'category_type': 'debit', 'icon': '💰', 'is_positive_asset': True, 'sort_order': 4},

            # Credit (信用卡类)
            {'name': _('Credit Card'), 'category_type': 'credit', 'icon': '💳', 'is_positive_asset': False, 'sort_order': 5},
            {'name': _('Others Credit Account'), 'category_type': 'credit', 'icon': '💳', 'is_positive_asset': False, 'sort_order': 6},

            # Borrow/Lend (借贷类)
            {'name': _('Lent'), 'category_type': 'borrow_lend', 'icon': '📤', 'is_positive_asset': True, 'sort_order': 7},
            {'name': _('Borrowed'), 'category_type': 'borrow_lend', 'icon': '📥', 'is_positive_asset': False, 'sort_order': 8},
            {'name': _('Loan'), 'category_type': 'borrow_lend', 'icon': '🏦', 'is_positive_asset': False, 'sort_order': 9},

            # Investment (投资类)
            {'name': _('Stock'), 'category_type': 'investment', 'icon': '📈', 'is_positive_asset': True, 'sort_order': 10},
            {'name': _('Fund'), 'category_type': 'investment', 'icon': '💹', 'is_positive_asset': True, 'sort_order': 11},
            {'name': _('Cryptocurrency Wallet'), 'category_type': 'investment', 'icon': '🪙', 'is_positive_asset': True, 'sort_order': 12},
            {'name': _('Others Investment'), 'category_type': 'investment', 'icon': '📝', 'is_positive_asset': True, 'sort_order': 13},
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