<template>
  <Transition name="fade">
    <div v-if="isLoading" class="page-loader-overlay">
      <div class="loader-content">
        <SpinningText 
          text="This · is · God · Dream" 
          :duration="10"
          :radius="8"
        />
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import SpinningText from './SpinningText.vue'

const router = useRouter()
const isLoading = ref(false)

// 监听路由变化
router.beforeEach((to, from, next) => {
  isLoading.value = true
  next()
})

router.afterEach(() => {
  // 延迟一点时间让动画更流畅
  setTimeout(() => {
    isLoading.value = false
  }, 500)
})
</script>

<style scoped>
.page-loader-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.85);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.loader-content {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 350px;
  width: 100%;
}

.loader-content :deep(.relative) {
  font-size: 1.2rem;
  font-weight: bold;
  color: rgba(0, 209, 175, 1);
  letter-spacing: 0.05em;
  text-shadow: 0 0 20px rgba(0, 209, 175, 0.5);
}

/* 淡入淡出动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
