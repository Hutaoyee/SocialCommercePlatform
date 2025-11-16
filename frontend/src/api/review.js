import axios from './axios'

export const reviewAPI = {
    // 获取我的评价列表
    getMyReviews(token) {
        return axios.get('/shopping/order-reviews/', {
            headers: { Authorization: `Bearer ${token}` }
        })
    },

    // 创建评价（支持图片上传）
    createReview(data, token) {
        const formData = new FormData()
        
        // 添加基本字段
        Object.keys(data).forEach(key => {
            if (key === 'uploaded_images' && data[key]) {
                // 添加图片文件
                data[key].forEach(file => {
                    formData.append('uploaded_images', file)
                })
            } else if (data[key] !== null && data[key] !== undefined) {
                formData.append(key, data[key])
            }
        })
        
        return axios.post('/shopping/order-reviews/', formData, {
            headers: { 
                Authorization: `Bearer ${token}`,
                'Content-Type': 'multipart/form-data'
            }
        })
    },

    // 更新评价（支持图片上传）
    updateReview(id, data, token) {
        const formData = new FormData()
        
        // 添加基本字段
        Object.keys(data).forEach(key => {
            if (key === 'uploaded_images' && data[key]) {
                // 添加图片文件
                data[key].forEach(file => {
                    formData.append('uploaded_images', file)
                })
            } else if (data[key] !== null && data[key] !== undefined) {
                formData.append(key, data[key])
            }
        })
        
        return axios.put(`/shopping/order-reviews/${id}/`, formData, {
            headers: { 
                Authorization: `Bearer ${token}`,
                'Content-Type': 'multipart/form-data'
            }
        })
    },

    // 删除评价
    deleteReview(id, token) {
        return axios.delete(`/shopping/order-reviews/${id}/`, {
            headers: { Authorization: `Bearer ${token}` }
        })
    },

    // 删除评价图片
    deleteReviewImage(reviewId, imageId, token) {
        return axios.delete(`/shopping/order-reviews/${reviewId}/images/${imageId}/`, {
            headers: { Authorization: `Bearer ${token}` }
        })
    }
}

export default reviewAPI
