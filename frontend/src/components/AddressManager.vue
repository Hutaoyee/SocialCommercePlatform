<template>
    <div class="address-manager">
        <!-- 未登录提示 -->
        <div v-if="!userStore.isLoggedIn" class="notification is-warning">
            <p class="has-text-centered">请先登录后再管理收货地址</p>
        </div>
        
        <!-- 地址列表 -->
        <div v-else-if="!showForm" class="addresses-list">
            <div class="level mb-4">
                <div class="level-left">
                    <h3 class="title is-5">我的地址</h3>
                </div>
                <div class="level-right">
                    <button class="button is-primary" @click="openAddressForm()">
                        <span class="icon">
                            <font-awesome-icon icon="fa-solid fa-plus" />
                        </span>
                        <span>添加新地址</span>
                    </button>
                </div>
            </div>

            <div v-if="loading" class="has-text-centered">
                <p>加载中...</p>
            </div>

            <div v-else-if="addresses.length === 0" class="notification">
                <p class="has-text-centered">还没有收货地址，点击"添加新地址"按钮创建</p>
            </div>

            <div v-else class="columns is-multiline">
                <div v-for="address in addresses" :key="address.id" class="column is-half">
                    <div class="box address-item" :class="{ 'is-default': address.is_default }">
                        <div class="level is-mobile mb-2">
                            <div class="level-left">
                                <span class="tag is-success" v-if="address.is_default">默认地址</span>
                            </div>
                            <div class="level-right">
                                <div class="buttons">
                                    <button class="button is-small is-info" @click="openAddressForm(address)">
                                        编辑
                                    </button>
                                    <button class="button is-small is-danger" @click="deleteAddress(address.id)" :disabled="address.is_default">
                                        删除
                                    </button>
                                </div>
                            </div>
                        </div>
                        
                        <p class="has-text-weight-bold">{{ address.name }} {{ address.phone }}</p>
                        <p class="mt-2">{{ address.province }} {{ address.city }} {{ address.district }}</p>
                        <p>{{ address.address }}</p>

                        <button 
                            v-if="!address.is_default" 
                            class="button is-small is-warning mt-3" 
                            @click="setDefault(address.id)">
                            设为默认地址
                        </button>
                    </div>
                </div>
            </div>
        </div>

        <!-- 地址表单 -->
        <div v-else class="address-form">
            <div class="level mb-4">
                <div class="level-left">
                    <h3 class="title is-5">{{ editingAddress ? '编辑地址' : '添加新地址' }}</h3>
                </div>
                <div class="level-right">
                    <button class="button" @click="cancelEdit">取消</button>
                </div>
            </div>

            <div class="box">
                <div class="field">
                    <label class="label">收货人姓名 <span class="has-text-danger">*</span></label>
                    <div class="control">
                        <input class="input" type="text" v-model="formData.name" placeholder="请输入收货人姓名">
                    </div>
                </div>

                <div class="field">
                    <label class="label">联系电话 <span class="has-text-danger">*</span></label>
                    <div class="control">
                        <input class="input" type="tel" v-model="formData.phone" placeholder="请输入手机号">
                    </div>
                </div>

                <div class="columns">
                    <div class="column">
                        <div class="field">
                            <label class="label">省份 <span class="has-text-danger">*</span></label>
                            <div class="control">
                                <input class="input" type="text" v-model="formData.province" placeholder="如：广东省">
                            </div>
                        </div>
                    </div>
                    <div class="column">
                        <div class="field">
                            <label class="label">城市 <span class="has-text-danger">*</span></label>
                            <div class="control">
                                <input class="input" type="text" v-model="formData.city" placeholder="如：深圳市">
                            </div>
                        </div>
                    </div>
                    <div class="column">
                        <div class="field">
                            <label class="label">区县 <span class="has-text-danger">*</span></label>
                            <div class="control">
                                <input class="input" type="text" v-model="formData.district" placeholder="如：南山区">
                            </div>
                        </div>
                    </div>
                </div>

                <div class="field">
                    <label class="label">详细地址 <span class="has-text-danger">*</span></label>
                    <div class="control">
                        <textarea class="textarea" v-model="formData.address" placeholder="请输入详细地址，如街道、门牌号等" rows="3"></textarea>
                    </div>
                </div>

                <div class="field">
                    <div class="control">
                        <label class="checkbox">
                            <input type="checkbox" v-model="formData.is_default">
                            设为默认地址
                        </label>
                    </div>
                </div>

                <div class="field is-grouped">
                    <div class="control">
                        <button class="button is-primary" @click="saveAddress" :class="{ 'is-loading': saving }">
                            保存
                        </button>
                    </div>
                    <div class="control">
                        <button class="button" @click="cancelEdit">取消</button>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { addressAPI } from '@/api/address'
import { useUserStore } from '@/stores/user'

export default {
    name: 'AddressManager',
    setup() {
        const userStore = useUserStore()
        
        const addresses = ref([])
        const loading = ref(false)
        const showForm = ref(false)
        const editingAddress = ref(null)
        const saving = ref(false)
        
        const formData = ref({
            name: '',
            phone: '',
            province: '',
            city: '',
            district: '',
            address: '',
            is_default: false
        })
        
        // 加载地址列表
        const loadAddresses = async () => {
            // 检查用户是否登录
            if (!userStore.isLoggedIn || !userStore.token) {
                console.log('用户未登录，跳过加载地址')
                return
            }
            
            loading.value = true
            try {
                const response = await addressAPI.getAddresses(userStore.token)
                addresses.value = response.data
                console.log('地址加载成功:', addresses.value)
            } catch (error) {
                console.error('加载地址失败:', error)
                console.error('错误详情:', error.response?.data)
                // 只在非认证错误时弹出提示
                if (error.response?.status !== 401) {
                    alert('加载地址失败: ' + (error.response?.data?.detail || error.message))
                }
            } finally {
                loading.value = false
            }
        }
        
        // 打开地址表单
        const openAddressForm = (address = null) => {
            if (address) {
                editingAddress.value = address
                formData.value = { ...address }
            } else {
                editingAddress.value = null
                formData.value = {
                    name: '',
                    phone: '',
                    province: '',
                    city: '',
                    district: '',
                    address: '',
                    is_default: false
                }
            }
            showForm.value = true
        }
        
        // 取消编辑
        const cancelEdit = () => {
            showForm.value = false
            editingAddress.value = null
        }
        
        // 保存地址
        const saveAddress = async () => {
            // 验证表单
            if (!formData.value.name || !formData.value.phone || 
                !formData.value.province || !formData.value.city || 
                !formData.value.district || !formData.value.address) {
                alert('请填写完整的地址信息')
                return
            }
            
            // 验证手机号
            const phoneRegex = /^1[3-9]\d{9}$/
            if (!phoneRegex.test(formData.value.phone)) {
                alert('请输入正确的手机号')
                return
            }
            
            saving.value = true
            try {
                if (editingAddress.value) {
                    // 更新地址
                    console.log('更新地址:', editingAddress.value.id, formData.value)
                    await addressAPI.updateAddress(editingAddress.value.id, formData.value, userStore.token)
                    alert('地址更新成功')
                } else {
                    // 创建地址
                    console.log('创建地址:', formData.value)
                    const response = await addressAPI.createAddress(formData.value, userStore.token)
                    console.log('创建成功:', response.data)
                    alert('地址添加成功')
                }
                showForm.value = false
                await loadAddresses()
            } catch (error) {
                console.error('保存地址失败:', error)
                console.error('错误详情:', error.response?.data)
                const errorMsg = error.response?.data?.error || 
                               error.response?.data?.phone?.[0] || 
                               error.response?.data?.detail ||
                               error.message ||
                               '保存地址失败'
                alert('保存失败: ' + errorMsg)
            } finally {
                saving.value = false
            }
        }
        
        // 删除地址
        const deleteAddress = async (id) => {
            if (!confirm('确定要删除这个地址吗？')) return
            
            try {
                await addressAPI.deleteAddress(id, userStore.token)
                alert('地址删除成功')
                loadAddresses()
            } catch (error) {
                console.error('删除地址失败:', error)
                alert('删除地址失败')
            }
        }
        
        // 设置默认地址
        const setDefault = async (id) => {
            try {
                await addressAPI.setDefaultAddress(id, userStore.token)
                loadAddresses()
            } catch (error) {
                console.error('设置默认地址失败:', error)
                alert('设置默认地址失败')
            }
        }
        
        onMounted(() => {
            loadAddresses()
        })
        
        return {
            userStore,
            addresses,
            loading,
            showForm,
            editingAddress,
            saving,
            formData,
            openAddressForm,
            cancelEdit,
            saveAddress,
            deleteAddress,
            setDefault
        }
    }
}
</script>

<style lang="scss" scoped>
.address-item {
    height: 100%;
    transition: all 0.3s ease;
    
    &.is-default {
        border: 2px solid #00d1af;
    }
    
    &:hover {
        box-shadow: 0 0.5em 1em -0.125em rgba(10, 10, 10, 0.2);
    }
}

/* 地址表单输入框聚焦样式 */
.address-form .input:focus,
.address-form .textarea:focus {
    border-color: hsl(171, 100%, 41%);
    box-shadow: 0 0 0 0.125em rgba(0, 209, 175, 0.25);
}
</style>
