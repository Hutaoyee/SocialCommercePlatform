<template>

  <LeftLogo />

  <div class="login-container ">
    <h2 class="is-size-2 has-text-centered has-text-weight-bold mb-4">登录</h2>
    
    <form @submit.prevent="handleSubmit">
      <div class="field mb-4">
        <label for="username" class="label">用户名：</label>
          <div class="control">
          <input 
            id="username"
            v-model="formData.username"
            class="input" 
            type="text" 
            placeholder="请输入用户名"
          >
          </div>
      </div>

      <div class="field mb-4">
        <label for="password" class="label">密码：</label>
        <div class="control">
          <input 
            id="password"
            v-model="formData.password"
            class="input" 
            type="password" 
            placeholder="请输入密码"
          >
        </div>
      </div>

      <div class="field">
        <p class="control mb-2">
          <button 
              class="button is-success"
              :class="{ 'is-loading': isSubmitting }"
              :disabled="isSubmitting"
          >
              登录
          </button>
        </p>

        <p class="control">还没有账号？<router-link to="/register">点击注册</router-link></p>
      </div>

      <!-- 错误提示 -->
      <div class="notification is-danger mt-4" v-if="errorMessage">
        {{ errorMessage }}
      </div>
    </form>
  </div>
</template>

<script>
import { userAPI } from '@/api/user'
import { useUserStore } from '@/stores/user'
import { useRouter } from 'vue-router'

import logoUrl from '@/assets/logo.svg'

import LeftLogo from '../components/LeftLogo.vue'

export default {
    components: {
      LeftLogo  // 必须注册组件才能使用
    },

    setup() {

      const userStore = useUserStore()
      const router = useRouter()

      return { userStore, router }
    },

    data() {
      return {

        formData: {
          username: '',
          password: ''
        },
        isSubmitting: false,
        errorMessage: '',

        logoUrl: logoUrl
      }
    },

    methods: {
      async handleSubmit() {
        this.isSubmitting = true
        this.errorMessage = ''
        
        try {
          // 调用登录 API
          const response = await userAPI.login(this.formData)
          console.log('登录成功:', response.data)
          
          // 保存用户信息和 Token 到 Store
          this.userStore.login(
            response.data.user,
            response.data.access
          )
          
          // // 跳转到首页
          // this.router.push('/')

          // 智能跳转：优先跳转到 redirect 参数指定的页面，否则跳转首页
          const redirect = this.$route.query.redirect || '/'
          this.router.push(redirect)

        } catch (error) {
          console.error('登录失败:', error)
          
          if (error.response) {
            const errors = error.response.data
            
            // 显示错误信息
            if (errors.non_field_errors) {
              this.errorMessage = errors.non_field_errors[0]
            } else if (errors.username) {
              this.errorMessage = errors.username[0]
            } else if (errors.password) {
              this.errorMessage = errors.password[0]
            } else {
              this.errorMessage = '登录失败，请重试'
            }
          } else if (error.request) {
            this.errorMessage = '网络错误，请检查连接'
          } else {
            this.errorMessage = '发生未知错误'
          }
        } finally {
          this.isSubmitting = false
        }
      }
    }
  }
</script>

<style lang="scss" scoped>
/* 自定义输入框聚焦时的边框颜色 */
.input:focus,
.input:active {
  border-color: hsl(171, 100%, 41%);
  box-shadow: 0 0 0 0.125em rgba(0, 209, 178, 0.25);
}

/* 按钮样式 */
.button.is-success {
  background-color: hsl(171, 100%, 41%);
  border-color: transparent;
}

.button.is-success:hover {
  background-color: hsl(171, 100%, 35%);
}
</style>