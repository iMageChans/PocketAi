from django.urls import path, include
from rest_framework import routers
from .views import MessageSessionViewSet, MessageViewSet

router = routers.DefaultRouter()
router.register(r'sessions', MessageSessionViewSet, basename='message-session')
router.register(r'', MessageViewSet, basename='message')

urlpatterns = [
    path('', include(router.urls)),
] 