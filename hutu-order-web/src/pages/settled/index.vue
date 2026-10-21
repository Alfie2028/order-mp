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
const statusTitle = computed(() => ({ paid: '已支付，等待商家接单', making: '订单正在制作', ready: '订单已可取餐', completed: '订单已完成' }[order.value?.status] || '订单处理中'))
const statusCopy = computed(() => ({ paid: '商家接单后开始制作', making: `预计 ${store.currentStore.value.waitMinutes} 分钟取餐`, ready: '取餐时请向档口人员出示取餐码', completed: '感谢您的使用' }[order.value?.status] || ''))

// ---- 评价 ----
const rating = ref(0)
const reviewText = ref('')
const myReview = computed(() => store.state.myReviews.find((r) => r.order_id === (order.value && order.value.dbId)))
const hasReview = computed(() => !!myReview.value)

let timer = null
onLoad((query) => { orderId.value = query.id || store.state.orders[0]?.id || '' })
onShow(() => {
  if (order.value && !['completed', 'pending'].includes(order.value.status)) { if (timer) clearInterval(timer); timer = setInterval(() => store.refreshOrder(order.value.id).catch(() => {}), 3000) }
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
        <view class="pickup-code"><text class="pickup-code-label">取餐码</text><text class="pickup-code-value">{{ order.pickupCode }}</text></view>
      </view>

      <view class="section progress-section">
        <view class="progress-card card">
          <view class="progress-line"><view class="progress-fill" :style="{ width: `${activeIndex / (steps.length - 1) * 100}%` }" /></view>
          <view class="steps"><view v-for="(step,index) in steps" :key="step.id" class="step" :class="{ active: index <= activeIndex }"><text class="step-dot">{{ index < activeIndex ? '✓' : index + 1 }}</text><text>{{ step.name }}</text></view></view>
          <button v-if="order.status !== 'completed' && order.status !== 'pending'" class="status-advance" @click="order.status === 'ready' ? confirmPickup() : refresh()">{{ order.status === 'ready' ? '确认取餐' : '刷新订单状态' }}</button>
        </view>
      </view>

      <view class="section">
        <view class="section-heading"><text class="section-title">订单详情</text><text class="section-link">{{ formatDateTime(order.createdAt) }}</text></view>
        <view class="detail-card card">
          <view class="store-row"><view><text class="store-name">{{ order.storeName }}</text><text class="order-no">订单号 {{ order.id }}</text></view><text class="mode">{{ order.mode === 'pickup' ? '到店自取' : '档口堂食' }}</text></view>
          <view v-for="item in order.items" :key="item.key" class="order-item"><image class="item-image" :src="item.image" mode="aspectFill" /><view class="item-main"><text class="item-name">{{ item.name }} × {{ item.quantity }}</text><text class="item-stall">{{ item.stallName }}</text><text class="item-options">{{ item.selectedOptions.map(option => option.name).join(' · ') || '标准制作' }}</text></view><text>{{ formatMoney(item.unitPriceCents * item.quantity) }}</text></view>
          <view class="bill"><view><text>餐品金额</text><text>{{ formatMoney(order.subtotalCents) }}</text></view><view><text>优惠</text><text>{{ order.discountCents ? `-${formatMoney(order.discountCents)}` : formatMoney(0) }}</text></view><view class="bill-total"><text>实付</text><text>{{ formatMoney(order.totalCents) }}</text></view></view>
        </view>
      </view>

      <view v-if="order.status === 'completed'" class="section review-section">
        <view class="review-card card">
          <template v-if="!hasReview">
            <text class="review-title">评价本次订单</text>
            <text class="review-sub">点亮星星，分享你的用餐体验</text>
            <view class="stars"><text v-for="n in 5" :key="n" class="star" :class="{ on: n <= rating }" @click="rating = n">{{ n <= rating ? '★' : '☆' }}</text></view>
            <textarea v-model="reviewText" class="review-input" placeholder="说说这次用餐体验（选填）" maxlength="200" />
            <button class="submit-review" :class="{ disabled: !rating }" @click="submitReview">提交评价</button>
          </template>
          <template v-else>
            <text class="review-title">我的评价</text>
            <view class="stars"><text v-for="n in 5" :key="n" class="star" :class="{ on: n <= myReview.rating }">{{ n <= myReview.rating ? '★' : '☆' }}</text></view>
            <text class="review-content">{{ myReview.content || '未填写文字评价' }}</text>
          </template>
        </view>
      </view>

      <view class="section actions"><button class="primary-button" @click="reorder">再来一单</button><button class="ghost-button" @click="uni.switchTab({ url: '/pages/home/index' })">返回首页</button></view>
    </template>
    <EmptyState v-else title="未查询到订单" description="请返回订单列表重新选择" action-text="前往点单" @action="uni.switchTab({ url: '/pages/order/index' })" />
  </view>
</template>

<style scoped lang="scss">
.settled-page{padding-bottom:60rpx}.status-hero{position:relative;padding:calc(105rpx + env(safe-area-inset-top)) 30rpx 100rpx;text-align:center;color:white;background:radial-gradient(circle at 50% 8%,#9b6d4f,#3c281f 62%)}.top-back{position:absolute;left:26rpx;top:calc(22rpx + env(safe-area-inset-top));width:66rpx;height:66rpx;display:flex;align-items:center;justify-content:center;border-radius:50%;background:rgba(255,255,255,.12);color:white;font-size:48rpx;line-height:1}.status-hero.ready{background:radial-gradient(circle at 50% 8%,#789379,#304535 62%)}.status-hero.completed{background:radial-gradient(circle at 50% 8%,#827c77,#393532 62%)}.status-kicker,.status-title,.status-copy{display:block}.status-kicker{font-size:18rpx;letter-spacing:5rpx;color:#dfbd91}.status-title{margin-top:18rpx;font-size:46rpx;font-weight:800}.status-copy{margin-top:12rpx;font-size:24rpx;color:rgba(255,255,255,.7)}.pickup-code{width:260rpx;margin:38rpx auto 0;padding:20rpx;border:1rpx solid rgba(255,255,255,.25);border-radius:20rpx;background:rgba(255,255,255,.08)}.pickup-code text{display:block}.pickup-code-label{font-size:20rpx;color:rgba(255,255,255,.65)}.pickup-code-value{margin-top:5rpx;font-size:64rpx;font-weight:800;letter-spacing:9rpx}.progress-section{margin-top:-48rpx}.progress-card{padding:30rpx 28rpx}.progress-line{position:relative;height:5rpx;margin:24rpx 60rpx -27rpx;background:var(--line)}.progress-fill{height:100%;background:var(--green);transition:width .3s}.steps{position:relative;display:flex;justify-content:space-between}.step{display:flex;flex-direction:column;align-items:center;color:var(--muted);font-size:20rpx}.step-dot{width:48rpx;height:48rpx;margin-bottom:10rpx;display:flex;align-items:center;justify-content:center;border-radius:50%;background:#eee8e0;border:5rpx solid white;font-weight:700}.step.active{color:var(--brand-800);font-weight:700}.step.active .step-dot{background:var(--green);color:white}.status-advance{margin:28rpx auto 0;color:var(--brand-700);font-size:22rpx;text-decoration:underline}.detail-card{padding:0 24rpx}.store-row{display:flex;align-items:flex-start;justify-content:space-between;padding:25rpx 0;border-bottom:1rpx solid var(--line)}.store-name,.order-no{display:block}.store-name{font-size:27rpx;font-weight:700}.order-no{margin-top:7rpx;color:var(--muted);font-size:19rpx}.mode{padding:8rpx 13rpx;border-radius:10rpx;background:var(--oat-100);font-size:20rpx;color:var(--brand-700)}.order-item{display:flex;align-items:center;padding:21rpx 0;border-bottom:1rpx solid var(--line);font-size:23rpx}.item-image{width:58rpx;height:58rpx;margin-right:14rpx;border-radius:14rpx}.item-main{flex:1}.item-main text{display:block}.item-name{font-weight:600}.item-options{margin-top:5rpx;color:var(--muted);font-size:19rpx}.bill{padding:16rpx 0}.bill>view{display:flex;justify-content:space-between;padding:9rpx 0;color:var(--muted);font-size:22rpx}.bill .bill-total{margin-top:8rpx;padding-top:18rpx;border-top:1rpx solid var(--line);font-size:28rpx;font-weight:800;color:var(--brand-900)}.actions{display:flex}.actions .primary-button{flex:1;margin-right:14rpx}.ghost-button{display:flex;flex:1;align-items:center;justify-content:center;border:1rpx solid var(--brand-700);border-radius:46rpx;color:var(--brand-700);font-size:27rpx}.review-section{margin-bottom:6rpx}.review-card{padding:28rpx}.review-title{display:block;font-size:28rpx;font-weight:700}.review-sub{display:block;margin-top:8rpx;color:var(--muted);font-size:21rpx}.stars{display:flex;margin-top:20rpx}.star{font-size:58rpx;color:#e2dcd4;line-height:1;margin-right:12rpx}.star.on{color:#f7b731}.review-input{width:100%;height:150rpx;margin-top:22rpx;padding:20rpx;border-radius:14rpx;background:var(--oat-50);font-size:24rpx;box-sizing:border-box}.submit-review{margin-top:20rpx;height:80rpx;display:flex;align-items:center;justify-content:center;border-radius:40rpx;background:var(--brand);color:#fff;font-size:26rpx;font-weight:700}.submit-review.disabled{background:#c9cdd6}.review-content{margin-top:16rpx;font-size:24rpx;color:var(--ink);line-height:1.6}
.status-hero{background:radial-gradient(circle at 50% 8%,#2458c8,#071a62 64%)}.status-hero.ready{background:radial-gradient(circle at 50% 8%,#2458c8,#071a62 64%)}
.item-main .item-stall{margin-top:5rpx;color:var(--brand);font-size:18rpx}
</style>
