import axios from './axios'

// 分类相关API
export const category = {
  // 获取所有分类
  getCategories() {
    return axios.get('/shopping/categories/')
  }
}

// SPU相关API
export const shopping = {
  // 获取SPU列表（支持分页和搜索）
  getSPUList(params = {}) {
    return axios.get('/shopping/spu/', { params })
  },

  // 获取SPU详情
  getSPUDetail(id) {
    return axios.get(`/shopping/spu/${id}/`)
  },

  // 获取SPU的SKU信息
  getSPUSKUs(id) {
    return axios.get(`/shopping/spu/${id}/skus/`)
  },

  // 获取SPU的评论
  getSPUReviews(id) {
    return axios.get(`/shopping/spu/${id}/reviews/`)
  },

  // 创建商品评论
  createReview(data) {
    return axios.post('/shopping/reviews/', data)
  },

  // 删除商品评论
  deleteReview(id) {
    return axios.delete(`/shopping/reviews/${id}/`)
  },

  // 切换收藏状态
  toggleFavorite(productId) {
    return axios.post(`/shopping/products/${productId}/favorite/`)
  },

  // 检查收藏状态
  checkFavorite(productId) {
    return axios.get(`/shopping/products/${productId}/check-favorite/`)
  },

  // 获取用户收藏的商品列表
  getFavorites(params = {}) {
    return axios.get('/product-favorites/', { params })
  }
}

// 购物车相关API
export const cart = {
  // 获取购物车列表
  getCartItems() {
    return axios.get('/cart/')
  },

  // 添加到购物车
  addToCart(data) {
    return axios.post('/cart-add/', data)
  },

  // 更新购物车商品数量
  updateQuantity(cartItemId, quantity) {
    return axios.patch(`/cart-update/${cartItemId}/`, { quantity })
  },

  // 从购物车移除商品
  removeFromCart(cartItemId) {
    return axios.delete(`/cart-remove/${cartItemId}/`)
  },

  // 批量删除购物车商品
  batchRemoveFromCart(cartItemIds) {
    return axios.post('/cart-batch-remove/', { cart_item_ids: cartItemIds })
  }
}
