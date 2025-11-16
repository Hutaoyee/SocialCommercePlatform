import apiClient from './axios';

export const communicateAPI = {
  
    // 获取帖子列表
    getPosts(params = {}) {
        return apiClient.get('/forum/posts/', { params });
    },

    // 创建帖子
    createPost(data) {
        return apiClient.post('/forum/posts/', data);
    },

    // 更新帖子
    updatePost(postId, data) {
        return apiClient.put(`/forum/posts/${postId}/`, data);
    },

    // 删除帖子
    deletePost(postId) {
        return apiClient.delete(`/forum/posts/${postId}/`);
    },

    // 获取标签列表
    getTags(params = {}) {
        return apiClient.get('/forum/tags/', { params });
    },

    // 创建标签
    createTag(data) {
        return apiClient.post('/forum/tags/', data);
    },

    // 上传图片
    uploadImage(formData) {
        return apiClient.post('/forum/images/', formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
        });
    },

    // 获取回复列表
    getReplies(params = {}) {
        return apiClient.get('/forum/replies/', { params });
    },

    // 创建回复
    createReply(data) {
        return apiClient.post('/forum/replies/', data);
    },

    // 删除回复
    deleteReply(replyId) {
        return apiClient.delete(`/forum/replies/${replyId}/`);
    }
};