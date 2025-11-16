<template>
    <div class="container is-max-desktop mt-6 mb-6">
        <h1 class="title">订单确认</h1>

        <div v-if="loading" class="has-text-centered">
            <p>加载中...</p>
        </div>

        <div v-else>
            <!-- 收货地址选择 -->
            <div class="box">
                <h2 class="subtitle">收货地址</h2>
                
                <div v-if="addresses.length === 0" class="notification is-warning">
                    <p>您还没有收货地址，请先添加地址</p>
                    <button class="button is-primary mt-3" @click="showAddressForm = true">添加地址</button>
                </div>

                <div v-else class="columns is-multiline">
                    <div v-for="address in addresses" :key="address.id" class="column is-half">
                        <div 
                            class="box address-card" 
                            :class="{ 'is-selected': selectedAddress?.id === address.id }"
                            @click="selectedAddress = address"
                            style="cursor: pointer;">
                            <span class="tag is-success mb-2" v-if="address.is_default">默认</span>
                            <p class="has-text-weight-bold">{{ address.name }} {{ address.phone }}</p>
                            <p class="mt-2">{{ address.province }} {{ address.city }} {{ address.district }}</p>
                            <p>{{ address.address }}</p>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 商品清单 -->
            <div class="box">
                <h2 class="subtitle">商品清单</h2>
                <div v-for="item in checkoutItems" :key="item.id" class="media mb-4">
                    <figure class="media-left">
                        <p class="image is-64x64">
                            <img :src="item.sku.image" :alt="item.sku.spu_name">
                        </p>
                    </figure>
                    <div class="media-content">
                        <p class="title is-6">{{ item.sku.spu_name }}</p>
                        <p class="subtitle is-7">{{ item.sku.title }}</p>
                        <p class="has-text-grey">¥{{ item.sku.price}} x {{ item.quantity }}</p>
                    </div>
                    <div class="media-right">
                        <p class="has-text-danger has-text-weight-bold">¥{{ item.total_price }}</p>
                    </div>
                </div>
            </div>

            <!-- 支付方式 -->
            <div class="box">
                <h2 class="subtitle">支付方式</h2>
                <div class="notification is-info is-light">
                    <p><strong>💳 Stripe 安全支付</strong></p>
                    <p class="is-size-7 mt-2">提交订单后将跳转到 Stripe 安全支付页面</p>
                    <p class="is-size-7">支持 Visa、Mastercard、American Express 等主流信用卡</p>
                </div>
            </div>

            <!-- 订单备注 -->
            <div class="box">
                <h2 class="subtitle">订单备注</h2>
                <textarea class="textarea" v-model="remark" placeholder="选填，可以告诉卖家您的特殊需求" rows="3"></textarea>
            </div>

            <!-- 订单总计 -->
            <div class="box">
                <div class="level">
                    <div class="level-left">
                        <div class="level-item">
                            <p class="title is-5">总计：{{ totalItems }} 件商品</p>
                        </div>
                    </div>
                    <div class="level-right">
                        <div class="level-item">
                            <p class="title is-4 has-text-danger">¥{{ totalPrice }}</p>
                        </div>
                    </div>
                </div>

                <div class="has-text-right">
                    <button 
                        class="button is-medium is-primary" 
                        @click="submitOrder"
                        :disabled="!selectedAddress || checkoutItems.length === 0 || submitting"
                        :class="{ 'is-loading': submitting }">
                        提交订单并支付
                    </button>
                </div>
            </div>
        </div>

        <!-- 简易地址表单模态框 -->
        <div class="modal" :class="{ 'is-active': showAddressForm }">
            <div class="modal-background" @click="showAddressForm = false"></div>
            <div class="modal-card">
                <header class="modal-card-head">
                    <p class="modal-card-title">添加收货地址</p>
                </header>
                <section class="modal-card-body">
                    <div class="field">
                        <label class="label">收货人姓名</label>
                        <input class="input" v-model="newAddress.name" type="text">
                    </div>
                    <div class="field">
                        <label class="label">联系电话</label>
                        <input class="input" v-model="newAddress.phone" type="tel">
                    </div>
                    <div class="columns">
                        <div class="column">
                            <div class="field">
                                <label class="label">省份</label>
                                <input class="input" v-model="newAddress.province" type="text">
                            </div>
                        </div>
                        <div class="column">
                            <div class="field">
                                <label class="label">城市</label>
                                <input class="input" v-model="newAddress.city" type="text">
                            </div>
                        </div>
                        <div class="column">
                            <div class="field">
                                <label class="label">区县</label>
                                <input class="input" v-model="newAddress.district" type="text">
                            </div>
                        </div>
                    </div>
                    <div class="field">
                        <label class="label">详细地址</label>
                        <textarea class="textarea" v-model="newAddress.address" rows="3"></textarea>
                    </div>
                </section>
                <footer class="modal-card-foot">
                    <button class="button is-primary" @click="saveNewAddress">保存</button>
                    <button class="button" @click="showAddressForm = false">取消</button>
                </footer>
            </div>
        </div>
    </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useCartStore } from '@/stores/cart'
import { addressAPI } from '@/api/address'
import { orderAPI } from '@/api/order'
import { loadStripe } from '@stripe/stripe-js'
import apiClient from '@/api/axios'  // 使用配置好的 axios 实例

export default {
    name: 'Checkout',
    setup() {
        const router = useRouter()
        const route = useRoute()
        const userStore = useUserStore()
        const cartStore = useCartStore()
        
        const loading = ref(true)
        const addresses = ref([])
        const selectedAddress = ref(null)
        const paymentMethod = ref('stripe')  // 固定使用 Stripe
        const remark = ref('')
        const submitting = ref(false)
        const showAddressForm = ref(false)
        
        const newAddress = ref({
            name: '',
            phone: '',
            province: '',
            city: '',
            district: '',
            address: '',
            is_default: false
        })
        
        // 从URL参数获取选中的商品ID
        const selectedItemIds = computed(() => {
            const itemsParam = route.query.items
            console.log('URL参数 items:', itemsParam)
            if (!itemsParam) return []
            const ids = itemsParam.split(',').map(id => parseInt(id))
            console.log('解析后的商品ID:', ids)
            return ids
        })
        
        // 从购物车获取要结算的商品（只返回选中的商品）
        const checkoutItems = computed(() => {
            console.log('购物车所有商品:', cartStore.cartItems.map(item => ({ id: item.id, name: item.sku.spu_name })))
            console.log('选中的商品ID:', selectedItemIds.value)
            
            if (selectedItemIds.value.length === 0) {
                // 如果没有传递选中的商品ID，返回所有购物车商品（向后兼容）
                console.log('没有传递商品ID，返回所有商品')
                return cartStore.cartItems
            }
            // 只返回选中的商品
            const filtered = cartStore.cartItems.filter(item => selectedItemIds.value.includes(item.id))
            console.log('过滤后的商品:', filtered.map(item => ({ id: item.id, name: item.sku.spu_name })))
            return filtered
        })
        
        const totalItems = computed(() => {
            return checkoutItems.value.reduce((sum, item) => sum + item.quantity, 0)
        })
        
        const totalPrice = computed(() => {
            return checkoutItems.value.reduce((sum, item) => sum + parseFloat(item.total_price), 0).toFixed(2)
        })
        
        // 加载地址列表
        const loadAddresses = async () => {
            try {
                const response = await addressAPI.getAddresses(userStore.token)
                addresses.value = response.data
                
                // 默认选中默认地址
                const defaultAddress = addresses.value.find(addr => addr.is_default)
                if (defaultAddress) {
                    selectedAddress.value = defaultAddress
                } else if (addresses.value.length > 0) {
                    selectedAddress.value = addresses.value[0]
                }
            } catch (error) {
                console.error('加载地址失败:', error)
                alert('加载地址失败')
            }
        }
        
        // 保存新地址
        const saveNewAddress = async () => {
            if (!newAddress.value.name || !newAddress.value.phone || 
                !newAddress.value.province || !newAddress.value.city || 
                !newAddress.value.district || !newAddress.value.address) {
                alert('请填写完整的地址信息')
                return
            }
            
            try {
                await addressAPI.createAddress(newAddress.value, userStore.token)
                showAddressForm.value = false
                await loadAddresses()
                alert('地址添加成功')
            } catch (error) {
                console.error('添加地址失败:', error)
                alert(error.response?.data?.error || '添加地址失败')
            }
        }
        
        // 提交订单并跳转到 Stripe 支付
        const submitOrder = async () => {
            if (!selectedAddress.value) {
                alert('请选择收货地址')
                return
            }
            
            if (checkoutItems.value.length === 0) {
                alert('购物车为空')
                return
            }
            
            submitting.value = true
            
            try {
                // 1. 创建订单
                const orderData = {
                    address_id: selectedAddress.value.id,
                    cart_item_ids: checkoutItems.value.map(item => item.id),
                    payment_method: 'stripe',
                    remark: remark.value
                }
                
                console.log('准备创建订单，数据:', orderData)
                console.log('选中的商品:', checkoutItems.value)
                
                const orderResponse = await orderAPI.createOrder(orderData, userStore.token)
                const order = orderResponse.data
                
                console.log('订单创建成功:', order)
                
                // 2. 创建 Stripe Checkout Session
                try {
                    const stripeResponse = await apiClient.post('/shopping/payments/create-checkout-session/', {
                        order_id: order.id,
                        success_url: `${window.location.origin}/order-success?session_id={CHECKOUT_SESSION_ID}`,
                        cancel_url: `${window.location.origin}/myself?tab=orders`
                    })
                    
                    const { sessionId, url, publishableKey } = stripeResponse.data
                    
                    console.log('Stripe Session 创建成功:', { sessionId, url })
                    
                    // 3. 直接跳转到 Stripe Checkout URL（新方法，替代已废弃的 redirectToCheckout）
                    if (url) {
                        window.location.href = url
                    } else {
                        throw new Error('未收到 Stripe Checkout URL')
                    }
                    
                } catch (stripeError) {
                    console.error('Stripe 支付创建失败:', stripeError)
                    console.error('Stripe 错误详情:', stripeError.response?.data)
                    console.error('Stripe 完整错误:', JSON.stringify(stripeError, null, 2))
                    
                    const errorMsg = stripeError.response?.data?.error || stripeError.message || '支付页面加载失败'
                    alert(`${errorMsg}\n\n请在"我的订单"中重新支付`)
                    router.push('/myself?tab=orders')
                }
                
            } catch (error) {
                console.error('创建订单失败:', error)
                console.error('错误详情:', error.response?.data)
                
                // 获取详细错误信息
                let errorMsg = '创建订单失败'
                if (error.response?.data) {
                    const data = error.response.data
                    if (typeof data === 'string') {
                        errorMsg = data
                    } else if (data.error) {
                        errorMsg = data.error
                    } else if (data.cart_item_ids) {
                        errorMsg = `购物车商品错误: ${data.cart_item_ids[0]}`
                    } else if (data.address_id) {
                        errorMsg = `收货地址错误: ${data.address_id[0]}`
                    } else {
                        // 显示所有错误字段
                        errorMsg = JSON.stringify(data, null, 2)
                    }
                }
                
                alert(errorMsg)
            } finally {
                submitting.value = false
            }
        }
        
        onMounted(async () => {
            loading.value = true
            
            // 加载购物车数据
            await cartStore.fetchCartItems()
            
            // 如果购物车为空，返回商品页面
            if (cartStore.cartItems.length === 0) {
                alert('购物车为空，请先添加商品')
                router.push('/merch')
                return
            }
            
            // 检查是否有选中的商品（如果传递了items参数）
            if (selectedItemIds.value.length > 0) {
                // 过滤后的结算商品
                const validItems = cartStore.cartItems.filter(item => selectedItemIds.value.includes(item.id))
                
                if (validItems.length === 0) {
                    alert('选中的商品不存在或已被移除')
                    router.push('/merch')
                    return
                }
            }
            
            // 加载地址列表
            await loadAddresses()
            
            loading.value = false
        })
        
        return {
            loading,
            addresses,
            selectedAddress,
            paymentMethod,
            remark,
            submitting,
            checkoutItems,
            totalItems,
            totalPrice,
            submitOrder,
            showAddressForm,
            newAddress,
            saveNewAddress
        }
    }
}
</script>

<style lang="scss" scoped>
.address-card {
    transition: all 0.3s ease;
    border: 2px solid transparent;
    
    &.is-selected {
        border-color: #00d1af;
    }
    
    &:hover {
        box-shadow: 0 0.5em 1em -0.125em rgba(10, 10, 10, 0.2);
    }
}
</style>
