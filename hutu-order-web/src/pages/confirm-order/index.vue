<script setup>
import { computed, ref } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { useAppStore } from '@/store/app'
import { formatMoney } from '@/utils/format'
import { getNavLayout } from '@/utils/nav'

const store = useAppStore()
const navLayout = getNavLayout()
const couponId = ref('')
const note = ref('')
const pickupTime = ref('尽快取餐')
const payment = ref('wechat')
const submitting = ref(false)

const availableCoupons = computed(() => (store.state.coupons || []).filter((coupon) => store.state.couponIds.includes(coupon.id) && (!coupon.thresholdCents || store.cartSubtotal.value >= coupon.thresholdCents)))
const chosenCoupon = computed(() => store.state.coupons.find((coupon) => coupon.id === couponId.value))
const discount = computed(() => chosenCoupon.value?.discountCents || 0)
const total = computed(() => Math.max(0, store.cartSubtotal.value - discount.value))

onLoad(() => {
  if (availableCoupons.value.length) couponId.value = availableCoupons.value[0].id
})

async function submit() {
  if (submitting.value) return
  if (!store.state.cart.length) { uni.showToast({ title: '购物车为空', icon: 'none' }); return }
  if (!store.state.user) { uni.navigateTo({ url: '/pages/login/index' }); return }
  submitting.value = true
  uni.showLoading({ title: '创建订单中' })
  try {
    const order = await store.createOrder({
      couponId: couponId.value || undefined,
      note: note.value.trim() || undefined,
      pickupTime: pickupTime.value,
      paymentMethod: payment.value,
    })
    uni.hideLoading()
    if (order && order.id) {
      uni.showToast({ title: '下单成功', icon: 'success' })
      setTimeout(() => {
        uni.redirectTo({ url: `/pages/settled/index?id=${order.id}` })
      }, 350)
    }
  } catch (e) {
    uni.hideLoading()
  } finally {
    submitting.value = false
  }
}

function goBack() {
  if (getCurrentPages().length > 1) uni.navigateBack()
  else uni.switchTab({ url: '/pages/order/index' })
}
</script>

<template>
  <view class="page-shell checkout-page">
    <view class="checkout-header" :style="{ paddingTop: (navLayout.capsuleTop + 44) + 'px' }">
      <button class="top-back" :style="{ top: navLayout.capsuleTop + 'px' }" @click="goBack">‹</button>
      <text class="header-title">确认订单</text>
      <text class="header-subtitle">请核对餐品、取餐方式与支付金额</text>
      <view class="mode-switch card">
        <button :class="{ active: store.state.orderMode === 'pickup' }" @click="store.setOrderMode('pickup')">到店自取</button>
        <button :class="{ active: store.state.orderMode === 'dineIn' }" @click="store.setOrderMode('dineIn')">档口堂食</button>
      </view>
      <view class="time-row">
        <button v-for="time in ['尽快取餐','15 分钟后','30 分钟后']" :key="time" class="time-chip" :class="{ active: pickupTime === time }" @click="pickupTime = time">{{ time }}</button>
      </view>
    </view>

    <view class="section first-section">
      <view class="store-card card">
        <view class="store-icon">
          <image class="store-mascot" src="/static/icon/store-shop.png" mode="aspectFit" />
        </view>
        <view class="store-main">
          <text class="store-name">{{ store.currentStore.value?.name }}</text>
          <text class="store-address">{{ store.currentStore.value?.address }}</text>
        </view>
        <text class="store-time">出餐约 {{ store.currentStore.value?.waitMinutes }} 分钟</text>
      </view>
    </view>

    <view class="section">
      <view class="section-heading">
        <text class="section-title">餐品清单</text>
        <text class="section-link">共 {{ store.cartCount.value }} 件</text>
      </view>
      <view class="items card">
        <view v-for="(item, index) in store.state.cart" :key="item.key" class="item-row" :class="{ last: index === store.state.cart.length - 1 }">
          <image v-if="item.image" class="item-visual" :src="item.image" mode="aspectFill" />
          <view v-else class="item-fallback">{{ item.fallback }}</view>
          <view class="item-info">
            <text class="item-name">{{ item.name }}</text>
            <text class="item-stall">{{ item.stallName }}</text>
            <text class="item-options">{{ item.selectedOptions.map((o) => o.name).join(' / ') || '标准制作' }}</text>
          </view>
          <view class="item-price">
            <text class="price">{{ formatMoney(item.unitPriceCents * item.quantity) }}</text>
            <text class="item-price-qty">x {{ item.quantity }}</text>
          </view>
        </view>
      </view>
    </view>

    <view class="section">
      <view class="form-card card">
        <view class="form-row coupon-row">
          <text>肥嘟嘟神券</text>
          <scroll-view scroll-x class="coupon-scroll" :show-scrollbar="false">
            <button class="coupon" :class="{ active: couponId === '' }" @click="couponId = ''">不使用</button>
            <button v-for="coupon in availableCoupons" :key="coupon.id" class="coupon" :class="{ active: couponId === coupon.id }" @click="couponId = coupon.id">
              {{ coupon.name }} -{{ formatMoney(coupon.discountCents) }}
            </button>
          </scroll-view>
        </view>
        <view class="form-row last">
          <text>备注要求</text>
          <input v-model="note" placeholder="如：多放葱/少辣/不要香菜等" maxlength="50" />
        </view>
      </view>
    </view>

    <view class="section">
      <view class="payment-card card">
        <button v-for="(item, index) in [
          {id:'wechat',name:'微信支付',icon:'/static/icon/pay-wechat.png'},
          {id:'alipay',name:'支付宝支付',icon:'/static/icon/pay-alipay.png'},
          {id:'balance',name:'会员余额支付',icon:'/static/icon/pay-balance.png'}
        ]" :key="item.id" class="payment-row" :class="{ last: index === 2 }" @click="payment = item.id">
          <image class="pay-method-icon" :src="item.icon" mode="aspectFit" />
          <text class="payment-name">{{ item.name }}</text>
          <view class="radio" :class="{ active: payment === item.id }">
            <text v-if="payment === item.id" class="radio-check">✓</text>
          </view>
        </button>
      </view>
    </view>

    <view class="section">
      <view class="summary card">
        <view><text>餐品金额</text><text>{{ formatMoney(store.cartSubtotal.value) }}</text></view>
        <view><text>肥嘟嘟立减 / 优惠券</text><text class="discount">{{ discount ? `-${formatMoney(discount)}` : formatMoney(0) }}</text></view>
        <view class="summary-total"><text>应付合计</text><text class="summary-total-price">{{ formatMoney(total) }}</text></view>
      </view>
    </view>

    <!-- 底部固定结算栏 -->
    <view class="pay-bar" :style="{ paddingBottom: (navLayout.bottomSafe ? navLayout.bottomSafe + 'px' : '') }">
      <view class="pay-bar-inner">
        <view class="pay-left">
          <text class="pay-label">实付 </text>
          <text class="pay-total">{{ formatMoney(total) }}</text>
        </view>
        <button class="pay-button" :class="{ disabled: !store.state.cart.length || submitting }" @click="submit">确认支付</button>
      </view>
    </view>
  </view>
</template>

<style scoped lang="scss">
.checkout-page {
  padding-bottom: calc(180rpx + constant(safe-area-inset-bottom));
  padding-bottom: calc(180rpx + env(safe-area-inset-bottom));
  background: #F7F8FA;
}
.checkout-header {
  position: relative;
  padding: calc(64rpx + var(--status-bar-height, 0px) + env(safe-area-inset-top, 0px)) 28rpx 70rpx;
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
.header-title {
  margin-top: 14rpx;
  font-size: 44rpx;
  font-weight: 900;
  display: block;
}
.header-subtitle {
  margin-top: 8rpx;
  font-size: 22rpx;
  color: rgba(34, 36, 38, .75);
  display: block;
}

.mode-switch {
  display: flex;
  padding: 8rpx;
  margin-top: 24rpx;
  border-radius: 20rpx;
  background: rgba(255, 255, 255, .8);
}
.mode-switch button {
  display: flex;
  flex: 1;
  align-items: center;
  justify-content: center;
  height: 74rpx;
  border-radius: 16rpx;
  color: #666;
  font-size: 25rpx;
  font-weight: 600;
}
.mode-switch button.active {
  background: #222426;
  color: #FFC300;
  font-weight: 800;
}

.time-row {
  display: flex;
  margin-top: 18rpx;
  overflow: auto;
}
.time-chip {
  flex-shrink: 0;
  margin-right: 12rpx;
  padding: 12rpx 24rpx;
  border-radius: 28rpx;
  background: rgba(255, 255, 255, .7);
  color: #222426;
  font-size: 22rpx;
  font-weight: 600;
}
.time-chip.active {
  background: #222426;
  color: #FFC300;
  font-weight: 800;
}

.first-section {
  position: relative;
  z-index: 2;
  margin-top: -36rpx;
}
.store-card {
  display: flex;
  align-items: center;
  padding: 24rpx;
}
.store-icon {
  width: 72rpx;
  height: 72rpx;
  margin-right: 18rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: #FFF7DB;
}
.store-mascot {
  width: 48rpx;
  height: 48rpx;
}
.store-main { flex: 1; min-width: 0; }
.store-name { font-size: 28rpx; font-weight: 800; color: #222426; display: block; }
.store-address { margin-top: 6rpx; color: #8E929E; font-size: 20rpx; display: block; }
.store-time { font-size: 21rpx; color: #07C160; margin-left: 18rpx; font-weight: 700; }

.items { padding: 4rpx 24rpx; }
.item-row {
  display: flex;
  align-items: center;
  padding: 22rpx 0;
  border-bottom: 1rpx solid #F0F0F2;
}
.item-row.last { border-bottom: 0; }
.item-visual {
  width: 90rpx;
  height: 90rpx;
  margin-right: 16rpx;
  border-radius: 14rpx;
  background: #F4F5F8;
}
.item-fallback {
  width: 90rpx;
  height: 90rpx;
  margin-right: 16rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 14rpx;
  background: #FFF9E6;
  font-size: 24rpx;
  font-weight: 800;
  color: #B37D00;
}
.item-info { flex: 1; min-width: 0; }
.item-name { font-weight: 800; font-size: 26rpx; color: #222426; display: block; }
.item-stall { margin-top: 4rpx; color: #B37D00; font-size: 19rpx; font-weight: 600; display: block; }
.item-options { margin-top: 4rpx; color: #8E929E; font-size: 20rpx; display: block; }
.item-price { text-align: right; font-size: 24rpx; }
.item-price .item-price-qty { margin-top: 6rpx; color: #8E929E; font-size: 20rpx; display: block; }

.form-card { padding: 4rpx 24rpx; }
.form-row {
  display: flex;
  align-items: center;
  min-height: 94rpx;
  border-bottom: 1rpx solid #F0F0F2;
  font-size: 25rpx;
}
.form-row.last { border-bottom: 0; }
.form-row > text { width: 130rpx; font-weight: 700; color: #222426; flex-shrink: 0; }
.form-row input { flex: 1; text-align: right; font-size: 24rpx; color: #222426; }
.coupon-row { align-items: center; }
.coupon-scroll { flex: 1; white-space: nowrap; }
.coupon {
  display: inline-flex;
  margin-left: 12rpx;
  padding: 10rpx 20rpx;
  border-radius: 24rpx;
  background: #F4F5F8;
  color: #666;
  font-size: 21rpx;
  font-weight: 600;
}
.coupon.active {
  background: #FFC300;
  color: #222426;
  font-weight: 800;
}

.payment-card { padding: 4rpx 24rpx; }
.payment-row {
  display: flex;
  align-items: center;
  width: 100%;
  height: 96rpx;
  border-bottom: 1rpx solid #F0F0F2;
  font-size: 26rpx;
  color: #222426;
}
.payment-row.last { border-bottom: 0; }
.pay-method-icon {
  width: 44rpx;
  height: 44rpx;
  margin-right: 18rpx;
  flex: 0 0 44rpx;
}
.payment-name { flex: 1; text-align: left; font-weight: 700; }
.radio {
  width: 40rpx;
  height: 40rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2rpx solid #D5D8DE;
  border-radius: 50%;
}
.radio.active {
  border-color: #FFC300;
  background: #FFC300;
}
.radio-check {
  font-size: 24rpx;
  font-weight: 900;
  color: #222426;
}

.summary { padding: 22rpx 24rpx; }
.summary > view { display: flex; justify-content: space-between; padding: 10rpx 0; color: #8E929E; font-size: 24rpx; }
.summary .discount { color: #FF4B3E; font-weight: 700; }
.summary .summary-total {
  margin-top: 10rpx;
  padding-top: 20rpx;
  border-top: 1rpx solid #F0F0F2;
  color: #222426;
  font-size: 28rpx;
  font-weight: 800;
}
.summary-total-price { color: #FF4B3E; font-size: 34rpx; font-weight: 900; }

.pay-bar {
  position: fixed;
  left: 50%;
  transform: translateX(-50%);
  width: 100%;
  max-width: 750px;
  bottom: 0;
  z-index: 20;
  background: #fff;
  border-top: 1rpx solid #F0F0F2;
  box-shadow: 0 -8rpx 24rpx rgba(0, 0, 0, .06);
  padding-bottom: constant(safe-area-inset-bottom);
  padding-bottom: env(safe-area-inset-bottom);
  box-sizing: border-box;
}
.pay-bar-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  max-width: 750px;
  margin: 0 auto;
  padding: 16rpx 28rpx;
  box-sizing: border-box;
}
.pay-left { display: flex; align-items: baseline; flex: 1; }
.pay-label { font-size: 22rpx; color: #8E929E; }
.pay-total { margin-left: 10rpx; color: #FF4B3E; font-size: 40rpx; font-weight: 900; }
.pay-button {
  flex: 0 0 auto;
  width: 280rpx;
  height: 84rpx;
  margin: 0 0 0 auto !important;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 42rpx;
  background: #FFC300;
  color: #222426;
  font-size: 28rpx;
  font-weight: 800;
  box-shadow: 0 6rpx 18rpx rgba(255, 195, 0, .4);
}
.pay-button::after { border: none; }
.pay-button.disabled { opacity: .45; }
</style>
