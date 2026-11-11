<script setup>
import { computed } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { useAppStore } from '@/store/app'
import { formatMoney } from '@/utils/format'
import { getNavLayout } from '@/utils/nav'

const store = useAppStore()
const navLayout = getNavLayout()
const d = computed(() => store.state.dashboard || {})

function load() { store.loadDashboard().catch(() => {}) }
onShow(() => {
  if (!store.state.user || store.state.user.role !== 'merchant') { uni.redirectTo({ url: '/pages/login/index' }); return }
  load()
})

const cards = computed(() => [
  { label: '待支付', value: d.value.pending_count || 0, color: '#8b8e97' },
  { label: '待接单', value: d.value.paid_count || 0, color: '#FF7700' },
  { label: '制作中', value: d.value.making_count || 0, color: '#FF9900' },
  { label: '待取餐', value: d.value.ready_count || 0, color: '#07C160' },
  { label: '已完成', value: d.value.completed_count || 0, color: '#222426' },
])
function back() {
  if (getCurrentPages().length > 1) uni.navigateBack({ fail: () => { uni.switchTab({ url: '/pages/home/index' }) } })
  else uni.switchTab({ url: '/pages/home/index' })
}
</script>

<template>
  <view class="page-shell merchant-sub">
    <view class="sub-header" :style="{ paddingTop: (navLayout.capsuleTop + 44) + 'px' }">
      <button class="top-back" :style="{ top: navLayout.capsuleTop + 'px' }" @click="back">‹</button>
      <text class="title">营业看板</text>
      <text class="subtitle">今日营业概览与订单状态分布</text>
    </view>

    <view class="hero">
      <view class="hero-card card">
        <text class="hero-number">{{ d.today_orders || 0 }}</text>
        <text class="hero-label">今日订单</text>
      </view>
      <view class="hero-card card last">
        <text class="hero-number">{{ formatMoney(d.today_sales_cents || 0) }}</text>
        <text class="hero-label">今日流水</text>
      </view>
    </view>

    <view class="grid">
      <view v-for="(c, index) in cards" :key="c.label" class="grid-card card" :class="{ last: index % 3 === 2 }">
        <text class="grid-number" :style="{ color: c.color }">{{ c.value }}</text>
        <text class="grid-label">{{ c.label }}</text>
      </view>
    </view>

    <view class="note">数据按「今日 0 点至今」统计，实时刷新可在工作台查看。</view>
  </view>
</template>

<style scoped lang="scss">
.merchant-sub { padding-bottom: 80rpx; background: #F7F8FA; }
.sub-header { position: relative; padding: calc(64rpx + var(--status-bar-height, 0px) + env(safe-area-inset-top, 0px)) 30rpx 40rpx; background: linear-gradient(135deg, #FFD21E 0%, #FFC300 70%, #FFAE00 100%); color: #222426; }
.top-back { position: absolute; left: 26rpx; top: calc(24rpx + var(--status-bar-height, 0px) + env(safe-area-inset-top, 0px)); width: 62rpx; height: 62rpx; display: flex; align-items: center; justify-content: center; border-radius: 50%; background: rgba(0, 0, 0, .08); color: #222426; font-size: 46rpx; line-height: 1; }
.eyebrow, .title, .subtitle { display: block; }
.eyebrow { font-size: 17rpx; letter-spacing: 5rpx; color: #8C5E00; }
.title { margin-top: 12rpx; font-size: 42rpx; font-weight: 900; color: #222426; }
.subtitle { margin-top: 8rpx; font-size: 21rpx; color: rgba(34, 36, 38, .75); }
.hero { display: flex; margin: -30rpx 28rpx 0; }
.hero-card { flex: 1; display: flex; flex-direction: column; margin-right: 20rpx; padding: 34rpx 28rpx; }
.hero-card.last { margin-right: 0; }
.hero-number { margin-bottom: 10rpx; font-size: 52rpx; font-weight: 800; color: var(--brand-900); }
.hero-label { font-size: 22rpx; color: var(--muted); }
.grid { display: flex; flex-wrap: wrap; padding: 26rpx 28rpx; }
.grid-card { width: calc((100% - 40rpx) / 3); margin-right: 20rpx; margin-bottom: 20rpx; display: flex; flex-direction: column; padding: 28rpx 24rpx; }
.grid-card.last { margin-right: 0; }
.grid-number { margin-bottom: 10rpx; }
.grid-number { font-size: 44rpx; font-weight: 800; }
.grid-label { font-size: 22rpx; color: var(--muted); }
.note { margin: 10rpx 28rpx 0; font-size: 20rpx; color: var(--muted); text-align: center; }
</style>
