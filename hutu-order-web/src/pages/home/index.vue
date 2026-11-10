<template>
  <view class="page-shell home-page">
    <!-- 顶部轮播：肥嘟嘟主题顶部 + 袋鼠Logo + 状态胶囊 -->
    <view class="hero">
      <swiper class="hero-swiper" circular autoplay :interval="4000" :duration="500" indicator-dots indicator-color="rgba(255,255,255,.5)" indicator-active-color="#FFC300">
        <swiper-item v-for="banner in banners" :key="banner.id">
          <view class="hero-slide" @click="onBannerTap(banner)">
            <image class="hero-image" :src="resolveImage(banner.image)" mode="aspectFill" />
          </view>
        </swiper-item>
      </swiper>
      <view class="hero-top-spacer" :style="{ height: statusBarHeight + 'px' }" />
      <view class="hero-nav">
        <view class="hero-brand">
          <image class="hero-logo" src="/static/image/kangaroo.png" mode="aspectFit" />
          <text class="hero-brand-name">肥嘟嘟餐饮</text>
        </view>
        <view class="hero-status-chip">
          <text class="status-dot" />
          <text>{{ currentStore.status === 'busy' ? '出餐繁忙' : '营业中' }} · {{ currentStore.hours }}</text>
        </view>
      </view>
    </view>

    <!-- 暖黄搜索栏：吸顶独立一行 -->
    <view class="search-dock">
      <view class="search-bar">
        <view class="search-glyph">
          <view class="search-icon-circle" />
          <view class="search-icon-stem" />
        </view>
        <input v-model="keyword" class="search-input" :placeholder="placeholder" confirm-type="search" @confirm="doSearch" @input="onKeywordInput" />
        <view v-if="keyword" class="search-clear-btn" @click="clearSearch">
          <text class="clear-x">×</text>
        </view>
        <view class="search-btn" @click="doSearch">搜索</view>
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
      <!-- 金刚区：仿品质外卖P1风格，纯图标无Emoji，两行五列十格 -->
      <view class="section">
        <view class="diamond card">
          <view class="diamond-grid">
            <view v-for="cat in categoryTabs" :key="cat.key" class="diamond-item" @click="onCategoryTap(cat)">
              <text v-if="cat.badge" class="diamond-badge" :class="cat.badgeClass">{{ cat.badge }}</text>
              <view class="diamond-icon-wrap">
                <image class="diamond-icon-img" :src="cat.icon" mode="aspectFit" />
              </view>
              <text class="diamond-name">{{ cat.name }}</text>
            </view>
          </view>
        </view>
      </view>

      <!-- 美食节横幅：暖黄与鲜美食材结合风格 -->
      <view class="section">
        <view class="festival" @click="startOrder('dumplings')">
          <view class="festival-copy">
            <view class="festival-brand">
              <text class="brand-pill">肥嘟嘟专送</text>
              <text class="brand-sub">超级品牌日 · 校园精选鲜饺</text>
            </view>
            <view class="festival-title">鲜饺尝鲜 · 校园美食节</view>
            <view class="festival-sub">现包现煮 皮薄汁多 · 平台立减 ¥6</view>
            <view class="festival-btn">
              <text>立即开吃</text>
              <text class="festival-arrow">›</text>
            </view>
          </view>
          <view class="festival-pic">
            <image class="festival-image" :src="festival.image" mode="aspectFill" />
          </view>
        </view>
      </view>

      <!-- 券卡 + 秒杀卡：双卡区 -->
      <view class="section">
        <view class="promo-row">
          <view class="promo voucher" @click="claimOne(couponPack[0])">
            <view class="v-header">
              <text class="v-tag">限时神券</text>
              <text class="v-badge-tip">肥嘟嘟专享</text>
            </view>
            <view class="v-ticket-body">
              <view class="v-ticket-left">
                <view class="v-price-row">
                  <text class="v-symbol">¥</text>
                  <text class="v-num">{{ voucherAmount }}</text>
                </view>
                <text class="v-ticket-type">津贴神券</text>
              </view>
              <view class="v-ticket-dash" />
              <view class="v-ticket-right">
                <text class="v-ticket-title">吃货专属红包</text>
                <text class="v-ticket-limit">无门槛 / 满20可用</text>
                <text class="v-ticket-save">最高狂省 ¥{{ voucherSave }}</text>
              </view>
            </view>
            <view class="v-btn" :class="{ claimed: voucherClaimed }">{{ voucherClaimed ? '已存入钱包' : '立即抢券 ›' }}</view>
          </view>
          <view class="promo flash" @click="openProduct(deal.id)">
            <view class="flash-head">
              <text class="flash-tag">原味特惠</text>
              <view class="flash-clock">
                <text class="clock-icon" />
                <text>{{ deal.clock }}</text>
              </view>
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

      <!-- 筛选栏 -->
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
              <view class="shop-rating-box">
                <text class="star-ico">★</text>
                <text class="shop-rating-num">{{ shop.rating || '4.8' }}</text>
              </view>
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
              <text class="quote-tag">肥嘟嘟力荐</text>
              <text class="quote-text">{{ shop.quote }}</text>
            </view>
          </view>
        </view>
        <view v-if="!visibleShops.length" class="shop-empty card">当前筛选下没有店铺，试试「综合排序」</view>
      </view>

      <!-- 人气餐品：加减按钮为圆形 (Circular Button) -->
      <view class="section recommend-section">
        <view class="section-heading"><text class="section-title">人气餐品</text><text class="section-link" @click="startOrder(state.selectedStallId)">全部餐品 ›</text></view>
        <scroll-view scroll-x class="recommend-scroll" :show-scrollbar="false">
          <view class="recommend-row">
            <view v-for="product in popularProducts" :key="product.id" class="recommend-card card" @click="openProduct(product.id)">
              <image class="recommend-image" :src="product.image" mode="aspectFill" />
              <text class="recommend-name">{{ product.name }}</text>
              <view class="recommend-bottom">
                <text class="recommend-price">{{ formatMoney(product.priceCents) }}</text>
                <view class="recommend-add-btn">
                  <text class="plus-symbol">＋</text>
                </view>
              </view>
            </view>
          </view>
        </scroll-view>
      </view>
    </template>

    <!-- 领券弹层 -->
    <view v-if="couponPopup.show" class="coupon-mask">
      <view class="coupon-popup-wrap">
        <view class="coupon-popup" @click.stop>
          <image class="popup-kangaroo" src="/static/image/kangaroo.png" mode="aspectFit" />
          <text class="coupon-popup-title">{{ couponPopup.title }}</text>
          <text class="coupon-popup-copy">{{ couponPopup.copy }}</text>
          <view class="coupon-popup-value">
            <text class="coupon-popup-symbol">¥</text>
            <text class="coupon-popup-number">{{ couponPopup.amount }}</text>
          </view>
          <button class="coupon-popup-btn" @click="goOrderFromPopup">去下单使用</button>
        </view>
        <button class="coupon-close" @click="couponPopup.show = false">×</button>
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
const placeholder = '搜美食、店铺、快餐或饮品'
const activeFilter = ref('rating')
const filterTabs = [
  { id: 'rating', name: '口碑榜首' },
  { id: 'all', name: '综合排序' },
  { id: 'deal', name: '超值特惠' },
  { id: 'promo', name: '满减专区' },
]

onShow(() => { loadCatalog().catch(() => {}); loadStoreReviewSummary().catch(() => {}) })

const popularProducts = computed(() => state.products.filter((product) => product.featured))

// 金刚区十格：使用P1提取的3D质感图标及同类配套图标，杜绝Emoji
const categoryTabs = [
  { key: 'foreign', name: '异国料理', icon: '/static/category/foreign.png', badge: '热门', badgeClass: 'hot', stallId: 'stir-fry' },
  { key: 'snack', name: '小吃馆', icon: '/static/category/snack.png', stallId: 'drinks' },
  { key: 'home', name: '家常菜', icon: '/static/category/home_cook.png', stallId: 'henan' },
  { key: 'tea', name: '下午茶', icon: '/static/category/afternoon_tea.png', badge: '精选', badgeClass: 'new', stallId: 'drinks' },
  { key: 'rice', name: '便当盖饭', icon: '/static/category/rice.png', stallId: 'stir-fry' },
  { key: 'noodle', name: '特色粉面', icon: '/static/category/noodle.png', stallId: 'noodles' },
  { key: 'dumpling', name: '水饺馄饨', icon: '/static/category/dumpling.png', badge: '手工', badgeClass: 'hand', stallId: 'dumplings' },
  { key: 'light', name: '减脂轻食', icon: '/static/category/light.png', stallId: 'light-food' },
  { key: 'fried', name: '炸鸡汉堡', icon: '/static/category/fried.png', stallId: 'stir-fry' },
  { key: 'night', name: '夜宵专场', icon: '/static/category/night.png', badge: '狂欢', badgeClass: 'cardnew', stallId: 'stir-fry' },
]

// 美食节横幅：取真实封面图
const festival = computed(() => {
  const product = state.products.find((p) => p.stallId === 'dumplings' && p.image) || state.products.find((p) => p.image) || { image: '' }
  return { image: product.image }
})

// 秒杀卡：黑椒鸡腿饭，保持原有后端参数接口不变
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
  if (!cat.stallId) { uni.showToast({ title: `${cat.name}正在准备中`, icon: 'none' }); return }
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

// 搜索：本地真实过滤，保持原本逻辑不变
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
.home-page {
  background: #F7F8FA;
  padding-bottom: 30rpx;
}

/* ---- hero：顶部暖黄微渐变 + 轮播 + 袋鼠Logo与状态 ---- */
.hero {
  position: relative;
  background: #FFC300;
}
.hero-swiper {
  height: 380rpx;
}
.hero-slide {
  position: relative;
  width: 100%;
  height: 100%;
}
.hero-image {
  width: 100%;
  height: 100%;
}
.hero-slide::after {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(180deg, rgba(20, 20, 20, .45) 0%, rgba(20, 20, 20, .15) 30%, rgba(20, 20, 20, 0) 65%);
}
.hero-top-spacer {
  position: absolute;
  left: 0;
  top: 0;
  right: 0;
  z-index: 3;
  pointer-events: none;
}
.hero-nav {
  position: absolute;
  z-index: 3;
  left: 0;
  top: 0;
  right: 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24rpx;
  padding-top: calc(env(safe-area-inset-top) + 12rpx);
}
.hero-brand {
  display: flex;
  align-items: center;
  padding: 6rpx 16rpx 6rpx 8rpx;
  border-radius: 30rpx;
  background: rgba(255, 255, 255, .92);
  box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, .12);
}
.hero-logo {
  width: 48rpx;
  height: 48rpx;
  margin-right: 10rpx;
  border-radius: 50%;
}
.hero-brand-name {
  font-size: 24rpx;
  font-weight: 900;
  color: #222426;
  letter-spacing: .5rpx;
}
.hero-status-chip {
  display: flex;
  align-items: center;
  padding: 8rpx 18rpx;
  border-radius: 24rpx;
  color: #222426;
  background: #FFC300;
  font-size: 20rpx;
  font-weight: 700;
  box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, .15);
}
.status-dot {
  width: 12rpx;
  height: 12rpx;
  margin-right: 8rpx;
  border-radius: 50%;
  background: #07C160;
}

/* ---- 品质外卖风格搜索栏 ---- */
.search-dock {
  position: sticky;
  top: 0;
  z-index: 30;
  padding: 16rpx 24rpx 10rpx;
  background: #F7F8FA;
}
.search-bar {
  display: flex;
  align-items: center;
  height: 82rpx;
  padding: 0 8rpx 0 26rpx;
  border-radius: 41rpx;
  background: #fff;
  border: 2rpx solid #FFC300;
  box-shadow: 0 6rpx 20rpx rgba(255, 195, 0, .15);
}
.search-glyph {
  position: relative;
  width: 32rpx;
  height: 32rpx;
  margin-right: 14rpx;
  flex: 0 0 32rpx;
}
.search-icon-circle {
  position: absolute;
  left: 0;
  top: 0;
  width: 20rpx;
  height: 20rpx;
  border: 3.5rpx solid #222426;
  border-radius: 50%;
}
.search-icon-stem {
  position: absolute;
  right: 2rpx;
  bottom: 2rpx;
  width: 12rpx;
  height: 4rpx;
  transform: rotate(45deg);
  background: #222426;
  border-radius: 2rpx;
}
.search-input {
  flex: 1;
  height: 82rpx;
  font-size: 25rpx;
  color: #222426;
}
.search-clear-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40rpx;
  height: 40rpx;
  margin-right: 12rpx;
  border-radius: 50%;
  background: #E8EAED;
}
.clear-x {
  color: #666;
  font-size: 26rpx;
  line-height: 1;
}
.search-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 66rpx;
  padding: 0 32rpx;
  border-radius: 33rpx;
  color: #222426;
  background: #FFC300;
  font-size: 25rpx;
  font-weight: 800;
}

/* ---- 通用楼层 ---- */
.section {
  padding: 0 24rpx;
  margin-top: 18rpx;
}
.section-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 14rpx;
}
.section-title {
  color: #222426;
  font-size: 30rpx;
  font-weight: 800;
}
.section-link {
  color: #8E929E;
  font-size: 22rpx;
}
.card {
  border-radius: 22rpx;
  background: #fff;
  box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, .03);
}

/* ---- 搜索结果 ---- */
.result-summary { margin-bottom: 10rpx; color: #8E929E; font-size: 21rpx; }
.result-list { padding: 4rpx 22rpx; }
.result-row { display: flex; align-items: center; padding: 22rpx 0; border-bottom: 1rpx solid #F0F0F2; }
.result-row:last-child { border-bottom: 0; }
.result-thumb { width: 92rpx; height: 92rpx; margin-right: 18rpx; border-radius: 14rpx; background: #F6F7F9; }
.result-copy { flex: 1; min-width: 0; }
.result-name { display: block; overflow: hidden; font-size: 26rpx; font-weight: 800; color: #222426; text-overflow: ellipsis; white-space: nowrap; }
.result-desc { display: block; margin-top: 6rpx; overflow: hidden; color: #8E929E; font-size: 20rpx; text-overflow: ellipsis; white-space: nowrap; }
.result-extra { margin-left: 14rpx; color: #FF4B3E; font-size: 24rpx; font-weight: 800; }
.result-empty { padding: 50rpx 0; text-align: center; color: #8E929E; font-size: 22rpx; }

/* ---- 金刚区：仿照P1，纯ICO食品图标 ---- */
.diamond {
  padding: 24rpx 8rpx 16rpx;
}
.diamond-grid {
  display: flex;
  flex-wrap: wrap;
}
.diamond-item {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 20%;
  padding: 8rpx 0 14rpx;
}
.diamond-badge {
  position: absolute;
  top: -2rpx;
  right: 16rpx;
  padding: 3rpx 8rpx;
  border-radius: 8rpx 8rpx 8rpx 0;
  color: #fff;
  font-size: 16rpx;
  font-weight: 800;
  line-height: 1.2;
  z-index: 2;
}
.diamond-badge.hot { background: linear-gradient(135deg, #FF5533, #FF2B1A); }
.diamond-badge.new { background: linear-gradient(135deg, #FF8800, #FF6600); }
.diamond-badge.hand { background: linear-gradient(135deg, #FF9900, #E67A00); }
.diamond-badge.cardnew { background: linear-gradient(135deg, #FF4B3E, #E52E20); }

.diamond-icon-wrap {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 96rpx;
  height: 96rpx;
  border-radius: 24rpx;
  background: #FFFBF2;
  transition: transform .12s ease;
}
.diamond-item:active .diamond-icon-wrap {
  transform: scale(.93);
}
.diamond-icon-img {
  width: 78rpx;
  height: 78rpx;
}
.diamond-name {
  margin-top: 10rpx;
  color: #333333;
  font-size: 22rpx;
  font-weight: 600;
  letter-spacing: .2rpx;
}

/* ---- 美食节 banner ---- */
.festival {
  position: relative;
  overflow: hidden;
  border-radius: 22rpx;
  background: linear-gradient(125deg, #FF7700 0%, #FF5000 50%, #E63800 100%);
  box-shadow: 0 8rpx 24rpx rgba(255, 80, 0, .2);
}
.festival-copy {
  position: relative;
  z-index: 2;
  min-height: 188rpx;
  padding: 24rpx 210rpx 24rpx 26rpx;
}
.festival-brand {
  display: flex;
  align-items: center;
}
.brand-pill {
  padding: 4rpx 10rpx;
  border-radius: 6rpx;
  color: #222426;
  background: #FFC300;
  font-size: 18rpx;
  font-weight: 800;
  letter-spacing: .5rpx;
}
.brand-sub {
  margin-left: 10rpx;
  color: rgba(255, 255, 255, .9);
  font-size: 18rpx;
}
.festival-title {
  margin-top: 10rpx;
  color: #fff;
  font-size: 40rpx;
  font-weight: 900;
  letter-spacing: 1rpx;
  line-height: 1.2;
}
.festival-sub {
  margin-top: 6rpx;
  color: rgba(255, 255, 255, .85);
  font-size: 20rpx;
}
.festival-btn {
  display: inline-flex;
  align-items: center;
  margin-top: 14rpx;
  padding: 10rpx 22rpx;
  border-radius: 20rpx;
  color: #222426;
  background: #FFC300;
  font-size: 22rpx;
  font-weight: 800;
  box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, .15);
}
.festival-arrow {
  margin-left: 6rpx;
  font-size: 22rpx;
  font-weight: 900;
}
.festival-pic {
  position: absolute;
  right: 18rpx;
  bottom: 12rpx;
  z-index: 2;
  width: 180rpx;
  height: 180rpx;
  overflow: hidden;
  border-radius: 50%;
  background: rgba(255, 255, 255, .15);
  box-shadow: 0 8rpx 22rpx rgba(0, 0, 0, .2);
}
.festival-image {
  width: 100%;
  height: 100%;
}

/* ---- 券卡 + 秒杀卡 (全新设计外卖红包券) ---- */
.promo-row {
  display: flex;
  margin-right: -16rpx;
}
.promo {
  position: relative;
  margin-right: 16rpx;
  padding: 20rpx;
  border-radius: 20rpx;
}
.voucher {
  flex: 1.05;
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, #FFF6F4 0%, #FFF0EB 60%, #FFE9E2 100%);
  border: 2rpx solid #FFD4C8;
  box-shadow: 0 4rpx 14rpx rgba(255, 75, 62, .08);
}
.v-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.v-tag {
  display: inline-block;
  padding: 4rpx 10rpx;
  border-radius: 6rpx;
  color: #fff;
  background: linear-gradient(90deg, #FF5B48, #FF3824);
  font-size: 18rpx;
  font-weight: 800;
  box-shadow: 0 2rpx 8rpx rgba(255, 56, 36, .3);
}
.v-badge-tip {
  color: #FF5A45;
  font-size: 18rpx;
  font-weight: 700;
}
.v-ticket-body {
  position: relative;
  display: flex;
  align-items: center;
  margin-top: 14rpx;
  padding: 12rpx 14rpx;
  border-radius: 12rpx;
  background: #fff;
  border: 1rpx dashed #FFCEC2;
}
.v-ticket-left {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  flex: 0 0 84rpx;
}
.v-price-row {
  display: flex;
  align-items: baseline;
}
.v-symbol {
  color: #FF3824;
  font-size: 22rpx;
  font-weight: 900;
}
.v-num {
  margin-left: 2rpx;
  color: #FF3824;
  font-size: 44rpx;
  font-weight: 900;
  line-height: 1;
}
.v-ticket-type {
  margin-top: 4rpx;
  color: #FF7700;
  font-size: 17rpx;
  font-weight: 700;
}
.v-ticket-dash {
  width: 2rpx;
  height: 56rpx;
  margin: 0 10rpx;
  background: repeating-linear-gradient(to bottom, #FFD0C4 0, #FFD0C4 6rpx, transparent 6rpx, transparent 12rpx);
}
.v-ticket-right {
  display: flex;
  flex-direction: column;
  min-width: 0;
  flex: 1;
}
.v-ticket-title {
  color: #222426;
  font-size: 22rpx;
  font-weight: 800;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.v-ticket-limit {
  margin-top: 4rpx;
  color: #8E929E;
  font-size: 17rpx;
}
.v-ticket-save {
  margin-top: 2rpx;
  color: #FF3824;
  font-size: 17rpx;
  font-weight: 700;
}
.v-btn {
  margin-top: 16rpx;
  padding: 12rpx 0;
  border-radius: 26rpx;
  text-align: center;
  color: #fff;
  background: linear-gradient(90deg, #FF5B48, #FF3824);
  font-size: 22rpx;
  font-weight: 800;
  box-shadow: 0 4rpx 14rpx rgba(255, 56, 36, .35);
  transition: all .15s ease;
}
.v-btn.claimed {
  background: #E8EAED;
  color: #8E929E;
  box-shadow: none;
}

.flash {
  flex: .96;
  display: flex;
  flex-direction: column;
  background: #fff;
  border: 2rpx solid #FFE4DD;
}
.flash-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.flash-tag {
  padding: 4rpx 10rpx;
  border-radius: 6rpx;
  color: #FF4B3E;
  background: #FFF0ED;
  font-size: 18rpx;
  font-weight: 800;
}
.flash-clock {
  display: flex;
  align-items: center;
  padding: 4rpx 10rpx;
  border-radius: 8rpx;
  color: #fff;
  background: #222426;
  font-size: 18rpx;
  font-weight: 700;
}
.flash-title {
  margin-top: 10rpx;
  color: #222426;
  font-size: 27rpx;
  font-weight: 800;
}
.flash-sub {
  margin-top: 4rpx;
  color: #8E929E;
  font-size: 18rpx;
}
.flash-sales {
  margin-top: 8rpx;
  color: #FF7700;
  font-size: 18rpx;
}
.flash-bar {
  height: 10rpx;
  margin-top: 10rpx;
  overflow: hidden;
  border-radius: 5rpx;
  background: #FFEBE6;
}
.flash-bar-fill {
  height: 100%;
  border-radius: 5rpx;
  background: linear-gradient(90deg, #FFAA88, #FF4B3E);
}
.flash-bar-tip {
  margin-top: 6rpx;
  color: #FF4B3E;
  font-size: 17rpx;
}
.flash-foot {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: auto;
  padding-top: 14rpx;
}
.flash-price {
  display: flex;
  align-items: baseline;
}
.flash-symbol {
  color: #FF4B3E;
  font-size: 20rpx;
  font-weight: 900;
}
.flash-num {
  margin-left: 2rpx;
  color: #FF4B3E;
  font-size: 40rpx;
  font-weight: 900;
  line-height: 1;
}
.flash-old {
  margin-left: 6rpx;
  color: #B5B8C0;
  font-size: 18rpx;
  text-decoration: line-through;
}
.flash-btn {
  padding: 11rpx 22rpx;
  border-radius: 20rpx;
  color: #fff;
  background: #FF4B3E;
  font-size: 21rpx;
  font-weight: 800;
}

/* ---- 筛选标签 ---- */
.filter-scroll { width: 100%; white-space: nowrap; }
.filter-row { display: flex; padding-right: 24rpx; }
.filter-pill {
  margin-right: 14rpx;
  padding: 10rpx 24rpx;
  border: 1rpx solid #EBECEF;
  border-radius: 28rpx;
  background: #fff;
  color: #666666;
  font-size: 22rpx;
  font-weight: 600;
}
.filter-pill.active {
  border-color: #222426;
  background: #222426;
  color: #FFC300;
  font-weight: 800;
}
.coupon-strip {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 12rpx;
  padding: 14rpx 20rpx;
  border-radius: 14rpx;
  background: #FFF7EB;
  color: #D95500;
  font-size: 21rpx;
  font-weight: 700;
}
.coupon-strip-sub { color: #A6754B; font-size: 19rpx; font-weight: 400; }

/* ---- 店铺卡 ---- */
.shop-card {
  display: flex;
  margin-bottom: 16rpx;
  padding: 16rpx;
}
.shop-cover {
  position: relative;
  width: 196rpx;
  height: 168rpx;
  flex: 0 0 196rpx;
  overflow: hidden;
  border-radius: 16rpx;
  background: #F4F5F8;
}
.shop-cover image { width: 100%; height: 100%; }
.shop-info { flex: 1; min-width: 0; padding: 4rpx 6rpx 4rpx 18rpx; }
.shop-title-row { display: flex; align-items: baseline; }
.shop-name { overflow: hidden; font-size: 28rpx; font-weight: 800; color: #222426; text-overflow: ellipsis; white-space: nowrap; }
.shop-store { margin-left: 10rpx; flex: 0 0 auto; color: #8E929E; font-size: 18rpx; }
.shop-meta-row { display: flex; align-items: center; margin-top: 8rpx; color: #666; font-size: 20rpx; white-space: nowrap; }
.shop-rating-box { display: flex; align-items: center; }
.star-ico { color: #FF9900; font-size: 22rpx; margin-right: 4rpx; }
.shop-rating-num { color: #FF7700; font-weight: 800; }
.shop-sep { margin: 0 8rpx; color: #D5D8DE; }
.shop-quote { display: flex; align-items: center; margin-top: 10rpx; overflow: hidden; }
.quote-tag {
  flex: 0 0 auto;
  padding: 3rpx 10rpx;
  margin-right: 10rpx;
  border-radius: 6rpx;
  color: #8C5700;
  background: #FFF4D9;
  font-size: 17rpx;
  font-weight: 800;
}
.quote-text { overflow: hidden; color: #8C6A48; font-size: 20rpx; text-overflow: ellipsis; white-space: nowrap; }
.shop-empty { padding: 48rpx; text-align: center; color: #8E929E; font-size: 22rpx; }

/* ---- 人气餐品 ---- */
.recommend-section { padding-right: 0; }
.recommend-scroll { width: 100%; white-space: nowrap; }
.recommend-row { display: flex; padding: 2rpx 24rpx 10rpx 0; }
.recommend-card {
  display: inline-flex;
  flex-direction: column;
  width: 204rpx;
  margin-right: 16rpx;
  padding: 12rpx;
}
.recommend-image { width: 180rpx; height: 150rpx; border-radius: 14rpx; background: #F4F5F8; }
.recommend-name { margin-top: 10rpx; overflow: hidden; font-size: 23rpx; font-weight: 800; color: #222426; text-overflow: ellipsis; white-space: nowrap; }
.recommend-bottom { display: flex; align-items: center; justify-content: space-between; margin-top: 10rpx; }
.recommend-price { color: #FF4B3E; font-size: 25rpx; font-weight: 900; }

/* 人气餐品圆形添加按钮 (Circular Add Button) */
.recommend-add-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 44rpx;
  height: 44rpx;
  border-radius: 50%;
  color: #222426;
  background: #FFC300;
  box-shadow: 0 4rpx 10rpx rgba(255, 195, 0, .4);
}
.plus-symbol {
  font-size: 26rpx;
  font-weight: 900;
  line-height: 1;
}

/* ---- 附近门店 ---- */
.store-strip { display: flex; flex-wrap: wrap; margin-right: -12rpx; }
.store-chip {
  display: flex;
  flex-direction: column;
  width: calc(33.33% - 12rpx);
  margin-right: 12rpx;
  padding: 16rpx 14rpx;
  transition: all .15s ease;
}
.store-chip.current {
  border: 2rpx solid #FFC300;
  background: #FFFDF5;
}
.store-chip-name { overflow: hidden; font-size: 22rpx; font-weight: 800; color: #222426; text-overflow: ellipsis; white-space: nowrap; }
.store-chip-meta { margin-top: 6rpx; color: #8E929E; font-size: 18rpx; }

/* ---- 领券弹层 ---- */
.coupon-mask {
  position: fixed;
  left: 0;
  top: 0;
  right: 0;
  bottom: 0;
  z-index: 100;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, .55);
}
.coupon-popup-wrap { display: flex; flex-direction: column; align-items: center; }
.coupon-popup {
  width: 540rpx;
  padding: 44rpx 36rpx 36rpx;
  border-radius: 28rpx;
  text-align: center;
  background: #fff;
  box-shadow: 0 24rpx 60rpx rgba(0, 0, 0, .3);
}
.popup-kangaroo {
  width: 120rpx;
  height: 120rpx;
  margin: 0 auto 16rpx;
}
.coupon-popup-title { display: block; font-size: 34rpx; font-weight: 900; color: #222426; }
.coupon-popup-copy { display: block; margin-top: 10rpx; color: #8E929E; font-size: 22rpx; }
.coupon-popup-value { display: flex; align-items: baseline; justify-content: center; margin-top: 22rpx; color: #FF4B3E; }
.coupon-popup-symbol { font-size: 32rpx; font-weight: 900; }
.coupon-popup-number { font-size: 84rpx; font-weight: 900; line-height: 1; }
.coupon-popup-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 84rpx;
  margin-top: 28rpx;
  border-radius: 42rpx;
  background: #FFC300;
  color: #222426;
  font-size: 28rpx;
  font-weight: 800;
  box-shadow: 0 6rpx 18rpx rgba(255, 195, 0, .4);
}
.coupon-close {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 66rpx;
  height: 66rpx;
  margin-top: 28rpx;
  border-radius: 50%;
  background: rgba(255, 255, 255, .25);
  color: #fff;
  font-size: 34rpx;
  line-height: 1;
}
</style>
