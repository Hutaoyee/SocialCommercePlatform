import axios from './axios'

export const ownedProductAPI = {
    // 获取我拥有的商品列表
    getMyProducts(token) {
        return axios.get('/shopping/owned-products/', {
            headers: { Authorization: `Bearer ${token}` }
        })
    },

    // 删除拥有记录
    deleteProduct(id, token) {
        return axios.delete(`/shopping/owned-products/${id}/`, {
            headers: { Authorization: `Bearer ${token}` }
        })
    }
}

export default ownedProductAPI
