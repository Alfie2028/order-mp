<script setup>
import { computed, ref } from 'vue'
import { onLoad, onShow, onUnload } from '@dcloudio/uni-app'
import EmptyState from '@/component/EmptyState.vue'
import { useAppStore } from '@/store/app'
import { formatDateTime, formatMoney } from '@/utils/format'

const store = useAppStore()
const orderId = ref('')
const order = computed(() => store.findOrder(orderId.value))
const steps = [{ id: 'paid', name: '已支付' }, { id: 'making', name: '制作中' }, { id: 'ready', name: '待取餐' }, { id: 'completed', name: '已完成' }]
const activeIndex = computed(() => Math.max(0, steps.findIndex((step) => step.id === order.value?.status)))
const statusTitle = computed(() => ({ paid: '已支付，等待商家接单', making: '档口正在精心制作中', ready: '餐品已备齐，请取餐', completed: '订单已完成' }[order.value?.status] || '订单处理中'))
const statusCopy = computed(() => ({ paid: '商家接单后开始制作', making: `预计 ${store.currentStore.value?.waitMinutes || 15} 分钟出餐`, ready: '取餐时请向档口出示取餐码', completed: '感谢您选择美团校园点餐' }[order.value?.status] || ''))

// ---- 评价 ----
const rating = ref(0)
const reviewText = ref('')
const myReview = computed(() => store.state.myReviews.find((r) => r.order_id === (order.value && order.value.dbId)))
const hasReview = computed(() => !!myReview.value)

let timer = null
onLoad((query) => { orderId.value = query.id || store.state.orders[0]?.id || '' })
onShow(() => {
  if (order.value && !['completed', 'pending'].includes(order.value.status)) {
    if (timer) clearInterval(timer)
    timer = setInterval(() => store.refreshOrder(order.value.id).catch(() => {}), 3000)
  }
  if (store.state.user) store.loadMyReviews().catch(() => {})
})
onUnload(() => { if (timer) { clearInterval(timer); timer = null } })

function refresh() {
  if (!order.value || order.value.status === 'completed') return
  store.refreshOrder(order.value.id).then(() => uni.showToast({ title: order.value.statusText, icon: 'none' })).catch(() => {})
}
function confirmPickup() {
  if (!order.value) return
  store.completeOrder(order.value.id).then(() => uni.showToast({ title: '取餐完成', icon: 'success' })).catch(() => {})
}
function reorder() {
  store.reorder(order.value.id)
  uni.switchTab({ url: '/pages/order/index' })
}
function submitReview() {
  if (!order.value) return
  if (!rating.value) { uni.showToast({ title: '请先选择星级', icon: 'none' }); return }
  store.submitReview(order.value.dbId, rating.value, reviewText.value.trim()).then(() => {
    uni.showToast({ title: '评价成功', icon: 'success' })
  }).catch(() => {})
}
function goBack() {
  if (getCurrentPages().length > 1) uni.navigateBack({ fail: () => { uni.switchTab({ url: '/pages/home/index' }) } })
  else uni.switchTab({ url: '/pages/home/index' })
}
</script>

<template>
  <view class="page-shell settled-page">
    <template v-if="order">
      <view class="status-hero" :class="order.status">
        <button class="top-back" @click="goBack">‹</button>
        <text class="status-title">{{ statusTitle }}</text>
        <text class="status-copy">{{ statusCopy }}</text>
        <view class="pickup-code">
          <text class="pickup-code-label">取餐号</text>
          <text class="pickup-code-value">{{ order.pickupCode }}</text>
        </view>
      </view>

      <view class="section progress-section">
        <view class="progress-card card">
          <view class="progress-line">
            <view class="progress-fill" :style="{ width: `${activeIndex / (steps.length - 1) * 100}%` }" />
          </view>
          <view class="steps">
            <view v-for="(step, index) in steps" :key="step.id" class="step" :class="{ active: index <= activeIndex }">
              <text class="step-dot">{{ index < activeIndex ? '✓' : index + 1 }}</text>
              <text class="step-name">{{ step.name }}</text>
            </view>
          </view>
          <button v-if="order.status !== 'completed' && order.status !== 'pending'" class="status-advance" @click="order.status === 'ready' ? confirmPickup() : refresh()">
            {{ order.status === 'ready' ? '我已取餐' : '刷新进度' }}
          </button>
        </view>
      </view>

      <view class="section">
        <view class="section-heading">
          <text class="section-title">订单详情</text>
          <text class="section-link">{{ formatDateTime(order.createdAt) }}</text>
        </view>
        <view class="detail-card card">
          <view class="store-row">
            <view>
              <text class="store-name">{{ order.storeName }}</text>
              <text class="order-no">订单号 {{ order.id }}</text>
            </view>
            <text class="mode">{{ order.mode === 'pickup' ? '到店自取' : '档口堂食' }}</text>
          </view>
          <view v-for="item in order.items" :key="item.key" class="order-item">
            <image class="item-image" :src="item.image" mode="aspectFill" />
            <view class="item-main">
              <text class="item-name">{{ item.name }} × {{ item.quantity }}</text>
              <text class="item-stall">{{ item.stallName }}</text>
              <text class="item-options">{{ item.selectedOptions.map(option => option.name).join(' · ') || '标准制作' }}</text>
            </view>
            <text class="price">{{ formatMoney(item.unitPriceCents * item.quantity) }}</text>
          </view>
          <view class="bill">
            <view><text>餐品总额</text><text>{{ formatMoney(order.subtotalCents) }}</text></view>
            <view><text>立减优惠</text><text class="discount">{{ order.discountCents ? `-${formatMoney(order.discountCents)}` : formatMoney(0) }}</text></view>
            <view class="bill-total"><text>实付款</text><text class="bill-total-price">{{ formatMoney(order.totalCents) }}</text></view>
          </view>
        </view>
      </view>

      <view v-if="order.status === 'completed'" class="section review-section">
        <view class="review-card card">
          <template v-if="!hasReview">
            <text class="review-title">评价本次订单</text>
            <text class="review-sub">点亮星星，分享你的用餐体验</text>
            <view class="stars">
              <text v-for="n in 5" :key="n" class="star" :class="{ on: n <= rating }" @click="rating = n">★</text>
            </view>
            <textarea v-model="reviewText" class="review-input" placeholder="说说这次用餐体验（选填）" maxlength="200" />
            <button class="submit-review" :class="{ disabled: !rating }" @click="submitReview">提交评价</button>
          </template>
          <template v-else>
            <text class="review-title">我的评价</text>
            <view class="stars">
              <text v-for="n in 5" :key="n" class="star" :class="{ on: n <= myReview.rating }">★</text>
            </view>
            <text class="review-content">{{ myReview.content || '未填写文字评价' }}</text>
          </template>
        </view>
      </view>

      <view class="section actions">
        <button class="primary-button reorder-btn" @click="reorder">再来一单</button>
        <button class="ghost-button" @click="uni.switchTab({ url: '/pages/home/index' })">返回首页</button>
      </view>
    </template>
    <EmptyState v-else title="未查询到订单" description="请返回订单列表重新选择" action-text="前往点单" @action="uni.switchTab({ url: '/pages/order/index' })" />
  </view>
</template>

<style scoped lang="scss">
.settled-page {
  padding-bottom: 60rpx;
  background: #F7F8FA;
}
.status-hero {
  position: relative;
  padding: calc(72rpx + env(safe-area-inset-top)) 30rpx 90rpx;
  text-align: center;
  color: #222426;
  background: linear-gradient(135deg, #FFD21E 0%, #FFC300 70%, #FFAE00 100%);
}
.status-hero.ready {
  background: linear-gradient(135deg, #07C160 0%, #059669 100%);
  color: #fff;
}
.status-hero.completed {
  background: linear-gradient(135deg, #333333 0%, #222426 100%);
  color: #fff;
}
.top-back {
  position: absolute;
  left: 26rpx;
  top: calc(22rpx + env(safe-area-inset-top));
  width: 66rpx;
  height: 66rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: rgba(0, 0, 0, .08);
  color: inherit;
  font-size: 48rpx;
  line-height: 1;
}

.status-title {
  margin-top: 14rpx;
  font-size: 42rpx;
  font-weight: 900;
  display: block;
}
.status-copy {
  margin-top: 8rpx;
  font-size: 22rpx;
  opacity: .85;
  display: block;
}

.pickup-code {
  width: 280rpx;
  margin: 32rpx auto 0;
  padding: 16rpx 20rpx;
  border-radius: 20rpx;
  background: rgba(255, 255, 255, .9);
  color: #222426;
  box-shadow: 0 4rpx 14rpx rgba(0, 0, 0, .1);
}
.pickup-code-label { font-size: 20rpx; color: #8E929E; font-weight: 700; display: block; }
.pickup-code-value {
  margin-top: 4rpx;
  font-size: 64rpx;
  font-weight: 900;
  letter-spacing: 8rpx;
  color: #222426;
  display: block;
}

.progress-section { margin-top: -44rpx; }
.progress-card { padding: 30rpx 28rpx; }
.progress-line {
  position: relative;
  height: 6rpx;
  margin: 24rpx 60rpx -27rpx;
  background: #EBECEF;
}
.progress-fill {
  height: 100%;
  background: #FFC300;
  transition: width .3s;
}
.steps {
  position: relative;
  display: flex;
  justify-content: space-between;
}
.step {
  display: flex;
  flex-direction: column;
  align-items: center;
  color: #8E929E;
  font-size: 21rpx;
}
.step-dot {
  width: 48rpx;
  height: 48rpx;
  margin-bottom: 10rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: #F3F4F7;
  border: 4rpx solid #fff;
  font-weight: 800;
  color: #8E929E;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, .08);
}
.step.active { color: #222426; font-weight: 800; }
.step.active .step-dot { background: #FFC300; color: #222426; }
.status-advance {
  margin: 28rpx auto 0;
  color: #8C5E00;
  font-size: 23rpx;
  font-weight: 700;
  text-decoration: underline;
}

.detail-card { padding: 4rpx 24rpx; }
.store-row {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  padding: 24rpx 0;
  border-bottom: 1rpx solid #F0F0F2;
}
.store-name { font-size: 28rpx; font-weight: 800; color: #222426; display: block; }
.order-no { margin-top: 6rpx; color: #8E929E; font-size: 20rpx; display: block; }
.mode {
  padding: 6rpx 14rpx;
  border-radius: 12rpx;
  background: #FFF7DB;
  font-size: 20rpx;
  font-weight: 800;
  color: #8C5E00;
}

.order-item {
  display: flex;
  align-items: center;
  padding: 20rpx 0;
  border-bottom: 1rpx solid #F0F0F2;
}
.item-image {
  width: 72rpx;
  height: 72rpx;
  margin-right: 16rpx;
  border-radius: 14rpx;
  background: #F4F5F8;
}
.item-main { flex: 1; }
.item-name { font-weight: 800; font-size: 24rpx; color: #222426; display: block; }
.item-stall { margin-top: 4rpx; color: #B37D00; font-size: 19rpx; display: block; }
.item-options { margin-top: 4rpx; color: #8E929E; font-size: 19rpx; display: block; }

.bill { padding: 18rpx 0; }
.bill > view { display: flex; justify-content: space-between; padding: 10rpx 0; color: #8E929E; font-size: 23rpx; }
.discount { color: #FF4B3E; }
.bill-total {
  margin-top: 10rpx;
  padding-top: 18rpx;
  border-top: 1rpx solid #F0F0F2;
  font-size: 28rpx;
  font-weight: 800;
  color: #222426;
}
.bill-total-price { color: #FF4B3E; font-size: 34rpx; font-weight: 900; }

.actions { display: flex; margin-top: 30rpx; }
.reorder-btn { flex: 1; margin-right: 16rpx; }
.ghost-button {
  display: flex;
  flex: 1;
  align-items: center;
  justify-content: center;
  height: 88rpx;
  border: 2rpx solid #FFC300;
  border-radius: 44rpx;
  background: #FFFDF5;
  color: #8C5E00;
  font-size: 28rpx;
  font-weight: 800;
}

.review-section { margin-bottom: 10rpx; }
.review-card { padding: 28rpx; }
.review-title { display: block; font-size: 28rpx; font-weight: 800; color: #222426; }
.review-sub { display: block; margin-top: 6rpx; color: #8E929E; font-size: 21rpx; }
.stars { display: flex; margin-top: 18rpx; }
.star {
  font-size: 52rpx;
  color: #E2DCD4;
  line-height: 1;
  margin-right: 12rpx;
}
.star.on { color: #FFAA00; }
.review-input {
  width: 100%;
  height: 150rpx;
  margin-top: 20rpx;
  padding: 20rpx;
  border-radius: 16rpx;
  background: #F7F8FA;
  font-size: 24rpx;
  box-sizing: border-box;
}
.submit-review {
  margin-top: 20rpx;
  height: 80rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 40rpx;
  background: #FFC300;
  color: #222426;
  font-size: 26rpx;
  font-weight: 800;
  box-shadow: 0 4rpx 14rpx rgba(255, 195, 0, .4);
}
.submit-review.disabled { background: #E5E6EB; color: #8E929E; box-shadow: none; }
.review-content { margin-top: 14rpx; font-size: 24rpx; color: #555; line-height: 1.5; }
</style>
