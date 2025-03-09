from django.urls import path, include
from rest_framework import routers
from .views import AssetViewSet, CurrencyRateViewSet

router = routers.DefaultRouter()
router.register(r'assets', AssetViewSet, basename='asset')
router.register(r'currency-rates', CurrencyRateViewSet, basename='currency-rate')

urlpatterns = [
    path('', include(router.urls)),
] 