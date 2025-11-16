<template>
  <section class="hero is-fullheight-with-navbar">
    <div class="hero-body">
      <div class="container">
        <div class="columns is-centered">
          <div class="column is-6-desktop is-8-tablet">
            <div class="box has-text-centered">

              <!-- 标题 -->
              <h1 class="title is-3 has-text-success mb-4">
                支付成功！
              </h1>

              <!-- 描述 -->
              <p class="subtitle is-5 has-text-grey mb-5">
                您的订单已成功支付，感谢您的购买
              </p>

              <!-- Session ID 信息 -->
              <div v-if="sessionId" class="notification mb-5">
                <p class="is-size-7 has-text-grey">
                  <strong>Session ID:</strong><br>
                  <span class="is-family-monospace">{{ sessionId }}</span>
                </p>
              </div>

              <!-- 操作按钮 -->
              <div class="buttons is-centered">
                <button @click="goToOrders" class="button is-primary is-medium">
                  <span>查看我的订单</span>
                </button>
                <button @click="goToHome" class="button is-warning is-medium">
                  <span>返回首页</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()
const sessionId = ref('')

onMounted(() => {

    document.body.classList.add('orderSuccess--page-active')
    document.getElementById('app')?.classList.add('orderSuccess--page-active')
  // 从 URL 参数获取 session_id
  sessionId.value = route.query.session_id || ''
  
  // 可以在这里调用后端 API 验证支付状态
  // 或者等待 webhook 处理完成
})

onUnmounted(() => {
    document.body.classList.remove('orderSuccess--page-active')
    document.getElementById('app')?.classList.remove('orderSuccess--page-active')
})

const goToOrders = () => {
  router.push('/myself?tab=orders')
}

const goToHome = () => {
  router.push('/')
}
</script>

<style>
    
    /* body.orderSuccess--page-active{
        align-items: start;
    } */

    #app.orderSuccess--page-active{
        display: grid;
        grid-template-columns: 1fr;
        width: 100%;
    }

    #app.orderSuccess--page-active > * {
        grid-column: 1 / -1;
    }
</style>

<style scoped>
/* 使用 Bulma 主题，添加动画效果 */
.icon-wrapper {
  animation: scaleIn 0.5s ease-out;
}

@keyframes scaleIn {
  0% {
    transform: scale(0);
    opacity: 0;
  }
  50% {
    transform: scale(1.1);
  }
  100% {
    transform: scale(1);
    opacity: 1;
  }
}

.box {
  border-radius: 8px;
  box-shadow: 0 8px 16px rgba(10, 10, 10, 0.1);
  animation: fadeInUp 0.6s ease-out;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.buttons {
  margin-top: 2rem;
}

.button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(10, 10, 10, 0.2);
  transition: all 0.3s ease;
}
</style>
