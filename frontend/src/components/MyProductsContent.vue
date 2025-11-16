<template>
  <div class="my-products-content">
    <!-- 加载状态 -->
    <div v-if="loading" class="has-text-centered py-6">
      <button class="button is-loading is-large is-ghost"></button>
    </div>

    <!-- 商品网格 -->
    <div v-else-if="products.length > 0" class="columns is-multiline">
      <div 
        v-for="product in products" 
        :key="product.id" 
        class="column is-one-quarter-desktop is-one-third-tablet is-half-mobile"
      >
        <div class="card product-card">
          <div class="card-image">
            <figure class="image is-square">
              <img :src="product.image || '/placeholder.png'" :alt="product.spu_name">
            </figure>
          </div>
          <div class="card-content">
            <p class="title is-6 mb-2">{{ product.spu_name }}</p>
            <p class="subtitle is-7 has-text-grey mb-2">{{ product.sku_title }}</p>
            <p class="is-size-7 has-text-grey mb-1">
              <span class="icon-text">
                <span >购买时间：<span class="has-text-warning">{{ formatDate(product.purchased_at) }}</span></span>
              </span>
            </p>
          </div>
          <footer class="card-footer">
            <a class="card-footer-item has-text-danger" @click="deleteProduct(product.id)">
              <span class="icon-text">
                <span>删除</span>
              </span>
            </a>
          </footer>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-else class="has-text-centered py-6">
      <div class="empty-state">
        <span class="icon is-large has-text-grey-light">
          <i class="fas fa-shopping-bag fa-3x"></i>
        </span>
        <p class="is-size-5 has-text-grey mt-4">您还没有拥有的商品</p>
        <p class="is-size-6 has-text-grey-light mt-2">完成订单后，商品将出现在这里</p>
        <router-link to="/merch" class="button is-primary mt-4">
          去购物
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import ownedProductAPI from '@/api/ownedProduct'

const userStore = useUserStore()

// 数据
const products = ref([])
const loading = ref(false)

// 方法
const fetchProducts = async () => {
  loading.value = true
  try {
    const response = await ownedProductAPI.getMyProducts(userStore.token)
    products.value = response.data.results || response.data
  } catch (error) {
    console.error('获取商品失败:', error)
  } finally {
    loading.value = false
  }
}

const refresh = () => {
  fetchProducts()
}

const deleteProduct = async (productId) => {
  if (!confirm('确定要删除这个商品记录吗？删除后将无法恢复。')) {
    return
  }
  
  try {
    await ownedProductAPI.deleteProduct(productId, userStore.token)
    alert('删除成功')
    // 从列表中移除
    products.value = products.value.filter(p => p.id !== productId)
  } catch (error) {
    console.error('删除商品失败:', error)
    alert(error.response?.data?.error || '删除失败，请稍后重试')
  }
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  })
}

// 暴露给父组件调用
defineExpose({
  refresh
})

// 生命周期
onMounted(() => {
  fetchProducts()
})
</script>

<style scoped>
.my-products-content {
  width: 100%;
}

.product-card {
  height: 100%;
  display: flex;
  flex-direction: column;
  transition: transform 0.2s, box-shadow 0.2s;
}

.product-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
}

.product-card .card-image {
  overflow: hidden;
}

.product-card .card-image img {
  object-fit: cover;
  transition: transform 0.3s;
}

.product-card:hover .card-image img {
  transform: scale(1.05);
}

.product-card .card-content {
  flex: 1;
  padding: 1rem;
}

.product-card .card-footer {
  margin-top: auto;
}

.empty-state {
  padding: 3rem 1rem;
}

.image.is-square {
  padding-top: 100%;
  position: relative;
}

.image.is-square img {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}
</style>
