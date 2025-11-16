import axios from 'axios';

// 后端 API 地址
const API_BASE_URL = `${import.meta.env.VITE_API_BASE_URL}`;;

// 创建统一的 axios 实例
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
});

// 添加请求拦截器，自动附加 token（如果存在）
apiClient.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  error => Promise.reject(error)
);

// 添加响应拦截器，处理 401 错误（token 过期或无效）
apiClient.interceptors.response.use(
  response => response,
  error => {
    // 如果是 401 错误且有 token，说明 token 已过期
    if (error.response?.status === 401 && localStorage.getItem('token')) {
      console.warn('Token 已过期或无效，清除本地 token');
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      
      // 可选：刷新页面或重新发起请求（不带 token）
      // 这里我们选择静默处理，让下次请求自动不带 token
    }
    return Promise.reject(error);
  }
);

export default apiClient;
