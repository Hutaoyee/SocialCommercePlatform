import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },

    {
      path: '/about',
      name: 'about',
      // route level code-splitting
      // this generates a separate chunk (About.[hash].js) for this route
      // which is lazy-loaded when the route is visited.
      component: () => import('../views/AboutView.vue'),
    },

    {
      path: '/login',
      name: 'Login',
      component: () => import('../views/Login.vue')
    },

    {
      path: '/register',
      name: 'Register',
      component: () => import('../views/Register.vue')
    },

    {
      path: '/myself',
      name: 'Myself',
      component: () => import('../views/Myself.vue')
    },

    {
      path: '/merch',
      name: 'Merch',
      component: () => import('../views/Merch.vue')
    },

    {
      path: '/checkout',
      name: 'Checkout',
      component: () => import('../views/Checkout.vue'),
      meta: { requiresAuth: true }
    },

    {
      path: '/publication',
      name: 'Publication',
      component: () => import('../views/Publication.vue')
    },

    {
      path: '/communicate',
      name: 'Communicate',
      component: () => import('../views/Communicate.vue')
    },

    {
      path: '/order-success',
      name: 'OrderSuccess',
      component: () => import('../views/OrderSuccess.vue')
    },
  ],
})

export default router