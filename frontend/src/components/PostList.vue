<template>
    <div class="posts-container">
        <!-- 加载中状态 -->
        <div v-if="isLoading" class="has-text-centered m-6">
            <progress class="progress is-small is-primary" max="100">15%</progress>
        </div>

        <!-- 暂无帖子提示 -->
        <div v-else-if="!posts || posts.length === 0" class="notification is-info is-light has-text-centered m-6">
            <p class="is-size-5">
                <span class="icon is-large">
                    <font-awesome-icon icon="fa-solid fa-blog" />
                </span>
            </p>
            <p class="mt-2">暂无帖子</p>
        </div>

        <article class="media mt-5 ml-3 box" v-for="post in posts" :key="post.id" v-else>
            <figure class="media-left">
                <p class="image is-64x64 is-square">
                    <img class="is-rounded" :src="post.author.avatar" />
                </p>
            </figure>

            <div class="media-content">
                <div class="content">
                    <div>
                        <strong class="has-text-info">{{ post.author?.name || '用户' }}</strong>
                        <small> 编辑于 {{ post.updated_at }}</small>
                        
                        <div class="mt-2">
                            <strong class="is-size-4">{{ post.title }}</strong>
                            <p>{{ post.content }}</p>
                        </div>
                    </div>
                </div>
                
                <div class="post-images mt-3" v-if="post.images && post.images.length">
                    <div class="post-images-container">
                        <figure class="image post-image" v-for="image in post.images" :key="image.id">
                            <img :src="image.file || image.url" alt="Post image" />
                        </figure>
                    </div>
                </div>

                <div v-if="post.products && post.products.length">
                    <span 
                        class="tag is-warning m-1 product-tag" 
                        v-for="product in post.products" 
                        :key="product.id"
                        @click="openProductSKU(product.id)"
                        style="cursor: pointer;"
                        title="点击加入购物车">
                        <span class="icon is-small">
                            <font-awesome-icon icon="fa-solid fa-cart-shopping" />
                        </span>
                        <span>{{ product.name }}</span>
                    </span>
                </div>

                <nav class="level is-mobile mt-2">
                    <div class="level-left">
                        <a class="level-item">
                            <span 
                                class="icon"
                                :class="post.is_favorited ? 'has-text-warning' : 'has-text-success'"
                                @click="handleToggleFavorite(post)"
                                style="cursor: pointer;">
                                <font-awesome-icon 
                                    :icon="post.is_favorited ? 'fa-solid fa-star' : 'fa-regular fa-star'" 
                                />
                            </span>

                            <span class="icon has-text-success" @click="openReplyModal(post)">
                                <font-awesome-icon icon="fa-regular fa-comment-dots" />
                            </span>

                            <span v-if="canEdit(post)"
                                class="icon has-text-warning"
                                @click="handleEdit(post)">
                                <font-awesome-icon icon="fa-regular fa-pen-to-square" />
                            </span>

                            <span v-if="canEdit(post)"
                                class="icon has-text-danger"
                                @click="handleDelete(post.id)">
                                <font-awesome-icon icon="fa-regular fa-trash-can" />
                            </span>
                        </a>
                    </div>
                </nav>
            </div>
        </article>

        <!-- 分页组件 -->
        <nav class="pagination is-centered is-rounded m-3" role="navigation" aria-label="pagination" v-if="totalPages > 1">
            <a 
                class="pagination-previous" 
                :class="{ 'is-disabled': currentPage <= 1 }"
                @click.prevent="currentPage > 1 && handlePageChange(currentPage - 1)">
                上一页
            </a>
            <a 
                class="pagination-next"
                :class="{ 'is-disabled': currentPage >= totalPages }"
                @click.prevent="currentPage < totalPages && handlePageChange(currentPage + 1)">
                下一页
            </a>
            
            <ul class="pagination-list">
                <li v-for="(page, index) in getPageNumbers()" :key="index">
                    <span 
                        v-if="page === '...'" 
                        class="pagination-ellipsis">
                        &hellip;
                    </span>
                    <a
                        v-else
                        class="pagination-link"
                        :class="{ 'is-current': page === currentPage }"
                        :aria-label="`Goto page ${page}`"
                        :aria-current="page === currentPage ? 'page' : undefined"
                        @click.prevent="handlePageChange(page)">
                        {{ page }}
                    </a>
                </li>
            </ul>
        </nav>

        <!-- 帖子编辑/创建模态框 -->
        <div class="modal" :class="{ 'is-active': isModalActive }">
            <div class="modal-background"></div>
            <div class="modal-card">
                <header class="modal-card-head">
                    <p class="modal-card-title">{{ editingPost ? '编辑帖子' : '发布帖子' }}</p>
                </header>

                <section class="modal-card-body insert-modal">
                    <form @submit.prevent="handleSubmitModal">
                        <div class="field">
                            <label class="label">标题</label>
                            <div class="control">
                                <input class="input" type="text" v-model="formData.title" required>
                            </div>
                        </div>

                        <div class="field">
                            <label class="label">内容</label>
                            <div class="control">
                                <textarea class="textarea" v-model="formData.content" required></textarea>
                            </div>
                        </div>
                        
                        <div class="field">
                            <div class="file is-primary">
                                <label class="file-label">
                                    <input 
                                        class="file-input" 
                                        type="file" 
                                        multiple 
                                        accept="image/*" 
                                        @change="handleImageUpload"
                                        ref="fileInput"
                                    />

                                    <span class="file-cta">
                                        <span class="file-icon">
                                            <font-awesome-icon icon="fa-solid fa-upload" />
                                        </span>
                                        <span class="file-label"> 上传图片… </span>
                                    </span>
                                </label>
                            </div>
                            
                            <!-- 预览已上传的图片 -->
                            <div class="preview-images mt-3" v-if="previewImages.length">
                                <div class="preview-images-container">
                                    <figure class="image preview-image" v-for="(image, index) in previewImages" :key="index">
                                        <img :src="image.url" :alt="`Preview ${index}`" />
                                        <button 
                                            type="button"
                                            class="delete-image-btn" 
                                            @click="removeImage(index)">
                                            <font-awesome-icon class="icon is-small" icon="fa-solid fa-xmark" />
                                        </button>
                                    </figure>
                                </div>
                            </div>
                        </div>

                        <div class="field">
                            <label class="label">标签</label>
                            <div class="control">
                                <div class="tags">
                                    <span class="tag is-medium m-1" 
                                        v-for="tag in availableTags" 
                                        :key="tag.id"
                                        :class="{ 'is-primary': formData.tag_ids.includes(tag.id), 'is-primary is-light': !formData.tag_ids.includes(tag.id) }"
                                        style="cursor: pointer;"
                                        @click="toggleTag(tag.id)">
                                        {{ tag.name }}
                                    </span>
                                </div>
                            </div>
                        </div>

                        <div class="field">
                            <label class="label">关联商品</label>
                            <div class="control">
                                <button type="button" class="button is-info is-light" @click="openProductSelector">
                                    <span class="icon">
                                        <font-awesome-icon icon="fa-solid fa-plus" />
                                    </span>
                                    <span>添加商品</span>
                                </button>
                            </div>
                            <!-- 显示已选择的商品 -->
                            <div class="tags mt-2" v-if="formData.product_ids.length > 0">
                                <span 
                                    class="tag is-warning is-medium m-1" 
                                    v-for="productId in formData.product_ids" 
                                    :key="productId">
                                    {{ getProductName(productId) }}
                                    <button class="delete is-small" @click="removeProduct(productId)"></button>
                                </span>
                            </div>
                        </div>
                    </form>
                </section>

                <footer class="modal-card-foot">
                    <div class="buttons">
                        <button class="button is-primary" @click="handleSubmitModal">
                            {{ editingPost ? '更新' : '发布' }}
                        </button>
                        <button class="button" @click="handleCloseModal">取消</button>
                    </div>
                </footer>
            </div>
        </div>

        <!-- 商品选择模态框 -->
        <div class="modal" :class="{ 'is-active': isProductSelectorActive }">
            <div class="modal-background" @click="closeProductSelector"></div>
            <div class="modal-card">
                <header class="modal-card-head">
                    <p class="modal-card-title">选择商品</p>
                    <button class="delete" aria-label="close" @click="closeProductSelector"></button>
                </header>
                <section class="modal-card-body product-selector-body">
                    <!-- 搜索框 -->
                    <div class="field">
                        <div class="control has-icons-left">
                            <input 
                                class="input" 
                                type="text" 
                                placeholder="搜索商品..." 
                                v-model="productSearchQuery"
                                @input="searchProducts">
                            <span class="icon is-left">
                                <font-awesome-icon icon="fa-solid fa-magnifying-glass" />
                            </span>
                        </div>
                    </div>

                    <!-- 商品列表 -->
                    <div v-if="loadingProducts" class="has-text-centered">
                        <progress class="progress is-small is-primary" max="100">加载中...</progress>
                    </div>
                    <div v-else-if="availableProducts.length === 0" class="notification is-info is-light">
                        暂无商品
                    </div>
                    <div v-else class="product-list">
                        <div 
                            class="box product-item" 
                            v-for="product in availableProducts" 
                            :key="product.id"
                            :class="{ 'is-selected': formData.product_ids.includes(product.id) }"
                            @click="toggleProduct(product.id)">
                            <div class="columns is-vcentered">
                                <div class="column is-narrow">
                                    <figure class="image is-64x64">
                                        <img :src="product.image" :alt="product.name" style="object-fit: cover;">
                                    </figure>
                                </div>
                                <div class="column">
                                    <p class="title is-6">{{ product.name }}</p>
                                    <p class="subtitle is-7 has-text-grey">{{ product.desc }}</p>
                                </div>
                                <div class="column is-narrow">
                                    <span class="icon has-text-success" v-if="formData.product_ids.includes(product.id)">
                                        <font-awesome-icon icon="fa-solid fa-check-circle" size="lg" />
                                    </span>
                                </div>
                            </div>
                        </div>
                    </div>
                </section>
                <footer class="modal-card-foot">
                    <button class="button is-primary mr-3" @click="closeProductSelector">确定</button>
                    <button class="button" @click="closeProductSelector">取消</button>
                </footer>
            </div>
        </div>


        <!-- SKU选择模态框 -->
        <SKUSelectDialog 
            :show="skuModalShow"
            :product="selectedProduct"
            @close="closeSKUModal"
            @success="handleSKUAdded"
        />


        <!-- 回复模态框 -->
        <div class="modal" :class="{ 'is-active': isReplyModalActive }">
            <div class="modal-background"></div>
            <div class="modal-card">
                <header class="modal-card-head">
                    <p class="modal-card-title">回复帖子</p>
                    <button class="delete" aria-label="close" @click="closeReplyModal"></button>
                </header>

                <section class="modal-card-body reply-modal" v-if="replyingPost">
                    <!-- 显示原帖内容 -->
                    <article class="media box">
                        <figure class="media-left">
                            <p class="image is-64x64 is-square">
                                <img class="is-rounded" :src="replyingPost.author.avatar" />
                            </p>
                        </figure>

                        <div class="media-content">
                            <div class="content">
                                <div>
                                    <strong class="has-text-info">{{ replyingPost.author?.name || '用户' }}</strong>
                                    <small> 编辑于 {{ replyingPost.updated_at }}</small>
                                    
                                    <div class="mt-2">
                                        <strong class="is-size-5">{{ replyingPost.title }}</strong>
                                        <p>{{ replyingPost.content }}</p>
                                    </div>
                                </div>
                            </div>
                            
                            <div class="post-images mt-3" v-if="replyingPost.images && replyingPost.images.length">
                                <div class="post-images-container">
                                    <figure class="image post-image" v-for="image in replyingPost.images" :key="image.id">
                                        <img :src="image.file || image.url" alt="Post image" />
                                    </figure>
                                </div>
                            </div>

                            <div v-if="replyingPost.products && replyingPost.products.length">
                                <div class="tag is-warning m-1" v-for="product in replyingPost.products" :key="product.id">
                                    {{ product.name }}
                                </div>
                            </div>
                        </div>
                    </article>

                    <!-- 回复表单 -->
                    <div class="box mt-4" :class="{ 'reply-highlight': replyingToReply }">
                        <form @submit.prevent="handleReplySubmit">
                            <div class="field" v-if="replyingToReply">
                                <div class="notification is-info is-light">
                                    <button class="delete" @click="cancelReplyToReply"></button>
                                    <strong>回复给 {{ replyingToReply.author.name }}</strong>: 
                                    {{ replyingToReply.content.substring(0, 50) }}{{ replyingToReply.content.length > 50 ? '...' : '' }}
                                </div>
                            </div>
                            
                            <div class="field">
                                <label class="label">{{ replyingToReply ? '你的回复' : '回复帖子' }}</label>
                                <div class="control">
                                    <textarea 
                                        class="textarea textarea-scrollbar" 
                                        v-model="replyContent" 
                                        :placeholder="replyingToReply ? `回复 @${replyingToReply.author.name}...` : '输入你的回复...'"
                                        rows="4"
                                        required>
                                    </textarea>
                                </div>
                            </div>

                            <div class="field">
                                <div class="control">
                                    <button type="submit" class="button is-primary" :disabled="isSubmitting">
                                        <span class="icon">
                                            <font-awesome-icon icon="fa-regular fa-paper-plane" />
                                        </span>
                                        <span>{{ isSubmitting ? '发送中...' : '发送回复' }}</span>
                                    </button>
                                    <button type="button" class="button ml-2" @click="cancelReplyToReply" v-if="replyingToReply">
                                        取消回复
                                    </button>
                                </div>
                            </div>
                        </form>
                    </div>

                    <!-- 显示现有回复列表 -->
                    <div class="box mt-4" v-if="currentReplies && currentReplies.length">
                        <h3 class="title is-5">全部回复 ({{ getTotalReplyCount(currentReplies) }})</h3>
                        <div class="replies-list">
                            <article class="media reply-item" v-for="reply in paginatedReplies" :key="reply.id">
                                <figure class="media-left">
                                    <p class="image is-48x48">
                                        <img class="is-rounded" :src="reply.author.avatar" />
                                    </p>
                                </figure>
                                <div class="media-content">
                                    <div class="content">
                                        <p>
                                            <strong class="has-text-info">{{ reply.author?.name || '用户' }}</strong>
                                            <small class="has-text-grey ml-2">{{ formatDate(reply.created_at) }}</small>
                                            <br>
                                            {{ reply.content }}
                                        </p>
                                    </div>
                                    
                                    <!-- 操作按钮 -->
                                    <nav class="level is-mobile">
                                        <div class="level-left">

                                            <!-- 回复按钮 -->
                                            <a class="level-item" @click="startReplyToReply(reply)">
                                                <span class="icon is-small has-text-primary">
                                                    <font-awesome-icon icon="fa-regular fa-comment-dots" />
                                                </span>
                                            </a>

                                            <!-- 删除按钮 -->
                                            <a class="level-item" 
                                                v-if="canEdit(reply)" 
                                                @click="handleDeleteReply(reply.id)">
                                                <span class="icon is-small has-text-danger">
                                                    <font-awesome-icon icon="fa-regular fa-trash-can" />
                                                </span>
                                            </a>
                                        </div>
                                    </nav>

                                    <!-- 子回复（二级回复） -->
                                    <article class="media child-reply" v-for="childReply in (reply.children || [])" :key="childReply.id">
                                        <figure class="media-left">
                                            <p class="image is-32x32">
                                                <img class="is-rounded" :src="childReply.author.avatar" />
                                            </p>
                                        </figure>
                                        <div class="media-content">
                                            <div class="content">
                                                <p>
                                                    <strong class="has-text-info is-size-6">{{ childReply.author?.name || '用户' }}</strong>
                                                    <small class="has-text-grey ml-2 is-size-6">{{ formatDate(childReply.created_at) }}</small>
                                                    <br>
                                                    <span class="is-size-6" v-html="formatReplyContent(childReply.content)"></span>
                                                </p>
                                            </div>
                                            
                                            <!-- 子回复操作 -->
                                            <nav class="level is-mobile">
                                                <div class="level-left">

                                                    <a class="level-item" @click="startReplyToReply(reply, childReply)">
                                                    <span class="icon is-small has-text-primary">
                                                        <font-awesome-icon icon="fa-regular fa-comment-dots" />
                                                    </span>
                                                    </a>
                                                    
                                                    <a class="level-item" 
                                                        v-if="canEdit(childReply)" 
                                                        @click="handleDeleteReply(childReply.id)">
                                                        <span class="icon is-small has-text-danger">
                                                            <font-awesome-icon icon="fa-regular fa-trash-can" />
                                                        </span>
                                                    </a>
                                                </div>
                                            </nav>
                                        </div>
                                    </article>
                                </div>
                            </article>
                        </div>

                        <!-- 回复分页 -->
                        <nav class="pagination is-centered is-rounded mt-4" role="navigation" aria-label="pagination" v-if="replyTotalPages > 1">
                            <a 
                                class="pagination-previous" 
                                :class="{ 'is-disabled': replyCurrentPage <= 1 }"
                                @click.prevent="replyCurrentPage > 1 && handleReplyPageChange(replyCurrentPage - 1)">
                                上一页
                            </a>
                            <a 
                                class="pagination-next"
                                :class="{ 'is-disabled': replyCurrentPage >= replyTotalPages }"
                                @click.prevent="replyCurrentPage < replyTotalPages && handleReplyPageChange(replyCurrentPage + 1)">
                                下一页
                            </a>
                            
                            <ul class="pagination-list">
                                <li v-for="(page, index) in getReplyPageNumbers()" :key="index">
                                    <span 
                                        v-if="page === '...'" 
                                        class="pagination-ellipsis">
                                        &hellip;
                                    </span>
                                    <a
                                        v-else
                                        class="pagination-link"
                                        :class="{ 'is-current': page === replyCurrentPage }"
                                        :aria-label="`Goto page ${page}`"
                                        :aria-current="page === replyCurrentPage ? 'page' : undefined"
                                        @click.prevent="handleReplyPageChange(page)">
                                        {{ page }}
                                    </a>
                                </li>
                            </ul>
                        </nav>
                    </div>
                </section>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { usePostsStore } from '@/stores/posts'
import { useProductsStore } from '@/stores/products'
import { storeToRefs } from 'pinia'
import { favoriteAPI } from '@/api/favorite'
import SKUSelectDialog from './SKUSelectDialog.vue'

const props = defineProps({
    posts: {
        type: Array,
        required: true,
        default: () => []
    },
    currentPage: {
        type: Number,
        default: 1
    },
    totalPages: {
        type: Number,
        default: 1
    },
    isLoading: {
        type: Boolean,
        default: false
    }
})

const emit = defineEmits(['edit', 'delete', 'page-change', 'submit', 'reply', 'delete-reply'])

const userStore = useUserStore()
const postsStore = usePostsStore()
const productsStore = useProductsStore()
const { availableTags } = storeToRefs(postsStore)

// 模态框状态
const isModalActive = ref(false)
const editingPost = ref(null)
const fileInput = ref(null)
const previewImages = ref([])

// 商品选择相关
const isProductSelectorActive = ref(false)
const availableProducts = ref([])
const productSearchQuery = ref('')
const loadingProducts = ref(false)
const productMap = ref({}) // 商品ID到商品对象的映射

// SKU模态框相关
const skuModalShow = ref(false)
const selectedProduct = ref(null)

// 回复模态框状态
const isReplyModalActive = ref(false)
const replyingPost = ref(null)
const replyContent = ref('')
const replyingToReply = ref(null) // 正在回复的评论
const currentReplies = ref([]) // 当前显示的回复列表
const isSubmitting = ref(false) // 提交状态

// 回复分页
const replyCurrentPage = ref(1)
const replyPageSize = 10
const replyTotalPages = ref(1)
const paginatedReplies = ref([]) // 当前页的回复

const formData = ref({
    title: '',
    content: '',
    tag_ids: [],
    uploadedImages: [],
    product_ids: []
})

// 检查是否可以编辑
const canEdit = (post) => {
    return userStore.user?.is_staff || userStore.user?.id === post.author.id
}

// 处理编辑
const handleEdit = (post) => {
    editingPost.value = post
    isModalActive.value = true
}

// 处理删除
const handleDelete = (postId) => {
    emit('delete', postId)
}

// 分页相关
const handlePageChange = (page) => {
    if (page >= 1 && page <= props.totalPages) {
        emit('page-change', page)
        window.scrollTo({ top: 0, behavior: 'smooth' })
    }
}

// 获取显示的页码列表
const getPageNumbers = () => {
    const current = props.currentPage
    const total = props.totalPages
    const pages = []

    if (total <= 7) {
        // 总页数少于7页，显示全部
        for (let i = 1; i <= total; i++) {
            pages.push(i)
        }
    } else {
        // 总页数多于7页，显示省略号
        if (current <= 3) {
            // 当前页在前面
            pages.push(1, 2, 3, 4, '...', total)
        } else if (current >= total - 2) {
            // 当前页在后面
            pages.push(1, '...', total - 3, total - 2, total - 1, total)
        } else {
            // 当前页在中间
            pages.push(1, '...', current - 1, current, current + 1, '...', total)
        }
    }

    return pages
}

// 模态框相关
const resetForm = () => {
    formData.value = {
        title: '',
        content: '',
        tag_ids: [],
        uploadedImages: [],
        product_ids: []
    }
    previewImages.value = []
}

// 监听编辑帖子的变化，更新表单数据
watch(editingPost, (newPost) => {
    if (newPost) {
        formData.value = {
            title: newPost.title,
            content: newPost.content,
            tag_ids: newPost.tags ? newPost.tags.map(tag => tag.id) : [],
            uploadedImages: newPost.images ? newPost.images.map(img => img.id) : [],
            product_ids: newPost.products ? newPost.products.map(p => p.id) : []
        }
        // 加载现有图片预览
        previewImages.value = newPost.images ? newPost.images.map(img => ({
            id: img.id,
            url: img.file || img.url
        })) : []
    } else {
        resetForm()
    }
})

// 切换标签选择
const toggleTag = (tagId) => {
    const index = formData.value.tag_ids.indexOf(tagId)
    if (index > -1) {
        formData.value.tag_ids.splice(index, 1)
    } else {
        formData.value.tag_ids.push(tagId)
    }
}

// 处理图片上传
const handleImageUpload = async (event) => {
    const files = Array.from(event.target.files)
    
    try {
        const imageIds = await postsStore.uploadImages(files)
        
        // 添加到已上传列表
        formData.value.uploadedImages.push(...imageIds)
        
        // 创建预览
        for (const file of files) {
            const reader = new FileReader()
            reader.onload = (e) => {
                previewImages.value.push({
                    url: e.target.result
                })
            }
            reader.readAsDataURL(file)
        }
        
        // 清空 input
        if (fileInput.value) {
            fileInput.value.value = ''
        }
    } catch (error) {
        alert('图片上传失败：' + error.message)
    }
}

// 移除图片
const removeImage = (index) => {
    previewImages.value.splice(index, 1)
    formData.value.uploadedImages.splice(index, 1)
}

// 处理收藏切换
const handleToggleFavorite = async (post) => {
    try {
        const response = await favoriteAPI.togglePostFavorite(post.id)
        post.is_favorited = response.data.is_favorited
    } catch (error) {
        console.error('收藏操作失败:', error)
        alert('操作失败：' + (error.response?.data?.error || error.message))
    }
}

// 加载帖子收藏状态
const loadFavoriteStatus = async () => {
    if (!props.posts || props.posts.length === 0) return
    
    try {
        // 为每个帖子检查收藏状态
        for (const post of props.posts) {
            try {
                const response = await favoriteAPI.checkPostFavorite(post.id)
                post.is_favorited = response.data.is_favorited
            } catch (error) {
                post.is_favorited = false
            }
        }
    } catch (error) {
        console.error('加载收藏状态失败:', error)
    }
}

// 监听posts变化，加载收藏状态
watch(() => props.posts, () => {
    loadFavoriteStatus()
    // 同时保存帖子中的商品信息到 productMap
    if (props.posts) {
        props.posts.forEach(post => {
            if (post.products && Array.isArray(post.products)) {
                post.products.forEach(product => {
                    if (product.id && !productMap.value[product.id]) {
                        productMap.value[product.id] = product
                    }
                })
            }
        })
    }
}, { immediate: true, deep: true })

// 处理关闭模态框
const handleCloseModal = () => {
    isModalActive.value = false
    editingPost.value = null
    resetForm()
}

// 处理提交模态框
const handleSubmitModal = () => {
    const data = {
        title: formData.value.title,
        content: formData.value.content,
        tag_ids: formData.value.tag_ids,
        image_ids: formData.value.uploadedImages,
        product_ids: formData.value.product_ids
    }
    
    if (editingPost.value) {
        emit('edit', editingPost.value, data)
    } else {
        emit('submit', data)
    }
    
    handleCloseModal()
}

// 商品选择相关函数
const openProductSelector = async () => {
    isProductSelectorActive.value = true
    loadingProducts.value = true
    try {
        await productsStore.fetchProducts(1, '')
        availableProducts.value = productsStore.products
        // 构建商品映射
        productMap.value = {}
        availableProducts.value.forEach(p => {
            productMap.value[p.id] = p
        })
    } catch (error) {
        console.error('加载商品列表失败:', error)
    } finally {
        loadingProducts.value = false
    }
}

const closeProductSelector = () => {
    isProductSelectorActive.value = false
    productSearchQuery.value = ''
}

const searchProducts = async () => {
    loadingProducts.value = true
    try {
        await productsStore.fetchProducts(1, productSearchQuery.value)
        availableProducts.value = productsStore.products
        // 更新商品映射
        availableProducts.value.forEach(p => {
            productMap.value[p.id] = p
        })
    } catch (error) {
        console.error('搜索商品失败:', error)
    } finally {
        loadingProducts.value = false
    }
}

const toggleProduct = (productId) => {
    const index = formData.value.product_ids.indexOf(productId)
    if (index > -1) {
        formData.value.product_ids.splice(index, 1)
    } else {
        formData.value.product_ids.push(productId)
        // 确保商品信息在 productMap 中
        if (!productMap.value[productId]) {
            const product = availableProducts.value.find(p => p.id === productId)
            if (product) {
                productMap.value[productId] = product
            }
        }
    }
}

const removeProduct = (productId) => {
    const index = formData.value.product_ids.indexOf(productId)
    if (index > -1) {
        formData.value.product_ids.splice(index, 1)
    }
}

const getProductName = (productId) => {
    return productMap.value[productId]?.name || '商品'
}

// SKU模态框相关函数
const openProductSKU = (productId) => {
    // 从已加载的商品列表或帖子中查找商品信息
    const product = productMap.value[productId]
    if (product) {
        selectedProduct.value = product
        skuModalShow.value = true
    } else {
        // 如果找不到，尝试从当前帖子的产品列表中查找
        for (const post of props.posts) {
            if (post.products) {
                const foundProduct = post.products.find(p => p.id === productId)
                if (foundProduct) {
                    selectedProduct.value = foundProduct
                    skuModalShow.value = true
                    return
                }
            }
        }
        alert('找不到商品信息')
    }
}

const closeSKUModal = () => {
    skuModalShow.value = false
    selectedProduct.value = null
}

const handleSKUAdded = () => {
    // SKU添加成功的回调
    closeSKUModal()
    console.log('商品已添加到购物车')
}

// 暴露打开模态框的方法，以便父组件可以调用
defineExpose({
    openModal: () => {
        editingPost.value = null
        isModalActive.value = true
    }
})

// 回复相关函数
const openReplyModal = async (post) => {
    replyingPost.value = post
    replyContent.value = ''
    replyingToReply.value = null
    replyCurrentPage.value = 1
    isReplyModalActive.value = true
    
    // 加载回复列表
    await loadReplies(post.id)
}

const closeReplyModal = () => {
    isReplyModalActive.value = false
    replyingPost.value = null
    replyContent.value = ''
    replyingToReply.value = null
    currentReplies.value = []
    paginatedReplies.value = []
    replyCurrentPage.value = 1
}

const loadReplies = async (postId) => {
    try {
        const replies = await postsStore.fetchReplies(postId)
        // 构建回复树结构：只保留顶级回复（parent为null），子回复会通过children字段获取
        // 注意：后端已经通过ReplySerializer的get_children方法构建了children
        currentReplies.value = replies.filter(r => !r.parent)
        
        // 计算分页
        replyTotalPages.value = Math.ceil(currentReplies.value.length / replyPageSize)
        updatePaginatedReplies()
    } catch (error) {
        console.error('加载回复失败:', error)
    }
}

// 更新分页后的回复列表
const updatePaginatedReplies = () => {
    const start = (replyCurrentPage.value - 1) * replyPageSize
    const end = start + replyPageSize
    paginatedReplies.value = currentReplies.value.slice(start, end)
}

// 处理回复分页变化
const handleReplyPageChange = (page) => {
    if (page >= 1 && page <= replyTotalPages.value) {
        replyCurrentPage.value = page
        updatePaginatedReplies()
        // 滚动到回复列表顶部
        setTimeout(() => {
            document.querySelector('.replies-list')?.scrollIntoView({ behavior: 'smooth', block: 'start' })
        }, 100)
    }
}

// 获取回复分页页码列表
const getReplyPageNumbers = () => {
    const current = replyCurrentPage.value
    const total = replyTotalPages.value
    const pages = []

    if (total <= 7) {
        for (let i = 1; i <= total; i++) {
            pages.push(i)
        }
    } else {
        if (current <= 3) {
            pages.push(1, 2, 3, 4, '...', total)
        } else if (current >= total - 2) {
            pages.push(1, '...', total - 3, total - 2, total - 1, total)
        } else {
            pages.push(1, '...', current - 1, current, current + 1, '...', total)
        }
    }

    return pages
}

const handleReplySubmit = async () => {
    if (!replyContent.value.trim() || isSubmitting.value) {
        return
    }
    
    isSubmitting.value = true
    
    try {
        // 构建回复内容，如果是回复某人，在内容前加上 @用户名
        let finalContent = replyContent.value
        if (replyingToReply.value && replyingToReply.value.author) {
            // 检查内容是否已经以@开头，避免重复添加
            if (!finalContent.startsWith(`@${replyingToReply.value.author.name}`)) {
                finalContent = `@${replyingToReply.value.author.name} ${finalContent}`
            }
        }
        
        const replyData = {
            postId: replyingPost.value.id,
            content: finalContent,
            // 使用parentReplyId作为实际的父评论ID（始终是一级评论）
            parentId: replyingToReply.value?.parentReplyId || null
        }
        
        // 触发emit事件
        emit('reply', replyData)
        
        // 等待一小段时间让后端处理
        await new Promise(resolve => setTimeout(resolve, 500))
        
        // 清空输入
        replyContent.value = ''
        replyingToReply.value = null
        
        // 重新加载回复列表以显示最新回复
        await loadReplies(replyingPost.value.id)
        
        // 回到第一页查看新回复
        replyCurrentPage.value = 1
        updatePaginatedReplies()
        
    } catch (error) {
        console.error('回复失败:', error)
        alert('回复失败：' + error.message)
    } finally {
        isSubmitting.value = false
    }
}

// 开始回复某个评论
const startReplyToReply = (parentReply, childReply = null) => {
    // 如果是回复子评论，显示被回复者是childReply，但实际parent是parentReply
    // 如果是回复一级评论，显示被回复者和parent都是parentReply
    if (childReply) {
        // 回复二级评论：显示回复的是childReply，但parent设为一级评论
        replyingToReply.value = {
            ...childReply,
            parentReplyId: parentReply.id  // 实际的父评论ID
        }
    } else {
        // 回复一级评论
        replyingToReply.value = {
            ...parentReply,
            parentReplyId: parentReply.id
        }
    }
    
    // 滚动到回复表单
    setTimeout(() => {
        document.querySelector('.reply-highlight')?.scrollIntoView({ behavior: 'smooth', block: 'center' })
    }, 100)
}

// 取消回复评论
const cancelReplyToReply = () => {
    replyingToReply.value = null
}

// 删除回复
const handleDeleteReply = async (replyId) => {
    if (!confirm('确定要删除这条回复吗？如果有子回复也会一并删除。')) {
        return
    }
    
    try {
        emit('delete-reply', replyId)
        
        // 等待删除完成
        await new Promise(resolve => setTimeout(resolve, 500))
        
        // 重新加载回复列表
        await loadReplies(replyingPost.value.id)
    } catch (error) {
        console.error('删除回复失败:', error)
        alert('删除失败：' + error.message)
    }
}

// 计算总回复数（包括子回复）
const getTotalReplyCount = (replies) => {
    let count = 0
    const countReplies = (list) => {
        list.forEach(reply => {
            count++
            if (reply.children && reply.children.length) {
                countReplies(reply.children)
            }
        })
    }
    countReplies(replies)
    return count
}

// 格式化日期
const formatDate = (dateString) => {
    const date = new Date(dateString)
    const now = new Date()
    const diff = now - date
    
    // 小于1分钟
    if (diff < 60000) {
        return '刚刚'
    }
    // 小于1小时
    if (diff < 3600000) {
        return `${Math.floor(diff / 60000)}分钟前`
    }
    // 小于1天
    if (diff < 86400000) {
        return `${Math.floor(diff / 3600000)}小时前`
    }
    // 小于7天
    if (diff < 604800000) {
        return `${Math.floor(diff / 86400000)}天前`
    }
    
    // 超过7天显示具体日期
    return date.toLocaleDateString('zh-CN', { 
        year: 'numeric', 
        month: '2-digit', 
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    })
}

// 格式化回复内容，将@用户名高亮显示
const formatReplyContent = (content) => {
    // 匹配 @用户名 格式（用户名后面跟空格或结束）
    return content.replace(/@(\S+)(\s|$)/g, '<strong class="has-text-link">@$1</strong>$2')
}
</script>

<style lang="scss" scoped>
.content p {
    white-space: pre-wrap;
}

.product-tag {
    transition: all 0.2s ease;
    
    &:hover {
        transform: translateY(-2px);
        box-shadow: 0 2px 8px rgba(0, 209, 175, 0.3);
    }
}

.post-images-container {
    display: flex;
    overflow-x: auto;
    gap: 1rem;
    padding-bottom: 0.5rem;

    &::-webkit-scrollbar {
        width: 1px;
    }
    
    &::-webkit-scrollbar-track {
        background: transparent;
    }
    
    &::-webkit-scrollbar-thumb {
        background: rgba(0, 209, 175, 1);
        border-radius: 3px;
    }
}

.post-image {
    flex-shrink: 0;
    width: 20%;
}

// 分页样式
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

// 模态框样式
.insert-modal {
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

.preview-images-container {
    display: flex;
    flex-wrap: wrap;
    gap: 1rem;
    margin-top: 0.5rem;
}

.preview-image {
    position: relative;
    width: 100px;
    height: 100px;
    
    img {
        width: 100%;
        height: 100%;
        object-fit: cover;
        border-radius: 4px;
    }
}

.delete-image-btn {
    position: absolute;
    top: -8px;
    right: -8px;
    width: 24px;
    height: 24px;
    border-radius: 50%;
    background-color: #f14668;
    color: white;
    border: none;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 14px;
    transition: background-color 0.2s;

    &:hover {
        background-color: #cc0f35;
    }
}

.input:focus {
    border-color: rgba(0, 209, 175, 1);
    box-shadow: 0 0 0 0.125em rgba(0, 209, 175, 0.25);
}

.textarea:focus {
    border-color: rgba(0, 209, 175, 1);
    box-shadow: 0 0 0 0.125em rgba(0, 209, 175, 0.25);
}

// 回复模态框样式
.reply-modal {
    max-height: 70vh;
    overflow-y: auto;

    &::-webkit-scrollbar {
        width: 6px;
    }
    
    &::-webkit-scrollbar-track {
        background: transparent;
    }
    
    &::-webkit-scrollbar-thumb {
        background: rgba(0, 209, 175, 0.5);
        border-radius: 3px;
    }
}

.reply-highlight {
    border: 2px solid rgba(0, 209, 175, 0.5);
    transition: border-color 0.3s ease;
}

.textarea-scrollbar {

    &::-webkit-scrollbar {
        width: 6px;
    }
    
    &::-webkit-scrollbar-track {
        background: transparent;
    }
    
    &::-webkit-scrollbar-thumb {
        background: rgba(0, 209, 175, 0.5);
        border-radius: 3px;
    }
}

.replies-list {
    .reply-item {

        &:last-child {
            border-bottom: none;
        }
    }

    .child-reply {
        margin-top: 1rem;
        margin-left: 1rem;
        padding-left: 1rem;
        border-left: 2px solid rgba(0, 209, 175, 0.3);
        
        &:last-child {
            margin-bottom: 0;
        }
    }

    .level-item {
        cursor: pointer;
        transition: color 0.2s;
        
        &:hover {
            color: rgba(0, 209, 175, 1);
            
            .icon {
                color: rgba(0, 209, 175, 1) !important;
            }
        }
    }
}
// 商品选择模态框样式
.product-selector-body,
.product-list {
    max-height: 60vh;
    overflow-y: auto;

    &::-webkit-scrollbar {
        width: 6px;
    }
    
    &::-webkit-scrollbar-track {
        background: transparent;
    }
    
    &::-webkit-scrollbar-thumb {
        background: rgba(0, 209, 175, 0.5);
        border-radius: 3px;
    }
}

.product-list {
    max-height: 50vh;
    overflow-y: auto;
}

.product-item {
    cursor: pointer;
    transition: all 0.2s ease;
    margin-bottom: 0.5rem;

    &:hover {
        box-shadow: 0 2px 8px rgba(0, 209, 175, 0.3);
    }

    &.is-selected {
        border: 2px solid rgba(0, 209, 175, 1);
        background-color: rgba(0, 209, 175, 0.05);
    }
}
</style>