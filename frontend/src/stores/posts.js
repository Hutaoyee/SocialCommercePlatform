
import { ref } from 'vue'
import { defineStore } from 'pinia'
import { communicateAPI } from '@/api/communicate'

export const usePostsStore = defineStore('posts', () => {

    const posts = ref([])
    const availableTags = ref([])

    // 分页信息
    const pagination = ref({
        count: 0,
        next: null,
        previous: null,
        currentPage: 1,
        totalPages: 1
    })

    // 获取帖子
    const fetchPosts = async (params = {}) => {
        try {
            const response = await communicateAPI.getPosts(params)

            // DRF 分页响应包含 count, next, previous, results
            if (response.data.results) {
                posts.value = response.data.results
                pagination.value = {
                    count: response.data.count,        // 总帖子数
                    next: response.data.next,          // 下一页URL (字符串或null)
                    previous: response.data.previous,  // 上一页URL (字符串或null)
                    currentPage: params.page || 1,     // 当前页码
                    totalPages: Math.ceil(response.data.count / 10) // 总页数
                }
            } else {
                posts.value = response.data
            }
        } catch (error) {

            console.error('获取帖子失败:', error)
        }
    }

    // 获取标签
    const fetchTags = async () => {
        try {
            const response = await communicateAPI.getTags()

            availableTags.value = response.data.results ?? response.data
        } catch (error) {

            console.error('获取标签失败:', error)
        }
    }

    // 创建标签
    const createTag = async (tagName) => {
        try {
            const response = await communicateAPI.createTag({ name: tagName })
            // 添加到本地列表
            availableTags.value.push(response.data)
            return response.data
        } catch (error) {
            console.error('创建标签失败:', error)
            throw error
        }
    }

    // 上传图片
    const uploadImage = async (file) => {
        try {
            const formData = new FormData()
            formData.append('file', file)
            
            const response = await communicateAPI.uploadImage(formData)
            return response.data.id  // 返回图片ID
        } catch (error) {
            console.error('上传图片失败:', error)
            throw error
        }
    }

    // 批量上传图片
    const uploadImages = async (files) => {
        try {
            const imageIds = []
            for (const file of files) {
                const imageId = await uploadImage(file)
                imageIds.push(imageId)
            }
            return imageIds
        } catch (error) {
            console.error('批量上传图片失败:', error)
            throw error
        }
    }

    // 创建帖子
    const createPost = async (data) => {
        try {
            const response = await communicateAPI.createPost(data)
            posts.value.unshift(response.data)  // 添加到列表开头
        } catch (error) {
            console.error('创建帖子失败:', error)
            throw error
        }
    }

    // 更新帖子
    const updatePost = async (postId, data) => {
        try {
            const response = await communicateAPI.updatePost(postId, data)
            const index = posts.value.findIndex(p => p.id === postId)
            if (index !== -1) {
                posts.value[index] = response.data
            }
        } catch (error) {
            console.error('更新帖子失败:', error)
            throw error
        }
    }

    // 删除帖子
    const deletePost = async (postId) => {
        try {
            await communicateAPI.deletePost(postId)
            // 删除成功后，从本地列表移除
            posts.value = posts.value.filter(post => post.id !== postId)
        } catch (error) {
            console.error('删除帖子失败:', error)
            throw error  // 抛出错误供调用者处理
        }
    }

    // 创建回复
    const createReply = async (postId, content, parentId = null) => {
        try {
            const data = {
                post: postId,
                content: content
            }
            
            if (parentId) {
                data.parent = parentId
            }
            
            const response = await communicateAPI.createReply(data)
            
            // 更新本地帖子的回复列表
            const post = posts.value.find(p => p.id === postId)
            if (post) {
                if (!post.replies) {
                    post.replies = []
                }
                post.replies.push(response.data)
            }
            
            return response.data
        } catch (error) {
            console.error('创建回复失败:', error)
            throw error
        }
    }

    // 获取帖子的回复
    const fetchReplies = async (postId) => {
        try {
            const response = await communicateAPI.getReplies({ post: postId })
            return response.data.results ?? response.data
        } catch (error) {
            console.error('获取回复失败:', error)
            throw error
        }
    }

    // 删除回复
    const deleteReply = async (replyId) => {
        try {
            await communicateAPI.deleteReply(replyId)
            
            // 从本地所有帖子中移除该回复
            posts.value.forEach(post => {
                if (post.replies) {
                    post.replies = post.replies.filter(r => r.id !== replyId)
                }
            })
        } catch (error) {
            console.error('删除回复失败:', error)
            throw error
        }
    }

    return { posts, availableTags, pagination, fetchPosts, fetchTags, createTag, uploadImage, uploadImages, deletePost, createPost, updatePost, createReply, fetchReplies, deleteReply }
})