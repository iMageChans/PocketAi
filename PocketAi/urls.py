"""
URL configuration for PocketAi project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Admin界面
    path('admin/', admin.site.urls),
    path('api/categories/', include('categorization.urls')),  # 分类API路由
    path('api/ledgers/', include('ledger.urls')),  # 添加账本API路由
    path('api/', include('assets.urls')),  # 添加资产API路由
    path('api/', include('transactions.urls')),  # 添加交易记录API路由
    path('api/goals/', include('goals.urls')),  # 添加梦想基金API路由
    path('api/ai_messages/', include('ai_messages.urls')),  # 添加消息会话API路由
]
