from django.urls import path, include
from rest_framework import routers
from .views import GoalViewSet

router = routers.DefaultRouter()
router.register(r'', GoalViewSet, basename='goal')

urlpatterns = [
    path('', include(router.urls)),
] 