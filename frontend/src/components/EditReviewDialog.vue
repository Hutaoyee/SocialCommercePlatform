<template>
  <div class="modal" :class="{ 'is-active': show }">
    <div class="modal-background" @click="$emit('close')"></div>
    <div class="modal-card">
      <header class="modal-card-head">
        <p class="modal-card-title">修改评价</p>
        <button class="delete" aria-label="close" @click="$emit('close')"></button>
      </header>
      <section class="modal-card-body">
        <!-- 商品信息 -->
        <div v-if="orderItem" class="media mb-4">
          <div class="media-left">
            <figure class="image is-64x64">
              <img :src="orderItem.image || '/placeholder.png'" :alt="orderItem.spu_name">
            </figure>
          </div>
          <div class="media-content">
            <p class="is-size-6 has-text-weight-semibold">{{ orderItem.spu_name }}</p>
            <p class="has-text-grey is-size-7">{{ orderItem.sku_title }}</p>
          </div>
        </div>

        <!-- 评价内容 -->
        <div class="field">
          <label class="label">评价内容 <span class="has-text-danger">*</span></label>
          <div class="control">
            <textarea 
              class="textarea" 
              v-model="formData.content"
              placeholder="请分享您的使用体验..."
              rows="5"
              maxlength="500"
            ></textarea>
          </div>
          <p class="help has-text-right">{{ formData.content.length }}/500</p>
        </div>

        <!-- 现有图片 -->
        <div v-if="existingImages.length > 0" class="field">
          <label class="label">已有图片</label>
          <div class="columns is-multiline">
            <div v-for="(image, index) in existingImages" :key="'existing-' + index" class="column is-one-quarter">
              <div class="image-preview">
                <img :src="image.url" alt="评价图片">
                <button class="delete-btn" @click="deleteExistingImage(image.id, index)">
                  <font-awesome-icon class="icon is-small" icon="fa-solid fa-xmark" />
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- 新增图片上传 -->
        <div class="field">
          <label class="label">添加新图片（可选，总计最多5张）</label>
          <div class="file has-name is-fullwidth">
            <label class="file-label">
              <input 
                class="file-input" 
                type="file" 
                accept="image/*" 
                multiple
                @change="handleFileChange"
                :disabled="existingImages.length + newFiles.length >= 5"
              >
              <span class="file-cta">
                <span class="file-icon">
                  <font-awesome-icon icon="fa-solid fa-upload" />
                </span>
                <span class="file-label">
                  选择图片
                </span>
              </span>
            </label>
          </div>
          <p class="help">支持 JPG、PNG 格式，每张图片不超过 5MB</p>
        </div>

        <!-- 新图片预览 -->
        <div v-if="newFiles.length > 0" class="field">
          <label class="label">新添加的图片</label>
          <div class="columns is-multiline">
            <div v-for="(file, index) in newFiles" :key="'new-' + index" class="column is-one-quarter">
              <div class="image-preview">
                <img :src="file.preview" :alt="file.name">
                <button class="delete-btn" @click="removeNewFile(index)">
                  <i class="fas fa-times"></i>
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- 错误提示 -->
        <div v-if="error" class="notification is-danger is-light">
          {{ error }}
        </div>
      </section>
      <footer class="modal-card-foot">
        <button class="button is-success mr-3" @click="submitUpdate" :class="{ 'is-loading': submitting }">
          保存修改
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
import reviewAPI from '@/api/review'

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  review: {
    type: Object,
    default: null
  },
  orderItem: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['close', 'success'])

const userStore = useUserStore()

// 表单数据
const formData = ref({
  content: ''
})

const existingImages = ref([])  // 现有图片
const newFiles = ref([])  // 新上传的文件
const submitting = ref(false)
const error = ref('')

// 处理文件选择
const handleFileChange = (event) => {
  const files = Array.from(event.target.files)
  
  // 检查总数量
  const totalImages = existingImages.value.length + newFiles.value.length
  if (totalImages + files.length > 5) {
    error.value = '最多只能有5张图片'
    return
  }
  
  // 验证每个文件
  for (const file of files) {
    // 检查文件大小 (5MB)
    if (file.size > 5 * 1024 * 1024) {
      error.value = `图片 ${file.name} 超过 5MB 限制`
      continue
    }
    
    // 检查文件类型
    if (!file.type.startsWith('image/')) {
      error.value = `文件 ${file.name} 不是图片格式`
      continue
    }
    
    // 创建预览
    const reader = new FileReader()
    reader.onload = (e) => {
      newFiles.value.push({
        file: file,
        name: file.name,
        preview: e.target.result
      })
    }
    reader.readAsDataURL(file)
  }
  
  // 清空 input
  event.target.value = ''
}

// 删除新文件
const removeNewFile = (index) => {
  newFiles.value.splice(index, 1)
  error.value = ''
}

// 删除现有图片
const deleteExistingImage = async (imageId, index) => {
  if (!confirm('确定要删除这张图片吗？')) {
    return
  }
  
  try {
    await reviewAPI.deleteReviewImage(props.review.id, imageId, userStore.token)
    existingImages.value.splice(index, 1)
    alert('图片已删除')
  } catch (err) {
    console.error('删除图片失败:', err)
    error.value = '删除图片失败，请稍后重试'
  }
}

// 监听对话框显示状态，填充现有数据
watch(() => props.show, (newVal) => {
  if (newVal && props.review) {
    formData.value = {
      content: props.review.content || ''
    }
    // 解析现有图片
    existingImages.value = (props.review.images || []).map((img) => {
      // 支持新格式（对象）和旧格式（字符串URL）
      if (typeof img === 'object' && img.id) {
        return {
          id: img.id,
          url: img.url || img.image
        }
      } else {
        // 旧格式，使用URL作为临时ID
        return {
          id: img,  // 使用URL作为ID
          url: img
        }
      }
    })
    newFiles.value = []
    error.value = ''
  }
})

// 提交修改
const submitUpdate = async () => {
  // 验证表单
  if (!formData.value.content.trim()) {
    error.value = '请输入评价内容'
    return
  }

  if (formData.value.content.length > 500) {
    error.value = '评价内容不能超过500字'
    return
  }

  if (!props.review || !props.review.id) {
    error.value = '评价信息错误'
    return
  }

  submitting.value = true
  error.value = ''

  try {
    const reviewData = {
      content: formData.value.content.trim(),
      uploaded_images: newFiles.value.map(f => f.file)
    }

    console.log('更新评价数据:', reviewData)

    await reviewAPI.updateReview(props.review.id, reviewData, userStore.token)
    emit('success')
    alert('评价修改成功！')
  } catch (err) {
    console.error('修改评价失败:', err)
    console.error('错误详情:', err.response?.data)
    
    // 处理详细的错误信息
    let errorMsg = '修改评价失败，请稍后重试'
    
    if (err.response?.data) {
      const data = err.response.data
      
      // 处理字段验证错误
      if (data.content) {
        errorMsg = Array.isArray(data.content) ? data.content[0] : data.content
      }
      else if (data.uploaded_images) {
        errorMsg = Array.isArray(data.uploaded_images) ? data.uploaded_images[0] : data.uploaded_images
      }
      // 处理通用错误
      else if (data.error) {
        errorMsg = data.error
      } 
      // 处理 detail 错误
      else if (data.detail) {
        errorMsg = data.detail
      }
      // 处理 non_field_errors
      else if (data.non_field_errors) {
        errorMsg = Array.isArray(data.non_field_errors) ? data.non_field_errors[0] : data.non_field_errors
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
.image.is-64x64 {
  width: 64px;
  height: 64px;
}

.image.is-64x64 img {
  object-fit: cover;
  border-radius: 4px;
}

.image-preview {
  position: relative;
  padding-top: 100%;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid hsl(0, 0%, 21%);
}

.image-preview img {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.delete-btn {
  position: absolute;
  top: 4px;
  right: 4px;
  background: rgba(255, 255, 255, 0.9);
  border: none;
  border-radius: 50%;
  width: 24px;
  height: 24px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #f14668;
  transition: all 0.2s;
}

.delete-btn:hover {
  background: #f14668;
  color: white;
  transform: scale(1.1);
}

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
