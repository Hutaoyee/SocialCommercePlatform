"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.conf import settings
from django.conf.urls.static import static

from django.contrib import admin
from django.urls import path, include

# 导入首页视图
from shopping.index_views import index, index_login

urlpatterns = [
    path('', index, name='index'),  # 首页
    path('login/', index_login, name='index_login'),  # 首页登录处理
    path('admin/', admin.site.urls),
    path('api/', include('user.urls')),
    path('api/shopping/', include('shopping.urls')),  # API 路由
    path('api/', include('publish.urls')),
    path('api/forum/', include('forum.urls')),
    path('manage/shopping/', include('shopping.admin_urls')),  # 管理页面路由
]

# ⭐ 开发环境：Django 提供文件服务
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# 生产环境：由 Nginx 或云存储提供文件服务，不需要额外配置