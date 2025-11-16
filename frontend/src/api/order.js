import axios from './axios'

export const orderAPI = {
    // 获取订单列表
    getOrders(params, token) {
        return axios.get('/shopping/orders/', {
            params,
            headers: { Authorization: `Bearer ${token}` }
        })
    },

    // 获取订单详情
    getOrderDetail(id, token) {
        return axios.get(`/shopping/orders/${id}/`, {
            headers: { Authorization: `Bearer ${token}` }
        })
    },

    // 创建订单
    createOrder(data, token) {
        return axios.post('/shopping/orders/', data, {
            headers: { Authorization: `Bearer ${token}` }
        })
    },

    // 取消订单
    cancelOrder(id, token) {
        return axios.post(`/shopping/orders/${id}/cancel/`, {}, {
            headers: { Authorization: `Bearer ${token}` }
        })
    },

    // 申请退款
    requestRefund(id, data, token) {
        return axios.post(`/shopping/orders/${id}/request_refund/`, data, {
            headers: { Authorization: `Bearer ${token}` }
        })
    },

    // 确认收货
    confirmDelivery(id, token) {
        return axios.post(`/shopping/orders/${id}/confirm_delivery/`, {}, {
            headers: { Authorization: `Bearer ${token}` }
        })
    },

    // 支付订单（模拟支付）
    payOrder(id, token) {
        return axios.post(`/shopping/orders/${id}/pay/`, {}, {
            headers: { Authorization: `Bearer ${token}` }
        })
    },

    // 确认收货（旧接口兼容）
    confirmOrder(id, token) {
        return axios.post(`/shopping/orders/${id}/confirm/`, {}, {
            headers: { Authorization: `Bearer ${token}` }
        })
    },

    // 获取我的订单
    getMyOrders(token) {
        return axios.get('/shopping/orders/', {
            headers: { Authorization: `Bearer ${token}` }
        })
    }
}

export default orderAPI
