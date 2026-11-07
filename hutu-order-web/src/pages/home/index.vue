<template>
  <view class="page-shell home-page">
    <!-- 顶部轮播：顶部留空 + 定位行叠在图上，搜索栏骑在图片下沿 -->
    <view class="hero">
      <swiper class="hero-swiper" circular autoplay :interval="4000" :duration="500" indicator-dots indicator-color="rgba(255,255,255,.45)" indicator-active-color="#ffffff">
        <swiper-item v-for="banner in banners" :key="banner.id">
          <view class="hero-slide" @click="onBannerTap(banner)">
            <image class="hero-image" :src="resolveImage(banner.image)" mode="aspectFill" />
          </view>
        </swiper-item>
      </swiper>
      <view class="hero-top-spacer" :style="{ height: statusBarHeight + 'px' }" />
      <view class="hero-nav">
        <view class="loc" @click="goStores">
          <image class="loc-icon" src="/static/icon/local.png" mode="aspectFit" />
          <text class="loc-text">{{ currentStore.shortName || currentStore.name }}</text>
          <text class="loc-arrow">›</text>
        </view>
        <view class="hero-status-chip">{{ currentStore.status === 'busy' ? '出餐繁忙' : '营业中' }} · {{ currentStore.hours }}</view>
      </view>
    </view>

    <!-- 搜索栏：吸顶，搜索真实可用 -->
    <view class="search-dock">
      <view class="search-bar">
        <view class="search-glyph" />
        <input v-model="keyword" class="search-input" :placeholder="placeholder" confirm-type="search" @confirm="doSearch" @input="onKeywordInput" />
        <text v-if="keyword" class="search-clear" @click="clearSearch">✕</text>
        <text class="search-btn" @click="doSearch">搜索</text>
      </view>
    </view>

    <!-- 搜索结果层 -->
    <view v-if="searching" class="section">
      <view class="section-heading">
        <text class="section-title">搜索结果</text>
        <text class="section-link" @click="clearSearch">返回首页</text>
      </view>
      <view class="result-summary">店铺 {{ searchShops.length }} 家 · 餐品 {{ searchProducts.length }} 个</view>
      <view class="result-list card">
        <view v-for="shop in searchShops" :key="'s-' + shop.id" class="result-row" @click="goStall(shop.id)">
          <view class="result-copy"><text class="result-name">{{ shop.name }}</text><text class="result-desc">{{ shop.description }}</text></view>
          <text class="result-extra">{{ formatDistance(shop.distance) }}</text>
        </view>
        <view v-for="product in searchProducts" :key="'p-' + product.id" class="result-row" @click="openProduct(product.id)">
          <image class="result-thumb" :src="product.image" mode="aspectFill" />
          <view class="result-copy"><text class="result-name">{{ product.name }}</text><text class="result-desc">{{ product.subtitle }}</text></view>
          <text class="result-extra">{{ formatMoney(product.priceCents) }}</text>
        </view>
        <view v-if="!searchShops.length && !searchProducts.length" class="result-empty">没有找到相关内容，换个词试试</view>
      </view>
    </view>

    <template v-else>
      <!-- 双模卡：商家配送 / 到店自取 -->
      <view class="section">
        <view class="channel-grid">
          <view class="channel-card" :class="{ active: state.channel === 'delivery' }" @click="chooseChannel('delivery')">
            <view class="channel-copy">
              <text class="channel-title">商家配送</text>
              <text class="channel-desc">校园地址固定，无需填写收货地址</text>
            </view>
            <view class="channel-icon">配</view>
          </view>
          <view class="channel-card" :class="{ active: state.channel === 'pickup' }" @click="chooseChannel('pickup')">
            <view class="channel-copy">
              <text class="channel-title">到店自取</text>
              <text class="channel-desc">提前点单，到店即取，免排队</text>
            </view>
            <view class="channel-icon pickup">取</view>
          </view>
        </view>
      </view>

      <!-- 金刚区：6 个门店 -->
      <view class="section">
        <view class="diamond-grid">
          <view v-for="stall in stallEntries" :key="stall.id" class="diamond-item" @click="goStall(stall.id)">
            <image class="diamond-icon" :src="stall.image" mode="aspectFill" />
            <text class="diamond-name">{{ stall.shortName || stall.name }}</text>
          </view>
        </view>
      </view>

      <!-- 美食节横幅 -->
      <view class="section" @click="startOrder(festival.stallId)">
        <view class="festival">
          <view class="festival-copy">
            <view class="festival-tag">校园美食节</view>
            <view class="festival-title">{{ festival.name }}</view>
            <view class="festival-sub">{{ festival.subtitle }}</view>
            <view class="festival-price"><text class="festival-symbol">¥</text><text class="festival-amount">{{ festival.price }}</text><text class="festival-cta">立即点单 ›</text></view>
          </view>
          <image class="festival-image" :src="festival.image" mode="aspectFill" />
        </view>
      </view>

      <!-- 券卡 + 今日特惠 -->
      <view class="section">
        <view class="promo-grid">
          <view class="promo-card coupon-card" @click="onClaimCoupon">
            <view class="promo-tag">吃货券</view>
            <view class="promo-title">{{ homeCoupon.title }}</view>
            <view class="promo-desc">{{ homeCoupon.desc }}</view>
            <view class="coupon-action">
              <text class="coupon-amount">¥{{ homeCoupon.discount }}</text>
              <view class="coupon-btn" :class="{ claimed: homeCoupon.claimed }">{{ homeCoupon.claimed ? '已领取' : (state.user ? '一键领取' : '登录领取') }}</view>
            </view>
          </view>
          <view class="promo-card deal-card" @click="openProduct(deal.id)">
            <view class="deal-head"><text class="promo-tag deal-tag">今日特惠</text><text class="deal-save">省 {{ deal.save }}</text></view>
            <view class="promo-title">{{ deal.name }}</view>
            <view class="promo-desc">{{ deal.subtitle }}</view>
            <view class="deal-bottom">
              <view class="deal-price"><text class="deal-cur">{{ deal.price }}</text><text class="deal-old">{{ deal.original }}</text></view>
              <text class="deal-btn">马上点</text>
            </view>
          </view>
        </view>
      </view>

      <!-- 筛选栏：口碑榜首在前，综合排序在后 -->
      <view class="section">
        <scroll-view scroll-x class="filter-scroll" :show-scrollbar="false">
          <view class="filter-row">
            <view v-for="tab in filterTabs" :key="tab.id" class="filter-pill" :class="{ active: activeFilter === tab.id }" @click="activeFilter = tab.id">{{ tab.name }}</view>
          </view>
        </scroll-view>
        <view v-if="activeFilter === 'promo'" class="coupon-strip">
          <text>满 30 减 5 · 满 50 减 10</text>
          <text class="coupon-strip-sub">结算时可选用，可与会员积分同享</text>
        </view>
      </view>

      <!-- 店铺流 -->
      <view class="section">
        <view class="section-heading">
          <text class="section-title">{{ filterTitle }}</text>
          <text class="section-link">{{ visibleShops.length }} 家店铺</text>
        </view>
        <view v-for="shop in visibleShops" :key="shop.id" class="shop-card card" @click="goStall(shop.id)">
          <view class="shop-cover">
            <image :src="shop.image" mode="aspectFill" />
            <text class="shop-cover-tag">{{ shop.badge }}</text>
          </view>
          <view class="shop-info">
            <view class="shop-title-row"><text class="shop-name">{{ shop.name }}</text><text class="shop-store">{{ shop.storeName }}</text></view>
            <view class="shop-meta-row">
              <text class="shop-rating">{{ shop.rating ? '★ ' + shop.rating : '暂无评分' }}</text>
              <text class="shop-sep">·</text>
              <text>月售 {{ shop.salesSum }}</text>
              <text class="shop-sep">·</text>
              <text>人均 {{ formatMoney(shop.avgPriceCents) }}</text>
            </view>
            <view class="shop-meta-row">
              <text>{{ formatDistance(shop.distance) }}</text>
              <text class="shop-sep">·</text>
              <text>出餐约 {{ shop.waitMinutes }} 分钟</text>
              <text class="shop-sep">·</text>
              <text>{{ shop.productCount }} 款餐品</text>
            </view>
            <view class="shop-quote">
              <text class="quote-tag">校友力荐</text>
              <text class="quote-text">{{ shop.quote }}</text>
            </view>
          </view>
        </view>
        <view v-if="!visibleShops.length" class="shop-empty card">当前筛选下没有店铺，试试「综合排序」</view>
      </view>

      <!-- 人气餐品 -->
      <view class="section recommend-section">
        <view class="section-heading"><text class="section-title">人气餐品</text><text class="section-link" @click="startOrder(state.selectedStallId)">全部餐品 ›</text></view>
        <scroll-view scroll-x class="recommend-scroll" :show-scrollbar="false">
          <view class="recommend-row">
            <view v-for="product in popularProducts" :key="product.id" class="recommend-card card" @click="openProduct(product.id)">
              <image class="recommend-image" :src="product.image" mode="aspectFill" />
              <text class="recommend-name">{{ product.name }}</text>
              <view class="recommend-bottom"><text class="recommend-price">{{ formatMoney(product.priceCents) }}</text><text class="recommend-add">+</text></view>
            </view>
          </view>
        </scroll-view>
      </view>

      <!-- 附近门店 -->
      <view class="section">
        <view class="section-heading"><text class="section-title">附近门店</text><text class="section-link" @click="goStores">地图查看 ›</text></view>
        <view class="store-strip">
          <view v-for="item in nearbyStores" :key="item.id" class="store-chip card" :class="{ current: item.id === currentStore.id }" @click="pickStore(item)">
            <text class="store-chip-name">{{ item.name }}</text>
            <text class="store-chip-meta">{{ formatDistance(item.distance) }} · 出餐约 {{ item.waitMinutes }} 分钟</text>
            <text class="store-chip-meta">{{ item.stallCount ? item.stallCount + ' 家店铺' : '店铺筹备中' }}</text>
          </view>
        </view>
      </view>
    </template>

    <view v-if="couponPopup.show" class="coupon-mask">
      <view class="coupon-popup-wrap">
        <view class="coupon-popup" @click.stop>
          <text class="coupon-popup-title">{{ couponPopup.title }}</text>
          <text class="coupon-popup-copy">{{ couponPopup.copy }}</text>
          <view class="coupon-popup-value"><text class="coupon-popup-symbol">¥</text><text class="coupon-popup-number">{{ couponPopup.amount }}</text></view>
          <button class="coupon-popup-btn" @click="goOrderFromPopup">去下单使用</button>
        </view>
        <button class="coupon-close" @click="couponPopup.show = false">✕</button>
      </view>
    </view>
  </view>
</template>

<script setup>
import { computed, reactive, ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { useAppStore } from '@/store/app'
import { formatDistance, formatMoney } from '@/utils/format'

const store = useAppStore()
const { state, currentStore, merchantCards, nearbyStores, setStall, setStore, setOrderMode, setChannel, claimCoupon, resolveImage, loadCatalog, loadStoreReviewSummary } = store

const statusBarHeight = (() => {
  try { const info = uni.getWindowInfo ? uni.getWindowInfo() : uni.getSystemInfoSync(); return (info && info.statusBarHeight) || 20 } catch (e) { return 20 }
})()

const keyword = ref('')
const searching = ref(false)
const placeholder = '搜店铺、门店或餐品'
const activeFilter = ref('rating')
const filterTabs = [
  { id: 'rating', name: '口碑榜首' },
  { id: 'all', name: '综合排序' },
  { id: 'deal', name: '超值特惠' },
  { id: 'promo', name: '满减专区' },
]

onShow(() => { loadCatalog().catch(() => {}); loadStoreReviewSummary().catch(() => {}) })

const stallEntries = computed(() => merchantCards.value.map((shop) => ({ id: shop.id, name: shop.name, shortName: (state.stalls.find((s) => s.id === shop.id) || {}).shortName, image: shop.image })))
const popularProducts = computed(() => state.products.filter((product) => product.featured))

// 美食节横幅：取真实高分餐品
const festival = computed(() => {
  const product = state.products.find((p) => p.id === 'braised-beef-noodles') || popularProducts.value[0] || { name: '今日现制', subtitle: '', priceCents: 0, image: '' }
  return { name: product.name, subtitle: product.subtitle, price: (product.priceCents / 100).toFixed(1), image: product.image, stallId: product.stallId }
})
// 今日特惠：黑椒鸡腿饭，价与原价都来自后端数据
const deal = computed(() => {
  const product = state.products.find((p) => p.id === 'black-pepper-chicken-rice') || state.products[0] || {}
  const cur = product.priceCents || 0
  const original = product.originalPriceCents || 0
  return {
    id: product.id, name: product.name, subtitle: product.subtitle,
    price: '¥' + (cur / 100).toFixed(1),
    original: original > cur ? '¥' + (original / 100).toFixed(1) : '',
    save: original > cur ? '¥' + ((original - cur) / 100).toFixed(1) : '限时价',
  }
})

// 首页主券：门槛最低的一张真实券
const homeCoupon = computed(() => {
  const list = (state.coupons || []).filter((c) => c.isActive !== false)
  const coupon = list.slice().sort((a, b) => (a.thresholdCents || 0) - (b.thresholdCents || 0))[0]
  if (!coupon) return { title: '暂无可用券', desc: '关注门店活动', discount: '0', claimed: true }
  const claimed = state.couponIds.includes(coupon.id)
  return {
    id: coupon.id,
    title: coupon.name,
    desc: coupon.thresholdCents ? `满 ¥${(coupon.thresholdCents / 100).toFixed(0)} 可用 · ${coupon.expires} 到期` : `无门槛 · ${coupon.expires} 到期`,
    discount: (coupon.discountCents / 100).toFixed(0),
    claimed,
  }
})

const visibleShops = computed(() => {
  const list = merchantCards.value.slice()
  if (activeFilter.value === 'rating') return list.sort((a, b) => b.rating - a.rating || b.salesSum - a.salesSum)
  if (activeFilter.value === 'deal') {
    return list.filter((shop) => state.products.some((p) => p.stallId === shop.id && p.originalPriceCents > p.priceCents))
  }
  return list
})
const filterTitle = computed(() => {
  if (activeFilter.value === 'rating') return '口碑榜首'
  if (activeFilter.value === 'deal') return '超值特惠'
  if (activeFilter.value === 'promo') return '满减专区'
  return '全部店铺'
})

// 搜索：本地真实过滤，店铺与餐品都命中
const searchShops = computed(() => {
  const key = keyword.value.trim()
  if (!key) return []
  return merchantCards.value.filter((s) => s.name.includes(key) || (s.description || '').includes(key) || s.quote.includes(key))
})
const searchProducts = computed(() => {
  const key = keyword.value.trim()
  if (!key) return []
  return state.products.filter((p) => p.name.includes(key) || (p.subtitle || '').includes(key) || (p.badge || '').includes(key))
})

function onKeywordInput(event) { const value = (event && event.detail && event.detail.value) || ''; keyword.value = value; searching.value = !!value.trim() }
function doSearch() {
  if (!keyword.value.trim()) { searching.value = false; uni.showToast({ title: '请输入店铺或餐品名称', icon: 'none' }); return }
  searching.value = true
}
function clearSearch() { keyword.value = ''; searching.value = false }

const banners = [
  { id: 1, image: '/uploads/catalog/banner/hero-campus-dining.png', link: 'pickup' },
  { id: 2, image: '/uploads/catalog/banner/coupon-newbie.jpg', link: 'coupon' },
  { id: 3, image: '/uploads/catalog/banner/store-dining-1.png', link: 'stores' },
  { id: 4, image: '/uploads/catalog/banner/store-dining-2.png', link: 'pickup' },
  { id: 5, image: '/uploads/catalog/banner/store-dining-3.png', link: 'pickup' },
]
const couponPopup = reactive({ show: false, title: '领取成功', copy: '券已放入账户，结算时可用', amount: '5' })

function onBannerTap(banner) {
  if (banner.link === 'coupon') { onClaimCoupon(); return }
  if (banner.link === 'stores') goStores()
  else startOrder(state.selectedStallId)
}
async function onClaimCoupon() {
  if (!state.user) { uni.navigateTo({ url: '/pages/login/index' }); return }
  const coupon = homeCoupon.value
  if (!coupon.id || coupon.claimed) { uni.showToast({ title: '这张券已经领过啦', icon: 'none' }); return }
  const result = await claimCoupon(coupon.id)
  if (result) {
    couponPopup.show = true
    couponPopup.title = '领取成功'
    couponPopup.copy = `${result.name} 已放入账户，结算时可用`
    couponPopup.amount = (result.discountCents / 100).toFixed(0)
  }
}
function goOrderFromPopup() { couponPopup.show = false; startOrder(state.selectedStallId) }

function chooseChannel(channel) { setChannel(channel); uni.showToast({ title: channel === 'delivery' ? '校园内由门店配送，无需填地址' : '已切换为到店自取', icon: 'none' }) }
function startOrder(stallId = '') { setOrderMode('pickup'); if (stallId) setStall(stallId); uni.switchTab({ url: '/pages/order/index' }) }
function goStall(stallId) { setStall(stallId); uni.switchTab({ url: '/pages/order/index' }) }
function goStores() { uni.switchTab({ url: '/pages/shop/index' }) }
function pickStore(item) {
  if (!item.stallCount) { uni.showToast({ title: `${item.name} 店铺筹备中`, icon: 'none' }); return }
  setStore(item.id); uni.showToast({ title: `已切换到${item.name}`, icon: 'none' })
}
function openProduct(id) {
  const product = state.products.find((p) => p.id === id)
  if (product && !product.isActive) { uni.showToast({ title: '该商品已售罄', icon: 'none' }); return }
  uni.navigateTo({ url: `/pages/item-detail/index?id=${id}` })
}
</script>

<style scoped lang="scss">
.home-page{background:#f6f7f9;padding-bottom:20rpx}
/* ---- hero：顶部留空 + 轮播 + 定位行 ---- */
.hero{position:relative;background:#0b1220}
.hero-swiper{height:400rpx}
.hero-slide{position:relative;width:100%;height:100%}
.hero-image{width:100%;height:100%}
.hero-slide::after{content:'';position:absolute;left:0;top:0;right:0;bottom:0;background:linear-gradient(180deg,rgba(6,16,40,.55) 0%,rgba(6,16,40,.22) 34%,rgba(6,16,40,0) 62%)}
.hero-top-spacer{position:absolute;left:0;top:0;right:0;z-index:3;pointer-events:none}
.hero-nav{position:absolute;z-index:3;left:0;top:0;right:0;display:flex;align-items:center;justify-content:space-between;padding:0 26rpx}
.hero-nav{padding-top:calc(env(safe-area-inset-top) + 12rpx)}
.loc{display:flex;align-items:center;min-width:0}
.loc-icon{width:26rpx;height:26rpx;margin-right:8rpx}
.loc-text{max-width:300rpx;overflow:hidden;color:#fff;font-size:26rpx;font-weight:700;text-overflow:ellipsis;white-space:nowrap}
.loc-arrow{margin-left:6rpx;color:rgba(255,255,255,.8);font-size:24rpx}
.hero-status-chip{padding:5rpx 14rpx;border-radius:20rpx;color:#fff;background:rgba(0,0,0,.28);font-size:19rpx}
/* ---- 搜索栏 ---- */
.search-dock{position:sticky;top:0;z-index:30;margin-top:-34rpx;padding:0 24rpx 10rpx}
.search-bar{display:flex;align-items:center;height:80rpx;padding:0 10rpx 0 24rpx;border-radius:40rpx;background:#fff;box-shadow:0 10rpx 28rpx rgba(12,26,64,.14)}
.search-glyph{position:relative;width:30rpx;height:30rpx;margin-right:14rpx;flex:0 0 30rpx}
.search-glyph::before{content:'';position:absolute;left:0;top:0;width:22rpx;height:22rpx;border:3rpx solid #9aa0ac;border-radius:50%}
.search-glyph::after{content:'';position:absolute;right:0;bottom:1rpx;width:10rpx;height:3rpx;transform:rotate(45deg);background:#9aa0ac;border-radius:2rpx}
.search-input{flex:1;height:80rpx;font-size:24rpx;color:var(--ink)}
.search-clear{padding:0 12rpx;color:#a8adb8;font-size:24rpx}
.search-btn{padding:10rpx 24rpx;border-radius:30rpx;color:#fff;background:var(--brand);font-size:22rpx;font-weight:700}
/* ---- 通用楼层 ---- */
.section{padding:0 24rpx;margin-top:16rpx}
.section-heading{display:flex;align-items:center;justify-content:space-between;margin-bottom:12rpx}
.section-title{color:var(--ink);font-size:28rpx;font-weight:800}
.section-link{color:var(--muted);font-size:21rpx}
.card{border-radius:20rpx;background:#fff;box-shadow:0 4rpx 14rpx rgba(16,38,90,.05)}
/* ---- 搜索结果 ---- */
.result-summary{margin-bottom:10rpx;color:var(--muted);font-size:21rpx}
.result-list{padding:4rpx 22rpx}
.result-row{display:flex;align-items:center;padding:22rpx 0;border-bottom:1rpx solid #f0f2f6}
.result-row:last-child{border-bottom:0}
.result-thumb{width:88rpx;height:88rpx;margin-right:16rpx;border-radius:14rpx;background:#f2f4f8}
.result-copy{flex:1;min-width:0}
.result-name{display:block;overflow:hidden;font-size:25rpx;font-weight:700;text-overflow:ellipsis;white-space:nowrap}
.result-desc{display:block;margin-top:5rpx;overflow:hidden;color:var(--muted);font-size:19rpx;text-overflow:ellipsis;white-space:nowrap}
.result-extra{margin-left:12rpx;color:var(--brand);font-size:22rpx;font-weight:700}
.result-empty{padding:50rpx 0;text-align:center;color:var(--muted);font-size:22rpx}
/* ---- 双模卡 ---- */
.channel-grid{display:flex;margin-right:-12rpx}
.channel-card{display:flex;align-items:center;width:calc(50% - 12rpx);margin-right:12rpx;padding:18rpx 18rpx;border:1rpx solid #e7eaf1;border-radius:20rpx;background:#fff}
.channel-card.active{border-color:var(--brand);background:#f3f6ff;box-shadow:0 6rpx 18rpx rgba(6,55,201,.1)}
.channel-copy{flex:1;min-width:0}
.channel-title{display:block;font-size:25rpx;font-weight:800}
.channel-desc{display:block;margin-top:5rpx;color:var(--muted);font-size:18rpx;line-height:1.35}
.channel-icon{display:flex;align-items:center;justify-content:center;width:52rpx;height:52rpx;flex:0 0 52rpx;margin-left:8rpx;border-radius:16rpx;color:#fff;background:linear-gradient(145deg,#0b4ee7,#062b9e);font-size:21rpx;font-weight:800}
.channel-icon.pickup{background:linear-gradient(145deg,#c99457,#8a5f2a)}
/* ---- 金刚区 ---- */
.diamond-grid{display:flex;flex-wrap:wrap;padding:16rpx 4rpx;border-radius:20rpx;background:#fff;box-shadow:0 4rpx 14rpx rgba(16,38,90,.05)}
.diamond-item{display:flex;flex-direction:column;align-items:center;width:33.33%;padding:10rpx 0}
.diamond-icon{width:76rpx;height:76rpx;border-radius:50%;background:#f4f6fa}
.diamond-name{margin-top:9rpx;color:var(--ink);font-size:21rpx;font-weight:700}
/* ---- 美食节 ---- */
.festival{position:relative;display:flex;overflow:hidden;border-radius:22rpx;background:linear-gradient(115deg,#fff4ef 0%,#ffe6da 62%,#ffd9c6 100%)}
.festival-copy{position:relative;z-index:2;flex:1;padding:24rpx 20rpx}
.festival-tag{display:inline-block;padding:3rpx 12rpx;border-radius:6rpx;color:#fff;background:#e8502c;font-size:18rpx;font-weight:700}
.festival-title{margin-top:10rpx;color:#4b1d0d;font-size:30rpx;font-weight:800}
.festival-sub{margin-top:6rpx;color:#8a5b47;font-size:19rpx;line-height:1.4}
.festival-price{display:flex;align-items:baseline;margin-top:12rpx}
.festival-symbol{color:#e8502c;font-size:22rpx;font-weight:800}
.festival-amount{color:#e8502c;font-size:42rpx;font-weight:900;letter-spacing:-1rpx}
.festival-cta{margin-left:14rpx;color:#4b1d0d;font-size:20rpx;font-weight:700}
.festival-image{width:220rpx;height:100%;min-height:180rpx;flex:0 0 220rpx;opacity:.96}
/* ---- 券卡 + 特惠 ---- */
.promo-grid{display:flex;margin-right:-12rpx}
.promo-card{width:calc(50% - 12rpx);margin-right:12rpx;padding:18rpx;border-radius:20rpx}
.coupon-card{background:linear-gradient(135deg,#fff6f5 0%,#ffeae6 100%);border:1rpx solid #ffd8d2}
.deal-card{background:linear-gradient(135deg,#fff9f5 0%,#fff0e4 100%);border:1rpx solid #ffe1cc}
.promo-tag{display:inline-block;padding:2rpx 10rpx;border-radius:6rpx;color:#fff;background:#e8502c;font-size:18rpx;font-weight:700}
.promo-tag.deal-tag{background:#f2761f}
.promo-title{margin-top:10rpx;overflow:hidden;color:#222;font-size:25rpx;font-weight:800;text-overflow:ellipsis;white-space:nowrap}
.promo-desc{margin-top:4rpx;overflow:hidden;color:#8b8f98;font-size:18rpx;text-overflow:ellipsis;white-space:nowrap}
.coupon-action{display:flex;align-items:center;justify-content:space-between;margin-top:12rpx}
.coupon-amount{color:#e8502c;font-size:34rpx;font-weight:900}
.coupon-btn{padding:5rpx 18rpx;border-radius:20rpx;color:#fff;background:#f2761f;font-size:19rpx;font-weight:700}
.coupon-btn.claimed{background:#c9ccd4}
.deal-head{display:flex;align-items:center;justify-content:space-between}
.deal-save{color:#f2761f;font-size:18rpx;font-weight:700}
.deal-bottom{display:flex;align-items:center;justify-content:space-between;margin-top:10rpx}
.deal-price{display:flex;align-items:baseline}
.deal-cur{color:#e8502c;font-size:30rpx;font-weight:900}
.deal-old{margin-left:6rpx;color:#b3b6bd;font-size:18rpx;text-decoration:line-through}
.deal-btn{padding:5rpx 16rpx;border-radius:18rpx;color:#fff;background:#e8502c;font-size:19rpx;font-weight:700}
/* ---- 筛选 ---- */
.filter-scroll{width:100%;white-space:nowrap}
.filter-row{display:flex;padding-right:24rpx}
.filter-pill{margin-right:12rpx;padding:9rpx 22rpx;border:1rpx solid #e6e9f0;border-radius:26rpx;background:#fff;color:#5c6270;font-size:21rpx}
.filter-pill.active{border-color:var(--brand);background:var(--brand);color:#fff;font-weight:700}
.coupon-strip{display:flex;align-items:center;justify-content:space-between;margin-top:12rpx;padding:14rpx 18rpx;border-radius:14rpx;background:#fff8f2;color:#c2410c;font-size:20rpx;font-weight:700}
.coupon-strip-sub{color:#9a7a63;font-size:18rpx;font-weight:400}
/* ---- 店铺卡 ---- */
.shop-card{display:flex;margin-bottom:14rpx;padding:14rpx}
.shop-cover{position:relative;width:196rpx;height:168rpx;flex:0 0 196rpx;overflow:hidden;border-radius:16rpx;background:#f2f4f8}
.shop-cover image{width:100%;height:100%}
.shop-cover-tag{position:absolute;left:8rpx;top:8rpx;padding:2rpx 10rpx;border-radius:8rpx;color:#fff;background:rgba(0,0,0,.42);font-size:17rpx}
.shop-info{flex:1;min-width:0;padding:4rpx 6rpx 4rpx 16rpx}
.shop-title-row{display:flex;align-items:baseline}
.shop-name{overflow:hidden;font-size:27rpx;font-weight:800;text-overflow:ellipsis;white-space:nowrap}
.shop-store{margin-left:10rpx;flex:0 0 auto;color:var(--muted);font-size:17rpx}
.shop-meta-row{display:flex;align-items:center;margin-top:7rpx;color:#6b7280;font-size:19rpx;white-space:nowrap}
.shop-rating{color:#f2761f;font-weight:800}
.shop-sep{margin:0 8rpx;color:#d3d6dd}
.shop-quote{display:flex;align-items:center;margin-top:9rpx;overflow:hidden}
.quote-tag{flex:0 0 auto;padding:2rpx 9rpx;margin-right:9rpx;border-radius:6rpx;color:#b45309;background:#fdf3e2;font-size:17rpx;font-weight:700}
.quote-text{overflow:hidden;color:#8b6a4a;font-size:19rpx;text-overflow:ellipsis;white-space:nowrap}
.shop-empty{padding:44rpx;text-align:center;color:var(--muted);font-size:22rpx}
/* ---- 人气餐品 ---- */
.recommend-section{padding-right:0}
.recommend-scroll{width:100%;white-space:nowrap}
.recommend-row{display:flex;padding:2rpx 24rpx 8rpx 0}
.recommend-card{display:inline-flex;flex-direction:column;width:200rpx;margin-right:14rpx;padding:10rpx}
.recommend-image{width:180rpx;height:150rpx;border-radius:14rpx;background:#f2f4f8}
.recommend-name{margin-top:10rpx;overflow:hidden;font-size:22rpx;font-weight:700;white-space:nowrap}
.recommend-bottom{display:flex;align-items:center;justify-content:space-between;margin-top:8rpx}
.recommend-price{color:#e8502c;font-size:23rpx;font-weight:800}
.recommend-add{display:flex;align-items:center;justify-content:center;width:36rpx;height:36rpx;border-radius:12rpx;color:#fff;background:var(--brand);font-size:24rpx}
/* ---- 附近门店 ---- */
.store-strip{display:flex;flex-wrap:wrap;margin-right:-12rpx}
.store-chip{display:flex;flex-direction:column;width:calc(33.33% - 12rpx);margin-right:12rpx;padding:14rpx 12rpx}
.store-chip.current{border:1rpx solid var(--brand);background:#f4f7ff}
.store-chip-name{overflow:hidden;font-size:21rpx;font-weight:700;text-overflow:ellipsis;white-space:nowrap}
.store-chip-meta{margin-top:5rpx;color:var(--muted);font-size:18rpx}
/* ---- 领券弹层 ---- */
.coupon-mask{position:fixed;left:0;top:0;right:0;bottom:0;z-index:100;display:flex;align-items:center;justify-content:center;background:rgba(0,0,0,.5)}
.coupon-popup-wrap{display:flex;flex-direction:column;align-items:center}
.coupon-popup{width:540rpx;padding:44rpx 36rpx 32rpx;border-radius:26rpx;text-align:center;background:#fff;box-shadow:0 24rpx 60rpx rgba(0,0,0,.25)}
.coupon-popup-title{display:block;font-size:32rpx;font-weight:800;color:var(--brand-950)}
.coupon-popup-copy{display:block;margin-top:12rpx;color:var(--muted);font-size:22rpx}
.coupon-popup-value{display:flex;align-items:baseline;justify-content:center;margin-top:22rpx;color:#e8502c}
.coupon-popup-symbol{font-size:30rpx;font-weight:800}
.coupon-popup-number{font-size:80rpx;font-weight:900;line-height:1}
.coupon-popup-btn{display:flex;align-items:center;justify-content:center;width:100%;height:80rpx;margin-top:24rpx;border-radius:40rpx;background:linear-gradient(135deg,#e8502c,#ff7a45);color:#fff;font-size:26rpx;font-weight:700}
.coupon-close{display:flex;align-items:center;justify-content:center;width:62rpx;height:62rpx;margin-top:26rpx;border-radius:50%;background:rgba(255,255,255,.16);color:#fff;font-size:30rpx;line-height:1}
</style>
