"""
快速创建测试管理员账户
用户名: admin
密码: admin123
"""
import os
import django

# 设置 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# 检查是否已存在
if User.objects.filter(username='admin').exists():
    print('❌ 管理员账户 "admin" 已存在！')
else:
    # 创建超级用户
    User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='admin123'
    )
    print('✅ 管理员账户创建成功！')
    print('👤 用户名: admin')
    print('🔑 密码: admin123')
    print('\n现在可以访问 http://localhost:8000 登录了！')
