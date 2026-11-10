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

const entries = [
  { key: 'products', short: '餐品管理', icon: '餐', color: '#FFC300', iconColor: '#222426', url: '/pages/merchant/products' },
  { key: 'stalls', short: '档口信息', icon: '档', color: '#FFA000', iconColor: '#222426', url: '/pages/merchant/stalls' },
  { key: 'coupons', short: '神券配置', icon: '券', color: '#FF7700', iconColor: '#fff', url: '/pages/merchant/coupons' },
  { key: 'reviews', short: '顾客评价', icon: '评', color: '#222426', iconColor: '#FFC300', url: '/pages/merchant/reviews' },
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
        <view class="header-brand-line">
          <image class="header-logo" src="/static/image/kangaroo.png" mode="aspectFit" />
          <text class="title">肥嘟嘟商家版</text>
        </view>
        <button class="logout" @click="logout">退出登录</button>
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
        <text class="open-text">{{ isOpen ? '档口正常营业中' : '档口已打烊' }}</text>
        <text class="open-action">{{ isOpen ? '点击打烊' : '点击开张' }}</text>
      </view>

      <text class="poll-hint">订单每 3 秒自动轮询，出餐请点击出餐完成</text>
    </view>

    <view class="entry-row">
      <view v-for="entry in entries" :key="entry.key" class="entry-item" hover-class="entry-item--tap" @click="goEntry(entry.url)">
        <view class="entry-icon" :style="{ background: entry.color, color: entry.iconColor }">{{ entry.icon }}</view>
        <text class="entry-label">{{ entry.short }}</text>
      </view>
    </view>

    <scroll-view scroll-x class="tabs" :show-scrollbar="false">
      <view class="tabs-inner">
        <button v-for="tab in tabs" :key="tab.id" :class="{ active: currentTab === tab.id }" @click="currentTab = tab.id">{{ tab.name }}</button>
      </view>
    </scroll-view>

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
.merchant-page { min-height: 100vh; padding-bottom: 60rpx; background: #F7F8FA; }
.merchant-header {
  padding: calc(58rpx + var(--status-bar-height, 0px) + env(safe-area-inset-top, 0px)) 30rpx 36rpx;
  background: linear-gradient(135deg, #FFD21E 0%, #FFC300 70%, #FFAE00 100%);
  color: #222426;
}
.header-top { display: flex; align-items: center; justify-content: space-between; }
.header-brand-line { display: flex; align-items: center; }
.header-logo { width: 52rpx; height: 52rpx; margin-right: 12rpx; }
.title { font-size: 44rpx; font-weight: 900; color: #222426; }
.logout {
  flex: 0 0 auto;
  width: auto;
  min-width: 144rpx;
  height: 56rpx;
  padding: 0 22rpx;
  margin: 0;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: 1rpx solid rgba(0, 0, 0, .12);
  border-radius: 999rpx;
  background: rgba(255, 255, 255, .4);
  color: #222426;
  font-size: 24rpx;
  font-weight: 700;
  line-height: 1;
  white-space: nowrap;
}
.logout::after { border: none; }

.stats-row { display: flex; margin-top: 28rpx; }
.stat-card {
  flex: 1;
  display: flex;
  flex-direction: column;
  margin-right: 16rpx;
  padding: 22rpx 20rpx;
  border-radius: 20rpx;
  background: rgba(255, 255, 255, .9);
  color: #222426;
  box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, .05);
}
.stat-card.last { margin-right: 0; }
.stat-number { margin-bottom: 6rpx; font-size: 38rpx; font-weight: 900; line-height: 1; }
.stat-label { font-size: 20rpx; color: #666; font-weight: 600; }

.open-toggle {
  display: flex;
  align-items: center;
  margin-top: 20rpx;
  padding: 18rpx 24rpx;
  border-radius: 20rpx;
  background: #222426;
  color: #fff;
}
.open-toggle.closed { background: #FF4B3E; }
.dot { width: 16rpx; height: 16rpx; margin-right: 12rpx; border-radius: 50%; background: #07C160; }
.open-toggle.closed .dot { background: #fff; }
.open-text { font-size: 25rpx; font-weight: 800; }
.open-action { margin-left: auto; font-size: 21rpx; color: #FFC300; font-weight: 700; }
.open-toggle.closed .open-action { color: #fff; }

.poll-hint { display: block; margin-top: 14rpx; font-size: 19rpx; color: rgba(34, 36, 38, .75); font-weight: 600; }

.entry-row {
  display: flex;
  margin: 22rpx 24rpx 10rpx;
  padding: 24rpx 8rpx 20rpx;
  background: #fff;
  border-radius: 22rpx;
  box-shadow: 0 4rpx 14rpx rgba(0, 0, 0, .04);
}
.entry-item { flex: 1; display: flex; flex-direction: column; align-items: center; }
.entry-item--tap { opacity: .7; }
.entry-icon {
  width: 80rpx;
  height: 80rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  font-size: 30rpx;
  font-weight: 900;
  box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, .08);
}
.entry-label { margin-top: 12rpx; font-size: 22rpx; font-weight: 700; color: #222426; }

.tabs { white-space: nowrap; background: #fff; border-bottom: 1rpx solid #F0F0F2; }
.tabs-inner { display: flex; padding: 16rpx 22rpx; }
.tabs button {
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 128rpx;
  height: 64rpx;
  margin-right: 12rpx;
  padding: 0 24rpx;
  border-radius: 32rpx;
  color: #8E929E;
  font-size: 24rpx;
  font-weight: 600;
}
.tabs button.active { background: #222426; color: #FFC300; font-weight: 800; }

.order-list { padding: 22rpx 24rpx; }
.order-card { margin-bottom: 20rpx; padding: 24rpx; }
.order-head { display: flex; align-items: flex-start; justify-content: space-between; padding-bottom: 18rpx; border-bottom: 1rpx solid #F0F0F2; }
.order-no { font-size: 26rpx; font-weight: 800; color: #222426; display: block; }
.order-time { margin-top: 6rpx; font-size: 20rpx; color: #8E929E; display: block; }
.status { padding: 6rpx 14rpx; border-radius: 10rpx; background: #F3F4F7; color: #8E929E; font-size: 21rpx; font-weight: 700; }
.status.paid { background: #FFF9E6; color: #B37D00; }
.status.making { background: #FFF9E6; color: #B37D00; }
.status.ready { background: #E6F8EE; color: #07C160; }
.status.completed { background: #F3F4F7; color: #8E929E; }

.items { padding: 14rpx 0; }
.item-row { display: flex; align-items: center; padding: 12rpx 0; }
.item-name { flex: 1; margin-right: 14rpx; font-size: 25rpx; font-weight: 700; color: #222426; }
.item-options { margin-right: 14rpx; color: #8E929E; font-size: 20rpx; }
.item-qty { font-size: 23rpx; font-weight: 700; color: #222426; }

.order-foot { display: flex; align-items: center; padding-top: 18rpx; border-top: 1rpx solid #F0F0F2; }
.pickup { display: flex; flex-direction: column; margin-right: 16rpx; }
.pickup-label { font-size: 18rpx; color: #8E929E; }
.pickup-code { margin-top: 4rpx; font-size: 42rpx; font-weight: 900; color: #222426; letter-spacing: 4rpx; }
.amount { flex: 1; text-align: right; font-size: 32rpx; font-weight: 900; color: #FF4B3E; }
.actions { margin-left: 18rpx; }
.actions .primary {
  min-width: 140rpx;
  height: 68rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 34rpx;
  background: #FFC300;
  color: #222426;
  font-size: 25rpx;
  font-weight: 800;
  box-shadow: 0 4rpx 12rpx rgba(255, 195, 0, .35);
}
.empty { padding: 120rpx 30rpx; text-align: center; color: #8E929E; font-size: 24rpx; }
</style>
