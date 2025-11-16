<template>
    <div class="favorite-container">
        <div class="tabs is-toggle is-toggle-rounded is-fullwidth">
            <ul>
                <li :class="{ 'is-active': activeTab === 'products' }">
                    <a @click="activeTab = 'products'">
                        <span>商品</span>
                    </a>
                </li>

                <li :class="{ 'is-active': activeTab === 'posts' }">
                    <a @click="activeTab = 'posts'">
                        <span>帖子</span>
                    </a>
                </li>
            </ul>
        </div>

        <!-- 商品收藏列表 -->
        <div v-if="activeTab === 'products'" class="favorites-content">
            <div v-if="loadingProducts" class="has-text-centered py-6">
                <i class="fas fa-spinner fa-spin fa-2x"></i>
            </div>
            <div v-else-if="!productFavorites || productFavorites.length === 0" class="empty-state notification is-info is-light has-text-centered m-6">
                <p class="is-size-5">
                    <span class="icon is-large">
                        <font-awesome-icon icon="fa-solid fa-shirt" />
                    </span>
                </p>
                <p class="mt-2">暂无收藏的商品</p>
            </div>
            <div v-else class="columns is-multiline">
                <div 
                    v-for="favorite in productFavorites" 
                    :key="favorite.id"
                    class="column is-one-quarter"
                >
                    <div class="card product-card" v-if="favorite.product">
                        <div class="card-image">
                            <figure class="image is-square">
                                <img 
                                    :src="favorite.product.image || '/placeholder.png'" 
                                    :alt="favorite.product.name || '商品'"
                                >
                            </figure>
                        </div>
                        <div class="card-content">
                            <p class="title is-6">{{ favorite.product.name || '未知商品' }}</p>
                            <p class="subtitle is-7 has-text-grey">{{ favorite.product.description || '' }}</p>
                        </div>
                        <footer class="card-footer">
                            <a 
                                @click="openSKUDialog(favorite.product)" 
                                class="card-footer-item has-text-success"
                            >
                                <span class="icon">
                                    <font-awesome-icon icon="fa-solid fa-cart-plus" />
                                </span>
                            </a>
                            <a 
                                @click="removeProductFavorite(favorite.id)" 
                                class="card-footer-item has-text-danger"
                            >
                                <span class="icon">
                                    <font-awesome-icon icon="fa-solid fa-trash" />
                                </span>
                            </a>
                        </footer>
                    </div>
                </div>
            </div>
        </div>

        <!-- 帖子收藏列表 -->
        <div v-if="activeTab === 'posts'" class="favorites-content">
            <div v-if="loadingPosts" class="has-text-centered py-6">
                <i class="fas fa-spinner fa-spin fa-2x"></i>
            </div>
            <div v-else-if="!postFavorites || postFavorites.length === 0" class="empty-state notification is-info is-light has-text-centered m-6">
                <p class="is-size-5">
                    <span class="icon is-large">
                        <font-awesome-icon icon="fa-solid fa-blog" />
                    </span>
                </p>
                <p class="mt-2">暂无收藏的帖子</p>
            </div>
            <div v-else>
                <PostList 
                    :posts="paginatedPosts" 
                    :current-page="currentPage"
                    :total-pages="totalPages"
                    @page-change="handlePageChange"
                    @edit="handleEditPost"
                    @delete="handleDeletePost"
                    @reply="handleReplyPost"
                    @delete-reply="handleDeleteReply"
                />
            </div>
        </div>
    </div>

    <!-- SKU选择对话框 -->
    <SKUSelectDialog
        :show="showSKUDialog"
        :product="selectedProduct"
        @close="closeSKUDialog"
        @success="handleAddToCartSuccess"
    />
</template>

<script setup>
import { ref, onMounted, computed, watch, onActivated } from 'vue'
import { useRouter } from 'vue-router'
import { usePostsStore } from '../stores/posts'
import { useUserStore } from '../stores/user'
import { useProductsStore } from '../stores/products'
import { favoriteAPI } from '../api/favorite'
import productFavoriteAPI from '../api/productFavorite'
import PostList from './PostList.vue'
import SKUSelectDialog from './SKUSelectDialog.vue'

const router = useRouter()
const postsStore = usePostsStore()
const userStore = useUserStore()
const productsStore = useProductsStore()

const activeTab = ref('products')
const loadingProducts = ref(false)
const loadingPosts = ref(false)
const productFavorites = ref([])
const postFavorites = ref([])
const favoritePosts = ref([])

// SKU选择对话框
const showSKUDialog = ref(false)
const selectedProduct = ref(null)

// 分页相关状态
const currentPage = ref(1)
const postsPerPage = 10

// 计算属性：总页数
const totalPages = computed(() => {
    const total = Math.ceil(favoritePosts.value.length / postsPerPage)
    console.log('帖子收藏 - 总页数:', total, '总帖子数:', favoritePosts.value.length)
    return total
})

// 计算属性：当前页的帖子
const paginatedPosts = computed(() => {
    const start = (currentPage.value - 1) * postsPerPage
    const end = start + postsPerPage
    const posts = favoritePosts.value.slice(start, end)
    console.log('帖子收藏 - 当前页:', currentPage.value, '显示帖子数:', posts.length)
    return posts
})

// 处理分页变化
const handlePageChange = (page) => {
    console.log('帖子收藏 - 切换到页码:', page)
    currentPage.value = page
    // 滚动到顶部
    window.scrollTo({ top: 0, behavior: 'smooth' })
}

// 获取商品收藏列表
const fetchProductFavorites = async () => {
    loadingProducts.value = true
    try {
        const response = await productFavoriteAPI.getUserFavorites()
        console.log('商品收藏API响应:', response)
        
        // 处理分页数据格式
        if (response.data && typeof response.data === 'object') {
            if (Array.isArray(response.data)) {
                productFavorites.value = response.data
            } else if (response.data.results && Array.isArray(response.data.results)) {
                productFavorites.value = response.data.results
            } else {
                productFavorites.value = []
            }
        } else {
            productFavorites.value = []
        }
        
        console.log('加载商品收藏成功，数量:', productFavorites.value.length)
    } catch (error) {
        console.error('获取商品收藏失败:', error)
        productFavorites.value = []
    } finally {
        loadingProducts.value = false
    }
}

// 获取帖子收藏列表
const fetchPostFavorites = async () => {
    loadingPosts.value = true
    try {
        const response = await favoriteAPI.getUserFavorites()
        console.log('帖子收藏API响应:', response)
        
        // 处理分页数据格式
        let favoritesList = []
        if (response.data && typeof response.data === 'object') {
            if (Array.isArray(response.data)) {
                favoritesList = response.data
            } else if (response.data.results && Array.isArray(response.data.results)) {
                favoritesList = response.data.results
            }
        }
        
        postFavorites.value = favoritesList
        // 提取帖子对象并过滤有效数据
        favoritePosts.value = favoritesList
            .filter(fav => fav && fav.post && fav.post.id)
            .map(fav => ({
                ...fav.post,
                is_favorited: true,
                favoriteId: fav.id  // 保存收藏ID，用于删除
            }))
        
        // 重置到第一页
        currentPage.value = 1
        
        console.log('加载帖子收藏成功，数量:', favoritePosts.value.length)
    } catch (error) {
        console.error('获取帖子收藏失败:', error)
        postFavorites.value = []
        favoritePosts.value = []
    } finally {
        loadingPosts.value = false
    }
}

// 移除商品收藏
const removeProductFavorite = async (favoriteId) => {
    if (!confirm('确定要取消收藏这个商品吗？')) return
    
    try {
        await productFavoriteAPI.removeFavorite(favoriteId)
        productFavorites.value = productFavorites.value.filter(f => f.id !== favoriteId)
    } catch (error) {
        console.error('移除商品收藏失败:', error)
        alert('操作失败，请重试')
    }
}

// 查看商品详情
const viewProduct = (productId) => {
    router.push(`/products/${productId}`)
}

// 打开SKU选择对话框
const openSKUDialog = (product) => {
    selectedProduct.value = product
    showSKUDialog.value = true
}

// 关闭SKU选择对话框
const closeSKUDialog = () => {
    showSKUDialog.value = false
    selectedProduct.value = null
}

// 处理加入购物车成功
const handleAddToCartSuccess = () => {
    closeSKUDialog()
    // 这里可以显示成功提示
    console.log('商品已成功加入购物车')
}

// 处理编辑帖子
const handleEditPost = async (post, data) => {
    try {
        await postsStore.updatePost(post.id, data)
        alert('帖子更新成功')
        // 刷新收藏列表
        await fetchPostFavorites()
    } catch (error) {
        alert('操作失败：' + error.message)
    }
}

// 删除帖子
const handleDeletePost = async (postId) => {
    if (confirm('确定删除此帖子？')) {
        try {
            await postsStore.deletePost(postId)
            alert('帖子删除成功')
            
            // 刷新收藏列表
            await fetchPostFavorites()
            
            // 如果当前页没有帖子了且不是第一页，回到上一页
            if (paginatedPosts.value.length === 0 && currentPage.value > 1) {
                currentPage.value--
            }
        } catch (error) {
            alert('删除失败：' + error.message)
        }
    }
}

// 处理回复帖子
const handleReplyPost = async ({ postId, content, parentId }) => {
    try {
        await postsStore.createReply(postId, content, parentId)
        // 回复成功，刷新收藏列表以更新回复数
        await fetchPostFavorites()
    } catch (error) {
        alert('回复失败：' + error.message)
        throw error
    }
}

// 处理删除回复
const handleDeleteReply = async (replyId) => {
    try {
        await postsStore.deleteReply(replyId)
        // 删除成功，刷新收藏列表以更新回复数
        await fetchPostFavorites()
    } catch (error) {
        alert('删除失败：' + error.message)
        throw error
    }
}

onMounted(() => {
    fetchProductFavorites()
    fetchPostFavorites()
})

// 监听组件被激活（从缓存中恢复）
onActivated(() => {
    // 刷新当前激活的 tab 数据
    if (activeTab.value === 'products') {
        fetchProductFavorites()
    } else if (activeTab.value === 'posts') {
        fetchPostFavorites()
    }
})

// 监听 tab 切换，重新加载数据
watch(activeTab, (newTab) => {
    if (newTab === 'products') {
        fetchProductFavorites()
    } else if (newTab === 'posts') {
        fetchPostFavorites()
    }
})

// 暴露刷新方法给父组件
defineExpose({
    refresh: () => {
        fetchProductFavorites()
        fetchPostFavorites()
    }
})
</script>

<style lang="scss" scoped>
.favorite-container {
    padding: 1rem;
}

.tabs ul li.is-active a {
    background-color: rgba(0, 209, 175, 1);
    border: none;
    color: white;
}

.favorites-content {
    margin-top: 2rem;
}

.empty-state {
    text-align: center;
    padding: 4rem 2rem;
}

.product-card {
    transition: transform 0.2s, box-shadow 0.2s;
    
    &:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
    }
    
    .card-image img {
        object-fit: cover;
        width: 100%;
        height: 100%;
    }
    
    .card-content {
        padding: 1rem;
        
        .title {
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            margin-bottom: 0.5rem;
        }
    }
}
</style>