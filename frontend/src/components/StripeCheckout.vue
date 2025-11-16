<template>
  <div class="stripe-checkout">
    <button 
      @click="handleCheckout" 
      :disabled="loading"
      class="checkout-button"
    >
      <span v-if="!loading">{{ buttonText }}</span>
      <span v-else>处理中...</span>
    </button>
    
    <div v-if="error" class="error-message">
      {{ error }}
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'

const props = defineProps({
  orderId: {
    type: [Number, String],
    required: true
  },
  buttonText: {
    type: String,
    default: '前往支付'
  }
})

const emit = defineEmits(['success', 'error', 'cancel'])

const loading = ref(false)
const error = ref('')

const handleCheckout = async () => {
  loading.value = true
  error.value = ''
  
  try {
    // 1. 调用后端 API 创建 Checkout Session
    const response = await axios.post('/api/shopping/payments/create-checkout-session/', {
      order_id: props.orderId,
      success_url: `${window.location.origin}/order-success?session_id={CHECKOUT_SESSION_ID}`,
      cancel_url: `${window.location.origin}/myself?tab=orders`
    })
    
    const { url } = response.data
    
    // 2. 直接跳转到 Stripe Checkout URL
    if (url) {
      window.location.href = url
    } else {
      throw new Error('未收到 Stripe Checkout URL')
    }
    
  } catch (err) {
    console.error('支付错误:', err)
    error.value = err.response?.data?.error || err.message || '支付失败，请重试'
    emit('error', err)
    loading.value = false  // 只在错误时设置，成功时页面会跳转
  }
}
</script>

<style scoped>
.stripe-checkout {
  display: inline-block;
}

.checkout-button {
  padding: 12px 24px;
  font-size: 16px;
  font-weight: 600;
  color: white;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.checkout-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
}

.checkout-button:active:not(:disabled) {
  transform: translateY(0);
}

.checkout-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.error-message {
  margin-top: 10px;
  padding: 10px;
  background-color: #fee;
  color: #c33;
  border-radius: 4px;
  font-size: 14px;
}
</style>
