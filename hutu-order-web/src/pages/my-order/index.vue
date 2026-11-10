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
    <view class="page-header">
      <button class="top-back" @click="goBack">‹</button>
      <text class="title">我的订单</text>
      <text class="subtitle">肥嘟嘟外卖平台 · 订单记录与进度</text>
    </view>
    <scroll-view scroll-x class="tabs" :show-scrollbar="false">
      <view class="tabs-inner">
        <button v-for="tab in tabs" :key="tab.id" :class="{ active: currentTab === tab.id }" @click="currentTab = tab.id">{{ tab.name }}</button>
      </view>
    </scroll-view>
    <view v-if="orders.length" class="order-list">
      <view v-for="order in orders" :key="order.id" class="order-card card" @click="openOrder(order.id)">
        <view class="order-head">
          <view>
            <text class="store-name">{{ order.storeName }}</text>
            <text class="order-time">{{ formatDateTime(order.createdAt) }}</text>
          </view>
          <text class="status" :class="order.status">{{ order.statusText }}</text>
        </view>
        <view class="preview-row">
          <view class="item-stack">
            <image v-for="(item, index) in order.items.slice(0, 3)" :key="item.key" class="thumb-img" :class="{ first: index === 0 }" :style="{ zIndex: 3 - index }" :src="item.image" mode="aspectFill" />
          </view>
          <view class="summary">
            <text class="summary-names">{{ order.items.map(item => item.name).join('、') }}</text>
            <text class="summary-meta">{{ stallCount(order) }} 个档口 · 共 {{ order.items.reduce((sum, item) => sum + item.quantity, 0) }} 件</text>
          </view>
          <text class="amount">{{ formatMoney(order.totalCents) }}</text>
        </view>
        <view class="order-foot">
          <text class="foot-code">取餐码 {{ order.pickupCode }}</text>
          <button class="reorder-action" @click.stop="reorder(order.id)">再来一单</button>
        </view>
      </view>
    </view>
    <EmptyState v-else title="暂无相关订单" description="订单提交后将在此展示" action-text="前往点单" @action="uni.switchTab({ url: '/pages/order/index' })" />
  </view>
</template>

<style scoped lang="scss">
.orders-page {
  padding-bottom: 50rpx;
  background: #F7F8FA;
}
.page-header {
  position: relative;
  padding: calc(64rpx + var(--status-bar-height, 0px) + env(safe-area-inset-top, 0px)) 30rpx 48rpx;
  background: linear-gradient(135deg, #FFD21E 0%, #FFC300 70%, #FFAE00 100%);
  color: #222426;
}
.top-back {
  position: absolute;
  left: 26rpx;
  top: calc(22rpx + var(--status-bar-height, 0px) + env(safe-area-inset-top, 0px));
  width: 66rpx;
  height: 66rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: rgba(0, 0, 0, .08);
  color: #222426;
  font-size: 48rpx;
  line-height: 1;
}
.title {
  margin-top: 14rpx;
  font-size: 44rpx;
  font-weight: 900;
  color: #222426;
  display: block;
}
.subtitle {
  margin-top: 8rpx;
  color: rgba(34, 36, 38, .75);
  font-size: 22rpx;
  display: block;
}

.tabs {
  z-index: 5;
  white-space: nowrap;
  background: #fff;
  border-bottom: 1rpx solid #F0F0F2;
}
.tabs-inner {
  display: flex;
  padding: 16rpx 22rpx;
}
.tabs button {
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 120rpx;
  height: 64rpx;
  margin-right: 12rpx;
  padding: 0 24rpx;
  border-radius: 32rpx;
  color: #8E929E;
  font-size: 24rpx;
  font-weight: 600;
}
.tabs button.active {
  background: #222426;
  color: #FFC300;
  font-weight: 800;
}

.order-list { padding: 22rpx 24rpx; }
.order-card {
  margin-bottom: 20rpx;
  padding: 24rpx;
}
.order-head, .preview-row, .order-foot { display: flex; align-items: center; }
.order-head {
  justify-content: space-between;
  padding-bottom: 18rpx;
  border-bottom: 1rpx solid #F0F0F2;
}
.store-name { font-size: 28rpx; font-weight: 800; color: #222426; display: block; }
.order-time { margin-top: 6rpx; font-size: 20rpx; color: #8E929E; display: block; }
.status {
  padding: 6rpx 14rpx;
  border-radius: 10rpx;
  background: #F3F4F7;
  color: #8E929E;
  font-size: 21rpx;
  font-weight: 700;
}
.status.making { background: #FFF9E6; color: #B37D00; }
.status.ready { background: #E6F8EE; color: #07C160; }
.status.completed { background: #F3F4F7; color: #8E929E; }

.preview-row { padding: 22rpx 0; }
.item-stack { display: flex; width: 116rpx; margin-right: 14rpx; }
.thumb-img {
  width: 64rpx;
  height: 64rpx;
  margin-left: -18rpx;
  border: 4rpx solid #fff;
  border-radius: 16rpx;
  background: #F4F5F8;
}
.thumb-img.first { margin-left: 0; }
.summary { flex: 1; min-width: 0; margin-right: 14rpx; }
.summary text { display: block; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.summary-names { font-size: 24rpx; font-weight: 700; color: #222426; }
.summary-meta { margin-top: 6rpx; color: #8E929E; font-size: 20rpx; }
.amount { font-size: 28rpx; font-weight: 900; color: #FF4B3E; }

.order-foot {
  justify-content: space-between;
  padding-top: 18rpx;
  border-top: 1rpx solid #F0F0F2;
}
.foot-code { font-size: 22rpx; color: #8E929E; font-weight: 600; }
.reorder-action {
  padding: 10rpx 24rpx;
  border: 2rpx solid #FFC300;
  border-radius: 28rpx;
  color: #222426;
  background: #FFFDF5;
  font-size: 22rpx;
  font-weight: 800;
}
</style>
