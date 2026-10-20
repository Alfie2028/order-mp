<template>
  <view class="page-shell home-page">
    <view class="banner-section">
      <swiper class="banner-swiper" circular autoplay :interval="3500" :duration="500" indicator-dots indicator-color="rgba(255,255,255,.5)" indicator-active-color="#fff">
        <swiper-item>
          <view class="banner-slide hero-slide" @click="startOrder('pickup')">
            <image class="hero-bg" :src="resolveImage('/uploads/catalog/banner/hero-campus-dining.png')" mode="aspectFill" />
            <view class="hero-copy"><view class="hero-title">多档口聚合<br/>一站式校园点餐</view><view class="hero-subtitle">餐品现制 · 支持自取与堂食</view><view class="hero-button" @click.stop="startOrder('pickup')">开始点餐</view></view>
          </view>
        </swiper-item>
        <swiper-item v-for="banner in banners" :key="banner.id">
          <view class="banner-slide" @click="onBannerTap(banner)">
            <image class="banner-image" :src="resolveImage(banner.image)" mode="aspectFill" />
            <button v-if="banner.link === 'coupon'" class="banner-coupon-btn" @click.stop="onClaimCoupon">领取优惠券</button>
          </view>
        </swiper-item>
      </swiper>
    </view>

    <view class="store-card card" @click="goStores">
      <view class="store-pin">餐厅</view>
      <view class="store-copy"><view class="store-label">当前餐厅 · 营业中</view><view class="store-name">{{ currentStore.name }}</view><view class="store-meta">{{ formatDistance(currentStore.distance) }} · {{ state.stalls.length }} 个档口 · 预计 {{ currentStore.waitMinutes }} 分钟取餐</view></view>
      <view class="arrow">›</view>
    </view>

    <view class="order-panel section">
      <view class="section-heading"><view class="section-title">选择取餐方式</view><view class="section-link" @click="goOrders">查看订单</view></view>
      <view class="mode-grid">
        <view class="mode-card pickup" @click="startOrder('pickup')"><view class="mode-icon">取</view><view><view class="mode-name">到店自取</view><view class="mode-desc">提前下单，到店即取</view></view><view class="mode-go">›</view></view>
        <view class="mode-card dine-in" @click="startOrder('dineIn')"><view class="mode-icon">享</view><view><view class="mode-name">到店堂食</view><view class="mode-desc">到店下单，店内用餐</view></view><view class="mode-go">›</view></view>
      </view>
    </view>

    <view class="section stall-section">
      <view class="section-heading"><view class="section-title">档口导航</view><view class="section-link" @click="startOrder('pickup')">全部餐品</view></view>
      <view class="stall-grid">
        <view v-for="stall in stallEntries" :key="stall.id" class="stall-card" @click="startOrder('pickup', stall.id)">
          <image :src="stall.image" mode="aspectFit" />
          <view><text class="stall-name">{{ stall.name }}</text><text class="stall-desc">{{ stall.description }}</text></view>
        </view>
      </view>
    </view>

    <view class="section">
      <view class="campaign-card">
        <view class="campaign-title">新用户优惠</view><view class="campaign-copy">单笔订单满 20 元<br/>结算时可减 5 元</view><view class="campaign-button" @click="startOrder('pickup')">前往点单</view>
        <view class="campaign-value"><text class="campaign-value-main">¥5</text><text class="campaign-value-sub">立减</text></view>
      </view>
    </view>

    <view class="section recommend-section">
      <view class="section-heading"><view class="section-title">人气餐品</view><view class="section-link" @click="startOrder('pickup')">查看菜单</view></view>
      <scroll-view scroll-x class="recommend-scroll" :show-scrollbar="false">
        <view class="recommend-row">
          <view v-for="product in popularProducts" :key="product.id" class="recommend-card card" :class="{ 'sold-out': !product.isActive }" @click="openProduct(product.id)">
            <view class="recommend-visual"><image :src="product.image" mode="aspectFit" @error="failedImages[product.id] = true"/><view v-if="failedImages[product.id]" class="recommend-fallback">{{ product.fallback }}</view><text v-if="!product.isActive" class="recommend-sold">售罄</text></view>
            <view class="recommend-name">{{ product.name }}</view><view class="recommend-bottom"><text class="price">{{ formatMoney(product.priceCents) }}</text><text class="recommend-add">+</text></view>
          </view>
        </view>
      </scroll-view>
    </view>

    <view class="member-card section" @click="goMine"><view><view class="member-kicker">LEVEL {{ user.level }} · 会员等级</view><view class="member-title">{{ user.points }} 会员积分</view><view class="member-desc">还需 {{ user.nextLevelPoints - user.points }} 积分升级</view></view><view class="member-progress"><view class="member-progress-value" :style="{ width: progress + '%' }"></view></view></view>

    <view v-if="couponPopup.show" class="coupon-mask">
      <view class="coupon-popup-wrap">
        <view class="coupon-popup" @click.stop>
          <text class="coupon-popup-emoji">🎁</text>
          <text class="coupon-popup-title">新人专享礼已到账</text>
          <text class="coupon-popup-copy">5 元立减券已放入账户，下单结算时可用</text>
          <view class="coupon-popup-value"><text class="coupon-popup-symbol">¥</text><text class="coupon-popup-number">5</text></view>
          <button class="coupon-popup-btn" @click="goOrderFromPopup">去下单使用</button>
        </view>
        <button class="coupon-close" @click="closeCouponPopup">✕</button>
      </view>
    </view>
  </view>
</template>

<script setup>
import { computed, reactive } from 'vue'
import { useAppStore } from '@/store/app'
import { formatDistance, formatMoney } from '@/utils/format'

const { state, currentStore, setOrderMode, setStall, claimCoupon, resolveImage } = useAppStore()
const failedImages = reactive({})
const user = computed(() => state.user || { avatar: '/uploads/catalog/avatar/default.png', level: 0, points: 0, nextLevelPoints: 1200 })
const popularProducts = computed(() => state.products.filter((product) => product.featured))
const stallEntries = computed(() => state.stalls.map((stall) => ({ ...stall, image: state.products.find((product) => product.stallId === stall.id)?.image })))
const progress = computed(() => Math.min(100, Math.round(user.value.points / user.value.nextLevelPoints * 100)))
const startOrder = (mode, stallId = '') => { setOrderMode(mode); if (stallId) setStall(stallId); uni.switchTab({ url: '/pages/order/index' }) }
const goStores = () => uni.switchTab({ url: '/pages/shop/index' })
const goOrders = () => uni.navigateTo({ url: '/pages/my-order/index' })
const goMine = () => uni.switchTab({ url: '/pages/my/index' })
const openProduct = (id) => { const product = state.products.find((p) => p.id === id); if (product && !product.isActive) { uni.showToast({ title: '该商品已售罄', icon: 'none' }); return } uni.navigateTo({ url: `/pages/item-detail/index?id=${id}` }) }

// 首页轮播图：第 1 张为主视觉「多档口聚合一站式校园点餐」，以下 4 张为占位图（后续替换真实素材）
// link: pickup=点单 / stores=餐厅 / coupon=领券
const banners = [
  { id: 2, image: '/uploads/catalog/store/store-campus.png', link: 'coupon' },
  { id: 3, image: '/uploads/catalog/store/store-street.png', link: 'stores' },
  { id: 4, image: '/uploads/catalog/store/store-town.png', link: 'pickup' },
  { id: 5, image: '/uploads/catalog/banner/hero-campus-dining.png', link: 'pickup' },
]
const couponPopup = reactive({ show: false })
function onBannerTap(banner) {
  if (banner.link === 'coupon') return
  if (banner.link === 'stores') goStores()
  else startOrder('pickup')
}
async function onClaimCoupon() {
  if (!state.user) { uni.navigateTo({ url: '/pages/login/index' }); return }
  if (state.couponIds.includes('newbie')) { uni.showToast({ title: '新人券已领取过啦', icon: 'none' }); return }
  const coupon = await claimCoupon('newbie')
  if (coupon) couponPopup.show = true
}
function closeCouponPopup() { couponPopup.show = false }
function goOrderFromPopup() { couponPopup.show = false; startOrder('pickup') }
</script>

<style scoped lang="scss">
.home-page{overflow:hidden;background:#f6f7f9}.hero-copy{position:relative;z-index:2;padding:calc(62rpx + env(safe-area-inset-top)) 34rpx 0}.hero-title{color:#10266f;font-size:47rpx;font-weight:800;line-height:1.2;letter-spacing:1rpx}.hero-subtitle{margin-top:13rpx;color:#7b7e87;font-size:22rpx}.hero-button{display:inline-flex;margin-top:23rpx;padding:13rpx 28rpx;border-radius:8rpx;color:#fff;background:var(--brand);font-size:21rpx;font-weight:700;box-shadow:0 9rpx 22rpx rgba(6,55,201,.22)}
.store-card{position:relative;z-index:3;display:flex;align-items:center;margin:16rpx 28rpx 0;padding:23rpx 25rpx}.store-pin{display:flex;align-items:center;justify-content:center;width:62rpx;height:62rpx;margin-right:18rpx;border-radius:18rpx;color:#fff;background:var(--brand);font-size:18rpx;font-weight:700}.store-copy{min-width:0;flex:1}.store-label{color:var(--brand);font-size:18rpx;font-weight:700}.store-name{margin-top:5rpx;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-size:26rpx;font-weight:700}.store-meta{margin-top:6rpx;color:var(--muted);font-size:19rpx}.arrow{color:var(--brand);font-size:40rpx;margin-left:18rpx}
.order-panel{margin-top:20rpx}.mode-grid{display:flex;flex-wrap:wrap;margin-right:-18rpx}.mode-card{position:relative;width:calc(50% - 18rpx);margin-right:18rpx;min-height:194rpx;padding:22rpx;border:1rpx solid #e7eaf1;border-radius:24rpx;background:#fff;box-shadow:0 8rpx 24rpx rgba(18,39,92,.05)}.pickup,.dine-in{color:var(--ink);background:#fff}.mode-icon{display:flex;align-items:center;justify-content:center;width:64rpx;height:64rpx;border-radius:18rpx;color:#fff;background:linear-gradient(145deg,#0b4ee7,#062b9e);font-size:27rpx;font-weight:800;box-shadow:0 8rpx 18rpx rgba(6,55,201,.2)}.dine-in .mode-icon{color:#785719;background:linear-gradient(145deg,#f4d99e,#d6a95c);box-shadow:0 8rpx 18rpx rgba(199,149,69,.18)}.mode-name{margin-top:16rpx;font-size:27rpx;font-weight:800}.mode-desc{margin-top:5rpx;color:var(--muted);font-size:18rpx}.mode-go{position:absolute;right:18rpx;top:30rpx;color:#a1a5ae;font-size:32rpx}
.campaign-card{position:relative;min-height:232rpx;padding:28rpx;overflow:hidden;border:1rpx solid #e5e9f2;border-radius:26rpx;color:var(--ink);background:linear-gradient(120deg,#fff 0%,#f7f9ff 72%,#edf2ff 100%);box-shadow:0 9rpx 28rpx rgba(16,40,101,.06)}.campaign-card::after{content:'';position:absolute;right:-55rpx;bottom:-80rpx;width:250rpx;height:250rpx;border:32rpx solid rgba(6,55,201,.08);border-radius:50%}.campaign-tag{color:var(--brand);font-size:17rpx;font-weight:800;letter-spacing:3rpx}.campaign-title{margin-top:10rpx;color:#10266f;font-size:34rpx;font-weight:800}.campaign-copy{margin-top:8rpx;color:#858891;font-size:20rpx;line-height:1.55}.campaign-button{display:inline-flex;margin-top:15rpx;padding:10rpx 22rpx;border-radius:7rpx;color:#fff;background:#d21f28;font-size:20rpx;font-weight:700}.campaign-value{position:absolute;z-index:2;right:38rpx;top:50%;transform:translateY(-42%);text-align:right}.campaign-value text{display:block}.campaign-value-main{color:#d21f28;font-size:70rpx;font-weight:800;letter-spacing:-3rpx}.campaign-value-sub{margin-top:-6rpx;color:#10266f;font-size:18rpx;font-weight:700;letter-spacing:5rpx}
.recommend-section{padding-right:0}.recommend-scroll{width:100%;white-space:nowrap}.recommend-row{display:flex;padding:2rpx 28rpx 18rpx 0}.recommend-card{display:inline-flex;flex-direction:column;width:244rpx;margin-right:18rpx;padding:14rpx}.recommend-visual{position:relative;height:190rpx;overflow:visible;border-radius:50%;background:linear-gradient(145deg,#f7f8fb,#edf1f8)}.recommend-visual image{width:100%;height:100%;transform:scale(1.04)}.recommend-fallback{position:absolute;left:0;top:0;right:0;bottom:0;display:flex;align-items:center;justify-content:center;font-size:82rpx;background:#f2f4f8}.recommend-sold{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);padding:7rpx 14rpx;border-radius:9rpx;color:#fff;background:rgba(60,60,66,.82);font-size:20rpx;font-weight:700}.recommend-card.sold-out .recommend-visual image{opacity:.55}.recommend-name{margin-top:15rpx;overflow:hidden;text-overflow:ellipsis;font-size:25rpx;font-weight:700}.recommend-bottom{display:flex;align-items:center;justify-content:space-between;margin-top:12rpx}.recommend-add{display:flex;align-items:center;justify-content:center;width:42rpx;height:42rpx;border-radius:13rpx;color:#fff;background:var(--brand);font-size:28rpx}.member-card{margin-bottom:20rpx;padding:30rpx;border-radius:28rpx;color:#fff;background:linear-gradient(120deg,#071a62,#123aa8)}.member-kicker{color:var(--caramel-300);font-size:19rpx;letter-spacing:2rpx}.member-title{margin-top:12rpx;font-size:34rpx;font-weight:700}.member-desc{margin-top:5rpx;color:rgba(255,255,255,.65);font-size:21rpx}.member-progress{height:8rpx;margin-top:22rpx;overflow:hidden;border-radius:4rpx;background:rgba(255,255,255,.18)}.member-progress-value{height:100%;border-radius:4rpx;background:var(--caramel-300)}
.hero-slide{position:relative;background-color:#fff}.hero-bg{position:absolute;left:0;top:0;right:0;bottom:0;width:100%;height:100%;z-index:0}.hero-slide::after{content:'';position:absolute;left:0;top:0;right:0;bottom:0;z-index:1;background:linear-gradient(90deg,rgba(255,255,255,.99) 0%,rgba(255,255,255,.94) 34%,rgba(255,255,255,.58) 54%,rgba(255,255,255,0) 76%)}
.stall-grid{display:flex;flex-wrap:wrap;margin-right:-14rpx}.stall-card{display:flex;align-items:center;width:calc(50% - 14rpx);margin-right:14rpx;margin-bottom:14rpx;min-width:0;min-height:128rpx;padding:12rpx 14rpx;border:1rpx solid #e6e9f0;border-radius:20rpx;background:#fff;box-shadow:0 7rpx 20rpx rgba(17,38,91,.045)}.stall-card image{width:84rpx;height:84rpx;flex:0 0 84rpx;margin-right:11rpx;border-radius:50%;background:#f2f4f8}.stall-card>view{min-width:0}.stall-name,.stall-desc{display:block}.stall-name{font-size:22rpx;font-weight:700;white-space:nowrap}.stall-desc{margin-top:5rpx;overflow:hidden;color:var(--muted);font-size:16rpx;text-overflow:ellipsis;white-space:nowrap}
.banner-section{position:relative}.banner-swiper{height:360rpx}.banner-slide{position:relative;width:100%;height:100%}.banner-image{width:100%;height:100%}.banner-coupon-btn{position:absolute;right:24rpx;bottom:24rpx;display:flex;align-items:center;justify-content:center;height:60rpx;padding:0 24rpx;border-radius:30rpx;background:linear-gradient(135deg,#d21f28,#ff5a3d);color:#fff;font-size:23rpx;font-weight:700;box-shadow:0 8rpx 20rpx rgba(210,31,40,.35)}
.coupon-mask{position:fixed;left:0;top:0;right:0;bottom:0;z-index:100;display:flex;align-items:center;justify-content:center;background:rgba(0,0,0,.5)}.coupon-popup-wrap{display:flex;flex-direction:column;align-items:center}.coupon-popup{width:560rpx;padding:48rpx 40rpx 36rpx;border-radius:28rpx;text-align:center;background:#fff;box-shadow:0 24rpx 60rpx rgba(0,0,0,.25)}.coupon-popup-emoji{display:block;font-size:88rpx;line-height:1}.coupon-popup-title{display:block;margin-top:20rpx;font-size:34rpx;font-weight:800;color:var(--brand-950)}.coupon-popup-copy{display:block;margin-top:12rpx;color:var(--muted);font-size:23rpx}.coupon-popup-value{display:flex;align-items:baseline;justify-content:center;margin-top:26rpx;color:#d21f28}.coupon-popup-symbol{font-size:34rpx;font-weight:800}.coupon-popup-number{font-size:88rpx;font-weight:900;line-height:1}.coupon-popup-btn{display:flex;align-items:center;justify-content:center;width:100%;height:82rpx;margin-top:26rpx;border-radius:41rpx;background:linear-gradient(135deg,#d21f28,#ff5a3d);color:#fff;font-size:27rpx;font-weight:700}.coupon-close{display:flex;align-items:center;justify-content:center;width:64rpx;height:64rpx;margin-top:28rpx;border-radius:50%;background:rgba(255,255,255,.16);color:#fff;font-size:32rpx;line-height:1}
</style>
