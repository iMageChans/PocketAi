from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LedgerCategoryViewSet, AssetCategoryViewSet, TransactionCategoryViewSet

app_name = 'categorization'

router = DefaultRouter()
router.register(r'ledger', LedgerCategoryViewSet, basename='ledger')
router.register(r'asset', AssetCategoryViewSet, basename='asset')
router.register(r'transaction', TransactionCategoryViewSet, basename='transaction')

urlpatterns = [
    path('', include(router.urls)),
]