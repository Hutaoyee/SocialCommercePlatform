"""
首页视图
"""
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views.decorators.http import require_http_methods


def index(request):
    """首页 - 管理系统入口"""
    return render(request, 'shopping/index.html')


@require_http_methods(["POST"])
def index_login(request):
    """首页登录处理"""
    username = request.POST.get('username')
    password = request.POST.get('password')
    
    user = authenticate(request, username=username, password=password)
    
    if user is not None:
        login(request, user)
        # 登录成功后跳转到首页
        return redirect('index')
    else:
        # 登录失败，返回首页并显示错误
        return render(request, 'shopping/index.html', {
            'error': '用户名或密码错误，请重试。'
        })
