# Social Commerce Platform

一个基于 Vue 3 + Django 的社交电商平台。

## 功能特性

- 🛍️ 商品管理
- 💬 社区论坛
- 🎵 内容发布
- 👤 用户系统
- 🛒 购物功能与支付系统

## 技术栈

### 后端
- Django
- Django REST Framework
- MySQL
- JWT

### 前端
- Vue 3 (Vite)
- Axios

## 快速开始

### 环境要求

- Python 3.11+
- Node.js 20.19.0+
- MySQL 8.0+

### 后端设置

1. 创建虚拟环境并安装依赖：

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

2. 配置环境变量：

```bash
# 复制环境变量模板
cp backend/.env.example backend/.env

# 编辑 backend/.env 文件，填写以下配置：
# - SECRET_KEY: Django 密钥（使用 python backend/generate_secret_key.py 生成）
# - DEBUG: 开发环境设为 True，生产环境设为 False
# - ALLOWED_HOSTS: 允许的主机名
# - DB_* : 数据库配置
# - STRIPE_*: Stripe 支付密钥（可选）
```

3. 数据库迁移：

```bash
python manage.py makemigrations
python manage.py migrate
```

4. 创建超级用户：

```bash
python manage.py createsuperuser
```

5. 运行开发服务器：

```bash
python manage.py runserver
```

### 前端设置

1. 安装依赖：

```bash
cd frontend
npm install
```

2. 运行开发服务器：

```bash
npm run dev
```

3. 构建生产版本：

```bash
npm run build
```

## 许可证

MIT License
