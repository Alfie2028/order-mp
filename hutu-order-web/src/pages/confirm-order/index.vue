<script setup>
import { computed, ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { useAppStore } from '@/store/app'
import { formatMoney } from '@/utils/format'

const store = useAppStore()
const pickupTime = ref('尽快取餐')
const remark = ref('')
const couponId = ref('')
const payment = ref('wechat')
const paying = ref(false)

onShow(() => { if (!store.state.cart.length) uni.showToast({ title: '购物车暂无餐品', icon: 'none' }) })

const availableCoupons = computed(() => store.state.coupons.filter((coupon) => store.state.couponIds.includes(coupon.id) && store.cartSubtotal.value >= coupon.thresholdCents))
const chosenCoupon = computed(() => store.state.coupons.find((coupon) => coupon.id === couponId.value))
const discount = computed(() => chosenCoupon.value?.discountCents || 0)
const total = computed(() => Math.max(0, store.cartSubtotal.value - discount.value))

async function submit() {
  if (!store.state.cart.length || paying.value) return
  if (!store.state.user) { uni.navigateTo({ url: '/pages/login/index' }); return }
  paying.value = true
  uni.showLoading({ title: '提交订单' })
  try {
    const order = await store.createOrder({ couponId: couponId.value, remark: remark.value.trim(), pickupTime: pickupTime.value })
    if (!order) { uni.hideLoading(); paying.value = false; return }
    uni.showLoading({ title: '支付中' })
    await store.payOrder(order.id)
    uni.hideLoading()
    paying.value = false
    uni.redirectTo({ url: `/pages/settled/index?id=${order.id}` })
  } catch (e) {
    uni.hideLoading()
    paying.value = false
  }
}

function goBack() {
  if (getCurrentPages().length > 1) uni.navigateBack({ fail: () => { uni.switchTab({ url: '/pages/home/index' }) } })
  else uni.switchTab({ url: '/pages/home/index' })
}
</script>

<template>
  <view class="page-shell checkout-page">
    <view class="checkout-header">
      <button class="top-back" @click="goBack">‹</button>
      <text class="header-title">确认订单</text><text class="header-subtitle">请确认餐品、取餐与支付信息</text>
    </view>

    <view class="section first-section">
      <view class="store-card card">
        <view class="store-icon">店</view>
        <view class="store-main"><text class="store-name">{{ store.currentStore.value.name }}</text><text class="store-address">{{ store.currentStore.value.address }}</text></view>
        <text class="store-time">约 {{ store.currentStore.value.waitMinutes }} 分钟</text>
      </view>
    </view>

    <view class="section">
      <view class="section-heading"><text class="section-title">取餐方式</text></view>
      <view class="mode-switch card">
        <button :class="{ active: store.state.orderMode === 'pickup' }" @click="store.setOrderMode('pickup')">到店自取</button>
        <button :class="{ active: store.state.orderMode === 'dineIn' }" @click="store.setOrderMode('dineIn')">档口堂食</button>
      </view>
      <view class="time-row">
        <button v-for="time in ['尽快取餐','15 分钟后','30 分钟后']" :key="time" class="time-chip" :class="{ active: pickupTime === time }" @click="pickupTime = time">{{ time }}</button>
      </view>
    </view>

    <view class="section">
      <view class="section-heading"><text class="section-title">餐品清单</text><text class="section-link">共 {{ store.cartCount.value }} 件</text></view>
      <view class="items card">
        <view v-for="(item, index) in store.state.cart" :key="item.key" class="item-row" :class="{ last: index === store.state.cart.length - 1 }">
          <image class="item-fallback" :src="item.image" mode="aspectFill" />
          <view class="item-info"><text class="item-name">{{ item.name }}</text><text class="item-stall">{{ item.stallName }}</text><text class="item-options">{{ item.selectedOptions.map(option => option.name).join(' · ') || '标准制作' }}</text></view>
          <view class="item-price"><text class="item-price-value">{{ formatMoney(item.unitPriceCents) }}</text><text class="item-price-qty">× {{ item.quantity }}</text></view>
        </view>
      </view>
    </view>

    <view class="section">
      <view class="section-heading"><text class="section-title">优惠与备注</text></view>
      <view class="form-card card">
        <view class="form-row coupon-row">
          <text>优惠券</text>
          <scroll-view scroll-x class="coupon-scroll">
            <button class="coupon" :class="{ active: couponId === '' }" @click="couponId = ''">不使用</button>
            <button v-for="coupon in availableCoupons" :key="coupon.id" class="coupon" :class="{ active: couponId === coupon.id }" @click="couponId = coupon.id">{{ coupon.name }} -{{ formatMoney(coupon.discountCents) }}</button>
          </scroll-view>
        </view>
        <view class="form-row last"><text>订单备注</text><input v-model="remark" maxlength="30" placeholder="口味偏好、取餐说明" /></view>
      </view>
    </view>

    <view class="section">
      <view class="section-heading"><text class="section-title">支付方式</text></view>
      <view class="payment-card card">
        <button v-for="(item, index) in [{id:'wechat',name:'微信支付'},{id:'alipay',name:'支付宝'},{id:'balance',name:'会员余额'}]" :key="item.id" class="payment-row" :class="{ last: index === 2 }" @click="payment = item.id">
          <text class="payment-name">{{ item.name }}</text><text class="radio" :class="{ active: payment === item.id }">{{ payment === item.id ? '✓' : '' }}</text>
        </button>
      </view>
    </view>

    <view class="summary section card">
      <view><text>餐品金额</text><text>{{ formatMoney(store.cartSubtotal.value) }}</text></view>
      <view><text>优惠</text><text class="discount">{{ discount ? `-${formatMoney(discount)}` : formatMoney(0) }}</text></view>
      <view class="summary-total"><text>合计</text><text>{{ formatMoney(total) }}</text></view>
    </view>

    <view class="pay-bar">
      <view><text class="pay-label">实付</text><text class="pay-total">{{ formatMoney(total) }}</text></view>
      <button class="pay-button" :class="{ disabled: !store.state.cart.length }" @click="submit">确认支付</button>
    </view>
  </view>
</template>

<style scoped lang="scss">
.checkout-page{padding-bottom:170rpx}.checkout-header{position:relative;padding:calc(92rpx + env(safe-area-inset-top)) 30rpx 78rpx;background:linear-gradient(145deg,#2f2019,#624432);color:white}.top-back{position:absolute;left:26rpx;top:calc(22rpx + env(safe-area-inset-top));width:66rpx;height:66rpx;display:flex;align-items:center;justify-content:center;border-radius:50%;background:rgba(255,255,255,.12);color:white;font-size:48rpx;line-height:1}.eyebrow,.header-title,.header-subtitle{display:block}.eyebrow{font-size:19rpx;letter-spacing:5rpx;color:#dfbd91}.header-title{margin-top:14rpx;font-size:48rpx;font-weight:800}.header-subtitle{margin-top:10rpx;font-size:24rpx;color:rgba(255,255,255,.65)}.first-section{position:relative;z-index:2;margin-top:-38rpx}.store-card{display:flex;align-items:center;padding:24rpx}.store-icon{width:66rpx;height:66rpx;margin-right:18rpx;display:flex;align-items:center;justify-content:center;border-radius:20rpx;background:var(--oat-100);color:var(--brand-700);font-weight:800}.store-main{flex:1;min-width:0}.store-name,.store-address{display:block}.store-name{font-size:28rpx;font-weight:700}.store-address{margin-top:7rpx;color:var(--muted);font-size:21rpx;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.store-time{font-size:22rpx;color:var(--green);margin-left:18rpx}
.mode-switch{display:flex;padding:8rpx}.mode-switch button{display:flex;flex:1;align-items:center;justify-content:center;height:74rpx;border-radius:18rpx;color:var(--muted);font-size:25rpx}.mode-switch button.active{background:var(--brand-800);color:white;font-weight:700}.time-row{display:flex;margin-top:16rpx;overflow:auto}.time-chip{flex-shrink:0;margin-right:12rpx;padding:17rpx 22rpx;border-radius:30rpx;background:#fff;color:var(--muted);font-size:22rpx}.time-chip.active{background:var(--oat-100);color:var(--brand-800);font-weight:700}
.items{padding:0 24rpx}.item-row{display:flex;align-items:center;padding:23rpx 0;border-bottom:1rpx solid var(--line)}.item-row.last{border-bottom:0}.item-fallback{width:82rpx;height:82rpx;margin-right:16rpx;display:flex;align-items:center;justify-content:center;border-radius:18rpx;background:var(--oat-100);font-size:42rpx}.item-info{flex:1;min-width:0}.item-name,.item-options,.item-price text{display:block}.item-name{font-weight:700;font-size:26rpx}.item-options{margin-top:7rpx;color:var(--muted);font-size:20rpx;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.item-price{text-align:right;font-size:23rpx}.item-price .item-price-qty{margin-top:8rpx;color:var(--muted)}
.form-card{padding:0 24rpx}.form-row{display:flex;align-items:center;min-height:92rpx;border-bottom:1rpx solid var(--line);font-size:25rpx}.form-row.last{border-bottom:0}.form-row>text{width:116rpx;margin-right:16rpx;font-weight:600}.form-row input{flex:1;text-align:right;font-size:23rpx}.coupon-row{align-items:flex-start;padding:20rpx 0}.coupon-row>text{padding-top:13rpx}.coupon-scroll{flex:1;white-space:nowrap}.coupon{display:inline-flex;margin-left:10rpx;padding:12rpx 18rpx;border-radius:24rpx;background:var(--oat-50);color:var(--muted);font-size:20rpx}.coupon.active{background:var(--brand-800);color:white}
.payment-card{padding:0 24rpx}.payment-row{display:flex;align-items:center;width:100%;height:90rpx;border-bottom:1rpx solid var(--line);font-size:25rpx;color:var(--ink)}.payment-row.last{border-bottom:0}.payment-name{flex:1;text-align:left}.radio{width:38rpx;height:38rpx;display:flex;align-items:center;justify-content:center;border:2rpx solid #d8cec2;border-radius:50%;font-size:20rpx}.radio.active{border-color:var(--brand-700);background:var(--brand-700);color:white}.summary{padding:20rpx 24rpx}.summary>view{display:flex;justify-content:space-between;padding:11rpx 0;color:var(--muted);font-size:23rpx}.summary .discount{color:var(--danger)}.summary .summary-total{margin-top:8rpx;padding-top:20rpx;border-top:1rpx solid var(--line);color:var(--brand-900);font-size:29rpx;font-weight:800}
.pay-bar{position:fixed;left:0;right:0;bottom:0;z-index:20;display:flex;align-items:center;justify-content:space-between;padding:18rpx 26rpx calc(18rpx + env(safe-area-inset-bottom));background:white;box-shadow:0 -8rpx 30rpx rgba(17,36,91,.08)}.pay-label{font-size:21rpx;color:var(--muted)}.pay-total{margin-left:10rpx;color:var(--danger);font-size:35rpx;font-weight:800}.pay-button{display:flex;align-items:center;justify-content:center;width:260rpx;height:82rpx;border-radius:20rpx;background:var(--brand);color:white;font-size:27rpx;font-weight:700}.pay-button.disabled{opacity:.4}.checkout-header{background:linear-gradient(145deg,#0637c9,#071a62)}.eyebrow{color:#edcf91}.store-icon{background:var(--brand-soft);color:var(--brand)}@media screen and (min-width:760px){.pay-bar{max-width:750px;margin:auto}}
.item-stall{display:block;margin-top:5rpx;color:var(--brand);font-size:18rpx}
</style>
