<template>
    <div class="container mt-5">

        <div class="field left-box box">

            <!-- 搜索框 -->
            <div class="field mt-2">
                <p class="control has-icons-left">
                    <input 
                        class="input is-rounded" 
                        type="text" 
                        placeholder="搜索标题或商品..."
                        v-model="searchQuery"
                        @input="handleSearch"
                        @focus="isFocused = true"
                        @blur="isFocused = false"
                    >

                    <span 
                    class="icon is-left"
                    :class="{ 'has-text-primary': isFocused }"
                    >
                        <font-awesome-icon icon="fa-solid fa-magnifying-glass" />
                    </span>
                </p>
            </div>

            <!-- 排序选项 -->
            <div class="field mt-4">
                <label class="label is-size-6 has-text-success">排序方式</label>
                <div class="control">
                    <div class="select is-fullwidth is-info">
                        <select v-model="sortBy" @change="handleFilterChange">
                            <option value="-updated_at">最新编辑</option>
                            <option value="-created_at">最新发布</option>
                            <option value="created_at">最早发布</option>
                        </select>
                    </div>
                </div>
            </div>

            <!-- 标签过滤 -->
            <div class="field mt-4">
                <label class="label is-size-6 has-text-success">按标签筛选</label>
                <div class="control">
                    <div class="tags is-justify-content-center">
                        <span 
                            class="tag is-medium m-1" 
                            v-for="tag in availableTags" 
                            :key="tag.id"
                            :class="{ 'is-danger': selectedTags.includes(tag.id), 'is-danger is-light': !selectedTags.includes(tag.id) }"
                            style="cursor: pointer;"
                            @click="toggleFilterTag(tag.id)">
                            {{ tag.name }}
                        </span>
                        <!-- 管理员添加标签入口 -->
                        <span 
                            v-if="isAdmin"
                            class="tag is-medium is-info m-1" 
                            style="cursor: pointer;"
                            @click="showAddTagModal = true">
                            <span class="icon">
                                <font-awesome-icon icon="fa-solid fa-plus" />
                            </span>
                            <span>添加标签</span>
                        </span>
                    </div>
                </div>
            </div>

            <!-- 清空筛选 -->
            <div class="field mt-4" v-if="searchQuery || selectedTags.length > 0">
                <button class="button is-small is-light is-fullwidth" @click="clearFilters">
                    <span class="icon">
                        <font-awesome-icon icon="fa-solid fa-rotate-right" />
                    </span>
                    <span>清空筛选</span>
                </button>
            </div>
        </div>

        <div>

            <button class="button is-primary ml-2" @click="openCreateModal">发帖</button>
        </div>
    </div>
    
    <div class="container">
        <PostList 
            :posts="posts"
            :isLoading="isLoading"
            :current-page="pagination.currentPage"
            :total-pages="pagination.totalPages"
            @edit="handleEditPost"
            @delete="handleDeletePost"
            @page-change="goToPage"
            @submit="handleSubmitPost"
            @reply="handleReplyPost"
            @delete-reply="handleDeleteReply"
            ref="postListRef"
        />
    </div>

    <!-- 添加标签模态框 -->
    <div class="modal" :class="{ 'is-active': showAddTagModal }">
        <div class="modal-background" @click="closeAddTagModal"></div>
        <div class="modal-card" style="max-width: 500px;">
            <header class="modal-card-head">
                <p class="modal-card-title">添加新标签</p>
                <button class="delete" aria-label="close" @click="closeAddTagModal"></button>
            </header>
            <section class="modal-card-body">
                <div class="field">
                    <label class="label">标签名称</label>
                    <div class="control">
                        <input 
                            class="input" 
                            type="text" 
                            v-model="newTagName"
                            placeholder="请输入标签名称"
                            maxlength="20"
                            @keyup.enter="handleAddTag">
                    </div>
                    <p class="help">标签名称不能超过20个字符</p>
                </div>
            </section>
            <footer class="modal-card-foot">
                <button 
                    class="button is-success mr-3" 
                    @click="handleAddTag"
                    :disabled="!newTagName.trim() || isAddingTag"
                    :class="{ 'is-loading': isAddingTag }">
                    添加
                </button>
                <button class="button" @click="closeAddTagModal">取消</button>
            </footer>
        </div>
    </div>
</template>

<script setup>
    import { onMounted, onUnmounted, ref, computed } from 'vue'
    import { storeToRefs } from 'pinia'
    import { usePostsStore } from '@/stores/posts'
    import { useUserStore } from '@/stores/user'
    import PostList from '@/components/PostList.vue'

    const postsStore = usePostsStore()
    const userStore = useUserStore()
    const { posts, availableTags, pagination } = storeToRefs(postsStore)

    const postListRef = ref(null)
    const isLoading = ref(true)  // 加载状态
    
    // 搜索和过滤状态
    const searchQuery = ref('')
    const sortBy = ref('-updated_at')  // 默认按更新时间倒序
    const selectedTags = ref([])
    const isFocused = ref(false)

    // 添加标签相关状态
    const showAddTagModal = ref(false)
    const newTagName = ref('')
    const isAddingTag = ref(false)

    // 判断是否为管理员
    const isAdmin = computed(() => {
        return userStore.user?.is_staff || userStore.user?.is_superuser
    })

    // 新建帖子模态框
    const openCreateModal = () => {
        postListRef.value?.openModal()
    }

    // 处理编辑帖子（由 PostList 触发）
    const handleEditPost = async (post, data) => {
        try {
            await postsStore.updatePost(post.id, data)
            alert('帖子更新成功')
        } catch (error) {
            alert('操作失败：' + error.message)
        }
    }

    // 处理新建帖子（由 PostList 触发）
    const handleSubmitPost = async (data) => {
        try {
            await postsStore.createPost(data)
            alert('帖子发布成功')
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
                
                // 刷新当前页，如果当前页没有帖子了，回到上一页
                await applyFilters(pagination.value.currentPage)
                
                // 如果当前页没有帖子且不是第一页，返回上一页
                if (posts.value.length === 0 && pagination.value.currentPage > 1) {
                    await applyFilters(pagination.value.currentPage - 1)
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
            // 回复成功，PostList组件会自动刷新
        } catch (error) {
            alert('回复失败：' + error.message)
            throw error
        }
    }

    // 处理删除回复
    const handleDeleteReply = async (replyId) => {
        try {
            await postsStore.deleteReply(replyId)
            // 删除成功，PostList组件会自动刷新
        } catch (error) {
            alert('删除失败：' + error.message)
            throw error
        }
    }

    // 切换到指定页面
    const goToPage = (page) => {
        if (page >= 1 && page <= pagination.value.totalPages) {
            applyFilters(page)
        }
    }

    // 切换标签过滤
    const toggleFilterTag = (tagId) => {
        const index = selectedTags.value.indexOf(tagId)
        if (index > -1) {
            selectedTags.value.splice(index, 1)
        } else {
            selectedTags.value.push(tagId)
        }
        handleFilterChange()
    }

    // 处理搜索输入（防抖）
    let searchTimeout = null
    const handleSearch = () => {
        clearTimeout(searchTimeout)
        searchTimeout = setTimeout(() => {
            handleFilterChange()
        }, 500) // 500ms 防抖
    }

    // 处理过滤条件变化
    const handleFilterChange = () => {
        applyFilters(1) // 重置到第一页
    }

    // 应用过滤条件
    const applyFilters = async (page = 1) => {
        const params = { page }

        // 搜索关键词
        if (searchQuery.value.trim()) {
            params.search = searchQuery.value.trim()
        }

        // 排序
        if (sortBy.value) {
            params.ordering = sortBy.value
        }

        // 标签过滤（交集）
        if (selectedTags.value.length > 0) {
            params.tags = selectedTags.value.join(',')
        }

        isLoading.value = true
        try {
            await postsStore.fetchPosts(params)
        } finally {
            isLoading.value = false
        }
    }

    // 清空筛选
    const clearFilters = () => {
        searchQuery.value = ''
        selectedTags.value = []
        sortBy.value = '-updated_at'
        applyFilters(1)
    }

    // 关闭添加标签模态框
    const closeAddTagModal = () => {
        showAddTagModal.value = false
        newTagName.value = ''
    }

    // 处理添加标签
    const handleAddTag = async () => {
        const tagName = newTagName.value.trim()
        if (!tagName) {
            alert('请输入标签名称')
            return
        }

        // 检查标签是否已存在
        if (availableTags.value.some(tag => tag.name === tagName)) {
            alert('该标签已存在')
            return
        }

        isAddingTag.value = true
        try {
            await postsStore.createTag(tagName)
            alert('标签添加成功')
            closeAddTagModal()
            // 重新获取标签列表
            await postsStore.fetchTags()
        } catch (error) {
            console.error('添加标签失败:', error)
            alert('添加标签失败：' + (error.response?.data?.name?.[0] || error.message))
        } finally {
            isAddingTag.value = false
        }
    }

    onMounted(async () => {
        document.body.classList.add('communicate-page-active')
        document.getElementById('app')?.classList.add('communicate-page-active')

        await postsStore.fetchTags()
        await applyFilters(1) // 使用过滤条件加载第一页
    })

    onUnmounted(() => {
        document.body.classList.remove('communicate-page-active')
        document.getElementById('app')?.classList.remove('communicate-page-active')
    })
</script>

<style>
    
    body.communicate-page-active{
        align-items: start;
    }

    #app.communicate-page-active{

        display: grid;
        grid-template-columns: 1fr 4fr;
        padding: 0 2rem;
        width: 100%;
    }
</style>

<style lang="scss" scoped>
.left-box {
    min-height: 82vh;
    padding: 1.5rem;
}

.radio {
    display: block;
    margin-bottom: 0.5rem;
    
    input[type="radio"] {
        margin-right: 0.5rem;
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
</style>