<script setup>
import { computed } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import EmptyState from '@/component/EmptyState.vue'
import { useAppStore } from '@/store/app'
import { formatDateTime } from '@/utils/format'

const store = useAppStore()
const reviews = computed(() => store.state.merchantReviews || [])
const avg = computed(() => reviews.value.length ? (reviews.value.reduce((s, r) => s + r.rating, 0) / reviews.value.length).toFixed(1) : '0.0')
const goodRate = computed(() => reviews.value.length ? Math.round(reviews.value.filter((r) => r.rating >= 4).length / reviews.value.length * 100) : 0)

onShow(() => {
  if (!store.state.user || store.state.user.role !== 'merchant') { uni.redirectTo({ url: '/pages/login/index' }); return }
  store.loadMerchantReviews().catch(() => {})
})

function stars(rating) { return '★★★★★'.slice(0, rating) + '☆☆☆☆☆'.slice(0, 5 - rating) }
function back() {
  if (getCurrentPages().length > 1) uni.navigateBack({ fail: () => { uni.switchTab({ url: '/pages/home/index' }) } })
  else uni.switchTab({ url: '/pages/home/index' })
}
</script>

<template>
  <view class="page-shell merchant-sub">
    <view class="sub-header">
      <button class="top-back" @click="back">‹</button>
      <text class="title">用户评价</text>
      <text class="subtitle">顾客评分与反馈，实时了解用餐口碑</text>
    </view>

    <view class="summary">
      <view class="sum-card card"><text class="sum-number">{{ avg }}</text><text class="sum-label">平均评分</text></view>
      <view class="sum-card card"><text class="sum-number">{{ reviews.length }}</text><text class="sum-label">评价总数</text></view>
      <view class="sum-card card last"><text class="sum-number">{{ goodRate }}%</text><text class="sum-label">好评率</text></view>
    </view>

    <view v-if="reviews.length" class="review-list">
      <view v-for="r in reviews" :key="r.id" class="review-card card">
        <view class="review-head">
          <view class="user-line"><text class="user-name">{{ r.username }}</text><text class="stars">{{ stars(r.rating) }}</text></view>
          <text class="time">{{ formatDateTime(r.createdAt) }}</text>
        </view>
        <text class="content">{{ r.content || '未填写文字评价' }}</text>
        <text class="order-no">订单号 {{ r.order_no }}</text>
      </view>
    </view>
    <EmptyState v-else title="暂无评价" description="顾客完成订单并评价后，将在此展示" />
  </view>
</template>

<style scoped lang="scss">
.merchant-sub { padding-bottom: 80rpx; }
.sub-header { padding: calc(70rpx + env(safe-area-inset-top)) 30rpx 36rpx; background: linear-gradient(145deg, #0637c9, #071a62); color: #fff; }
.top-back { position: absolute; left: 26rpx; top: calc(24rpx + env(safe-area-inset-top)); width: 62rpx; height: 62rpx; display: flex; align-items: center; justify-content: center; border-radius: 50%; background: rgba(255,255,255,.12); color: #fff; font-size: 46rpx; line-height: 1; }
.eyebrow, .title, .subtitle { display: block; }
.eyebrow { font-size: 17rpx; letter-spacing: 5rpx; color: #edcf91; }
.title { margin-top: 12rpx; font-size: 42rpx; font-weight: 800; }
.subtitle { margin-top: 8rpx; font-size: 21rpx; color: rgba(255,255,255,.65); }
.summary { display: flex; margin: -30rpx 28rpx 0; }
.sum-card { flex: 1; display: flex; flex-direction: column; margin-right: 20rpx; padding: 32rpx 20rpx; }
.sum-card.last { margin-right: 0; }
.sum-number { margin-bottom: 10rpx; font-size: 46rpx; font-weight: 800; color: var(--brand-900); }
.sum-label { font-size: 21rpx; color: var(--muted); }
.review-list { padding: 26rpx 28rpx; }
.review-card { margin-bottom: 20rpx; padding: 24rpx; }
.review-head { display: flex; align-items: flex-start; justify-content: space-between; }
.user-line { display: flex; flex-direction: column; }
.user-name { margin-bottom: 8rpx; font-size: 26rpx; font-weight: 700; }
.stars { font-size: 26rpx; color: #f7b731; letter-spacing: 3rpx; }
.time { font-size: 19rpx; color: var(--muted); }
.content { display: block; margin-top: 16rpx; font-size: 24rpx; color: var(--ink); line-height: 1.6; }
.order-no { display: block; margin-top: 12rpx; padding-top: 14rpx; border-top: 1rpx solid var(--line); font-size: 19rpx; color: var(--muted); }
</style>
