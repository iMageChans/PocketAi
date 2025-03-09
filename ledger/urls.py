from django.urls import path, include
from rest_framework import routers
from .views import LedgerViewSet

router = routers.DefaultRouter()
router.register(r'', LedgerViewSet, basename='ledger')

urlpatterns = [
    path('', include(router.urls)),
] 