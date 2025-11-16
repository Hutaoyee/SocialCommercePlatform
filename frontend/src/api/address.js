import axios from './axios'

export const addressAPI = {
    // 获取地址列表
    getAddresses(token) {
        return axios.get('/addresses/', {
            headers: { Authorization: `Bearer ${token}` }
        })
    },

    // 创建地址
    createAddress(data, token) {
        return axios.post('/addresses/', data, {
            headers: { Authorization: `Bearer ${token}` }
        })
    },

    // 更新地址
    updateAddress(id, data, token) {
        return axios.put(`/addresses/${id}/`, data, {
            headers: { Authorization: `Bearer ${token}` }
        })
    },

    // 删除地址
    deleteAddress(id, token) {
        return axios.delete(`/addresses/${id}/`, {
            headers: { Authorization: `Bearer ${token}` }
        })
    },

    // 设置默认地址
    setDefaultAddress(id, token) {
        return axios.post(`/addresses/${id}/set-default/`, {}, {
            headers: { Authorization: `Bearer ${token}` }
        })
    }
}
