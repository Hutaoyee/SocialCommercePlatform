<script setup lang="ts">
import { onMounted } from 'vue'
import { RouterLink, RouterView } from 'vue-router'

import Navbar from './components/Navbar.vue'
import PageLoader from './components/PageLoader.vue'

import { useCartStore } from './stores/cart'
import { useUserStore } from './stores/user'

const cartStore = useCartStore()
const userStore = useUserStore()

// 应用启动时加载购物车数据
onMounted(() => {
  if (userStore.isLoggedIn) {
    cartStore.fetchCartItems()
  }
})
</script>

<template>

  <Navbar />

  <RouterView />

  <PageLoader />

</template>

<style scoped>

</style>