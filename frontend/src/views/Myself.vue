<template>
    <div class="container1">
        <div class="card">
            <div class="card-content">
                <!-- 头像区域 -->
                <div class="has-text-centered mb-5">
                    <figure class="image is-128x128 is-inline-block">
                        <img 
                            class="is-rounded"
                            :src="userStore.avatar" 
                            alt="用户头像"
                            @click="triggerFileInput"
                            title="点击更改头像"
                            style="cursor: pointer;"
                        >

                    </figure>

                    <!-- 隐藏的文件输入框 -->
                    <input 
                        ref="fileInput"
                        type="file" 
                        accept="image/*" 
                        @change="handleAvatarUpload"
                        style="display: none;"
                    >
                </div>
                
                <!-- 用户信息区域 -->
                <div class="content">
                    <div class="field is-horizontal mb-3">
                        <div class="field-label is-normal">
                            <label class="label has-text-danger-light">ID</label>
                        </div>
                        <div class="field-body">
                            <div class="field">
                                <p class="control">
                                    <span class="tag is-warning is-medium">{{ userStore.id }}</span>
                                </p>
                            </div>
                        </div>
                    </div>

                    <div class="field is-horizontal mb-3">
                        <div class="field-label is-normal">
                            <label class="label has-text-danger-light">用户名</label>
                        </div>
                        <div class="field-body">
                            <div class="field">
                                <p class="control">
                                    <span class="tag is-info is-medium">{{ userStore.username }}</span>
                                </p>
                            </div>
                        </div>
                    </div>

                    <div class="field is-horizontal mb-3">
                        <div class="field-label is-normal">
                            <label class="label has-text-danger-light">邮箱</label>
                        </div>
                        <div class="field-body">
                            <div class="field">
                                <p class="control">
                                    <span class="tag is-link is-medium">{{ userStore.email || '未设置' }}</span>
                                </p>
                            </div>
                        </div>
                    </div>

                    <div class="field is-horizontal mb-3">
                        <div class="field-label is-normal">
                            <label class="label has-text-danger-light">注册时间</label>
                        </div>
                        <div class="field-body">
                            <div class="field">
                                <p class="control">
                                    <span class="tag is-success is-medium">{{ userStore.dateJoined }}</span>
                                </p>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="field is-grouped">
                    <p class="control">
                        <button 
                            class="button is-warning is-dark" 
                            @click="handleLogout"
                        >
                            <span>退出登录</span>
                        </button>
                    </p>
                    <p class="control">
                        <button 
                            class="button is-danger is-dark" 
                            @click="handleDeleteAccount" 
                        >
                            <span>注销账户</span>
                        </button>
                    </p>
                </div>

            </div>
        </div>

        <div class="card">

            <div class="card-content">

                <header class="card-header">
                    <label class="label has-text-danger-light">个人简介</label>
                </header>

                <div class="card-content">
                    <div class="content bio-content">
                        {{ userStore.bio || '这个人很懒，什么都没写...' }}
                    </div>
                </div>

                <footer class="card-footer">
                    <a class="card-footer-item" @click="triggerUpdateBio">编辑</a>
                </footer>

                <!-- 编辑简介的模态框 -->
                <div class="modal" :class="{ 'is-active': showBioModal }">
                    <div class="modal-background" @click="showBioModal = false"></div>
                    <div class="modal-card">
                        <header class="modal-card-head">
                            <p class="modal-card-title">编辑个人简介</p>
                        </header>
                        <section class="modal-card-body">
                            <textarea
                                class="textarea"
                                v-model="editBio"
                                maxlength="300"
                                rows="6"
                                placeholder="请输入个人简介"
                            ></textarea>
                            <p class="help has-text-right">{{ editBio.length }}/300</p>
                        </section>
                        <footer class="modal-card-foot">
                            <button class="button is-success m-2" @click="saveBio" :disabled="savingBio">保存</button>
                            <button class="button is-dark m-2" @click="showBioModal = false">取消</button>
                        </footer>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- 删除账户确认模态框 -->
    <div class="modal" :class="{ 'is-active': showDeleteModal }">
        <div class="modal-background" @click="showDeleteModal = false"></div>
        <div class="modal-card">
            <header class="modal-card-head has-background-danger">
                <p class="modal-card-title has-text-white">⚠️ 警告</p>
            </header>
            <section class="modal-card-body">
                <p class="has-text-centered is-size-5 mb-4">
                    <strong>确定要注销账户吗？</strong>
                </p>
                <div class="notification is-danger is-light">
                    <p>⚠️ 注销后将：</p>
                    <ul class="ml-5 mt-2">
                        <li>永久删除您的账户</li>
                        <li>清除所有个人信息</li>
                        <li>删除所有相关数据</li>
                        <li><strong>此操作不可恢复！</strong></li>
                    </ul>
                </div>
                <p class="has-text-centered mt-4">
                    请输入您的用户名 <strong class="has-text-danger">{{ userStore.username }}</strong> 和 
                    <strong class="has-text-danger">密码</strong> 确认：
                </p>
                <div class="field mt-3">
                    <div class="control mb-3">
                        <input 
                            class="input" 
                            type="text" 
                            v-model="confirmUsername"
                            placeholder="输入用户名确认"
                        >
                    </div>
                    <div class="control">
                        <input 
                            class="input" 
                            type="password" 
                            v-model="confirmPassword"
                            placeholder="输入密码确认"
                        >
                    </div>
                </div>
            </section>
            <footer class="modal-card-foot">
                <button 
                    class="button is-danger m-1" 
                    @click="confirmDelete"
                    :disabled="!confirmUsername || !confirmPassword"
                >
                    确认注销
                </button>
                <button class="button" @click="showDeleteModal = false">
                    取消
                </button>
            </footer>
        </div>
    </div>

    <div class="container2">
        
        <div class="tabs is-toggle is-toggle-rounded is-fullwidth">
            <ul>
                <li :class="{ 'is-active': activeTab === 'orders' }">
                    <a @click="activeTab = 'orders'">
                        <span>订单</span>
                    </a>
                </li>

                <li :class="{ 'is-active': activeTab === 'posts' }">
                    <a @click="activeTab = 'posts'">
                        <span>帖子</span>
                    </a>
                </li>

                <li :class="{ 'is-active': activeTab === 'owned' }">
                    <a @click="activeTab = 'owned'">
                        <span>拥有</span>
                    </a>
                </li>

                <li :class="{ 'is-active': activeTab === 'favorites' }">
                    <a @click="activeTab = 'favorites'">
                        <span>收藏</span>
                    </a>
                </li>
            </ul>
        </div>

        <!-- 帖子内容区域 -->
        <div v-show="activeTab === 'posts'" class="mt-4">
            <PostList 
                :posts="paginatedUserPosts"
                :isLoading="isLoading"
                :current-page="currentPage"
                :total-pages="totalPages"
                @edit="handleEditPost"
                @delete="handleDeletePost"
                @page-change="handlePageChange"
                @reply="handleReplyPost"
                @delete-reply="handleDeleteReply"
            />
        </div>

        <!-- 订单内容区域 -->
        <div v-show="activeTab === 'orders'" class="mt-4">
            <MyOrdersContent ref="ordersRef" />
        </div>

        <!-- 拥有商品内容区域 -->
        <div v-show="activeTab === 'owned'" class="mt-4">
            <MyProductsContent ref="productsRef" />
        </div>

        <!-- 收藏内容区域 -->
        <div v-show="activeTab === 'favorites'" class="mt-4">
            <Favorite ref="favoriteRef" />
        </div>
    </div>
</template>

<script>
    import { useUserStore } from '@/stores/user'
    import { usePostsStore } from '@/stores/posts'
    import { useRouter } from 'vue-router'
    import { onMounted, onUnmounted, ref, computed, watch } from 'vue'
    import { userAPI } from '@/api/user'
    import PostList from '@/components/PostList.vue'
    import Favorite from '@/components/Favorite.vue'
    import MyOrdersContent from '@/components/MyOrdersContent.vue'
    import MyProductsContent from '@/components/MyProductsContent.vue'
    import { storeToRefs } from 'pinia'
    
    export default {
        components: {
            PostList,
            Favorite,
            MyOrdersContent,
            MyProductsContent
        },
        setup() {
            const userStore = useUserStore()
            const postsStore = usePostsStore()
            const router = useRouter()

            const { posts } = storeToRefs(postsStore)

            const fileInput = ref(null)  // 文件输入框的引用

            const showDeleteModal = ref(false)  // 控制注销确认对话框
            const confirmUsername = ref('')     // 确认输入的用户名
            const confirmPassword = ref('')  // 用户输入的密码

            const showBioModal = ref(false)
            const editBio = ref('')
            const savingBio = ref(false)

            // 标签页状态 - 默认显示订单
            const activeTab = ref('orders')
            const favoriteRef = ref(null)  // Favorite 组件引用
            const ordersRef = ref(null)    // Orders 组件引用
            const productsRef = ref(null)  // Products 组件引用

            // 分页状态
            const currentPage = ref(1)
            const postsPerPage = 10  // 改回10条
            const isLoading = ref(true)  // 加载状态

            // 计算属性：当前用户的帖子
            const userPosts = computed(() => {
                const filtered = posts.value.filter(post => post.author.id === userStore.id)
                console.log('用户帖子总数:', filtered.length)
                return filtered
            })

            // 计算属性：总页数
            const totalPages = computed(() => {
                const total = Math.ceil(userPosts.value.length / postsPerPage)
                console.log('总页数:', total, '每页:', postsPerPage, '总帖子数:', userPosts.value.length)
                return total
            })

            // 计算属性：当前页的帖子
            const paginatedUserPosts = computed(() => {
                const start = (currentPage.value - 1) * postsPerPage
                const end = start + postsPerPage
                const paginated = userPosts.value.slice(start, end)
                console.log('当前页帖子数:', paginated.length, '页码:', currentPage.value)
                return paginated
            })

            // 处理分页变化
            const handlePageChange = (page) => {
                currentPage.value = page
            }

            const handleLogout = () => {
                userStore.logout()
                router.push('/login')
            }

            
            // 显示注销确认对话框
            const handleDeleteAccount = () => {
                showDeleteModal.value = true
                confirmUsername.value = ''  // 清空输入
                confirmPassword.value = ''  // 清空密码输入
            }

            // 确认注销账户
            const confirmDelete = async () => {
                // 前端验证用户名
                if (confirmUsername.value !== userStore.username) {
                    alert('用户名不匹配')
                    return
                }

                // 密码验证由后端完成
                if (!confirmPassword.value) {
                    alert('请输入密码')
                    return
                }

                try {
                    const response = await userAPI.deleteAccount(confirmPassword.value, userStore.token)

                    alert(response.data.message)
                    
                    // 清除本地数据
                    userStore.logout()
                    
                    // 跳转到注册页面
                    router.push('/')
                    
                } catch (error) {
                    console.error('注销失败:', error)
                    const errorMsg = error.response?.data?.error || '请重试'
                    alert(`账户注销失败：${errorMsg}`)
                }
            }


            // 头像：触发文件选择
            const triggerFileInput = () => {
                fileInput.value?.click()
            }

            const handleAvatarUpload = async (event) => {

                const file = event.target.files[0]
                if (!file) return

                // 检查文件类型
                if (!file.type.startsWith('image/')) {
                    alert('请选择图片文件')
                    return
                }

                // 检查文件大小（限制 2MB）
                if (file.size > 2 * 1024 * 1024) {
                    alert('图片大小不能超过 2MB')
                    return
                }

                // 创建 FormData
                const formData = new FormData()
                formData.append('avatar', file)

                try {
                    const response = await userAPI.uploadAvatar(formData, userStore.token)

                    console.log('后端返回:', response.data)  // 调试信息

                    // 更新 store 中的用户信息（后端返回完整的 user 对象）
                    const updatedUser = response.data.user
                    userStore.login(updatedUser, userStore.token)

                    alert('头像上传成功！')
                    
                    // 清空文件输入框，允许重复上传同一文件
                    event.target.value = ''
                } catch (error) {
                    console.error('上传失败:', error)
                    console.error('错误详情:', error.response?.data)
                    alert(`头像上传失败：${error.response?.data?.error || '请重试'}`)
                }
            }


            // 打开编辑简介模态框
            const triggerUpdateBio = () => {
                editBio.value = userStore.bio || ''
                showBioModal.value = true
            }

            // 保存简介
            const saveBio = async () => {
                if (savingBio.value) return
                savingBio.value = true

                try {
                    const response = await userAPI.updateBio(editBio.value, userStore.token)    
                    const updatedUser = response.data.user
                    userStore.login(updatedUser, userStore.token)
                    showBioModal.value = false

                    alert('个人简介更新成功！')
                } catch (error) {
                    alert(error.response?.data?.error || '更新失败')
                } finally {
                    savingBio.value = false
                }
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

            // 删除帖子
            const handleDeletePost = async (postId) => {
                if (confirm('确定删除此帖子？')) {
                    try {
                        await postsStore.deletePost(postId)
                        alert('帖子删除成功')
                        
                        // 重新加载用户帖子
                        await postsStore.fetchPosts({ 
                            author: userStore.id,
                            page_size: 1000
                        })
                        
                        // 如果当前页没有帖子了且不是第一页，回到上一页
                        if (paginatedUserPosts.value.length === 0 && currentPage.value > 1) {
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

            // 监听标签页切换
            watch(activeTab, async (newTab, oldTab) => {
                // 切换到收藏页面时，刷新收藏数据
                if (newTab === 'favorites') {
                    console.log('切换到收藏页面，刷新收藏数据')
                    setTimeout(() => {
                        favoriteRef.value?.refresh()
                    }, 100)
                }
                // 切换到帖子页面时，刷新帖子数据
                else if (newTab === 'posts' && oldTab !== 'posts') {
                    console.log('切换到帖子页面，刷新帖子数据')
                    isLoading.value = true
                    try {
                        await postsStore.fetchPosts({ 
                            author: userStore.id,
                            page_size: 1000
                        })
                    } catch (error) {
                        console.error('刷新帖子失败:', error)
                    } finally {
                        isLoading.value = false
                    }
                }
                // 切换到订单页面时，刷新订单数据
                else if (newTab === 'orders') {
                    console.log('切换到订单页面，刷新订单数据')
                    setTimeout(() => {
                        ordersRef.value?.refresh()
                    }, 100)
                }
                // 切换到拥有商品页面时，刷新商品数据
                else if (newTab === 'owned') {
                    console.log('切换到拥有商品页面，刷新商品数据')
                    setTimeout(() => {
                        productsRef.value?.refresh()
                    }, 100)
                }
            })

            // 组件挂载时添加样式类
            onMounted(async () => {
                document.body.classList.add('myself-page-active')
                document.getElementById('app')?.classList.add('myself-page-active')

                // 加载标签数据（用于编辑帖子时显示）
                await postsStore.fetchTags()

                // 加载当前用户的所有帖子
                isLoading.value = true
                try {
                    await postsStore.fetchPosts({ 
                        author: userStore.id,
                        page_size: 1000  // 获取最多1000条，足够显示所有帖子
                    })
                    console.log('成功加载用户帖子')
                } catch (error) {
                    console.error('加载帖子失败:', error)
                } finally {
                    isLoading.value = false
                }
            })

            // 组件卸载时移除样式类
            onUnmounted(() => {
                document.body.classList.remove('myself-page-active')
                document.getElementById('app')?.classList.remove('myself-page-active')
            })

            return {
                userStore,            // 用户信息 Store

                handleAvatarUpload,   // 处理头像上传
                triggerFileInput,     // 触发文件输入
                fileInput,            // 文件输入框的引用

                handleLogout,         // 处理注销
                handleDeleteAccount,  // 显示对话框的函数
                showDeleteModal,      // 控制对话框显示的变量
                confirmUsername,      // 用户输入的确认用户名
                confirmPassword,      // 用户输入的确认密码
                confirmDelete,        // 确认注销的函数

                showBioModal,         // 控制简介模态框显示
                editBio,              // 编辑的简介内容
                savingBio,            // 保存简介的状态
                triggerUpdateBio,     // 方法：触发编辑简介
                saveBio,              // 方法：保存简介

                activeTab,            // 当前标签页
                favoriteRef,          // Favorite 组件引用
                ordersRef,            // Orders 组件引用
                productsRef,          // Products 组件引用
                userPosts,            // 用户的帖子列表
                paginatedUserPosts,   // 分页后的帖子列表
                currentPage,          // 当前页码
                totalPages,           // 总页数
                isLoading,            // 加载状态
                handlePageChange,     // 处理分页变化
                handleEditPost,       // 处理编辑帖子
                handleDeletePost,     // 删除帖子
                handleReplyPost,      // 回复帖子
                handleDeleteReply,    // 删除回复
            }
        },
    }
</script>

<style>
    /* 只在 Myself 页面生效 */
    body.myself-page-active{
        align-items: start;
        justify-content: start;
    }

    #app.myself-page-active{

        display: flex;
        padding: 0 2rem;
        width: 100%;
    }
</style>

<style lang="scss" scoped>

    .container1 {
        padding: 2rem;
    }

    .container2 {
        width: 100%;
        padding: 2rem;
    }

    .card {
        box-shadow: 0 0.5em 1em -0.125em rgba(10, 10, 10, 0.1), 
                    0 0px 0 1px rgba(10, 10, 10, 0.02);
        border-radius: 8px;
    }

    .image.is-128x128 {

        img {
            width: 128px;
            height: 128px;
            object-fit: cover;
            border: 3px solid #f5f5f5;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }
    }

    .field-label {
        flex-grow: 0;
        flex-shrink: 0;
        margin-right: 1.5rem;
        text-align: right;
        min-width: 100px;
    }

    .label {
        color: #363636;
        font-weight: 600;
    }

    .tag {
        padding: 0.5rem 1rem;
    }

    .field.is-grouped{

        justify-content: center;
    }

    .bio-content {
        max-height: 100px;      // 最大高度
        max-width: 300px;       // 最大宽度
        overflow-y: auto;        // 超出显示滚动条
        white-space: pre-wrap;   // 保留换行符，自动换行
        word-wrap: break-word;   // 长单词自动换行
        word-break: break-all;   // 在任意字符间换行


        // 极简滚动条
        // Webkit
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

        // // Firefox
        // scrollbar-width: thin;
        // scrollbar-color: #485fc7 #f5f5f5;  // Bulma 主色调
        
    }

.tabs ul li.is-active a {
    background-color: rgba(0, 209, 175, 1);
    border: none;
}
</style>