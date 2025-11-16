<template>
  <div class="home-container">
    <FallingStarsBg      
      class="falling-stars-background bg-white dark:bg-black"
      :color="isDark ? '#FFF' : '#555'"
    />

    <div class="content-layer">
      <div class="container">
        <div class="columns">
          <router-link class="nav-card" to="/merch">
            
          <div class="column">
            <section class="hero is-danger is-halfheight"
            :class="{ 'hovered': isHovered }"
            @mouseover="isHovered = true"
            @mouseleave="isHovered = false"
            >
              <div class="hero-body">
                <div class="">
                  <p class="title">Merch</p>
                </div>
              </div>
            </section>
          </div>
          </router-link>
          
          <router-link class="nav-card" to="/publication">

          <div class="column">
            <section class="hero is-warning is-halfheight"
            :class="{ 'hovered': isHovered2 }"
            @mouseover="isHovered2 = true"
            @mouseleave="isHovered2 = false"
            >
              <div class="hero-body">
                <div class="">
                  <p class="title">Publication</p>
                </div>
              </div>
            </section>
          </div>
          </router-link>

          <router-link class="nav-card" to="/communicate">

          <div class="column">
            <section class="hero is-success is-halfheight"
            :class="{ 'hovered': isHovered3 }"
            @mouseover="isHovered3 = true"
            @mouseleave="isHovered3 = false"
            >
              <div class="hero-body">
                <div class="">
                  <p class="title">Communicate</p>
                </div>
              </div>
            </section>
          </div>
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { useColorMode } from "@vueuse/core";
  import { onMounted, onUnmounted, ref, computed } from 'vue';

  import FallingStarsBg from '@/components/FallingStarsBg.vue';

  const isHovered = ref(false);
  const isHovered2 = ref(false);
  const isHovered3 = ref(false);

  const isDark = computed(() => useColorMode().value == "dark");

  onMounted(async () => {
    document.documentElement.classList.add('home-page-active')
    document.body.classList.add('home-page-active')
    document.getElementById('app')?.classList.add('home-page-active')
  })

  onUnmounted(() => {
    document.documentElement.classList.remove('home-page-active')
    document.body.classList.remove('home-page-active')
    document.getElementById('app')?.classList.remove('home-page-active')
  })
</script>

<style>
    
    html.home-page-active,
    body.home-page-active{
      justify-content: start;
      align-items: start;
      overflow: hidden;
      height: 100vh;
      margin: 0;
      padding: 0;
    }

    #app.home-page-active{
      display: flex;
      width: 100%;
      height: 100vh;
      padding: 0;
      overflow: hidden;
    }
</style>

<style scoped>
  .home-container {
    position: relative;
    width: 100vw;
    height: 100vh;
    overflow: hidden;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .falling-stars-background {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: 0;
    pointer-events: none;
  }

  .content-layer {
    position: relative;
    z-index: 1;
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .container {
    width: auto;
    max-width: 1400px;
  }

  .columns {
    display: flex;
    gap: 2rem;
    align-items: center;
    justify-content: center;
  }

  .nav-card {
    opacity: 0.75;
    transition: opacity 0.3s ease;
  }

  .nav-card:hover {
    opacity: 1;
  }

  .hero {
    border-radius: 100%;
    /* 添加平滑过渡，应用于所有状态 */
    transition: all 1.5s ease;
  }

  .hero.hovered {
    background-color: #000000;
    box-shadow: -4px -4px 5px rgba(0,209,178);
    border-radius: 0%;
  }

  .title {

    width: 240px;
  }
</style>