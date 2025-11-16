<template>
    <div class="container mt-6 pr-1">
        <!-- 搜索和分类过滤 -->
        <div class="box left-box">
            <!-- 搜索框 -->
            <div class="field has-addons mb-4">
                <div class="control is-expanded">
                    <input class="input" type="text" v-model="store.searchQuery" placeholder="搜索商品..." @keyup.enter="store.searchProducts">
                </div>
            </div>
            
            <!-- 分类过滤 -->
            <div class="category-filter">
                <h3 class="title is-6 mb-3">商品分类</h3>
                <div class="menu">
                    <ul class="menu-list">
                        <li>
                            <a :class="{ 'is-active': selectedCategory === null }" 
                               @click="filterByCategory(null)"
                               class="category-item level-all">
                                全部商品
                            </a>
                        </li>
                        <li v-for="cat in categories" :key="cat.id">
                            <a :class="{ 'is-active': selectedCategory === cat.id }" 
                               @click="filterByCategory(cat.id)"
                               :class-name="`category-item level-${cat.level}`"
                               :style="{ 
                                   paddingLeft: (cat.level * 1.2 + 0.75) + 'rem',
                                   fontSize: cat.level === 0 ? '0.95rem' : '0.875rem',
                                   fontWeight: cat.level === 0 ? '600' : '400'
                               }">
                                {{ cat.name }}
                            </a>
                        </li>
                    </ul>
                </div>
            </div>
        </div>
    </div>

    <div class="container mt-6 products-container">
        <div class="box m-1 spu-box" v-for="product in store.products" :key="product.id">
            <figure class="image spu-image">
                <img :src="product.image" :alt="product.name">
            </figure>
            
            <p class="title is-5 mb-2 mt-2">{{ product.name }}</p>
            
            <div class="is-flex is-align-items-flex-end is-justify-content-space-between">
                <button class="button is-success mr-2" @click="showSKUModal(product)">添加到购物车</button>

                <div class="is-flex is-align-items-center">
                    <!-- 评论按钮 -->
                    <span class="icon fa-lg has-text-primary mr-2" @click="showReviewsModal(product)" style="cursor: pointer;" :title="`${product.review_count} 条评论`">
                        <font-awesome-icon icon="fa-regular fa-comment" />
                    </span>
                    
                    <!-- 收藏按钮 -->
                    <span class="icon fa-lg"
                    :class="product.is_favorited ? 'has-text-warning' : 'has-text-primary'"
                    @click="store.toggleFavorite(product)"
                    style="cursor: pointer;">
                        <font-awesome-icon :icon="product.is_favorited ? 'fa-solid fa-star' : 'fa-regular fa-star'" />
                    </span>
                </div>
            </div>
        </div>
    </div>

    <!-- 分页 -->
    <nav class="pagination is-centered is-rounded mt-6 mb-6" role="navigation" aria-label="pagination" v-if="store.totalPages > 1">
        <a 
            class="pagination-previous" 
            :class="{ 'is-disabled': store.currentPage <= 1 }"
            @click.prevent="store.currentPage > 1 && changePage(store.currentPage - 1)">
            上一页
        </a>
        <a 
            class="pagination-next"
            :class="{ 'is-disabled': store.currentPage >= store.totalPages }"
            @click.prevent="store.currentPage < store.totalPages && changePage(store.currentPage + 1)">
            下一页
        </a>
        
        <ul class="pagination-list">
            <li v-for="(page, index) in visiblePages" :key="index">
                <span 
                    v-if="page === '...'" 
                    class="pagination-ellipsis">
                    &hellip;
                </span>
                <a
                    v-else
                    class="pagination-link"
                    :class="{ 'is-current': page === store.currentPage }"
                    :aria-label="`Goto page ${page}`"
                    :aria-current="page === store.currentPage ? 'page' : undefined"
                    @click.prevent="changePage(page)">
                    {{ page }}
                </a>
            </li>
        </ul>
    </nav>

    <!-- SKU选择模态框 -->
    <div class="modal modal-sku" :class="{ 'is-active': skuModal.show }">
        <div class="modal-background" @click="closeSKUModal"></div>
        <div class="modal-card">
            <header class="modal-card-head">
                <p class="modal-card-title">选择商品规格</p>
                <button class="delete" aria-label="close" @click="closeSKUModal"></button>
            </header>
            <section class="modal-card-body">
                <div v-if="skuModal.product">
                    <!-- 商品图片 - 根据选中的SKU显示 -->
                    <div class="mb-4">
                        <figure class="image is-4by3">
                            <img :src="selectedSKU ? selectedSKU.image : skuModal.product.image" 
                                 :alt="skuModal.product.name" 
                                 style="object-fit: cover;">
                        </figure>
                    </div>
                    
                    <h2 class="title is-5">{{ skuModal.product.name }}</h2>
                    
                    <!-- 属性选择 -->
                    <div v-for="attr in skuModal.attributes" :key="attr.id" class="mb-4">
                        <label class="label">{{ attr.name }}</label>
                        <div class="buttons">
                            <button 
                                v-for="value in attr.values" 
                                :key="value.id"
                                class="button is-rounded"
                                :class="{ 'is-primary is-selected': skuModal.selectedAttrs[attr.id] === value.id }"
                                @click="selectAttribute(attr.id, value.id)">
                                {{ value.value }}
                            </button>
                        </div>
                    </div>
                    
                    <!-- 选中的SKU信息 -->
                    <div v-if="selectedSKU" class="box">
                        <p><strong>价格：</strong>¥{{ selectedSKU.price }}</p>
                        <p><strong>库存：</strong>{{ selectedSKU.stock }}</p>
                        
                        <div class="field is-horizontal mt-4">
                            <div class="field-label is-normal">
                                <label class="label">数量</label>
                            </div>
                            <div class="field-body">
                                <div class="field has-addons">
                                    <p class="control">
                                        <button class="button" @click="decreaseQuantity">-</button>
                                    </p>
                                    <p class="control">
                                        <input class="input quantity-input" type="number" v-model.number="skuModal.quantity" min="1" :max="selectedSKU.stock" style="width: 80px; text-align: center;">
                                    </p>
                                    <p class="control">
                                        <button class="button" @click="increaseQuantity">+</button>
                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div v-else class="notification is-warning">
                        请选择完整的商品规格
                    </div>
                </div>
            </section>
            <footer class="modal-card-foot">
                <button class="button is-success mr-3" @click="addToCart" :disabled="!selectedSKU">确认添加</button>
                <button class="button" @click="closeSKUModal">取消</button>
            </footer>
        </div>
    </div>

    <!-- 评论模态框 -->
    <div class="modal modal-reviews" :class="{ 'is-active': reviewsModal.show }">
        <div class="modal-background" @click="closeReviewsModal"></div>
        <div class="modal-card" style="width: 90%; max-width: 700px;">
            <header class="modal-card-head">
                <p class="modal-card-title">商品评论</p>
            </header>

            <section class="modal-card-body">
                <div v-if="reviewsModal.product">
                    <h2 class="title is-5 mb-4">{{ reviewsModal.product.name }}</h2>
                    
                    <div v-if="reviewsModal.loading" class="has-text-centered">
                        <p>加载中...</p>
                    </div>
                    
                    <div v-else-if="reviewsModal.reviews.length === 0" class="notification">
                        <p class="has-text-centered">暂无评论</p>
                    </div>
                    
                    <div v-else>
                        <div class="box mb-3" v-for="review in reviewsModal.reviews" :key="review.id">
                            <div class="media">
                                <div class="media-left">
                                    <figure class="image is-48x48">
                                        <img class="is-rounded" :src="review.user_avatar || defaultAvatar" :alt="review.username">
                                    </figure>
                                </div>
                                <div class="media-content">
                                    <p class="title is-6">{{ review.username }}</p>
                                    <p class="subtitle is-7 has-text-grey">
                                        {{ new Date(review.created_at).toLocaleDateString() }}
                                    </p>
                                    <p class="mb-3">{{ review.content }}</p>
                                    
                                    <!-- 评价图片 -->
                                    <div v-if="review.images && review.images.length > 0" class="review-images">
                                        <div class="columns is-mobile is-multiline">
                                            <div v-for="(image, idx) in review.images" :key="idx" class="column is-one-quarter-tablet is-one-third-mobile">
                                                <figure class="image is-square">
                                                    <img :src="image.url || image.image || image" :alt="`评价图片${idx + 1}`" style="object-fit: cover; cursor: pointer;" @click="previewImage(image.url || image.image || image)">
                                                </figure>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>
            <footer class="modal-card-foot">
                <button class="button" @click="closeReviewsModal">关闭</button>
            </footer>
        </div>
    </div>
</template>

<script>
    import { onMounted, onUnmounted, ref, computed } from 'vue'
    import { useProductsStore } from '@/stores/products'
    import { useCartStore } from '@/stores/cart'
    import { shopping, category } from '@/api/shopping'
    import defaultAvatar from '@/assets/defaultAvatar.png'

    export default {
        setup(){
            const store = useProductsStore()
            const cartStore = useCartStore()
            
            // 分类相关
            const categories = ref([])
            const selectedCategory = ref(null)
            
            // SKU选择模态框状态
            const skuModal = ref({
                show: false,
                product: null,
                attributes: [],
                skus: [],
                selectedAttrs: {},
                quantity: 1
            })
            
            // 评论模态框状态
            const reviewsModal = ref({
                show: false,
                product: null,
                reviews: [],
                loading: false
            })
            
            // 计算选中的SKU
            const selectedSKU = computed(() => {
                if (!skuModal.value.skus || skuModal.value.skus.length === 0) {
                    return null
                }
                
                // 检查是否所有属性都已选择
                const allSelected = skuModal.value.attributes.every(
                    attr => skuModal.value.selectedAttrs[attr.id] !== undefined
                )
                
                if (!allSelected) {
                    return null
                }
                
                // 查找匹配的SKU
                return skuModal.value.skus.find(sku => {
                    return Object.keys(skuModal.value.selectedAttrs).every(
                        attrId => sku.attributes[attrId] === skuModal.value.selectedAttrs[attrId]
                    )
                })
            })
            
            // 计算可见的页码
            const visiblePages = computed(() => {
                const pages = []
                const current = store.currentPage
                const total = store.totalPages
                
                if (total <= 7) {
                    for (let i = 1; i <= total; i++) {
                        pages.push(i)
                    }
                } else {
                    if (current <= 4) {
                        for (let i = 1; i <= 5; i++) pages.push(i)
                        pages.push('...')
                        pages.push(total)
                    } else if (current >= total - 3) {
                        pages.push(1)
                        pages.push('...')
                        for (let i = total - 4; i <= total; i++) pages.push(i)
                    } else {
                        pages.push(1)
                        pages.push('...')
                        for (let i = current - 1; i <= current + 1; i++) pages.push(i)
                        pages.push('...')
                        pages.push(total)
                    }
                }
                
                return pages
            })
            
            // 切换页面
            const changePage = (page) => {
                if (page >= 1 && page <= store.totalPages) {
                    store.fetchProducts(page, store.searchQuery)
                    window.scrollTo(0, 0)
                }
            }
            
            // 显示SKU选择模态框
            const showSKUModal = async (product) => {
                try {
                    const data = await store.getSPUSKUs(product.id)
                    skuModal.value = {
                        show: true,
                        product: product,
                        attributes: data.attributes,
                        skus: data.skus,
                        selectedAttrs: {},
                        quantity: 1
                    }
                } catch (error) {
                    alert('获取商品信息失败')
                }
            }
            
            // 关闭SKU选择模态框
            const closeSKUModal = () => {
                skuModal.value.show = false
            }
            
            // 选择属性
            const selectAttribute = (attrId, valueId) => {
                skuModal.value.selectedAttrs[attrId] = valueId
            }
            
            // 增加数量
            const increaseQuantity = () => {
                if (selectedSKU.value && skuModal.value.quantity < selectedSKU.value.stock) {
                    skuModal.value.quantity++
                }
            }
            
            // 减少数量
            const decreaseQuantity = () => {
                if (skuModal.value.quantity > 1) {
                    skuModal.value.quantity--
                }
            }
            
            // 添加到购物车
            const addToCart = async () => {
                if (!selectedSKU.value) {
                    return
                }
                
                const success = await cartStore.addItem(selectedSKU.value.sku_code, skuModal.value.quantity)
                if (success) {
                    closeSKUModal()
                    alert('已添加到购物车！')
                }
            }
            
            // 显示评论模态框
            const showReviewsModal = async (product) => {
                reviewsModal.value = {
                    show: true,
                    product: product,
                    reviews: [],
                    loading: true
                }
                
                try {
                    const response = await shopping.getSPUReviews(product.id)
                    reviewsModal.value.reviews = response.data
                } catch (error) {
                    console.error('获取评论失败:', error)
                    alert('获取评论失败')
                } finally {
                    reviewsModal.value.loading = false
                }
            }
            
            // 关闭评论模态框
            const closeReviewsModal = () => {
                reviewsModal.value.show = false
            }
            
            // 预览图片
            const previewImage = (imageUrl) => {
                window.open(imageUrl, '_blank')
            }
            
            // 获取分类列表
            const fetchCategories = async () => {
                try {
                    const response = await category.getCategories()
                    // 现在应该直接返回数组了（禁用分页后）
                    categories.value = Array.isArray(response.data) 
                        ? response.data 
                        : (response.data.results || [])
                } catch (error) {
                    console.error('获取分类失败:', error)
                    categories.value = []
                }
            }
            
            // 按分类过滤商品
            const filterByCategory = (categoryId) => {
                selectedCategory.value = categoryId
                store.fetchProducts(1, store.searchQuery, categoryId)
            }

            // 组件挂载时添加样式类并获取数据
            onMounted(() => {
                document.body.classList.add('merch-page-active')
                document.getElementById('app')?.classList.add('merch-page-active')
                fetchCategories()
                store.fetchProducts()
            })

            // 组件卸载时移除样式类
            onUnmounted(() => {
                document.body.classList.remove('merch-page-active')
                document.getElementById('app')?.classList.remove('merch-page-active')
            })

            return {
                store,
                cartStore,
                categories,
                selectedCategory,
                skuModal,
                reviewsModal,
                selectedSKU,
                visiblePages,
                defaultAvatar,
                changePage,
                filterByCategory,
                showSKUModal,
                closeSKUModal,
                selectAttribute,
                increaseQuantity,
                decreaseQuantity,
                addToCart,
                showReviewsModal,
                closeReviewsModal,
                previewImage
            }
        },
    }
</script>

<style>
    body.merch-page-active{
        align-items: start;
        /* justify-content: start; */
    }

    #app.merch-page-active{
        grid-template-columns: minmax(10vw, 1fr) minmax(70vw, 4.5fr);
    }
</style>

<style lang="scss" scoped>
.products-container {
    display: flex;
    flex-wrap: wrap;
    align-content: flex-start;
    align-items: flex-start;
}

.left-box {
    min-height: 82vh;
    max-height: 82vh;
    padding: 1.5rem;
    display: flex;
    flex-direction: column;
    
    .field {
        flex-shrink: 0;
    }
    
    .category-filter {
        flex: 1;
        overflow-y: auto;
        margin-top: 1rem;
        padding-right: 0.5rem;
        
        // 自定义滚动条
        &::-webkit-scrollbar {
            width: 6px;
        }
        
        &::-webkit-scrollbar-thumb {
            background: hsl(171, 100%, 41%);
            border-radius: 3px;
            
            &:hover {
                background: hsl(171, 100%, 35%);
            }
        }
        
        .menu-list {
            li {
                margin-bottom: 2px;
            }
            
            a {
                border-radius: 4px;
                transition: all 0.2s ease;
                padding-top: 0.5rem;
                padding-bottom: 0.5rem;
                color: hsl(0, 0%, 29%);
                
                &:hover {

                    color: hsl(171, 100%, 41%);
                    transform: translateX(3px);
                }
                
                &.is-active {
                    background-color: hsl(171, 100%, 41%);
                    color: white;
                    font-weight: 600;
                }
                
                // 顶级分类样式
                &.level-all {
                    font-weight: 600;
                    font-size: 0.95rem;
                    border-bottom: 1px solid rgba(0, 209, 175, 1);
                    border-radius: 0;
                    margin-bottom: 0.5rem;
                }
            }
        }
    }
}

.spu-box{
    width: 24%;
    height: fit-content;  /* 根据内容自适应高度 */
    align-self: flex-start;  /* 防止被拉伸 */

    .spu-image{
        width: 100%;
    }
}

/* 选中的属性按钮样式增强 */
.button.is-selected {
    font-weight: bold;
    box-shadow: 0 0 0 2px hsl(171, 100%, 41%);
}

/* 隐藏number input的增减按钮 */
.quantity-input::-webkit-outer-spin-button,
.quantity-input::-webkit-inner-spin-button {
    -webkit-appearance: none;
    margin: 0;
}

.quantity-input[type=number] {
    -moz-appearance: textfield;
    appearance: textfield;
}

.modal-sku {

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
}

.modal-reviews {

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
}

/* 评价图片样式 */
.review-images {
    margin-top: 0.75rem;
    
    .image.is-square {
        border-radius: 8px;
        overflow: hidden;
        border: 1px solid hsl(0, 0%, 21%);
        transition: transform 0.2s;
        
        &:hover {
            transform: scale(1.05);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
        }
    }
}

.pagination {

    grid-column: 1 / -1;
}

/* 搜索框聚焦样式 */
.left-box .input:focus {
    border-color: hsl(171, 100%, 41%);
    box-shadow: 0 0 0 0.125em rgba(0, 209, 175, 0.25);
}

/* 分页样式 */
.pagination-link.is-current {
    background-color: rgba(0, 209, 175, 1) !important;
    border-color: rgba(0, 209, 175, 1) !important;
    color: rgb(0, 0, 0) !important;
}

.pagination-previous.is-disabled,
.pagination-next.is-disabled {
    cursor: not-allowed !important;
    opacity: 0.5;
    pointer-events: none;
}
</style>