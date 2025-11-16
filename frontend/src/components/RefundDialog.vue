<template>
  <div class="modal" :class="{ 'is-active': show }">
    <div class="modal-background" @click="$emit('close')"></div>
    <div class="modal-card">
      <header class="modal-card-head">
        <p class="modal-card-title">申请退款</p>
        <button class="delete" aria-label="close" @click="$emit('close')"></button>
      </header>
      <section class="modal-card-body">
        <!-- 订单信息 -->
        <div v-if="order" class="box mb-4">
          <p class="mb-2"><strong>订单号：</strong>{{ order.order_number }}</p>
          <p><strong>订单金额：</strong><span class="has-text-danger">¥{{ order.total_amount }}</span></p>
        </div>

        <!-- 退款原因 -->
        <div class="field">
          <label class="label">退款原因 <span class="has-text-danger">*</span></label>
          <div class="control">
            <div class="select is-fullwidth">
              <select v-model="formData.reason">
                <option value="">请选择退款原因</option>
                <option value="not_received">未收到货</option>
                <option value="not_as_described">与描述不符</option>
                <option value="quality_issue">质量问题</option>
                <option value="wrong_item">发错货</option>
                <option value="other">其他原因</option>
              </select>
            </div>
          </div>
        </div>

        <!-- 详细说明 -->
        <div class="field">
          <label class="label">详细说明 <span class="has-text-danger">*</span></label>
          <div class="control">
            <textarea 
              class="textarea" 
              v-model="formData.description"
              placeholder="请详细描述您申请退款的原因..."
              rows="5"
              maxlength="500"
            ></textarea>
          </div>
          <p class="help has-text-right">{{ formData.description.length }}/500</p>
        </div>

        <!-- 错误提示 -->
        <div v-if="error" class="notification is-danger is-light">
          {{ error }}
        </div>
      </section>
      <footer class="modal-card-foot">
        <button class="button is-warning mr-3" @click="submitRefund" :class="{ 'is-loading': submitting }">
          提交申请
        </button>
        <button class="button" @click="$emit('close')" :disabled="submitting">
          取消
        </button>
      </footer>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useUserStore } from '@/stores/user'
import orderAPI from '@/api/order'

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  order: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['close', 'success'])

const userStore = useUserStore()

// 表单数据
const formData = ref({
  reason: '',
  description: ''
})

const submitting = ref(false)
const error = ref('')

// 监听对话框显示状态，重置表单
watch(() => props.show, (newVal) => {
  if (newVal) {
    formData.value = {
      reason: '',
      description: ''
    }
    error.value = ''
  }
})

// 提交退款申请
const submitRefund = async () => {
  // 验证表单
  if (!formData.value.reason) {
    error.value = '请选择退款原因'
    return
  }
  
  if (!formData.value.description.trim()) {
    error.value = '请输入详细说明'
    return
  }

  if (formData.value.description.length > 500) {
    error.value = '详细说明不能超过500字'
    return
  }

  if (!props.order || !props.order.id) {
    error.value = '订单信息错误'
    return
  }

  submitting.value = true
  error.value = ''

  try {
    const refundData = {
      reason: formData.value.reason,
      description: formData.value.description.trim()
    }

    await orderAPI.requestRefund(props.order.id, refundData, userStore.token)
    emit('success')
    alert('退款申请已提交，请等待审核！')
  } catch (err) {
    console.error('提交退款申请失败:', err)
    
    // 处理详细的错误信息
    let errorMsg = '提交失败，请稍后重试'
    
    if (err.response?.data) {
      const data = err.response.data
      
      // 处理字段验证错误
      if (data.reason || data.description) {
        errorMsg = data.reason?.[0] || data.description?.[0] || errorMsg
      } 
      // 处理通用错误
      else if (data.error) {
        errorMsg = data.error
      } 
      // 处理 detail 错误
      else if (data.detail) {
        errorMsg = data.detail
      }
      // 处理其他字段错误
      else if (typeof data === 'object') {
        const firstError = Object.values(data)[0]
        if (Array.isArray(firstError)) {
          errorMsg = firstError[0]
        } else if (typeof firstError === 'string') {
          errorMsg = firstError
        }
      }
    }
    
    error.value = errorMsg
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>


.modal-card-body {

  &::-webkit-scrollbar {
      width: 2px;
  }
  
  &::-webkit-scrollbar-track {
      background: transparent;
  }
  
  &::-webkit-scrollbar-thumb {
      background: rgba(0, 209, 175, 1);
      border-radius: 3px;
      
  }
}
</style>
