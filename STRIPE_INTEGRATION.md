# Stripe 支付集成指南

## 概述

本项目已集成 Stripe Checkout 支付方式，支持在线支付功能。使用沙盒（测试）环境，不会产生真实扣款。

## 已完成的配置

### 后端（Django）

1. **安装依赖**
   - 已安装 `stripe` Python 包

2. **配置密钥**（`backend/backend/settings.py`）
   ```python
   STRIPE_SECRET_KEY = 'sk_test_51SM2kuFpHG4cnOsZ...'
   STRIPE_PUBLISHABLE_KEY = 'pk_test_51SM2kuFpHG4cnOsZ...'
   STRIPE_WEBHOOK_SECRET = ''  # 使用 stripe listen 时会提供
   ```

3. **API 端点**
   - `POST /api/shopping/payments/create-checkout-session/` - 创建支付会话
   - `POST /api/shopping/payments/webhook/` - 接收 Stripe webhook 事件

### 前端（Vue3）

1. **安装依赖**
   - 已安装 `@stripe/stripe-js`

2. **组件**
   - `src/components/StripeCheckout.vue` - 支付按钮组件
   - `src/views/OrderSuccess.vue` - 支付成功页面

## 使用方法

### 在订单页面集成支付按钮

```vue
<template>
  <div class="order-detail">
    <!-- 订单信息 -->
    <div class="order-info">
      <p>订单号：{{ order.id }}</p>
      <p>总金额：¥{{ order.total_amount }}</p>
    </div>
    
    <!-- Stripe 支付按钮 -->
    <StripeCheckout 
      v-if="order.status === 'pending'"
      :order-id="order.id"
      button-text="使用 Stripe 支付"
      @success="handlePaymentSuccess"
      @error="handlePaymentError"
    />
  </div>
</template>

<script setup>
import StripeCheckout from '@/components/StripeCheckout.vue'

const handlePaymentSuccess = () => {
  console.log('支付成功')
}

const handlePaymentError = (error) => {
  console.error('支付失败:', error)
}
</script>
```

## 本地测试步骤

### 1. 启动后端服务

```powershell
cd backend
python manage.py runserver
```

### 2. 启动前端服务

```powershell
cd frontend
npm run dev
```

### 3. 设置 Webhook 转发（使用 Stripe CLI）

#### 安装 Stripe CLI

Windows (使用 Scoop):
```powershell
scoop install stripe
```

或直接下载：https://stripe.com/docs/stripe-cli

#### 登录 Stripe CLI

```powershell
stripe login
```

这会在浏览器中打开 Stripe Dashboard 进行授权。

#### 启动 Webhook 转发

```powershell
stripe listen --forward-to http://localhost:8000/api/shopping/payments/webhook/
```

**重要**：执行后会输出一个 webhook signing secret，类似：
```
> Ready! Your webhook signing secret is whsec_xxxxxxxxxxxxx
```

将这个 `whsec_xxxxxxxxxxxxx` 添加到后端的环境变量或 settings.py：

```python
STRIPE_WEBHOOK_SECRET = 'whsec_xxxxxxxxxxxxx'
```

### 4. 测试支付流程

1. 在前端创建一个订单
2. 点击"使用 Stripe 支付"按钮
3. 会跳转到 Stripe Checkout 页面
4. 使用测试卡号进行支付：

**Stripe 测试卡号**：
- 成功支付：`4242 4242 4242 4242`
- 需要验证：`4000 0025 0000 3155`
- 支付失败：`4000 0000 0000 9995`
- 过期日期：任何未来日期（如 `12/34`）
- CVC：任意3位数字（如 `123`）
- 邮编：任意邮编（如 `12345`）

5. 支付成功后会跳转到 `/order-success` 页面
6. 同时 Stripe CLI 会转发 webhook 到后端，后端会自动更新订单状态为"已支付"

### 5. 查看 Webhook 日志

在运行 `stripe listen` 的终端中可以看到所有转发的事件：

```
2025-01-09 10:30:15   --> checkout.session.completed [evt_xxx]
2025-01-09 10:30:15  <--  [200] POST http://localhost:8000/api/shopping/payments/webhook/ [evt_xxx]
```

## 测试事件触发

可以使用 Stripe CLI 手动触发测试事件：

```powershell
# 触发支付成功事件
stripe trigger checkout.session.completed

# 触发支付意图成功事件
stripe trigger payment_intent.succeeded
```

## API 请求示例

### 创建 Checkout Session

```javascript
const response = await axios.post('/api/shopping/payments/create-checkout-session/', {
  order_id: 123,
  success_url: 'http://localhost:5173/order-success?session_id={CHECKOUT_SESSION_ID}',
  cancel_url: 'http://localhost:5173/orders'
})

// 返回
{
  "sessionId": "cs_test_xxxxxxxxxxxxx",
  "url": "https://checkout.stripe.com/c/pay/cs_test_xxxxxxxxxxxxx",
  "publishableKey": "pk_test_xxxxxxxxxxxxx"
}
```

## 安全注意事项

⚠️ **重要安全提示**：

1. **不要将密钥提交到代码仓库**
   - 密钥应该存储在环境变量中
   - 在 `.gitignore` 中添加 `.env` 文件

2. **使用环境变量**
   
   创建 `backend/.env` 文件：
   ```env
   STRIPE_SECRET_KEY=sk_test_xxxxxxxxxxxxx
   STRIPE_PUBLISHABLE_KEY=pk_test_xxxxxxxxxxxxx
   STRIPE_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxx
   ```

3. **生产环境配置**
   - 替换为生产环境密钥（`sk_live_xxx` 和 `pk_live_xxx`）
   - 确保使用 HTTPS
   - 在 Stripe Dashboard 中配置真实的 webhook URL
   - 启用 webhook 签名验证（必须）

4. **PCI 合规**
   - 使用 Stripe Checkout，卡片信息不经过你的服务器
   - 不要在前端或后端存储完整卡号
   - 所有敏感数据由 Stripe 处理

## 常见问题

### Q: Webhook 没有收到事件？
A: 确保 `stripe listen` 正在运行，并且 webhook URL 正确。检查防火墙是否阻止了连接。

### Q: 支付成功但订单状态未更新？
A: 检查 webhook 处理逻辑，查看后端日志是否有错误。确保 `STRIPE_WEBHOOK_SECRET` 配置正确。

### Q: 前端跳转到 Stripe 页面失败？
A: 检查浏览器控制台错误，确认后端 API 返回了正确的 sessionId。

### Q: 如何在生产环境部署？
A: 
1. 替换为生产环境密钥
2. 在 Stripe Dashboard 配置真实 webhook URL
3. 确保使用 HTTPS
4. 配置正确的 CORS 和 ALLOWED_HOSTS

## 相关链接

- [Stripe 文档](https://stripe.com/docs)
- [Stripe Checkout 文档](https://stripe.com/docs/payments/checkout)
- [Stripe CLI 文档](https://stripe.com/docs/stripe-cli)
- [测试卡号列表](https://stripe.com/docs/testing)

## 支持

如有问题，请查看：
1. 后端日志：`backend/` 目录下的控制台输出
2. 前端控制台：浏览器开发者工具
3. Stripe Dashboard：https://dashboard.stripe.com/test/payments
