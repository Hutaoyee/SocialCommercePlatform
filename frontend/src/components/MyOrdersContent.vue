<template>
  <div class="my-orders-content">
    <!-- 订单状态筛选 -->
    <div class="tabs is-boxed">
      <ul>
        <li :class="{ 'is-active': currentStatus === 'all' }" @click="filterOrders('all')">
          <a>全部订单</a>
        </li>
        <li :class="{ 'is-active': currentStatus === 'pending' }" @click="filterOrders('pending')">
          <a>待付款</a>
        </li>
        <li :class="{ 'is-active': currentStatus === 'paid' }" @click="filterOrders('paid')">
          <a>待发货</a>
        </li>
        <li :class="{ 'is-active': currentStatus === 'shipped' }" @click="filterOrders('shipped')">
          <a>待收货</a>
        </li>
        <li :class="{ 'is-active': currentStatus === 'completed' }" @click="filterOrders('completed')">
          <a>已完成</a>
        </li>
        <li :class="{ 'is-active': currentStatus === 'cancelled' }" @click="filterOrders('cancelled')">
          <a>已取消</a>
        </li>
      </ul>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="has-text-centered py-6">
      <button class="button is-loading is-large is-ghost"></button>
    </div>

    <!-- 订单列表 -->
    <div v-else-if="filteredOrders.length > 0" class="orders-list">
      <div v-for="order in filteredOrders" :key="order.id" class="box order-item">
        <!-- 订单头部 -->
        <div class="order-header">
          <div class="level">
            <div class="level-left">
              <div class="level-item">
                <span class="has-text-grey">订单号：{{ order.order_number }}</span>
              </div>
              <div class="level-item">
                <span class="tag" :class="getStatusClass(order.status)">
                  {{ getStatusText(order.status) }}
                </span>
              </div>
            </div>
            <div class="level-right">
              <div class="level-item">
                <span class="has-text-grey">{{ formatDate(order.created_at) }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 订单商品 -->
        <div class="order-items">
          <div v-for="item in order.items" :key="item.id" class="order-item-row">
            <div class="columns is-vcentered">
              <div class="column is-narrow">
                <figure class="image is-96x96">
                  <img :src="item.image || '/placeholder.png'" :alt="item.spu_name">
                </figure>
              </div>
              <div class="column">
                <p class="is-size-6 has-text-weight-semibold">{{ item.spu_name }}</p>
                <p class="has-text-grey is-size-7">{{ item.sku_title }}</p>
              </div>
              <div class="column is-narrow">
                <p class="has-text-grey">x{{ item.quantity }}</p>
              </div>
              <div class="column is-narrow">
                <p class="has-text-weight-semibold">¥{{ item.price }}</p>
              </div>
              <div class="column is-narrow">
                <!-- 未评价：显示评价按钮 -->
                <button 
                  v-if="order.status === 'completed' && !item.is_reviewed" 
                  class="button is-small is-primary" 
                  @click="openReviewDialog(order, item)"
                >
                  评价
                </button>
                
                <!-- 已评价：显示修改和删除按钮 -->
                <div v-else-if="item.is_reviewed && item.review" class="buttons are-small">
                  <button class="button is-info" @click="editReview(item.review)">
                    <span>修改</span>
                  </button>

                  <button class="button is-danger" @click="deleteReview(item.review.id, order, item)">
                    <span>删除</span>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 订单金额和操作 -->
        <div class="order-footer">
          <div class="level">
            <div class="level-left">
              <div class="level-item" v-if="order.shipping_address">
                <span class="icon-text">
                  <span class="icon has-text-info"><font-awesome-icon icon="fa-solid fa-location-dot" /></span>
                  <span>{{ order.shipping_address }}</span>
                </span>
              </div>
              <!-- 物流信息 -->
              <div class="level-item" v-if="order.shipping_company && order.tracking_number">
                <span class="icon-text">
                  <span class="icon has-text-info"><font-awesome-icon icon="fa-solid fa-truck-fast" /></span>
                  <span>{{ order.shipping_company }}: {{ order.tracking_number }}</span>
                </span>
              </div>
            </div>
            <div class="level-right">
              <div class="level-item">
                <div class="has-text-right">
                  <p class="is-size-7 has-text-grey">订单总额</p>
                  <p class="is-size-5 has-text-danger has-text-weight-bold">¥{{ order.total_amount }}</p>
                </div>
              </div>
              <div class="level-item">
                <div class="buttons">
                  <!-- 待付款：显示 Stripe 支付按钮和取消按钮 -->
                  <template v-if="order.status === 'pending'">
                    <StripeCheckout 
                      :order-id="order.id"
                      button-text="立即支付"
                      @success="handlePaymentSuccess"
                      @error="handlePaymentError"
                    />
                    <button 
                      class="button is-danger is-outlined is-small"
                      @click="cancelOrder(order.id)">
                      取消订单
                    </button>
                  </template>
                  
                  <!-- 已付款或已发货：可以申请退款（如果没有退款记录） -->
                  <button 
                    v-if="(order.status === 'paid' || order.status === 'shipped') && !order.refund_request" 
                    class="button is-warning"
                    @click="openRefundDialog(order)">
                    申请退款
                  </button>
                  
                  <!-- 已发货：可以确认收货 -->
                  <button 
                    v-if="order.status === 'shipped'" 
                    class="button is-success"
                    @click="confirmDelivery(order.id)">
                    确认收货
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 退款状态 -->
        <div v-if="order.refund_request" class="notification is-warning is-light mt-3">
          <p><strong>退款状态：</strong>{{ getRefundStatusText(order.refund_request.status) }}</p>
          <p v-if="order.refund_request.admin_note" class="mt-2">
            <strong>处理备注：</strong>{{ order.refund_request.admin_note }}
          </p>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-else class="has-text-centered py-6">
      <p class="is-size-5 has-text-grey">暂无订单</p>
    </div>

    <!-- 评价对话框 -->
    <OrderReviewDialog
      :show="showReviewDialog"
      :order="selectedOrder"
      :orderItem="selectedOrderItem"
      @close="closeReviewDialog"
      @success="handleReviewSuccess"
    />

    <!-- 编辑评价对话框 -->
    <EditReviewDialog
      :show="showEditReviewDialog"
      :review="selectedReview"
      :orderItem="selectedOrderItem"
      @close="closeEditReviewDialog"
      @success="handleEditReviewSuccess"
    />

    <!-- 退款对话框 -->
    <RefundDialog
      :show="showRefundDialog"
      :order="selectedOrder"
      @close="closeRefundDialog"
      @success="handleRefundSuccess"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import orderAPI from '@/api/order'
import reviewAPI from '@/api/review'
import OrderReviewDialog from '@/components/OrderReviewDialog.vue'
import EditReviewDialog from '@/components/EditReviewDialog.vue'
import RefundDialog from '@/components/RefundDialog.vue'
import StripeCheckout from '@/components/StripeCheckout.vue'

const userStore = useUserStore()

// 数据
const orders = ref([])
const loading = ref(false)
const currentStatus = ref('all')

// 对话框状态
const showReviewDialog = ref(false)
const showEditReviewDialog = ref(false)
const showRefundDialog = ref(false)
const selectedOrder = ref(null)
const selectedOrderItem = ref(null)
const selectedReview = ref(null)

// 计算属性
const filteredOrders = computed(() => {
  if (currentStatus.value === 'all') {
    return orders.value
  }
  return orders.value.filter(order => order.status === currentStatus.value)
})

// 方法
const fetchOrders = async () => {
  loading.value = true
  try {
    const response = await orderAPI.getMyOrders(userStore.token)
    orders.value = response.data.results || response.data
  } catch (error) {
    console.error('获取订单失败:', error)
  } finally {
    loading.value = false
  }
}

const refresh = () => {
  fetchOrders()
}

const filterOrders = (status) => {
  currentStatus.value = status
}

const getStatusClass = (status) => {
  const statusClasses = {
    'pending': 'is-warning',
    'paid': 'is-info',
    'shipped': 'is-primary',
    'completed': 'is-success',
    'cancelled': 'is-danger'
  }
  return statusClasses[status] || 'is-light'
}

const getStatusText = (status) => {
  const statusTexts = {
    'pending': '待付款',
    'paid': '待发货',
    'shipped': '待收货',
    'completed': '已完成',
    'cancelled': '已取消'
  }
  return statusTexts[status] || status
}

const getRefundStatusText = (status) => {
  const refundStatusTexts = {
    'pending': '退款审核中',
    'approved': '退款已批准',
    'rejected': '退款已拒绝',
    'processing': '退款处理中',
    'completed': '退款已完成'
  }
  return refundStatusTexts[status] || status
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const cancelOrder = async (orderId) => {
  if (!confirm('确定要取消这个订单吗？')) return
  
  try {
    await orderAPI.cancelOrder(orderId, userStore.token)
    alert('订单已取消')
    fetchOrders()
  } catch (error) {
    console.error('取消订单失败:', error)
    alert(error.response?.data?.error || '取消订单失败')
  }
}

const confirmDelivery = async (orderId) => {
  if (!confirm('确认已收到商品吗？')) return
  
  try {
    await orderAPI.confirmDelivery(orderId, userStore.token)
    alert('确认收货成功，商品已添加到"我拥有的商品"')
    fetchOrders()
  } catch (error) {
    console.error('确认收货失败:', error)
    alert(error.response?.data?.error || '确认收货失败')
  }
}

const openReviewDialog = (order, item) => {
  selectedOrder.value = order
  selectedOrderItem.value = item
  showReviewDialog.value = true
}

const closeReviewDialog = () => {
  showReviewDialog.value = false
  selectedOrder.value = null
  selectedOrderItem.value = null
}

const handleReviewSuccess = () => {
  closeReviewDialog()
  fetchOrders()
}

const openRefundDialog = (order) => {
  selectedOrder.value = order
  showRefundDialog.value = true
}

const closeRefundDialog = () => {
  showRefundDialog.value = false
  selectedOrder.value = null
}

const handleRefundSuccess = () => {
  closeRefundDialog()
  fetchOrders()
}

// 编辑评价
const editReview = (review) => {
  selectedReview.value = review
  // 找到对应的 orderItem
  for (const order of orders.value) {
    const item = order.items.find(i => i.review && i.review.id === review.id)
    if (item) {
      selectedOrderItem.value = item
      break
    }
  }
  showEditReviewDialog.value = true
}

const closeEditReviewDialog = () => {
  showEditReviewDialog.value = false
  selectedReview.value = null
  selectedOrderItem.value = null
}

const handleEditReviewSuccess = () => {
  closeEditReviewDialog()
  fetchOrders()
}

// 删除评价
const deleteReview = async (reviewId, order, item) => {
  if (!confirm('确定要删除这条评价吗？')) {
    return
  }

  try {
    await reviewAPI.deleteReview(reviewId, userStore.token)
    alert('评价已删除')
    // 刷新订单列表
    fetchOrders()
  } catch (error) {
    console.error('删除评价失败:', error)
    alert(error.response?.data?.error || error.response?.data?.detail || '删除评价失败')
  }
}

// Stripe 支付成功回调
const handlePaymentSuccess = () => {
  console.log('支付成功')
  // 刷新订单列表
  fetchOrders()
}

// Stripe 支付失败回调
const handlePaymentError = (error) => {
  console.error('支付失败:', error)
  alert('支付失败，请重试')
}

// 暴露给父组件调用
defineExpose({
  refresh
})

// 生命周期
onMounted(() => {
  fetchOrders()
})
</script>

<style scoped>
.my-orders-content {
  width: 100%;
}

.order-item {
  margin-bottom: 1.5rem;
}

.order-header {
  padding-bottom: 1rem;
  border-bottom: 1px solid hsl(141, 53%, 31%);
  margin-bottom: 1rem;
}

.order-items {
  margin-bottom: 1rem;
}

.order-item-row {
  padding: 0.5rem 0;
}

.order-item-row:not(:last-child) {
  border-bottom: 1px dashed hsl(204, 71%, 39%);
}

.order-footer {
  padding-top: 1rem;
  border-top: 1px solid hsl(0, 0%, 20%);
}

.image.is-96x96 {
  width: 96px;
  height: 96px;
}

.image.is-96x96 img {
  object-fit: cover;
  border-radius: 4px;
}

/* 自定义选中状态的颜色 */
.tabs.is-boxed li.is-active a {

  color: hsl(171, 100%, 41%);
}

.tabs.is-boxed li.is-active a:hover {

  border-color: hsl(171, 100%, 41%);
}
</style>
