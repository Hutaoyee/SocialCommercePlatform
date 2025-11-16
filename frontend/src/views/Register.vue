<template>

    <LeftLogo />

    <div class="register-container ">
        <h2 class="is-size-2 has-text-centered has-text-weight-bold mb-4">注册</h2>
        <form @submit.prevent="handleSubmit">
            <div class="field mb-4">
                <label for="username" class="label">用户名：</label>
                <div class="control">
                    <input 
                        id="username"
                        v-model="formData.username"
                        :class="{
                            'is-danger': usernameTouched && (!isUsernameValid || fieldErrors.username),
                            'is-success': usernameTouched && isUsernameValid && !fieldErrors.username
                        }"
                        class="input" 
                        type="text" 
                        placeholder="请输入用户名"
                        @blur="usernameTouched = true"
                        @input="fieldErrors.username = ''"
                    >
                </div>
                <p class="help is-danger" v-if="usernameTouched && !isUsernameValid">
                    请输入用户名
                </p>
                <p class="help is-danger" v-if="fieldErrors.username">
                    {{ fieldErrors.username }}
                </p>
            </div>

            <div class="field mb-4">
                <label for="email" class="label">邮箱：</label>
                <div class="control">
                    <input 
                        id="email"
                        v-model="formData.email"
                        :class="{
                            'is-danger': emailTouched && (!isEmailValid || fieldErrors.email),
                            'is-success': emailTouched && isEmailValid && !fieldErrors.email
                        }"
                        class="input" 
                        type="email" 
                        placeholder="请输入邮箱"
                        @blur="emailTouched = true"
                        @input="validateEmail"
                    >
                </div>

                <p class="help is-danger" v-if="emailTouched && !isEmailValid">
                    请输入有效的邮箱地址
                </p>
                <p class="help is-danger" v-if="fieldErrors.email">
                    {{ fieldErrors.email }}
                </p>
            </div>

            <div class="field mb-4">
                <label for="password" class="label">密码：</label>
                <div class="control">
                    <input 
                        id="password"
                        v-model="formData.password"
                        :class="{
                            'is-danger': passwordTouched && (!isPasswordValid || fieldErrors.password),
                            'is-success': passwordTouched && isPasswordValid && !fieldErrors.password
                        }"
                        class="input" 
                        type="password" 
                        placeholder="请输入密码"
                        @blur="passwordTouched = true"
                        @input="fieldErrors.password = ''"
                    >
                </div>
                <p class="help is-danger" v-if="passwordTouched && !isPasswordValid">
                    密码至少需要 6 个字符
                </p>
                <p class="help is-danger" v-if="fieldErrors.password">
                    {{ fieldErrors.password }}
                </p>
            </div>

            <div class="field">
                <p class="control mb-2">
                    <button class="button is-success"
                        :class="{ 'is-loading': isSubmitting }"
                        :disabled="isSubmitting"
                    >
                        注册
                    </button>
                </p>

                <p class="control">已有账号？<router-link to="/login">点击登录</router-link></p>
                
            </div>

            <!-- 错误提示 -->
            <div class="notification is-danger mt-4" v-if="errorMessage">
                {{ errorMessage }}
            </div>

            <!-- 成功提示 -->
            <div class="notification is-success mt-4" v-if="successMessage">
                {{ successMessage }}
            </div>
        </form>
    </div>
</template>

<script>
import { userAPI } from '@/api/user';

import logoUrl from '@/assets/logo.svg';

import LeftLogo from '../components/LeftLogo.vue'
export default {
    components: {
      LeftLogo
    },

    data() {
        return {
        formData: {
            username: '',
            email: '',
            password: ''
            },
        
        isSubmitting: false, // 标记是否正在提交
        
        errorMessage: '', // 错误提示信息
        successMessage: '', // 成功提示信息

        // 标记输入框是否被触碰过
        usernameTouched: false,
        emailTouched: false,
        passwordTouched: false,

        // 后端返回的字段级错误
        fieldErrors: {
            username: '',
            email: '',
            password: ''
        },

        logoUrl: logoUrl
        }
    },

    computed: {
        // 计算用户名是否有效
        isUsernameValid() {
            return this.formData.username.length > 0;
        },

        // 计算邮箱是否有效
        isEmailValid() {
            if (!this.formData.email) {
            return false;
            }
            // 邮箱正则表达式
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            return emailRegex.test(this.formData.email);
        },

        // 计算密码是否有效
        isPasswordValid() {
            return this.formData.password.length >= 6;
        }
    },

    methods: {
        // 点击文本框监测
        validateEmail() {
            // 实时验证邮箱
            if (this.formData.email) {
                this.emailTouched = true;
            }
            // 清空邮箱的字段错误
            this.fieldErrors.email = '';
        },

        // 提交注册信息
        async handleSubmit() {
            
            // 标记所有字段为已触碰
            this.usernameTouched = true;
            this.emailTouched = true;
            this.passwordTouched = true;

            // 验证所有字段
            if (!this.isUsernameValid || !this.isEmailValid || !this.isPasswordValid) {
                return;
            }

            this.isSubmitting = true;
            this.errorMessage = '';
            this.successMessage = '';
            // 清空字段错误
            this.fieldErrors = { username: '', email: '', password: '' };

            try {
                // 调用后端注册 API
                const response = await userAPI.register(this.formData);
                console.log('注册成功:', response.data);
                
                this.successMessage = '注册成功！正在跳转...';
                
                // 2秒后跳转到登录页
                setTimeout(() => {
                    this.$router.push('/login');
                }, 2000);
                
            } catch (error) {
                console.error('注册失败:', error);
                
                if (error.response) {
                    // 处理后端返回的错误
                    const errors = error.response.data;
                    
                    // 保存字段级错误
                    if (errors.username) {
                        this.fieldErrors.username = errors.username[0];
                    }
                    if (errors.email) {
                        this.fieldErrors.email = errors.email[0];
                    }
                    if (errors.password) {
                        this.fieldErrors.password = errors.password[0];
                    }
                    
                    // 设置通用错误消息
                    // if (errors.username) {
                    //     this.errorMessage = errors.username[0];
                    // } else if (errors.email) {
                    //     this.errorMessage = errors.email[0];
                    // } else if (errors.password) {
                    //     this.errorMessage = errors.password[0];
                    // } else {
                    //     this.errorMessage = '注册失败，请重试';
                    // }
                    if (error){

                        this.errorMessage = '注册失败，请重试';
                    }
                } else if (error.request) {
                    this.errorMessage = '网络错误，请检查连接';
                } else {
                    this.errorMessage = '发生未知错误';
                }
            } finally {
                this.isSubmitting = false;
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