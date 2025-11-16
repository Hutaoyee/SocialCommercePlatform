<template>
  <div class="modal" :class="{ 'is-active': show }">
    <div class="modal-background" @click="closeDialog"></div>
    <div class="modal-card" style="max-width: 600px;">
      <header class="modal-card-head">
        <p class="modal-card-title">选择商品规格</p>
        <button class="delete" aria-label="close" @click="closeDialog"></button>
      </header>
      <section class="modal-card-body">
        <div v-if="loading" class="has-text-centered py-6">
          <i class="fas fa-spinner fa-spin fa-2x"></i>
        </div>
        
        <div v-else-if="product">
          <!-- 商品信息 -->
          <div class="media mb-4">
            <figure class="media-left">
              <p class="image is-128x128">
                <img :src="product.image || '/placeholder.png'" :alt="product.name">
              </p>
            </figure>
            <div class="media-content">
              <p class="title is-5">{{ product.name }}</p>
              <p class="subtitle is-6 has-text-grey">{{ product.description }}</p>
              <p v-if="selectedSKU" class="has-text-weight-bold has-text-danger is-size-4">
                ¥{{ selectedSKU.price }}
              </p>
            </div>
          </div>

          <!-- 属性选择 -->
          <div v-if="skuData.attributes && skuData.attributes.length > 0" class="mb-4">
            <div v-for="attr in skuData.attributes" :key="attr.id" class="field">
              <label class="label">{{ attr.name }}</label>
              <div class="buttons">
                <button
                  v-for="value in attr.values"
                  :key="value.id"
                  class="button"
                  :class="{ 'is-primary': selectedAttributes[attr.id] === value.id }"
                  @click="selectAttribute(attr.id, value.id)"
                >
                  {{ value.value }}
                </button>
              </div>
            </div>
          </div>

          <!-- SKU信息 -->
          <div v-if="selectedSKU" class="notification is-info is-light">
            <p><strong>库存：</strong>{{ selectedSKU.stock }} 件</p>
          </div>

          <div v-if="!selectedSKU && skuData.attributes && skuData.attributes.length > 0" class="notification is-warning is-light">
            <p>请选择完整的商品规格</p>
          </div>

          <!-- 数量选择 -->
          <div v-if="selectedSKU" class="field">
            <label class="label">数量</label>
            <div class="field has-addons">
              <p class="control">
                <button class="button" @click="decreaseQuantity" :disabled="quantity <= 1">
                  <span class="icon">
                    <font-awesome-icon icon="fa-solid fa-minus" />
                  </span>
                </button>
              </p>
              <p class="control">
                <input 
                  class="input" 
                  type="number" 
                  v-model.number="quantity"
                  :min="1"
                  :max="selectedSKU.stock"
                  style="width: 80px; text-align: center;">
              </p>
              <p class="control">
                <button class="button" @click="increaseQuantity" :disabled="quantity >= selectedSKU.stock">
                  <span class="icon">
                    <font-awesome-icon icon="fa-solid fa-plus" />
                  </span>
                </button>
              </p>
            </div>
          </div>
        </div>
      </section>
      <footer class="modal-card-foot">
        <button 
          class="button is-success mr-3" 
          @click="confirmAddToCart"
          :disabled="!selectedSKU || submitting"
          :class="{ 'is-loading': submitting }">
          加入购物车
        </button>
        
        <button class="button" @click="closeDialog">取消</button>
      </footer>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useProductsStore } from '@/stores/products'
import { useCartStore } from '@/stores/cart'

const props = defineProps({
  show: {
    type: Boolean,
    required: true
  },
  product: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['close', 'success'])

const productsStore = useProductsStore()
const cartStore = useCartStore()

const loading = ref(false)
const submitting = ref(false)
const skuData = ref({ attributes: [], skus: [] })
const selectedAttributes = ref({})
const quantity = ref(1)

// 计算当前选中的SKU
const selectedSKU = computed(() => {
  if (!skuData.value.skus || skuData.value.skus.length === 0) {
    return null
  }

  // 如果没有属性，返回第一个SKU
  if (skuData.value.attributes.length === 0) {
    return skuData.value.skus[0]
  }

  // 检查是否所有属性都已选择
  const allAttributesSelected = skuData.value.attributes.every(
    attr => selectedAttributes.value[attr.id] !== undefined
  )

  if (!allAttributesSelected) {
    return null
  }

  // 查找匹配的SKU
  return skuData.value.skus.find(sku => {
    return Object.keys(selectedAttributes.value).every(
      attrId => sku.attributes[attrId] === selectedAttributes.value[attrId]
    )
  })
})

// 加载SKU数据
const loadSKUData = async () => {
  if (!props.product || !props.product.id) {
    return
  }

  loading.value = true
  try {
    skuData.value = await productsStore.getSPUSKUs(props.product.id)
    
    // 如果没有属性，自动选择第一个SKU
    if (skuData.value.attributes.length === 0 && skuData.value.skus.length > 0) {
      // 不需要选择属性
    }
    
    // 重置选择
    selectedAttributes.value = {}
    quantity.value = 1
  } catch (error) {
    console.error('加载SKU数据失败:', error)
    alert('加载商品信息失败')
  } finally {
    loading.value = false
  }
}

// 选择属性
const selectAttribute = (attrId, valueId) => {
  selectedAttributes.value[attrId] = valueId
}

// 减少数量
const decreaseQuantity = () => {
  if (quantity.value > 1) {
    quantity.value--
  }
}

// 增加数量
const increaseQuantity = () => {
  if (selectedSKU.value && quantity.value < selectedSKU.value.stock) {
    quantity.value++
  }
}

// 确认加入购物车
const confirmAddToCart = async () => {
  if (!selectedSKU.value) {
    alert('请选择完整的商品规格')
    return
  }

  submitting.value = true
  try {
    const success = await cartStore.addItem(selectedSKU.value.sku_code, quantity.value)
    if (success) {
      emit('success')
      closeDialog()
    }
  } catch (error) {
    console.error('加入购物车失败:', error)
  } finally {
    submitting.value = false
  }
}

// 关闭对话框
const closeDialog = () => {
  emit('close')
}

// 监听show变化，加载数据
watch(() => props.show, (newVal) => {
  if (newVal && props.product) {
    loadSKUData()
  }
})
</script>

<style scoped>
.image.is-128x128 {
  width: 128px;
  height: 128px;
}

.image.is-128x128 img {
  object-fit: cover;
  border-radius: 4px;
}

/* 隐藏数字输入框的上下箭头 */
input[type="number"]::-webkit-outer-spin-button,
input[type="number"]::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

input[type="number"] {
  -moz-appearance: textfield;
  appearance: textfield;
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
