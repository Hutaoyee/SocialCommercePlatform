<template>
  <nav class="navbar is-fixed-top">
    <div class="container">
      <div class="navbar-brand">

        <router-link class="navbar-item" to="/">
          
          <img :src="logoUrl" alt="Logo" width="80" height="80">
        </router-link>

        <a class="navbar-burger" 
           :class="{ 'is-active': isMobileMenuActive }"
           role="button" 
           aria-label="menu" 
           :aria-expanded="isMobileMenuActive"
           @click="toggleMobileMenu">
          <span aria-hidden="true"></span>
          <span aria-hidden="true"></span>
          <span aria-hidden="true"></span>
          <span aria-hidden="true"></span>
        </a>
      </div>

      <div id="navMenu" class="navbar-menu" :class="{ 'is-active': isMobileMenuActive }">

        <div class="navbar-start">
          <router-link class="navbar-item has-text-primary has-text-weight-bold" to="/merch">Merch</router-link>
          <router-link class="navbar-item has-text-primary has-text-weight-bold" to="/publication">Publication</router-link>
          <router-link class="navbar-item has-text-primary has-text-weight-bold" to="/communicate">Communicate</router-link>
        </div>

        <div class="navbar-end">

          <div class="navbar-item">

            <!-- 购物车功能 - 使用span而非router-link -->
            <span class="navbar-item has-text-primary is-size-5" @click="openCartModal" style="cursor: pointer;">
              <font-awesome-icon icon="fa-solid fa-cart-shopping" />
            </span>

            <!-- 地址管理入口 -->
            <span class="navbar-item has-text-primary is-size-5" @click="openAddressModal" style="cursor: pointer;" title="地址管理" v-if="userStore.isLoggedIn">
              <font-awesome-icon icon="fa-solid fa-location-dot" />
            </span>

            <!-- 头像 -->
            <router-link :to="userStore.isLoggedIn ? '/myself' : '/login'">
              <figure class="image is-flex is-align-items-center is-justify-content-center">

                <img 
                  class="is-rounded" 
                  :src="userStore.avatar" 
                >
              </figure>
            </router-link>
          </div>
        </div>

      </div>
    </div>
  </nav>

  <!-- 购物车模态框 -->
  <div class="modal" :class="{ 'is-active': showCart }">
    <div class="modal-background" @click="closeCartModal"></div>
    <div class="modal-card" style="width: 95%; max-width: 1000px; max-height: 90vh;">
      <header class="modal-card-head">
        <p class="modal-card-title">购物车</p>
        <button class="delete" aria-label="close" @click="closeCartModal"></button>
      </header>
      <section class="modal-card-body" style="overflow-y: auto;">
        <div v-if="cartStore.loading" class="has-text-centered">
          <p>加载中...</p>
        </div>
        
        <div v-else-if="cartStore.cartItems.length === 0" class="notification">
          <p class="has-text-centered">购物车是空的</p>
        </div>
        
        <div v-else>
          <!-- 批量操作栏 -->
          <div class="box mb-4">
            <div class="level is-mobile">
              <div class="level-left">
                <div class="level-item">
                  <label class="checkbox">
                    <input type="checkbox" v-model="selectAll" @change="toggleSelectAll">
                    <span class="ml-2">全选</span>
                  </label>
                </div>
                <div class="level-item">
                  <button class="button is-danger is-small" 
                          @click="batchDelete" 
                          :disabled="selectedItems.length === 0">
                    <span class="icon is-small">
                      <font-awesome-icon icon="fa-solid fa-trash" />
                    </span>
                    <span>删除选中</span>
                  </button>
                </div>

                <div class="level-item" v-if="invalidItems.length > 0">
                  <button class="button is-warning is-small" 
                          @click="clearInvalid">
                    <span class="icon is-small">
                      <font-awesome-icon icon="fa-solid fa-broom" />
                    </span>
                    <span>清理失效 ({{ invalidItems.length }})</span>
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- 购物车项列表 -->
          <div class="box mb-3" v-for="item in cartStore.cartItems" :key="item.id">
            <div class="columns is-vcentered is-mobile">
              <!-- 选择框 -->
              <div class="column is-narrow">
                <label class="checkbox">
                  <input type="checkbox" 
                         :value="item.id" 
                         v-model="selectedItems"
                         :disabled="!item.sku.is_active">
                </label>
              </div>

              <!-- 商品图片 -->
              <div class="column is-narrow">
                <figure class="image is-64x64">
                  <img :src="item.sku.image || defaultImage" :alt="item.sku.spu_name">
                </figure>
              </div>

              <!-- 商品信息 -->
              <div class="column">
                <p class="title is-6 mb-1">
                  {{ item.sku.spu_name }}
                  <span v-if="!item.sku.is_active" class="tag is-danger is-small ml-2">已失效</span>
                </p>
                <p class="subtitle is-7 has-text-grey mb-1">{{ item.sku.title }}</p>
                <p class="has-text-weight-semibold has-text-primary">¥{{ item.sku.price }}</p>
                <p class="help" :class="{ 'has-text-danger': item.quantity > item.sku.stock }">
                  库存: {{ item.sku.stock }}
                  <span v-if="item.quantity > item.sku.stock" class="has-text-danger ml-2">⚠️ 库存不足</span>
                </p>
              </div>

              <!-- 数量控制 -->
              <div class="column is-narrow">
                <div class="field has-addons">
                  <p class="control">
                    <button class="button is-small" 
                            @click="decreaseQuantity(item)"
                            :disabled="item.quantity <= 1 || !item.sku.is_active">
                      <span class="icon is-small">
                        <font-awesome-icon icon="fa-solid fa-minus" />
                      </span>
                    </button>
                  </p>
                  <p class="control">
                    <input class="input is-small" 
                           type="number" 
                           v-model.number="item.quantity"
                           @change="updateQuantity(item)"
                           :disabled="!item.sku.is_active"
                           :min="1"
                           :max="item.sku.stock"
                           style="width: 60px; text-align: center;">
                  </p>
                  <p class="control">
                    <button class="button is-small" 
                            @click="increaseQuantity(item)"
                            :disabled="item.quantity >= item.sku.stock || !item.sku.is_active">
                      <span class="icon is-small">
                        <font-awesome-icon icon="fa-solid fa-plus" />
                      </span>
                    </button>
                  </p>
                </div>
              </div>

              <!-- 小计 -->
              <div class="column is-narrow has-text-right">
                <p class="has-text-weight-bold has-text-danger">
                  ¥{{ item.total_price }}
                </p>
              </div>

              <!-- 删除按钮 -->
              <div class="column is-narrow">
                <button class="button is-small is-ghost" 
                        @click="removeItem(item.id)"
                        title="删除">
                  <span class="icon has-text-primary">
                    <font-awesome-icon icon="fa-solid fa-trash" />
                  </span>
                </button>
              </div>
            </div>
          </div>

          <!-- 结算栏 -->
          <div class="box has-background-primary-dark">
            <div class="level is-mobile">
              <div class="level-left">
                <div class="level-item">
                  <span class="has-text-weight-semibold">
                    已选 {{ selectedItems.length }} 件商品
                  </span>
                </div>
              </div>
              <div class="level-right">
                <div class="level-item">
                  <span class="mr-3">
                    合计: <span class="has-text-danger has-text-weight-bold is-size-4">¥{{ selectedTotalPrice }}</span>
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
      <footer class="modal-card-foot">
        <button class="button is-success mr-3" 
                @click="goToCheckout"
                :disabled="selectedItems.length === 0 || hasInvalidSelected">
          <span class="icon">
            <font-awesome-icon icon="fa-solid fa-credit-card" />
          </span>
          <span>结算</span>
        </button>

        <button class="button" @click="closeCartModal">关闭</button>
      </footer>
    </div>
  </div>

  <!-- 地址管理模态框 -->
  <div class="modal" :class="{ 'is-active': showAddressModal }">
    <div class="modal-background"></div>
    <div class="modal-card" style="width: 90%; max-width: 1000px; max-height: 90vh;">
      <header class="modal-card-head">
        <p class="modal-card-title">地址管理</p>
        <button class="delete" aria-label="close" @click="closeAddressModal"></button>
      </header>
      <section class="modal-card-body" style="overflow-y: auto;">
        <AddressManager />
      </section>
    </div>
  </div>
</template>

<script>

  import { ref, computed } from 'vue'
  import { useRouter } from 'vue-router'
  import { useUserStore } from '@/stores/user'
  import { useCartStore } from '@/stores/cart'
  import AddressManager from './AddressManager.vue'

  import logoUrl from '@/assets/logoFront.png';

  export default {

    components: {
      AddressManager
    },

    setup() {
      const router = useRouter()
      const userStore = useUserStore()
      const cartStore = useCartStore()
      const showCart = ref(false)
      const showAddressModal = ref(false)
      const selectedItems = ref([])
      const selectAll = ref(false)
      const defaultImage = '/default-product.png'
      const isMobileMenuActive = ref(false)

      // 切换移动端菜单
      const toggleMobileMenu = () => {
        isMobileMenuActive.value = !isMobileMenuActive.value
      }

      // 计算失效商品
      const invalidItems = computed(() => {
        return cartStore.cartItems.filter(item => !item.sku.is_active)
      })

      // 计算选中商品的总价
      const selectedTotalPrice = computed(() => {
        const total = cartStore.cartItems
          .filter(item => selectedItems.value.includes(item.id))
          .reduce((sum, item) => sum + parseFloat(item.total_price), 0)
        return total.toFixed(2)
      })

      // 检查选中项中是否有失效商品
      const hasInvalidSelected = computed(() => {
        return cartStore.cartItems
          .filter(item => selectedItems.value.includes(item.id))
          .some(item => !item.sku.is_active || item.quantity > item.sku.stock)
      })

      // 全选/取消全选
      const toggleSelectAll = () => {
        if (selectAll.value) {
          // 只选择有效商品
          selectedItems.value = cartStore.cartItems
            .filter(item => item.sku.is_active)
            .map(item => item.id)
        } else {
          selectedItems.value = []
        }
      }

      // 减少数量
      const decreaseQuantity = (item) => {
        if (item.quantity > 1) {
          cartStore.updateQuantity(item.id, item.quantity - 1)
        }
      }

      // 增加数量
      const increaseQuantity = (item) => {
        if (item.quantity < item.sku.stock) {
          cartStore.updateQuantity(item.id, item.quantity + 1)
        } else {
          alert('库存不足')
        }
      }

      // 更新数量
      const updateQuantity = (item) => {
        if (item.quantity < 1) {
          item.quantity = 1
          return
        }
        if (item.quantity > item.sku.stock) {
          alert('库存不足')
          item.quantity = item.sku.stock
          return
        }
        cartStore.updateQuantity(item.id, item.quantity)
      }

      // 删除单个商品
      const removeItem = async (itemId) => {
        if (confirm('确定要删除这个商品吗？')) {
          await cartStore.removeItem(itemId)
          // 从选中列表中移除
          selectedItems.value = selectedItems.value.filter(id => id !== itemId)
        }
      }

      // 批量删除
      const batchDelete = async () => {
        if (selectedItems.value.length === 0) return
        
        if (confirm(`确定要删除选中的 ${selectedItems.value.length} 个商品吗？`)) {
          const success = await cartStore.batchRemoveItems(selectedItems.value)
          if (success) {
            selectedItems.value = []
            selectAll.value = false
          }
        }
      }

      // 清理失效商品
      const clearInvalid = async () => {
        const invalidIds = invalidItems.value.map(item => item.id)
        if (invalidIds.length === 0) return

        if (confirm(`确定要清理 ${invalidIds.length} 个失效商品吗？`)) {
          const success = await cartStore.batchRemoveItems(invalidIds)
          if (success) {
            selectedItems.value = selectedItems.value.filter(id => !invalidIds.includes(id))
            selectAll.value = false
          }
        }
      }

      const openCartModal = () => {
        showCart.value = true
        cartStore.fetchCartItems()
        // 重置选择状态
        selectedItems.value = []
        selectAll.value = false
      }

      const closeCartModal = () => {
        showCart.value = false
        // 不在这里清空选择，让其他函数决定何时清空
      }

      const openAddressModal = () => {
        showAddressModal.value = true
      }

      const closeAddressModal = () => {
        showAddressModal.value = false
      }

      const goToCheckout = () => {
        if (selectedItems.value.length === 0) {
          alert('请选择要结算的商品')
          return
        }

        if (hasInvalidSelected.value) {
          alert('选中的商品中有失效或库存不足的商品，请重新选择')
          return
        }

        console.log('准备结算，选中的商品ID:', selectedItems.value)
        const itemsParam = selectedItems.value.join(',')
        console.log('将要传递的query参数:', itemsParam)

        // 先关闭模态框
        showCart.value = false
        
        // 然后跳转
        router.push({
          path: '/checkout',
          query: {
            items: itemsParam
          }
        }).then(() => {
          // 跳转成功后清空选择
          selectedItems.value = []
          selectAll.value = false
        })
      }

      return {
        userStore,
        cartStore,
        showCart,
        showAddressModal,
        selectedItems,
        selectAll,
        defaultImage,
        invalidItems,
        selectedTotalPrice,
        hasInvalidSelected,
        isMobileMenuActive,
        toggleMobileMenu,
        toggleSelectAll,
        decreaseQuantity,
        increaseQuantity,
        updateQuantity,
        removeItem,
        batchDelete,
        clearInvalid,
        openCartModal,
        closeCartModal,
        openAddressModal,
        closeAddressModal,
        goToCheckout
      }
    },

    data() {
      return {
        logoUrl: logoUrl,
      }
    }
  }

</script>

<style lang="scss" scoped>
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

/* 响应式调整 */
@media screen and (max-width: 768px) {
  .modal-card {
    width: 100% !important;
    max-width: 100% !important;
  }
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
