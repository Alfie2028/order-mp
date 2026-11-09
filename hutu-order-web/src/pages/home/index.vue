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

    <!-- 搜索栏：位于轮播图下方独立一行，吸顶，搜索真实可用 -->
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
      <!-- 金刚区：两行五列十格，分区口径按点单区 mock，点击进对应门店 -->
      <view class="section">
        <view class="diamond card">
          <view class="diamond-grid">
            <view v-for="cat in categoryTabs" :key="cat.key" class="diamond-item" @click="onCategoryTap(cat)">
              <text v-if="cat.badge" class="diamond-badge" :class="cat.badgeClass">{{ cat.badge }}</text>
              <view class="diamond-icon">{{ cat.icon }}</view>
              <text class="diamond-name">{{ cat.name }}</text>
            </view>
          </view>
        </view>
      </view>

      <!-- 美食节横幅：绿底 + 商家配送标 + 立即开吃 -->
      <view class="section">
        <view class="festival" @click="startOrder('dumplings')">
          <view class="festival-copy">
            <view class="festival-brand">
              <text class="brand-pill">商家配送</text>
              <text class="brand-sub">超级品牌日 · 校园精选鲜饺</text>
            </view>
            <view class="festival-title">鲜饺尝鲜 · 校园美食节</view>
            <view class="festival-sub">现包现煮 皮薄汁多 · 平台立减 ¥6</view>
            <view class="festival-btn">立即开吃 <text class="festival-arrow">›</text></view>
          </view>
          <view class="festival-pic">
            <image class="festival-image" :src="festival.image" mode="aspectFill" />
          </view>
        </view>
      </view>

      <!-- 券卡 + 秒杀卡：复用肥嘟嘟双卡样式 -->
      <view class="section">
        <view class="promo-row">
          <view class="promo voucher" @click="claimOne(couponPack[0])">
            <text class="v-tag">限时吃券</text>
            <view class="v-title">吃货专属津贴券</view>
            <view class="v-sub">最高狂省 ¥{{ voucherSave }}</view>
            <view class="v-mid"><text class="v-symbol">¥</text><text class="v-num">{{ voucherAmount }}</text></view>
            <view class="v-btn" :class="{ claimed: voucherClaimed }">{{ voucherClaimed ? '已领取' : '一键领券' }}</view>
          </view>
          <view class="promo flash" @click="openProduct(deal.id)">
            <view class="flash-head">
              <text class="flash-tag">原味特惠</text>
              <text class="flash-clock">{{ deal.clock }}</text>
            </view>
            <view class="flash-title">{{ deal.name }}秒杀</view>
            <view class="flash-sub">现做现发 · 门店现制</view>
            <view class="flash-sales">已售 {{ deal.sales }} 份 · 剩 {{ deal.stock }} 份</view>
            <view class="flash-bar"><view class="flash-bar-fill" :style="{ width: deal.stockPercent + '%' }" /></view>
            <view class="flash-bar-tip">已抢 {{ deal.stockPercent }}%，手慢无</view>
            <view class="flash-foot">
              <view class="flash-price">
                <text class="flash-symbol">¥</text>
                <text class="flash-num">{{ deal.priceNum }}</text>
                <text v-if="deal.originalNum" class="flash-old">¥{{ deal.originalNum }}</text>
              </view>
              <view class="flash-btn">马上抢</view>
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
const { state, currentStore, merchantCards, nearbyStores, setStall, setStore, setOrderMode, claimCoupon, resolveImage, loadCatalog, loadStoreReviewSummary } = store

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

const popularProducts = computed(() => state.products.filter((product) => product.featured))

// 金刚区十格：品类在点单区按门店 mock，超出的分区落到最接近的真实门店
const categoryTabs = [
  { key: 'rice', name: '便当盖饭', icon: '🍱', badge: '热门', badgeClass: 'hot', stallId: 'stir-fry' },
  { key: 'noodle', name: '特色粉面', icon: '🍜', stallId: 'noodles' },
  { key: 'wok', name: '家常热炒', icon: '🥘', stallId: 'henan' },
  { key: 'fried', name: '炸鸡汉堡', icon: '🍗', badge: '新品', badgeClass: 'new', stallId: 'stir-fry' },
  { key: 'light', name: '减脂轻食', icon: '🥗', stallId: 'light-food' },
  { key: 'drink', name: '鲜果茶饮', icon: '🧋', stallId: 'drinks' },
  { key: 'dumpling', name: '水饺馄饨', icon: '🥟', badge: '手工', badgeClass: 'hand', stallId: 'dumplings' },
  { key: 'snack', name: '小吃卤味', icon: '🍢', stallId: 'drinks' },
  { key: 'night', name: '夜宵专场', icon: '🌙', stallId: 'stir-fry' },
  { key: 'mart', name: '超市便利', icon: '🏪', badge: '新卡', badgeClass: 'cardnew', stallId: '' },
]

// 美食节横幅：取水饺门店的真实封面图
const festival = computed(() => {
  const product = state.products.find((p) => p.stallId === 'dumplings' && p.image) || state.products.find((p) => p.image) || { image: '' }
  return { image: product.image }
})

// 秒杀卡：黑椒鸡腿饭，价格与销量都来自后端；库存进度为首页展示用的前端值
const deal = computed(() => {
  const product = state.products.find((p) => p.id === 'black-pepper-chicken-rice') || state.products[0] || {}
  const cur = product.priceCents || 0
  const original = product.originalPriceCents || 0
  return {
    id: product.id,
    name: product.name || '黑椒鸡腿饭',
    priceNum: (cur / 100).toFixed(1),
    originalNum: original > cur ? (original / 100).toFixed(1) : '',
    sales: product.sales || 0,
    stock: 40,
    stockPercent: 92,
    clock: '11:30',
  }
})

// 券包：按后端真实券列表排三张，已领的置灰
const couponPack = computed(() => {
  const list = (state.coupons || []).filter((c) => c.isActive !== false)
  return list.slice()
    .sort((a, b) => (a.thresholdCents || 0) - (b.thresholdCents || 0))
    .slice(0, 3)
    .map((c) => ({
      id: c.id,
      amount: (c.discountCents / 100).toFixed(0),
      thresholdText: c.thresholdCents ? `满 ${(c.thresholdCents / 100).toFixed(0)} 元可用` : '无门槛',
      expires: c.expires,
      claimed: state.couponIds.includes(c.id),
    }))
})
const voucherTotal = computed(() => (state.coupons || []).reduce((sum, c) => sum + (c.discountCents || 0), 0))
const voucherSave = computed(() => (voucherTotal.value / 100).toFixed(0))
const voucherAmount = computed(() => (couponPack.value[0] ? couponPack.value[0].amount : '0'))
const voucherClaimed = computed(() => (couponPack.value.length ? couponPack.value.every((c) => c.claimed) : true))

function onCategoryTap(cat) {
  if (!cat.stallId) { uni.showToast({ title: '超市便利试营业中，先逛逛门店', icon: 'none' }); return }
  goStall(cat.stallId)
}
function goMyCoupons() { uni.switchTab({ url: '/pages/my/index' }) }
async function claimOne(coupon) {
  if (!coupon || !coupon.id) { uni.showToast({ title: '券正在准备中', icon: 'none' }); return }
  if (!state.user) { uni.navigateTo({ url: '/pages/login/index' }); return }
  if (coupon.claimed) { goMyCoupons(); return }
  const result = await claimCoupon(coupon.id)
  if (result) {
    couponPopup.show = true
    couponPopup.title = '领取成功'
    couponPopup.copy = `${result.name} 已放入账户，结算时可用`
    couponPopup.amount = (result.discountCents / 100).toFixed(0)
  }
}

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
.search-dock{position:sticky;top:0;z-index:30;margin-top:0;padding:18rpx 24rpx 4rpx;background:var(--oat-50)}
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
/* ---- 金刚区：两行五列 ---- */
.diamond{padding:20rpx 10rpx 18rpx}
.diamond-grid{display:flex;flex-wrap:wrap}
.diamond-item{position:relative;display:flex;flex-direction:column;align-items:center;width:20%;padding:10rpx 0}
.diamond-badge{position:absolute;top:0;left:50%;transform:translateX(16rpx);padding:4rpx 8rpx 3rpx;border-radius:9rpx 9rpx 9rpx 0;color:#fff;font-size:17rpx;font-weight:700;line-height:1.2;z-index:2}
.diamond-badge.hot{background:linear-gradient(135deg,#ff6b4a,#f03b23)}
.diamond-badge.new{background:linear-gradient(135deg,#ff8a5c,#f5452b)}
.diamond-badge.hand{background:linear-gradient(135deg,#ff9b4a,#ef7a22)}
.diamond-badge.cardnew{background:linear-gradient(135deg,#ff7357,#e83e2c)}
.diamond-icon{display:flex;align-items:center;justify-content:center;width:82rpx;height:82rpx;border-radius:18rpx;background:linear-gradient(180deg,#fffdf8,#fff4e3);font-size:44rpx;line-height:1}
.diamond-item:nth-child(5n+2) .diamond-icon{background:linear-gradient(180deg,#fffaf8,#ffeee5)}
.diamond-item:nth-child(5n+3) .diamond-icon{background:linear-gradient(180deg,#fefcef,#fff6df)}
.diamond-item:nth-child(5n+4) .diamond-icon{background:linear-gradient(180deg,#fbfdf5,#f1f9e3)}
.diamond-item:nth-child(5n) .diamond-icon{background:linear-gradient(180deg,#f8fbfe,#eaf4ff)}
.diamond-name{margin-top:10rpx;color:#2b2f36;font-size:23rpx;letter-spacing:.2rpx}
/* ---- 美食节 banner：绿底 ---- */
.festival{position:relative;overflow:hidden;border-radius:20rpx;background:linear-gradient(120deg,#14a06b 0%,#0a7a52 62%,#0a6a48 100%)}
.festival-copy{position:relative;z-index:2;min-height:186rpx;padding:22rpx 206rpx 22rpx 24rpx}
.festival-brand{display:flex;align-items:center}
.brand-pill{padding:5rpx 9rpx;border-radius:6rpx;color:#5a3d05;background:#f7d774;font-size:18rpx;font-weight:700;letter-spacing:.5rpx}
.brand-sub{margin-left:10rpx;color:rgba(255,255,255,.78);font-size:18rpx}
.festival-title{margin-top:12rpx;color:#fff;font-size:42rpx;font-weight:800;letter-spacing:1rpx;line-height:1.18}
.festival-sub{margin-top:8rpx;color:rgba(255,255,255,.8);font-size:20rpx}
.festival-btn{display:inline-flex;align-items:center;margin-top:14rpx;padding:11rpx 18rpx;border-radius:12rpx;color:#123d2c;background:#fff;font-size:21rpx;font-weight:700}
.festival-arrow{margin-left:8rpx;font-size:20rpx}
.festival-pic{position:absolute;right:18rpx;bottom:10rpx;z-index:2;width:186rpx;height:186rpx;overflow:hidden;border-radius:50%;background:#0b6647;box-shadow:0 10rpx 26rpx rgba(0,0,0,.22)}
.festival-image{width:100%;height:100%}
/* ---- 券卡 + 秒杀卡 ---- */
.promo-row{display:flex;margin-right:-16rpx}
.promo{position:relative;margin-right:16rpx;padding:18rpx;border-radius:18rpx}
.voucher{flex:1.02;background:linear-gradient(160deg,#fff1ec 0%,#ffe3d9 100%);border:3rpx solid #ffd0c2}
.v-tag{display:inline-block;padding:4rpx 9rpx;border-radius:8rpx;color:#f0432c;background:#fff;font-size:17rpx;font-weight:700;box-shadow:0 2rpx 6rpx rgba(240,67,44,.16)}
.v-title{margin-top:10rpx;color:#4a2a22;font-size:28rpx;font-weight:800}
.v-sub{margin-top:4rpx;color:#9c6a55;font-size:19rpx}
.v-mid{display:flex;align-items:flex-end;margin-top:10rpx}
.v-symbol{margin-bottom:6rpx;color:#ef3f28;font-size:22rpx;font-weight:800;line-height:1}
.v-num{margin-left:10rpx;color:#ef3f28;font-size:62rpx;font-weight:800;line-height:.95}
.v-btn{margin-top:12rpx;padding:13rpx 0;border-radius:14rpx;text-align:center;color:#fff;background:linear-gradient(100deg,#ff8a4c,#f5452b);font-size:22rpx;font-weight:700;box-shadow:0 6rpx 14rpx rgba(240,69,43,.28)}
.v-btn.claimed{background:#e9ecf2;color:#9aa0ad;box-shadow:none}
.flash{flex:.96;display:flex;flex-direction:column;background:#fff;border:3rpx solid #ffd4c6}
.flash-head{display:flex;align-items:center;justify-content:space-between}
.flash-tag{padding:4rpx 8rpx;border-radius:6rpx;color:#f0432c;background:#fff4ef;font-size:16rpx;font-weight:700}
.flash-clock{padding:4rpx 9rpx;border-radius:7rpx;color:#fff;background:#22262c;font-size:17rpx;letter-spacing:.5rpx}
.flash-title{margin-top:10rpx;color:#3a241f;font-size:27rpx;font-weight:800}
.flash-sub{margin-top:4rpx;color:#a07a6c;font-size:18rpx}
.flash-sales{margin-top:8rpx;color:#b8826d;font-size:17rpx}
.flash-bar{height:10rpx;margin-top:10rpx;overflow:hidden;border-radius:6rpx;background:#ffe6dc}
.flash-bar-fill{height:100%;border-radius:6rpx;background:linear-gradient(90deg,#ffb08a,#f0452b)}
.flash-bar-tip{margin-top:6rpx;color:#b0745f;font-size:16rpx}
.flash-foot{display:flex;align-items:center;justify-content:space-between;margin-top:auto;padding-top:12rpx}
.flash-price{display:flex;align-items:baseline}
.flash-symbol{color:#ef3f28;font-size:20rpx;font-weight:800}
.flash-num{margin-left:2rpx;color:#ef3f28;font-size:42rpx;font-weight:800;line-height:1}
.flash-old{margin-left:6rpx;color:#a9adb6;font-size:18rpx;text-decoration:line-through}
.flash-btn{padding:11rpx 22rpx;border-radius:12rpx;color:#fff;background:linear-gradient(100deg,#ff6a44,#e6341f);font-size:21rpx;font-weight:700}
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
