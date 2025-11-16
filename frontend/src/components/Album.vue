<template>
    <div v-if="albums.length === 0">暂无专辑</div>

    <div v-else class="is-flex is-flex-wrap-wrap is-justify-content-center">

        <div v-for="album in albums" :key="album.id" class="box box-size m-3 has-text-centered">

            <figure class="image image-size is-1by1">
                <img :src="album.cover_image" alt="" @click="openModal(album)" />
            </figure>
            <p class="title is-5 m-1" @click="openModal(album)">{{ album.name }}</p>
            <p class="subtitle is-6">
                <!-- <span class="has-text-weight-bold">{{ album.artist.name }}</span> |  -->
                {{ album.release_date }}
            </p>
        </div>
    </div>

    <div class="modal" :class="{ 'is-active': isModalActive }">
        <div class="modal-background" @click="closeModal"></div>
        <div class="modal-content ">
            
            <div v-if="isnotpublic" class="box">
                <p class="title has-text-centered">COMING SOON</p>
            </div>
            
            <div v-else-if="selectedAlbum && dynamicPlaylistId && isModalActive">
                <iframe @load="onIframeLoaded" data-testid="embed-iframe" style="border-radius:12px" :src="`https://open.spotify.com/embed/album/${dynamicPlaylistId}?utm_source=generator`" width="100%" height="352" frameBorder="0" allowfullscreen="" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" loading="lazy"></iframe>
                
                <div v-if="isIframeLoaded" class="mt-3">
                    <button 
                        class="button is-success is-fullwidth" 
                        @click="handleBuyAlbum"
                        :disabled="!selectedAlbum.product_info">
                        {{ selectedAlbum.product_info ? '购买专辑' : '暂无商品' }}
                    </button>
                </div>
            </div>
        </div>
    </div>

    <!-- SKU选择模态框 -->
    <div class="modal modal-sku" :class="{ 'is-active': skuModal.show }">
        <div class="modal-background" @click="closeSKUModal"></div>
        <div class="modal-card">
            <header class="modal-card-head">
                <p class="modal-card-title">选择专辑规格</p>
                <button class="delete" aria-label="close" @click="closeSKUModal"></button>
            </header>
            <section class="modal-card-body">
                <div v-if="skuModal.loading" class="has-text-centered py-6">
                    <span class="icon is-large">
                        <i class="fas fa-spinner fa-pulse fa-2x"></i>
                    </span>
                </div>
                
                <div v-else-if="skuModal.product">
                    <!-- 商品图片 - 根据选中的SKU显示 -->
                    <div class="mb-4">
                        <figure class="image is-4by3">
                            <img :src="getDisplayImage()" 
                                 :alt="skuModal.product.name" 
                                 style="object-fit: cover; border-radius: 8px;">
                        </figure>
                    </div>
                    
                    <h2 class="title is-5">{{ skuModal.product.name }}</h2>
                    <p class="subtitle is-6 has-text-grey mb-4">{{ skuModal.product.description }}</p>
                    
                    <!-- 属性选择 -->
                    <div v-for="attr in skuModal.attributes" :key="attr.id" class="mb-4">
                        <label class="label">{{ attr.name }}</label>
                        <div class="buttons">
                            <button 
                                v-for="value in attr.values" 
                                :key="value.id"
                                class="button is-rounded"
                                :class="{ 'is-primary is-selected': skuModal.selectedAttrs[attr.id] === value.id }"
                                @click="selectAttribute(attr.id, value.id)">
                                {{ value.value }}
                            </button>
                        </div>
                    </div>
                    
                    <!-- 选中的SKU信息 -->
                    <div v-if="selectedSKU" class="box">
                        <p class="mb-2"><strong>价格：</strong><span class="has-text-danger is-size-4">¥{{ selectedSKU.price }}</span></p>
                        <p class="mb-3"><strong>库存：</strong>{{ selectedSKU.stock }} 件</p>
                        
                        <div class="field is-horizontal">
                            <div class="field-label is-normal">
                                <label class="label">数量</label>
                            </div>
                            <div class="field-body">
                                <div class="field has-addons">
                                    <p class="control">
                                        <button class="button" @click="decreaseQuantity" :disabled="skuModal.quantity <= 1">
                                            <span class="icon">
                                                <i class="fas fa-minus"></i>
                                            </span>
                                        </button>
                                    </p>
                                    <p class="control">
                                        <input 
                                            class="input quantity-input" 
                                            type="number" 
                                            v-model.number="skuModal.quantity" 
                                            min="1" 
                                            :max="selectedSKU.stock" 
                                            style="width: 80px; text-align: center;">
                                    </p>
                                    <p class="control">
                                        <button class="button" @click="increaseQuantity" :disabled="skuModal.quantity >= selectedSKU.stock">
                                            <span class="icon">
                                                <i class="fas fa-plus"></i>
                                            </span>
                                        </button>
                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div v-else class="notification is-warning is-light">
                        <p>请选择完整的商品规格</p>
                    </div>
                </div>
            </section>
            <footer class="modal-card-foot">
                <button 
                    class="button is-success mr-3" 
                    @click="addToCart" 
                    :disabled="!selectedSKU || skuModal.submitting"
                    :class="{ 'is-loading': skuModal.submitting }">
                    加入购物车
                </button>
                <button class="button" @click="closeSKUModal">取消</button>
            </footer>
        </div>
    </div>
</template>

<script setup>
    import { storeToRefs } from 'pinia'
    import { useAlbumsStore } from '@/stores/albums'
    import { useCartStore } from '@/stores/cart'
    import { useProductsStore } from '@/stores/products'
    import { ref, computed, onMounted } from 'vue'

    const albumStore = useAlbumsStore()
    const cartStore = useCartStore()
    const productsStore = useProductsStore()
    const { albums } = storeToRefs(albumStore)

    const isModalActive = ref(false)
    const selectedAlbum = ref(null)
    const isnotpublic = ref(false)
    const isIframeLoaded = ref(false)
    
    // SKU模态框状态
    const skuModal = ref({
        show: false,
        product: null,
        attributes: [],
        skus: [],
        selectedAttrs: {},
        quantity: 1,
        loading: false,
        submitting: false
    })

    const openModal = (album) => {
        selectedAlbum.value = album
        isModalActive.value = true
        isIframeLoaded.value = false
        isnotpublic.value = album.name === 'BULLY'
    }

    const closeModal = () => {
        isModalActive.value = false
        selectedAlbum.value = null
        isIframeLoaded.value = false
    }

    const onIframeLoaded = () => {
         isIframeLoaded.value = true
    }

    // 处理购买专辑
    const handleBuyAlbum = async () => {
        if (!selectedAlbum.value || !selectedAlbum.value.product_info) {
            alert('该专辑暂无关联商品')
            return
        }
        
        const productInfo = selectedAlbum.value.product_info
        
        // 打开模态框并加载SKU数据
        skuModal.value.show = true
        skuModal.value.loading = true
        skuModal.value.product = productInfo
        skuModal.value.selectedAttrs = {}
        skuModal.value.quantity = 1
        
        try {
            // 获取商品的SKU数据
            const skuData = await productsStore.getSPUSKUs(productInfo.id)
            skuModal.value.attributes = skuData.attributes || []
            skuModal.value.skus = skuData.skus || []
        } catch (error) {
            console.error('加载SKU数据失败:', error)
            alert('加载商品信息失败')
            closeSKUModal()
        } finally {
            skuModal.value.loading = false
        }
    }
    
    // 选择属性
    const selectAttribute = (attrId, valueId) => {
        skuModal.value.selectedAttrs[attrId] = valueId
    }
    
    // 计算选中的SKU
    const selectedSKU = computed(() => {
        if (!skuModal.value.skus || skuModal.value.skus.length === 0) {
            return null
        }
        
        // 如果没有属性,返回第一个SKU
        if (skuModal.value.attributes.length === 0) {
            return skuModal.value.skus[0]
        }
        
        // 检查是否所有属性都已选择
        const allSelected = skuModal.value.attributes.every(
            attr => skuModal.value.selectedAttrs[attr.id] !== undefined
        )
        
        if (!allSelected) {
            return null
        }
        
        // 查找匹配的SKU
        return skuModal.value.skus.find(sku => {
            return Object.keys(skuModal.value.selectedAttrs).every(
                attrId => sku.attributes[attrId] === skuModal.value.selectedAttrs[attrId]
            )
        })
    })
    
    // 获取要显示的图片
    const getDisplayImage = () => {
        // 优先显示选中SKU的图片
        if (selectedSKU.value && selectedSKU.value.image) {
            return selectedSKU.value.image
        }
        // 其次显示第一个SKU的图片
        if (skuModal.value.skus && skuModal.value.skus.length > 0 && skuModal.value.skus[0].image) {
            return skuModal.value.skus[0].image
        }
        // 最后使用产品的默认图片（如果有的话）
        if (skuModal.value.product && skuModal.value.product.image) {
            return skuModal.value.product.image
        }
        // 如果都没有，返回默认图片
        return '/default-product.png'
    }
    
    // 增加数量
    const increaseQuantity = () => {
        if (selectedSKU.value && skuModal.value.quantity < selectedSKU.value.stock) {
            skuModal.value.quantity++
        }
    }
    
    // 减少数量
    const decreaseQuantity = () => {
        if (skuModal.value.quantity > 1) {
            skuModal.value.quantity--
        }
    }
    
    // 添加到购物车
    const addToCart = async () => {
        if (!selectedSKU.value) {
            alert('请选择完整的商品规格')
            return
        }
        
        skuModal.value.submitting = true
        try {
            const success = await cartStore.addItem(selectedSKU.value.sku_code, skuModal.value.quantity)
            if (success) {
                alert('已成功添加到购物车！')
                closeSKUModal()
            }
        } catch (error) {
            console.error('加入购物车失败:', error)
            alert('添加失败，请重试')
        } finally {
            skuModal.value.submitting = false
        }
    }
    
    // 关闭SKU模态框
    const closeSKUModal = () => {
        skuModal.value.show = false
        skuModal.value.product = null
        skuModal.value.attributes = []
        skuModal.value.skus = []
        skuModal.value.selectedAttrs = {}
        skuModal.value.quantity = 1
        skuModal.value.loading = false
        skuModal.value.submitting = false
    }

    // Spotify Playlist IDs for albums
    const playlistMap = {
        'The College Dropout': '4Uv86qWpGTxf7fU7lG5X6F',
        'Late Registration': '5ll74bqtkcXlKE7wwkMq4g',
        'Graduation': '4SZko61aMnmgvNhfhgTuD3',
        '808s & Heartbreak': '3WFTGIO6E3Xh4paEOBY9OU',
        'My Beautiful Dark Twisted Fantasy': '20r762YmB5HeofjMCiPMLv',
        'Watch The Throne': '2if1gb3t6IkhiKzrtS9Glc',
        'Yeezus': '7D2NdGvBHIavgLhmcwhluK',
        'The Life Of Pablo': '7gsWAHLeT0w7es6FofOXk1',
        'ye': '2Ek1q2haOnxVqhvVKqMvJe',
        'KIDS SEE GHOSTS': '6pwuKxMUkNg673KETsXPUV',
        'JESUS IS KING': '0FgZKfoU2Br5sHOfvZKTI9',
        'Donda': '2Wiyo7LzdeBCsVZiRA6vVZ',
        'VULTURES 1': '4DOsPwJtokv6HEifZ6t5j6',
        'VULTURES 2': '5RV2TNyjylqWJNxQyHBTeJ',
        'DONDA 2': '1ZkGNUz1un0b3Z7EsJl3ci'
    }

    const dynamicPlaylistId = computed(() => {
        const a = selectedAlbum.value
        if (!a || !a.name) return ''
        return playlistMap[a.name] || ''
    })

    onMounted(() => {
        albumStore.fetchAlbums()
    })
</script>

<style lang="scss" scoped>
.box-size {
    width: 20%;
}

.image-size {
    width: 100%;
}

/* SKU模态框样式 */
.modal-sku {
    .modal-card {
        max-width: 600px;
        width: 90%;
    }
    
    .modal-card-body {
        max-height: 70vh;
        overflow-y: auto;
        
        &::-webkit-scrollbar {
            width: 6px;
        }
        
        &::-webkit-scrollbar-track {
            background: transparent;
        }
        
        &::-webkit-scrollbar-thumb {
            background: rgba(0, 209, 175, 1);
            border-radius: 3px;
        }
    }
    
    .button.is-selected {
        font-weight: bold;
    }
    
    .quantity-input {
        &::-webkit-outer-spin-button,
        &::-webkit-inner-spin-button {
            -webkit-appearance: none;
            margin: 0;
        }
        -moz-appearance: textfield;
        appearance: textfield;
    }
}
</style>
