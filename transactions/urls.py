from django.urls import path, include
from rest_framework import routers
from .views import TransactionViewSet

router = routers.DefaultRouter()
router.register(r'transactions', TransactionViewSet, basename='transaction')

urlpatterns = [
    path('', include(router.urls)),
] 