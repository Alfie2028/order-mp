<script setup>
import { computed, ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import EmptyState from '@/component/EmptyState.vue'
import { useAppStore } from '@/store/app'
import { formatDateTime, formatMoney } from '@/utils/format'

const store = useAppStore()
const currentTab = ref('all')
const tabs = [{ id: 'all', name: '全部' }, { id: 'making', name: '制作中' }, { id: 'ready', name: '待取餐' }, { id: 'completed', name: '已完成' }]
const orders = computed(() => currentTab.value === 'all' ? store.state.orders : store.state.orders.filter((order) => order.status === currentTab.value))

onShow(() => { if (store.state.user) store.loadOrders().catch(() => {}) })

function openOrder(id) { uni.navigateTo({ url: `/pages/settled/index?id=${id}` }) }
function reorder(id) { store.reorder(id); uni.switchTab({ url: '/pages/order/index' }) }
function stallCount(order) { return new Set(order.items.map((item) => item.stallName).filter(Boolean)).size }
function goBack() {
  if (getCurrentPages().length > 1) uni.navigateBack({ fail: () => { uni.switchTab({ url: '/pages/home/index' }) } })
  else uni.switchTab({ url: '/pages/home/index' })
}
</script>

<template>
  <view class="page-shell orders-page">
    <view class="page-header"><button class="top-back" @click="goBack">‹</button><text class="title">我的订单</text><text class="subtitle">查看订单进度与历史记录</text></view>
    <scroll-view scroll-x class="tabs"><view class="tabs-inner"><button v-for="tab in tabs" :key="tab.id" :class="{ active: currentTab === tab.id }" @click="currentTab = tab.id">{{ tab.name }}</button></view></scroll-view>
    <view v-if="orders.length" class="order-list">
      <view v-for="order in orders" :key="order.id" class="order-card card" @click="openOrder(order.id)">
        <view class="order-head"><view><text class="store-name">{{ order.storeName }}</text><text class="order-time">{{ formatDateTime(order.createdAt) }}</text></view><text class="status" :class="order.status">{{ order.statusText }}</text></view>
        <view class="preview-row">
          <view class="emoji-stack"><image v-for="(item,index) in order.items.slice(0,3)" :key="item.key" class="emoji" :class="{ first: index === 0 }" :style="{ zIndex: 3-index }" :src="item.image" mode="aspectFill" /></view>
          <view class="summary"><text class="summary-names">{{ order.items.map(item => item.name).join('、') }}</text><text class="summary-meta">{{ stallCount(order) }} 个档口 · 共 {{ order.items.reduce((sum,item) => sum + item.quantity, 0) }} 件</text></view>
          <text class="amount">{{ formatMoney(order.totalCents) }}</text>
        </view>
        <view class="order-foot"><text>取餐码 {{ order.pickupCode }}</text><button @click.stop="reorder(order.id)">再来一单</button></view>
      </view>
    </view>
    <EmptyState v-else title="暂无相关订单" description="订单提交后将在此展示" action-text="前往点单" @action="uni.switchTab({ url: '/pages/order/index' })" />
  </view>
</template>

<style scoped lang="scss">
.orders-page{padding-bottom:50rpx}.page-header{position:relative;padding:calc(92rpx + env(safe-area-inset-top)) 30rpx 44rpx;background:linear-gradient(150deg,#35231b,#78523e);color:#fff}.top-back{position:absolute;left:26rpx;top:calc(22rpx + env(safe-area-inset-top));width:66rpx;height:66rpx;display:flex;align-items:center;justify-content:center;border-radius:50%;background:rgba(255,255,255,.12);color:white;font-size:48rpx;line-height:1}.eyebrow,.title,.subtitle{display:block}.eyebrow{font-size:18rpx;letter-spacing:5rpx;color:var(--caramel-300)}.title{margin-top:12rpx;font-size:47rpx;font-weight:800}.subtitle{margin-top:9rpx;color:rgba(255,255,255,.62);font-size:23rpx}.tabs{z-index:5;white-space:nowrap;background:rgba(251,248,243,.96);border-bottom:1rpx solid var(--line)}.tabs-inner{display:flex;padding:16rpx 22rpx}.tabs button{display:flex;align-items:center;justify-content:center;min-width:120rpx;height:60rpx;margin-right:10rpx;padding:0 20rpx;border-radius:30rpx;color:var(--muted);font-size:23rpx}.tabs button.active{background:var(--brand-800);color:#fff;font-weight:700}.order-list{padding:22rpx 28rpx}.order-card{margin-bottom:20rpx;padding:24rpx}.order-head,.preview-row,.order-foot{display:flex;align-items:center}.order-head{justify-content:space-between;padding-bottom:20rpx;border-bottom:1rpx solid var(--line)}.store-name,.order-time{display:block}.store-name{font-size:27rpx;font-weight:700}.order-time{margin-top:6rpx;font-size:19rpx;color:var(--muted)}.status{padding:8rpx 14rpx;border-radius:12rpx;background:#eee9e4;color:var(--muted);font-size:21rpx}.status.making{background:#f7ead7;color:#98642f}.status.ready{background:#e3eee4;color:var(--green)}.preview-row{padding:24rpx 0}.emoji-stack{display:flex;width:116rpx;margin-right:14rpx}.emoji{width:60rpx;height:60rpx;margin-left:-18rpx;border:4rpx solid #fff;border-radius:18rpx;background:var(--oat-100)}.emoji.first{margin-left:0}.summary{flex:1;min-width:0;margin-right:14rpx}.summary text{display:block;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.summary-names{font-size:23rpx}.summary-meta{margin-top:7rpx;color:var(--muted);font-size:19rpx}.amount{font-size:27rpx;font-weight:800;color:var(--brand-900)}.order-foot{justify-content:space-between;padding-top:18rpx;border-top:1rpx solid var(--line);font-size:21rpx;color:var(--muted)}.order-foot button{padding:14rpx 22rpx;border:1rpx solid var(--brand-700);border-radius:28rpx;color:var(--brand-700);font-size:21rpx;font-weight:600}
.page-header{background:linear-gradient(145deg,#0637c9,#071a62)}
</style>
