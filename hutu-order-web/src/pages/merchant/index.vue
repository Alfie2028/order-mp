<script setup>
import { computed, ref } from 'vue'
import { onShow, onUnload } from '@dcloudio/uni-app'
import { useAppStore } from '@/store/app'
import { formatDateTime, formatMoney } from '@/utils/format'

const store = useAppStore()
const currentTab = ref('paid')
const tabs = [
  { id: 'paid', name: '待接单' },
  { id: 'making', name: '制作中' },
  { id: 'ready', name: '待取餐' },
  { id: 'completed', name: '已完成' },
]
// 功能入口：压缩成一行 4 个「图标 + 短标签」，把纵向空间还给订单列表
// 「营业看板」不再单独占入口，改为点击头部「今日订单 / 今日流水」进入
const entries = [
  { key: 'products', short: '餐品', icon: '餐', color: '#0637c9', url: '/pages/merchant/products' },
  { key: 'stalls', short: '档口', icon: '档', color: '#0f8b8d', url: '/pages/merchant/stalls' },
  { key: 'coupons', short: '优惠券', icon: '券', color: '#d99000', url: '/pages/merchant/coupons' },
  { key: 'reviews', short: '评价', icon: '评', color: '#7a4fd0', url: '/pages/merchant/reviews' },
]
let timer = null

const orders = computed(() => (store.state.merchantOrders || []).filter((order) => order.status === currentTab.value))
const pendingCount = computed(() => (store.state.merchantOrders || []).filter((order) => order.status === 'paid').length)
const todayOrders = computed(() => (store.state.dashboard && store.state.dashboard.today_orders) || 0)
const todaySales = computed(() => (store.state.dashboard && store.state.dashboard.today_sales_cents) || 0)
const storeStatus = computed(() => {
  const s = store.state.stores.find((x) => x.id === 'henau-canteen')
  return s ? s.status : 'open'
})
const isOpen = computed(() => storeStatus.value !== 'closed')

function load() {
  store.loadMerchantOrders().catch(() => {})
  store.loadDashboard().catch(() => {})
  store.loadCatalog().catch(() => {})
}

onShow(() => {
  if (!store.state.user || store.state.user.role !== 'merchant') { uni.redirectTo({ url: '/pages/login/index' }); return }
  load()
  if (timer) clearInterval(timer)
  timer = setInterval(load, 3000)
})
onUnload(() => { if (timer) { clearInterval(timer); timer = null } })

async function accept(orderId) { await store.acceptOrder(orderId); uni.showToast({ title: '已接单', icon: 'success' }); load() }
async function ready(orderId) { await store.readyOrder(orderId); uni.showToast({ title: '已出餐', icon: 'success' }); load() }
async function toggleOpen() {
  const res = await store.toggleStoreStatus()
  uni.showToast({ title: res.status === 'closed' ? '已打烊' : '已开张', icon: 'none' })
}
function goEntry(url) { uni.navigateTo({ url }) }
function goDashboard() { uni.navigateTo({ url: '/pages/merchant/dashboard' }) }
function logout() { store.logout(); uni.redirectTo({ url: '/pages/login/index' }) }
</script>

<template>
  <view class="page-shell merchant-page">
    <view class="merchant-header">
      <view class="header-top">
        <view><text class="title">商家工作台</text></view>
        <button class="logout" @click="logout">退出</button>
      </view>

      <view class="stats-row">
        <view class="stat-card">
          <text class="stat-number">{{ pendingCount }}</text>
          <text class="stat-label">待接订单</text>
        </view>
        <view class="stat-card" @click="goDashboard">
          <text class="stat-number">{{ todayOrders }}</text>
          <text class="stat-label">今日订单</text>
        </view>
        <view class="stat-card last" @click="goDashboard">
          <text class="stat-number">{{ formatMoney(todaySales) }}</text>
          <text class="stat-label">今日流水</text>
        </view>
      </view>

      <view class="open-toggle" :class="{ closed: !isOpen }" @click="toggleOpen">
        <text class="dot" />
        <text class="open-text">{{ isOpen ? '营业中' : '已打烊' }}</text>
        <text class="open-action">{{ isOpen ? '点击打烊' : '点击开张' }}</text>
      </view>

      <text class="poll-hint">订单每 3 秒自动刷新，请保持页面开启</text>
    </view>

    <view class="entry-row">
      <view v-for="entry in entries" :key="entry.key" class="entry-item" hover-class="entry-item--tap" @click="goEntry(entry.url)">
        <view class="entry-icon" :style="{ background: entry.color }">{{ entry.icon }}</view>
        <text class="entry-label">{{ entry.short }}</text>
      </view>
    </view>

    <scroll-view scroll-x class="tabs"><view class="tabs-inner"><button v-for="tab in tabs" :key="tab.id" :class="{ active: currentTab === tab.id }" @click="currentTab = tab.id">{{ tab.name }}</button></view></scroll-view>

    <view v-if="orders.length" class="order-list">
      <view v-for="order in orders" :key="order.id" class="order-card card">
        <view class="order-head">
          <view><text class="order-no">订单号 {{ order.id }}</text><text class="order-time">{{ formatDateTime(order.createdAt) }}</text></view>
          <text class="status" :class="order.status">{{ order.statusText }}</text>
        </view>
        <view class="items">
          <view v-for="item in order.items" :key="item.key" class="item-row">
            <text class="item-name">{{ item.name }}</text>
            <text class="item-options">{{ item.selectedOptions.map(option => option.name).join(' · ') || '标准制作' }}</text>
            <text class="item-qty">× {{ item.quantity }}</text>
          </view>
        </view>
        <view class="order-foot">
          <view class="pickup"><text class="pickup-label">取餐码</text><text class="pickup-code">{{ order.pickupCode }}</text></view>
          <text class="amount">{{ formatMoney(order.totalCents) }}</text>
          <view class="actions">
            <button v-if="order.status === 'paid'" class="primary" @click="accept(order.id)">接单</button>
            <button v-if="order.status === 'making'" class="primary" @click="ready(order.id)">出餐</button>
          </view>
        </view>
      </view>
    </view>
    <view v-else class="empty">当前「{{ tabs.find(tab => tab.id === currentTab).name }}」暂无订单</view>
  </view>
</template>

<style scoped lang="scss">
.merchant-page { min-height: 100vh; padding-bottom: 60rpx; }
.merchant-header { padding: calc(58rpx + env(safe-area-inset-top)) 30rpx 34rpx; background: linear-gradient(145deg, #0637c9, #071a62); color: #fff; }
.header-top { display: flex; align-items: flex-start; justify-content: space-between; }
.eyebrow, .title { display: block; }
.eyebrow { font-size: 18rpx; letter-spacing: 5rpx; color: #edcf91; }
.title { margin-top: 12rpx; font-size: 44rpx; font-weight: 800; }
.logout { width: 130rpx; height: 60rpx; display: flex; align-items: center; justify-content: center; border: 1rpx solid rgba(255,255,255,.3); border-radius: 30rpx; background: transparent; color: #fff; font-size: 22rpx; }
.stats-row { display: flex; margin-top: 30rpx; }
.stat-card { flex: 1; display: flex; flex-direction: column; margin-right: 18rpx; padding: 22rpx 20rpx; border-radius: 18rpx; background: rgba(255,255,255,.1); }
.stat-card.last { margin-right: 0; }
.stat-number { margin-bottom: 6rpx; font-size: 40rpx; font-weight: 800; line-height: 1; }
.stat-label { font-size: 20rpx; color: rgba(255,255,255,.7); }
.open-toggle { display: flex; align-items: center; margin-top: 20rpx; padding: 20rpx 24rpx; border-radius: 18rpx; background: rgba(255,255,255,.12); }
.open-toggle.closed { background: rgba(240, 75, 47, .25); }
.dot { width: 16rpx; height: 16rpx; margin-right: 12rpx; border-radius: 50%; background: #6ee7a0; }
.open-toggle.closed .dot { background: #fbb8ab; }
.open-text { font-size: 26rpx; font-weight: 700; }
.open-action { margin-left: auto; font-size: 22rpx; color: rgba(255,255,255,.75); }
.poll-hint { display: block; margin-top: 16rpx; font-size: 18rpx; color: rgba(255,255,255,.5); }

/* 功能入口：一行 4 个，紧凑排列，不再每个占半屏 */
.entry-row { display: flex; margin: 22rpx 24rpx 4rpx; padding: 24rpx 6rpx 20rpx; background: #fff; border-radius: 20rpx; }
.entry-item { flex: 1; display: flex; flex-direction: column; align-items: center; }
.entry-item--tap { opacity: .7; }
.entry-icon { width: 78rpx; height: 78rpx; display: flex; align-items: center; justify-content: center; border-radius: 50%; color: #fff; font-size: 30rpx; font-weight: 700; }
.entry-label { margin-top: 12rpx; font-size: 22rpx; color: #41506e; }

.tabs { white-space: nowrap; background: #fff; border-bottom: 1rpx solid var(--line); }
.tabs-inner { display: flex; padding: 16rpx 22rpx; }
.tabs button { display: flex; align-items: center; justify-content: center; min-width: 128rpx; height: 62rpx; margin-right: 10rpx; padding: 0 20rpx; border-radius: 31rpx; color: var(--muted); font-size: 23rpx; }
.tabs button.active { background: var(--brand-800); color: #fff; font-weight: 700; }
.order-list { padding: 22rpx 28rpx; }
.order-card { margin-bottom: 20rpx; padding: 24rpx; }
.order-head { display: flex; align-items: flex-start; justify-content: space-between; padding-bottom: 18rpx; border-bottom: 1rpx solid var(--line); }
.order-no, .order-time { display: block; }
.order-no { font-size: 25rpx; font-weight: 700; }
.order-time { margin-top: 6rpx; font-size: 19rpx; color: var(--muted); }
.status { padding: 8rpx 14rpx; border-radius: 12rpx; background: #eee9e4; color: var(--muted); font-size: 21rpx; }
.status.paid { background: #f7ead7; color: #98642f; }
.status.making { background: #f7ead7; color: #98642f; }
.status.ready { background: #e3eee4; color: var(--green); }
.status.completed { background: #eee9e4; color: var(--muted); }
.items { padding: 14rpx 0; }
.item-row { display: flex; align-items: center; padding: 12rpx 0; }
.item-name { flex: 1; margin-right: 14rpx; font-size: 24rpx; font-weight: 600; }
.item-options { margin-right: 14rpx; color: var(--muted); font-size: 19rpx; }
.item-qty { font-size: 22rpx; }
.order-foot { display: flex; align-items: center; padding-top: 16rpx; border-top: 1rpx solid var(--line); }
.pickup { display: flex; flex-direction: column; margin-right: 16rpx; }
.pickup-label { font-size: 18rpx; color: var(--muted); }
.pickup-code { margin-top: 4rpx; font-size: 40rpx; font-weight: 800; color: var(--brand-900); letter-spacing: 4rpx; }
.amount { flex: 1; text-align: right; font-size: 30rpx; font-weight: 800; color: var(--brand-900); }
.actions { margin-left: 16rpx; }
.actions .primary { min-width: 130rpx; height: 66rpx; display: flex; align-items: center; justify-content: center; border-radius: 33rpx; background: var(--brand); color: #fff; font-size: 24rpx; font-weight: 700; }
.empty { padding: 120rpx 30rpx; text-align: center; color: var(--muted); font-size: 24rpx; }
</style>
