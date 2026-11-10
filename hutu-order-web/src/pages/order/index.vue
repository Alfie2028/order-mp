<template>
  <view class="page-shell order-page">
    <view class="order-header" :style="{ paddingTop: (navLayout.capsuleTop + 4) + 'px' }">
      <view class="header-top" :style="{ paddingRight: (navLayout.capsuleRight || 12) + 'px' }">
        <view class="mode-tabs">
          <text :class="{ active: state.orderMode === 'pickup' }" @click="setOrderMode('pickup')">自取</text>
          <text class="divider">|</text>
          <text :class="{ active: state.orderMode === 'dineIn' }" @click="setOrderMode('dineIn')">堂食</text>
        </view>
        <view class="header-brand-badge">
          <image class="header-mascot" src="/static/image/kangaroo.png" mode="aspectFit" />
          <text>肥嘟嘟点餐</text>
        </view>
      </view>
      <view class="store-line" @click="goStores">
        <view class="store-pin-ico">
          <view class="pin-dot" />
        </view>
        <text class="header-store">{{ currentStore.shortName }}</text>
        <text class="store-distance">{{ currentStore.distance < 1000 ? `${currentStore.distance}m` : `${(currentStore.distance / 1000).toFixed(1)}km` }}</text>
        <text class="store-arrow">›</text>
      </view>
      <view class="search-box">
        <view class="search-ico-small">
          <view class="ico-c" />
          <view class="ico-s" />
        </view>
        <input v-model="keyword" placeholder="搜索档口或餐品" />
        <text v-if="keyword" class="search-clear-ico" @click="keyword = ''">×</text>
      </view>
    </view>

    <view class="menu-shell">
      <scroll-view scroll-y class="category-side" :show-scrollbar="false">
        <view v-for="stall in state.stalls" :key="stall.id" :class="['category-item', { active: activeStall === stall.id }]" @click="activeStall = stall.id">
          <text class="stall-title-text">{{ stall.name }}</text>
        </view>
      </scroll-view>
      <scroll-view scroll-y class="menu-content" :show-scrollbar="false">
        <view v-if="!keyword" class="category-banner">
          <view>
            <view class="banner-kicker">{{ activeStallInfo.name }}</view>
            <view class="banner-copy">{{ activeStallInfo.description }} · 约 {{ currentStore.waitMinutes }} 分钟</view>
          </view>
          <image class="banner-mascot" src="/static/image/kangaroo.png" mode="aspectFit" />
        </view>
        <view class="menu-title">
          <text class="menu-title-main">{{ keyword ? `“${keyword}”的搜索结果` : '档口餐品' }}</text>
          <text class="menu-title-count">{{ visibleCount }} 道</text>
        </view>
        <ProductCard v-for="product in ownProducts" :key="product.id" :product="product" @open="openProduct" @add="quickAdd" />
        <view v-if="!keyword && extraProducts.length" class="group-head">
          <view class="group-bar" />
          <text class="group-title">同店其他档口 · 也受欢迎</text>
          <text class="group-note">按销量排序</text>
        </view>
        <ProductCard v-for="product in extraProducts" :key="product.id" :product="product" @open="openProduct" @add="quickAdd" />
        <EmptyState v-if="keyword && !searchResults.length" title="未检索到相关餐品" description="请调整搜索关键词" action="重置搜索" @action="keyword = ''" />
        <view class="menu-spacer" />
      </scroll-view>
    </view>

    <!-- 现代外卖风悬浮购物车栏 -->
    <view v-if="cartCount" class="cart-bar" :style="{ bottom: (navLayout.bottomSafe ? (navLayout.bottomSafe + 55) + 'px' : '') }">
      <view class="cart-round" @click="showCart = true">
        <image class="cart-icon-img" src="/static/image/home-shop.png" mode="aspectFit" />
        <text class="cart-count">{{ cartCount }}</text>
      </view>
      <view class="cart-price" @click="showCart = true">
        <view class="cart-total">{{ formatMoney(cartSubtotal) }}</view>
        <text class="cart-desc">已选 {{ cartCount }} 件 · 免费包装</text>
      </view>
      <button class="checkout" @click="checkout">去结算</button>
    </view>

    <!-- 购物车抽屉弹层：加减按钮为圆形按钮 (Circular Stepper Buttons) -->
    <view v-if="showCart" class="drawer-mask" @click="showCart = false"></view>
    <view class="cart-drawer" :class="{ show: showCart }">
      <view class="drawer-handle"></view>
      <view class="drawer-header">
        <view>
          <text class="drawer-title">购物车</text>
          <text class="drawer-sub">{{ currentStore.shortName }}</text>
        </view>
        <text class="clear-cart" @click="clearCart">清空</text>
      </view>
      <scroll-view scroll-y class="drawer-list" :style="{ height: drawerListHeight + 'px' }">
        <view v-for="item in state.cart" :key="item.key" class="cart-item">
          <image class="cart-visual" :src="item.image" mode="aspectFill" />
          <view class="cart-info">
            <view class="cart-name">{{ item.name }}</view>
            <view class="cart-stall">{{ item.stallName }}</view>
            <view class="cart-options">{{ optionText(item) || '标准制作' }}</view>
            <view class="price">{{ formatMoney(item.unitPriceCents) }}</view>
          </view>
          <!-- 圆形按钮步进器 (Circular Stepper Buttons) -->
          <view class="stepper">
            <button class="stepper-btn minus" @click="updateCartQuantity(item.key, item.quantity - 1)">
              <text class="step-text">−</text>
            </button>
            <text class="step-qty">{{ item.quantity }}</text>
            <button class="stepper-btn plus" @click="updateCartQuantity(item.key, item.quantity + 1)">
              <text class="step-text">＋</text>
            </button>
          </view>
        </view>
      </scroll-view>
      <view class="drawer-footer">
        <view>
          <text class="muted">合计 </text>
          <text class="drawer-total">{{ formatMoney(cartSubtotal) }}</text>
        </view>
        <button class="primary-button" @click="checkout">确认结算</button>
      </view>
    </view>
  </view>
</template>

<script setup>
import { computed, ref } from 'vue'
import ProductCard from '@/component/ProductCard.vue'
import EmptyState from '@/component/EmptyState.vue'
import { useAppStore } from '@/store/app'
import { formatMoney } from '@/utils/format'
import { getNavLayout } from '@/utils/nav'

const navLayout = getNavLayout()

const keyword = ref('')
const showCart = ref(false)
const windowHeight = uni.getSystemInfoSync().windowHeight
const drawerListHeight = Math.floor(windowHeight * 0.46)
const { state, currentStore, cartCount, cartSubtotal, setOrderMode, setStall, addToCart, updateCartQuantity, clearCart } = useAppStore()
const activeStall = computed({ get: () => state.selectedStallId || state.stalls[0]?.id, set: (value) => setStall(value) })
const activeStallInfo = computed(() => state.stalls.find((item) => item.id === activeStall.value) || state.stalls[0])
const searchResults = computed(() => { const key = keyword.value.trim().toLowerCase(); if (!key) return []; return state.products.filter((product) => `${product.name}${product.subtitle}${product.badge}${product.stallName}`.toLowerCase().includes(key)) })

const ownProducts = computed(() => (keyword.value.trim() ? searchResults.value : state.products.filter((product) => product.stallId === activeStall.value)))
const extraProducts = computed(() => {
  if (keyword.value.trim()) return []
  const ownIds = ownProducts.value.map((product) => product.id)
  return state.products
    .filter((product) => product.stallId !== activeStall.value && !ownIds.includes(product.id) && product.isActive !== false)
    .slice()
    .sort((a, b) => (b.sales || 0) - (a.sales || 0))
    .slice(0, 6)
})
const visibleCount = computed(() => ownProducts.value.length + extraProducts.value.length)
const quickAdd = (product) => {
  if (!product.isActive) { uni.showToast({ title: '该商品已售罄', icon: 'none' }); return }
  if (product.options.length) openProduct(product)
  else { addToCart(product.id); uni.showToast({ title: '已加入购物车', icon: 'success' }) }
}
const openProduct = (product) => {
  if (!product.isActive) { uni.showToast({ title: '该商品已售罄', icon: 'none' }); return }
  uni.navigateTo({ url: `/pages/item-detail/index?id=${product.id}` })
}
const optionText = (item) => item.selectedOptions.map((option) => option.name).join(' / ')
const checkout = () => { if (!state.cart.length) return; showCart.value = false; uni.navigateTo({ url: '/pages/confirm-order/index' }) }
const goStores = () => uni.switchTab({ url: '/pages/shop/index' })
</script>

<style scoped lang="scss">
.order-page {
  height: 100vh;
  overflow: hidden;
  padding: 0;
  background: #fff;
}
.order-header {
  position: relative;
  z-index: 8;
  padding: 18rpx 26rpx;
  background: #fff;
  border-bottom: 1rpx solid #F2F2F4;
  box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, .04);
}
.header-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.mode-tabs {
  display: flex;
  align-items: center;
  color: #8E929E;
  font-size: 28rpx;
  font-weight: 700;
}
.mode-tabs text { margin-right: 14rpx; }
.mode-tabs .active {
  color: #222426;
  font-size: 34rpx;
  font-weight: 900;
  position: relative;
}
.mode-tabs .divider { color: #E5E6EB; font-weight: 400; }

.header-brand-badge {
  display: flex;
  align-items: center;
  padding: 4rpx 14rpx 4rpx 8rpx;
  border-radius: 20rpx;
  background: #FFF7DB;
  color: #8C5E00;
  font-size: 20rpx;
  font-weight: 800;
}
.header-mascot {
  width: 32rpx;
  height: 32rpx;
  margin-right: 6rpx;
}

.store-line {
  display: flex;
  align-items: center;
  margin-top: 18rpx;
}
.store-pin-ico {
  width: 28rpx;
  height: 28rpx;
  margin-right: 10rpx;
  position: relative;
  border-radius: 50% 50% 50% 0;
  transform: rotate(-45deg);
  background: #FFC300;
  display: flex;
  align-items: center;
  justify-content: center;
}
.pin-dot {
  width: 10rpx;
  height: 10rpx;
  border-radius: 50%;
  background: #fff;
}
.header-store {
  max-width: 380rpx;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 26rpx;
  font-weight: 800;
  color: #222426;
}
.store-distance {
  margin-left: 12rpx;
  color: #8E929E;
  font-size: 20rpx;
}
.store-arrow {
  margin-left: 6rpx;
  color: #8E929E;
  font-size: 32rpx;
}

.search-box {
  display: flex;
  align-items: center;
  height: 68rpx;
  margin-top: 16rpx;
  padding: 0 20rpx;
  border-radius: 34rpx;
  background: #F5F6F8;
}
.search-ico-small {
  position: relative;
  width: 24rpx;
  height: 24rpx;
  margin-right: 12rpx;
}
.ico-c {
  position: absolute;
  left: 0;
  top: 0;
  width: 16rpx;
  height: 16rpx;
  border: 3rpx solid #999;
  border-radius: 50%;
}
.ico-s {
  position: absolute;
  right: 0;
  bottom: 0;
  width: 8rpx;
  height: 3rpx;
  transform: rotate(45deg);
  background: #999;
}
.search-box input {
  flex: 1;
  font-size: 23rpx;
  color: #222426;
}
.search-clear-ico {
  padding: 0 10rpx;
  color: #8E929E;
  font-size: 28rpx;
}

/* ---- 左右菜单布局 ---- */
.menu-shell {
  display: flex;
  height: calc(100vh - 306rpx - var(--status-bar-height, 0px) - env(safe-area-inset-top, 0px) - env(safe-area-inset-bottom, 0px));
  min-height: 560rpx;
  background: #fff;
}
.category-side {
  width: 160rpx;
  flex: 0 0 160rpx;
  height: 100%;
  background: #F7F8FA;
}
.category-item {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 106rpx;
  padding: 16rpx 12rpx;
  color: #666666;
  font-size: 22rpx;
  text-align: center;
}
.stall-title-text {
  line-height: 1.35;
}
.category-item.active {
  color: #222426;
  background: #fff;
  font-weight: 900;
}
.category-item.active::before {
  content: '';
  position: absolute;
  left: 0;
  top: 30rpx;
  bottom: 30rpx;
  width: 8rpx;
  border-radius: 0 6rpx 6rpx 0;
  background: #FFC300;
}

.menu-content {
  flex: 1;
  height: 100%;
  padding: 18rpx 18rpx 0;
  background: #fff;
}
.category-banner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  min-height: 114rpx;
  padding: 20rpx 24rpx;
  border-radius: 20rpx;
  color: #222426;
  background: linear-gradient(125deg, #FFDE6A 0%, #FFC300 100%);
  box-shadow: 0 6rpx 20rpx rgba(255, 195, 0, .25);
}
.banner-kicker { font-size: 28rpx; font-weight: 900; }
.banner-copy { margin-top: 6rpx; color: #594300; font-size: 20rpx; font-weight: 600; }
.banner-mascot { width: 80rpx; height: 80rpx; }

.menu-title {
  display: flex;
  justify-content: space-between;
  margin: 22rpx 4rpx 14rpx;
  font-size: 28rpx;
  font-weight: 900;
  color: #222426;
}
.menu-title-count { color: #8E929E; font-size: 20rpx; font-weight: 400; }
.menu-spacer { height: 190rpx; }

.group-head {
  display: flex;
  align-items: center;
  margin: 30rpx 4rpx 16rpx;
  padding-top: 24rpx;
  border-top: 1rpx dashed #EAECEF;
}
.group-bar {
  width: 6rpx;
  height: 24rpx;
  margin-right: 12rpx;
  border-radius: 3rpx;
  background: #FFC300;
}
.group-title { font-size: 23rpx; font-weight: 800; color: #222426; }
.group-note { margin-left: auto; color: #8E929E; font-size: 19rpx; }

/* ---- 品质外卖风格底部浮动购物车条 ---- */
.cart-bar {
  position: fixed;
  z-index: 20;
  left: 24rpx;
  right: 24rpx;
  bottom: calc(110rpx + constant(safe-area-inset-bottom));
  bottom: calc(110rpx + env(safe-area-inset-bottom));
  display: flex;
  align-items: center;
  height: 98rpx;
  padding: 10rpx 12rpx 10rpx 20rpx;
  border-radius: 49rpx;
  color: #fff;
  background: #222426;
  box-shadow: 0 16rpx 40rpx rgba(0, 0, 0, .28);
}
.cart-round {
  position: relative;
  width: 76rpx;
  height: 76rpx;
  border-radius: 50%;
  background: #FFC300;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4rpx 14rpx rgba(255, 195, 0, .4);
}
.cart-icon-img {
  width: 44rpx;
  height: 44rpx;
}
.cart-count {
  position: absolute;
  right: -8rpx;
  top: -8rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 32rpx;
  height: 32rpx;
  padding: 0 8rpx;
  border-radius: 16rpx;
  background: #FF4B3E;
  color: #fff;
  font-size: 18rpx;
  font-weight: 900;
  border: 2rpx solid #222426;
}
.cart-price {
  flex: 1;
  margin-left: 20rpx;
}
.cart-total {
  font-size: 32rpx;
  font-weight: 900;
  color: #fff;
}
.cart-desc {
  display: block;
  margin-top: 2rpx;
  color: rgba(255, 255, 255, .65);
  font-size: 19rpx;
}
.checkout {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 76rpx;
  padding: 0 36rpx;
  border-radius: 38rpx;
  color: #222426;
  background: #FFC300;
  font-size: 26rpx;
  font-weight: 800;
}

/* ---- 购物车抽屉 ---- */
.drawer-mask {
  position: fixed;
  z-index: 30;
  left: 0;
  top: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, .5);
}
.cart-drawer {
  position: fixed;
  z-index: 31;
  left: 0;
  right: 0;
  bottom: 0;
  max-height: 75vh;
  padding: 16rpx 28rpx calc(28rpx + env(safe-area-inset-bottom));
  border-radius: 36rpx 36rpx 0 0;
  background: #fff;
  transform: translateY(110%);
  transition: transform .25s ease;
}
.cart-drawer.show { transform: translateY(0); }
.drawer-handle {
  width: 80rpx;
  height: 8rpx;
  margin: 0 auto 18rpx;
  border-radius: 4rpx;
  background: #E5E6EB;
}
.drawer-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10rpx 0 20rpx;
  border-bottom: 1rpx solid #F2F3F5;
}
.drawer-title { font-size: 32rpx; font-weight: 900; color: #222426; }
.drawer-sub { margin-left: 14rpx; color: #8E929E; font-size: 21rpx; }
.clear-cart { color: #8E929E; font-size: 23rpx; }

.cart-item {
  display: flex;
  align-items: center;
  padding: 22rpx 0;
  border-bottom: 1rpx solid #F5F6F8;
}
.cart-visual {
  width: 104rpx;
  height: 104rpx;
  flex: 0 0 104rpx;
  margin-right: 18rpx;
  border-radius: 16rpx;
  background: #F7F8FA;
}
.cart-info { min-width: 0; flex: 1; }
.cart-name { font-size: 27rpx; font-weight: 800; color: #222426; }
.cart-stall { margin-top: 4rpx; color: #B37D00; font-size: 19rpx; font-weight: 600; }
.cart-options {
  margin: 6rpx 0;
  overflow: hidden;
  color: #8E929E;
  font-size: 19rpx;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* 圆形添加减少按钮 (Circular Add & Minus Stepper Buttons) */
.stepper {
  display: flex;
  align-items: center;
}
.stepper-btn {
  width: 48rpx;
  height: 48rpx;
  padding: 0;
  margin: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  line-height: 1;
  transition: transform .1s ease;
}
.stepper-btn:active { transform: scale(.92); }
.stepper-btn.minus {
  border: 2rpx solid #FFC300;
  background: #fff;
  color: #222426;
}
.stepper-btn.plus {
  background: #FFC300;
  color: #222426;
  box-shadow: 0 4rpx 10rpx rgba(255, 195, 0, .4);
}
.step-text {
  font-size: 28rpx;
  font-weight: 900;
  line-height: 1;
  transform: translateY(-1rpx);
}
.step-qty {
  min-width: 44rpx;
  padding: 0 8rpx;
  text-align: center;
  font-weight: 800;
  font-size: 26rpx;
  color: #222426;
}

.drawer-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 24rpx;
}
.drawer-total { font-size: 38rpx; font-weight: 900; color: #FF4B3E; }
.drawer-footer .primary-button { min-height: 80rpx; font-size: 27rpx; }

@media screen and (min-width: 760px) {
  .cart-bar { left: 50%; right: auto; width: 700px; transform: translateX(-50%); }
  .cart-drawer { left: 50%; right: auto; width: 750px; transform: translate(-50%, 110%); }
  .cart-drawer.show { transform: translate(-50%, 0); }
}
</style>
