<template>
  <view class="page-shell order-page">
    <view class="order-header">
      <view class="header-top">
        <view class="mode-tabs"><text :class="{ active: state.orderMode === 'pickup' }" @click="setOrderMode('pickup')">自取</text><text class="divider">|</text><text :class="{ active: state.orderMode === 'dineIn' }" @click="setOrderMode('dineIn')">堂食</text></view>
      </view>
      <view class="store-line" @click="goStores"><text class="store-pin">⌖</text><text class="header-store">{{ currentStore.shortName }}</text><text class="store-distance">{{ currentStore.distance < 1000 ? `${currentStore.distance}m` : `${(currentStore.distance / 1000).toFixed(1)}km` }}</text><text class="store-arrow">›</text></view>
      <view class="search-box"><text>⌕</text><input v-model="keyword" placeholder="搜索档口或餐品"/><text v-if="keyword" @click="keyword = ''">×</text></view>
    </view>

    <view class="menu-shell">
      <scroll-view scroll-y class="category-side" :show-scrollbar="false">
        <view v-for="stall in state.stalls" :key="stall.id" :class="['category-item', { active: activeStall === stall.id }]" @click="activeStall = stall.id">{{ stall.name }}</view>
      </scroll-view>
      <scroll-view scroll-y class="menu-content" :show-scrollbar="false">
        <view v-if="!keyword" class="category-banner"><view><view class="banner-kicker">{{ activeStallInfo.name }}</view><view class="banner-copy">{{ activeStallInfo.description }} · 约 {{ currentStore.waitMinutes }} 分钟</view></view></view>
        <view class="menu-title"><text class="menu-title-main">{{ keyword ? `“${keyword}”的搜索结果` : '本档口餐品' }}</text><text class="menu-title-count">{{ filteredProducts.length }} 道</text></view>
        <ProductCard v-for="product in filteredProducts" :key="product.id" :product="product" @open="openProduct" @add="quickAdd" />
        <EmptyState v-if="!filteredProducts.length" title="未检索到相关餐品" description="请调整搜索关键词" action="重置搜索" @action="keyword = ''" />
        <view class="menu-spacer" />
      </scroll-view>
    </view>

    <view v-if="cartCount" class="cart-bar">
      <view class="cart-round" @click="showCart = true"><text class="cart-label">购物车</text><text class="cart-count">{{ cartCount }}</text></view>
      <view class="cart-price" @click="showCart = true"><view>{{ formatMoney(cartSubtotal) }}</view><text>已选 {{ cartCount }} 件</text></view>
      <button class="checkout" @click="checkout">去结算</button>
    </view>

    <view v-if="showCart" class="drawer-mask" @click="showCart = false"></view>
    <view class="cart-drawer" :class="{ show: showCart }">
      <view class="drawer-handle"></view><view class="drawer-header"><view><text class="drawer-title">购物车</text><text class="drawer-sub">{{ currentStore.shortName }}</text></view><text class="clear-cart" @click="clearCart">清空</text></view>
      <scroll-view scroll-y class="drawer-list" :style="{ height: drawerListHeight + 'px' }">
        <view v-for="item in state.cart" :key="item.key" class="cart-item">
          <image class="cart-visual" :src="item.image" mode="aspectFill" /><view class="cart-info"><view class="cart-name">{{ item.name }}</view><view class="cart-stall">{{ item.stallName }}</view><view class="cart-options">{{ optionText(item) || '标准制作' }}</view><view class="price">{{ formatMoney(item.unitPriceCents) }}</view></view>
          <view class="stepper"><button @click="updateCartQuantity(item.key, item.quantity - 1)">−</button><text>{{ item.quantity }}</text><button @click="updateCartQuantity(item.key, item.quantity + 1)">＋</button></view>
        </view>
      </scroll-view>
      <view class="drawer-footer"><view><text class="muted">合计 </text><text class="drawer-total">{{ formatMoney(cartSubtotal) }}</text></view><button class="primary-button" @click="checkout">确认结算</button></view>
    </view>
  </view>
</template>

<script setup>
import { computed, ref } from 'vue'
import ProductCard from '@/component/ProductCard.vue'
import EmptyState from '@/component/EmptyState.vue'
import { useAppStore } from '@/store/app'
import { formatMoney } from '@/utils/format'

const keyword = ref('')
const showCart = ref(false)
const windowHeight = uni.getSystemInfoSync().windowHeight
const drawerListHeight = Math.floor(windowHeight * 0.46)
const { state, currentStore, cartCount, cartSubtotal, setOrderMode, setStall, addToCart, updateCartQuantity, clearCart } = useAppStore()
const activeStall = computed({ get: () => state.selectedStallId || state.stalls[0]?.id, set: (value) => setStall(value) })
const activeStallInfo = computed(() => state.stalls.find((item) => item.id === activeStall.value) || state.stalls[0])
const filteredProducts = computed(() => { const key = keyword.value.trim().toLowerCase(); return key ? state.products.filter((product) => `${product.name}${product.subtitle}${product.badge}${product.stallName}`.toLowerCase().includes(key)) : state.products.filter((product) => product.stallId === activeStall.value) })
const quickAdd = (product) => { if (!product.isActive) { uni.showToast({ title: '该商品已售罄', icon: 'none' }); return } if (product.options.length) openProduct(product); else { addToCart(product.id); uni.showToast({ title: '已加入购物车', icon: 'success' }) } }
const openProduct = (product) => { if (!product.isActive) { uni.showToast({ title: '该商品已售罄', icon: 'none' }); return } uni.navigateTo({ url: `/pages/item-detail/index?id=${product.id}` }) }
const optionText = (item) => item.selectedOptions.map((option) => option.name).join(' / ')
const checkout = () => { if (!state.cart.length) return; showCart.value = false; uni.navigateTo({ url: '/pages/confirm-order/index' }) }
const goStores = () => uni.switchTab({ url: '/pages/shop/index' })
</script>

<style scoped lang="scss">
.order-page{height:100vh;overflow:hidden;padding:0;background:#fff}.order-header{position:relative;z-index:8;padding:calc(58rpx + env(safe-area-inset-top)) 26rpx 18rpx;background:rgba(255,255,255,.98);box-shadow:0 8rpx 24rpx rgba(18,34,78,.08)}.header-top{display:flex;align-items:center;justify-content:space-between}.mode-tabs{display:flex;align-items:center;color:#a4a6ac;font-size:28rpx;font-weight:600}.mode-tabs text{margin-right:14rpx}.mode-tabs .active{color:var(--ink);font-size:34rpx;font-weight:800}.mode-tabs .divider{color:#d5d7dc;font-weight:400}.store-line{display:flex;align-items:center;margin-top:22rpx}.store-line text{margin-right:9rpx}.store-pin{color:var(--brand);font-size:31rpx}.header-store{max-width:380rpx;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-size:24rpx;font-weight:700}.store-distance{color:#34363c;font-size:20rpx}.store-arrow{color:#676a72;font-size:34rpx}.search-box{display:flex;align-items:center;height:66rpx;margin-top:18rpx;padding:0 20rpx;border-radius:14rpx;background:#f3f4f6}.search-box text{margin-right:13rpx}.search-box input{flex:1;font-size:22rpx}.menu-shell{display:flex;height:calc(100vh - 306rpx - env(safe-area-inset-top) - env(safe-area-inset-bottom));min-height:560rpx;background:#fff}.category-side{width:154rpx;flex:0 0 154rpx;height:100%;background:#f2f3f5}.category-item{position:relative;display:flex;align-items:center;justify-content:center;min-height:104rpx;padding:16rpx 10rpx;color:#62656d;font-size:21rpx;text-align:center}.category-item.active{color:#1f2228;background:#fff;font-weight:800}.category-item.active::before{content:'';position:absolute;left:0;top:26rpx;bottom:26rpx;width:7rpx;border-radius:0 5rpx 5rpx 0;background:var(--brand)}.hot{margin-right:4rpx;font-size:22rpx}.menu-content{flex:1;height:100%;padding:18rpx 18rpx 0;background:#fff}.category-banner{display:flex;align-items:center;justify-content:space-between;min-height:112rpx;padding:20rpx 22rpx;border-radius:20rpx;color:#fff;background:linear-gradient(120deg,#0637c9,#10266f);box-shadow:0 10rpx 24rpx rgba(6,55,201,.16)}.banner-kicker{font-size:27rpx;font-weight:800}.banner-copy{margin-top:6rpx;color:rgba(255,255,255,.72);font-size:18rpx}.menu-title{display:flex;justify-content:space-between;margin:22rpx 3rpx 12rpx;font-size:27rpx;font-weight:800}.menu-title-count{color:var(--muted);font-size:18rpx;font-weight:400}.menu-spacer{height:180rpx}
.cart-bar{position:fixed;z-index:20;left:24rpx;right:24rpx;bottom:calc(110rpx + env(safe-area-inset-bottom));display:flex;align-items:center;height:96rpx;padding:10rpx 10rpx 10rpx 22rpx;border-radius:26rpx;color:#fff;background:#20242b;box-shadow:0 18rpx 40rpx rgba(18,29,57,.26)}.cart-round{position:relative;min-width:82rpx}.cart-label{font-size:20rpx;font-weight:700}.cart-count{position:absolute;right:-2rpx;top:-20rpx;display:flex;align-items:center;justify-content:center;min-width:30rpx;height:30rpx;padding:0 7rpx;border-radius:15rpx;background:var(--danger);font-size:17rpx}.cart-price{flex:1;margin-left:16rpx;font-size:30rpx;font-weight:700}.cart-price text{display:block;margin-top:2rpx;color:rgba(255,255,255,.6);font-size:18rpx;font-weight:400}.checkout{display:flex;align-items:center;justify-content:center;height:76rpx;padding:0 32rpx;border-radius:18rpx;color:#fff;background:var(--brand);font-size:26rpx;font-weight:700}
.drawer-mask { position:fixed; z-index:30; left:0; top:0; right:0; bottom:0; background:rgba(39,26,20,.45); }.cart-drawer { position:fixed; z-index:31; left:0; right:0; bottom:0; max-height:74vh; padding:14rpx 28rpx calc(28rpx + env(safe-area-inset-bottom)); border-radius:34rpx 34rpx 0 0; background:#fff; transform:translateY(110%); transition:transform .25s ease; }.cart-drawer.show { transform:translateY(0); }.drawer-handle { width:80rpx; height:8rpx; margin:0 auto 18rpx; border-radius:4rpx; background:#ddd4cc; }.drawer-header { display:flex; justify-content:space-between; align-items:center; padding:10rpx 0 20rpx; }.drawer-title { font-size:34rpx; font-weight:700; }.drawer-sub { margin-left:14rpx; color:var(--muted); font-size:20rpx; }.clear-cart { color:var(--muted); font-size:22rpx; }.cart-item { display:flex; align-items:center; padding:20rpx 0; border-bottom:1rpx solid var(--line); }.cart-visual { width:100rpx;height:100rpx;flex:0 0 100rpx;margin-right:18rpx;border-radius:20rpx;background:var(--oat-100) }.cart-info { min-width:0; flex:1; }.cart-name { font-size:26rpx; font-weight:700; }.cart-options { margin:7rpx 0; overflow:hidden; color:var(--muted); font-size:19rpx; text-overflow:ellipsis; white-space:nowrap; }.stepper { display:flex; align-items:center; }.stepper button { width:46rpx;height:46rpx;padding:0;margin-right:16rpx;display:flex;align-items:center;justify-content:center;border:1rpx solid var(--line);border-radius:50%;line-height:1;font-size:25rpx }.stepper text { min-width:24rpx; margin-right:16rpx; text-align:center; }.drawer-footer { display:flex; align-items:center; justify-content:space-between; padding-top:24rpx; }.drawer-total { font-size:36rpx; font-weight:700; }.drawer-footer .primary-button { min-height:76rpx; font-size:25rpx; }
@media screen and (min-width:760px) { .cart-bar { left:50%; right:auto; width:700px; transform:translateX(-50%); }.cart-drawer { left:50%; right:auto; width:750px; transform:translate(-50%,110%); }.cart-drawer.show { transform:translate(-50%,0); } }
.cart-stall{margin-top:6rpx;color:var(--brand);font-size:18rpx}
</style>
