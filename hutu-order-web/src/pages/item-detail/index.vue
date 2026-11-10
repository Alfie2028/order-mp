<script setup>
import { computed, reactive, ref, watch } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { useAppStore } from '@/store/app'
import { get } from '@/utils/request'
import { formatMoney } from '@/utils/format'

const store = useAppStore()
const productId = ref('')
const product = computed(() => store.state.products.find((item) => item.id === productId.value) || store.state.products[0])
const selected = reactive({})
const quantity = ref(1)
const imageFailed = ref(false)
// 评价：按门店汇总，公开只读接口，失败时整块不显示，不影响点餐
const reviewSummary = ref(null)

const storeId = computed(() => {
  const current = product.value
  const stall = current ? (store.state.stalls || []).find((item) => item.id === current.stallId) : null
  return (stall && stall.storeId) || store.state.currentStoreId || ''
})

const reviewStars = computed(() => {
  if (!reviewSummary.value || !reviewSummary.value.count) return ''
  const full = Math.round(reviewSummary.value.avg_rating)
  return '★'.repeat(full) + '☆'.repeat(Math.max(0, 5 - full))
})

function loadReviews() {
  if (!storeId.value) { console.log('[评价] storeId 为空，跳过请求'); return }
  console.log('[评价] 请求门店', storeId.value)
  get(`/api/reviews/store/${storeId.value}`).then((data) => {
    console.log('[评价] 返回', data)
    reviewSummary.value = data
  }).catch((err) => {
    console.warn('[评价] 请求失败', err)
    reviewSummary.value = null
  })
}

watch(storeId, () => loadReviews(), { immediate: true })

function formatDate(value) {
  return value ? String(value).slice(0, 10) : ''
}

onLoad((query) => {
  productId.value = query.id || store.state.products[0]?.id
  const current = product.value
  if (current) current.options.forEach((group) => { selected[group.id] = group.multiple ? [] : group.options[0]?.id })
})

const favorite = computed(() => store.state.favoriteIds.includes(product.value.id))
const selectedOptions = computed(() => product.value.options.reduce((acc, group) => {
  const ids = Array.isArray(selected[group.id]) ? selected[group.id] : [selected[group.id]]
  return acc.concat(group.options.filter((option) => ids.includes(option.id)).map((option) => ({ ...option, groupName: group.name })))
}, []))
const unitPrice = computed(() => product.value.priceCents + selectedOptions.value.reduce((sum, option) => sum + option.extraCents, 0))
const totalPrice = computed(() => unitPrice.value * quantity.value)

function choose(group, optionId) {
  if (!group.multiple) {
    selected[group.id] = optionId
    return
  }
  const values = selected[group.id]
  selected[group.id] = values.includes(optionId) ? values.filter((id) => id !== optionId) : [...values, optionId]
}

function isSelected(groupId, optionId) {
  const value = selected[groupId]
  return Array.isArray(value) ? value.includes(optionId) : value === optionId
}

function add(goCheckout = false) {
  if (!product.value.isActive) { uni.showToast({ title: '该商品已售罄', icon: 'none' }); return }
  store.addToCart(product.value.id, selectedOptions.value, quantity.value)
  uni.showToast({ title: '已加入购物车', icon: 'success' })
  if (goCheckout) setTimeout(() => uni.navigateTo({ url: '/pages/confirm-order/index' }), 250)
}

function goBack() {
  if (getCurrentPages().length > 1) uni.navigateBack({ fail: () => { uni.switchTab({ url: '/pages/home/index' }) } })
  else uni.switchTab({ url: '/pages/home/index' })
}
</script>

<template>
  <view class="page-shell detail-page">
    <view class="visual">
      <image v-if="!imageFailed" class="visual-image" :src="product.image" mode="aspectFit" @error="imageFailed = true" />
      <text v-else class="visual-fallback">{{ product.fallback }}</text>
      <button class="back-button" @click="goBack">‹</button>
      <button class="favorite-button" :class="{ active: favorite }" @click="store.toggleFavorite(product.id)">
        <text class="heart-ico">{{ favorite ? '♥' : '♡' }}</text>
      </button>
      <view class="visual-glow" />
    </view>

    <view class="content">
      <view class="headline">
        <view class="headline-main">
          <text v-if="product.badge" class="badge">{{ product.badge }}</text>
          <text class="title">{{ product.name }}</text>
          <text class="subtitle">{{ product.subtitle }}</text>
        </view>
        <view class="price-block">
          <text class="price">{{ formatMoney(unitPrice) }}</text>
          <text class="sales">{{ product.stallName }}</text>
        </view>
      </view>

      <view v-if="product.options.length" class="option-card card">
        <view v-for="(group, index) in product.options" :key="group.id" class="option-group" :class="{ last: index === product.options.length - 1 }">
          <view class="option-heading">
            <text class="option-title">{{ group.name }}</text>
            <text class="option-tip">{{ group.multiple ? '可多选' : '单选' }}</text>
          </view>
          <view class="option-grid">
            <button v-for="option in group.options" :key="option.id" class="option" :class="{ selected: isSelected(group.id, option.id) }" @click="choose(group, option.id)">
              <text>{{ option.name }}</text>
              <text v-if="option.extraCents" class="option-extra">+{{ formatMoney(option.extraCents) }}</text>
            </button>
          </view>
        </view>
      </view>

      <view v-if="reviewSummary" class="review-card card">
        <view v-if="reviewSummary.count" class="review-head">
          <view class="review-score">
            <text class="review-score-value">{{ reviewSummary.avg_rating.toFixed(1) }}</text>
            <text class="review-score-label">综合评分</text>
          </view>
          <view class="review-head-main">
            <text class="review-stars">{{ reviewStars }}</text>
            <text class="review-sub">{{ reviewSummary.count }} 条评价 · 好评率 {{ reviewSummary.good_rate }}%</text>
          </view>
        </view>
        <view v-if="reviewSummary.count" class="review-list">
          <view v-for="item in reviewSummary.recent" :key="item.id" class="review-item">
            <view class="review-item-head">
              <text class="review-user">{{ item.username }}</text>
              <text class="review-stars small">{{ '★'.repeat(item.rating) }}</text>
            </view>
            <text class="review-content">{{ item.content }}</text>
            <text class="review-date">{{ formatDate(item.created_at) }}</text>
          </view>
        </view>
        <view v-else class="review-empty">这个档口还没有评价，等你来写第一条</view>
      </view>

      <view class="notice card">
        <view class="notice-side-bar" />
        <view>
          <text class="notice-title">肥嘟嘟品质现制</text>
          <text class="notice-copy">餐品将在下单后新鲜现做，请按预计出餐时间前往档口自取或等候配送。</text>
        </view>
      </view>
    </view>

    <!-- 底部操作栏：圆形加减按钮 (Circular Stepper Buttons) -->
    <view class="action-bar">
      <view class="stepper">
        <button class="circle-btn minus" @click="quantity = Math.max(1, quantity - 1)">
          <text class="btn-glyph">−</text>
        </button>
        <text class="stepper-count">{{ quantity }}</text>
        <button class="circle-btn plus" @click="quantity += 1">
          <text class="btn-glyph">＋</text>
        </button>
      </view>
      <button class="secondary-action" @click="add(false)">加入购物车</button>
      <button class="primary-action" @click="add(true)">去结算 · {{ formatMoney(totalPrice) }}</button>
    </view>
  </view>
</template>

<style scoped lang="scss">
.detail-page { padding-bottom: 180rpx; background: #F7F8FA; }
.visual {
  height: 580rpx;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  background: radial-gradient(circle at 50% 44%, #FFFFFF 0%, #FFF9EB 55%, #FFEEC4 100%);
}
.visual-image { width: 86%; height: 86%; position: relative; z-index: 2; }
.visual-fallback { position: relative; z-index: 2; font-size: 220rpx; }
.visual-glow {
  position: absolute;
  width: 380rpx;
  height: 80rpx;
  bottom: 50rpx;
  border-radius: 50%;
  background: rgba(255, 195, 0, .25);
}
.back-button, .favorite-button {
  position: fixed;
  top: calc(24rpx + var(--status-bar-height, 0px) + env(safe-area-inset-top, 0px));
  z-index: 4;
  width: 72rpx;
  height: 72rpx;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, .92);
  color: #222426;
  box-shadow: 0 4rpx 14rpx rgba(0, 0, 0, .1);
}
.back-button { left: 26rpx; font-size: 48rpx; line-height: 1; }
.favorite-button { right: 26rpx; }
.heart-ico { font-size: 38rpx; color: #8E929E; }
.favorite-button.active .heart-ico { color: #FF4B3E; }

.content {
  position: relative;
  z-index: 3;
  margin-top: -40rpx;
  padding: 34rpx 24rpx 0;
  border-radius: 36rpx 36rpx 0 0;
  background: #F7F8FA;
}
.headline { display: flex; justify-content: space-between; }
.headline-main { flex: 1; min-width: 0; }
.badge {
  display: inline-block;
  margin-bottom: 12rpx;
  padding: 6rpx 14rpx;
  border-radius: 8rpx;
  background: linear-gradient(135deg, #FF6040, #FF3824);
  color: #fff;
  font-size: 19rpx;
  font-weight: 800;
}
.title { font-size: 40rpx; font-weight: 900; color: #222426; display: block; }
.subtitle { margin-top: 10rpx; color: #8E929E; font-size: 23rpx; line-height: 1.5; display: block; }

.price-block { text-align: right; padding-top: 28rpx; }
.price { font-size: 36rpx; font-weight: 900; color: #FF4B3E; }
.sales { margin-top: 6rpx; font-size: 19rpx; color: #B37D00; font-weight: 600; display: block; }

.option-card { margin-top: 26rpx; padding: 10rpx 26rpx; }
.option-group { padding: 24rpx 0; border-bottom: 1rpx solid #F0F0F2; }
.option-group.last { border-bottom: 0; }
.option-heading { display: flex; align-items: center; justify-content: space-between; margin-bottom: 18rpx; }
.option-title { font-weight: 800; font-size: 28rpx; color: #222426; }
.option-tip { font-size: 20rpx; color: #8E929E; }
.option-grid { display: flex; flex-wrap: wrap; margin-right: -14rpx; }
.option {
  width: calc(50% - 14rpx);
  margin-right: 14rpx;
  margin-bottom: 14rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 76rpx;
  padding: 0 16rpx;
  border: 2rpx solid #EBECEF;
  border-radius: 18rpx;
  color: #222426;
  background: #fff;
  font-size: 24rpx;
  transition: all .12s ease;
}
.option.selected {
  border-color: #FFC300;
  background: #FFF9E6;
  color: #222426;
  font-weight: 800;
}
.option-extra { margin-left: 6rpx; font-size: 19rpx; color: #FF4B3E; }

.review-card { margin-top: 22rpx; padding: 24rpx; }
.review-head { display: flex; align-items: center; padding-bottom: 20rpx; border-bottom: 1rpx solid #F0F0F2; }
.review-score {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-right: 24rpx;
  padding-right: 24rpx;
  border-right: 1rpx solid #F0F0F2;
}
.review-score-value { font-size: 46rpx; font-weight: 900; line-height: 1; color: #FF7700; }
.review-score-label { margin-top: 6rpx; font-size: 18rpx; color: #8E929E; }
.review-head-main { flex: 1; }
.review-stars { font-size: 28rpx; letter-spacing: 2rpx; color: #FF9900; }
.review-stars.small { font-size: 20rpx; }
.review-sub { display: block; margin-top: 8rpx; font-size: 20rpx; color: #8E929E; }
.review-list { margin-top: 6rpx; }
.review-item { padding: 18rpx 0; border-bottom: 1rpx solid #F5F6F8; }
.review-item:last-child { border-bottom: 0; }
.review-item-head { display: flex; align-items: center; justify-content: space-between; }
.review-user { font-size: 23rpx; font-weight: 800; color: #222426; }
.review-content { display: block; margin-top: 8rpx; font-size: 22rpx; line-height: 1.5; color: #555; }
.review-date { display: block; margin-top: 6rpx; font-size: 18rpx; color: #8E929E; }
.review-empty { padding: 24rpx 0; text-align: center; font-size: 22rpx; color: #8E929E; }

.notice {
  display: flex;
  margin-top: 22rpx;
  padding: 24rpx;
  position: relative;
  overflow: hidden;
}
.notice-side-bar {
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 8rpx;
  background: #FFC300;
}
.notice-title { font-size: 25rpx; font-weight: 800; color: #222426; display: block; }
.notice-copy { margin-top: 6rpx; font-size: 21rpx; color: #8E929E; line-height: 1.5; display: block; }

/* ---- 底部操作栏 ---- */
.action-bar {
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 20;
  display: flex;
  align-items: center;
  padding: 16rpx 24rpx calc(16rpx + env(safe-area-inset-bottom));
  background: #fff;
  border-top: 1rpx solid #F0F0F2;
  box-shadow: 0 -8rpx 24rpx rgba(0, 0, 0, .06);
}

/* 圆形添加减少按钮 (Circular Stepper Buttons) */
.stepper {
  display: flex;
  align-items: center;
  margin-right: 18rpx;
}
.circle-btn {
  width: 52rpx;
  height: 52rpx;
  padding: 0;
  margin: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  line-height: 1;
  transition: transform .1s ease;
}
.circle-btn:active { transform: scale(.92); }
.circle-btn.minus {
  border: 2rpx solid #FFC300;
  background: #fff;
  color: #222426;
}
.circle-btn.plus {
  background: #FFC300;
  color: #222426;
  box-shadow: 0 4rpx 10rpx rgba(255, 195, 0, .4);
}
.btn-glyph {
  font-size: 30rpx;
  font-weight: 900;
  line-height: 1;
  transform: translateY(-1rpx);
}
.stepper-count {
  min-width: 44rpx;
  padding: 0 8rpx;
  text-align: center;
  font-weight: 800;
  font-size: 28rpx;
  color: #222426;
}

.secondary-action, .primary-action {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 80rpx;
  border-radius: 40rpx;
  font-size: 25rpx;
  font-weight: 800;
}
.secondary-action {
  padding: 0 26rpx;
  border: 2rpx solid #FFC300;
  background: #FFFDF5;
  color: #8C5E00;
  margin-right: 14rpx;
}
.primary-action {
  flex: 1;
  background: #FFC300;
  color: #222426;
  white-space: nowrap;
  box-shadow: 0 4rpx 16rpx rgba(255, 195, 0, .35);
}

@media screen and (min-width: 760px) {
  .action-bar { max-width: 750px; margin: 0 auto; }
}
</style>
