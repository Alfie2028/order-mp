<script setup>
import { computed } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import ProductCard from '@/component/ProductCard.vue'
import { useAppStore } from '@/store/app'

const store = useAppStore()
const user = computed(() => store.state.user)
const isCustomAvatar = computed(() => user.value && typeof user.value.avatar === 'string' && user.value.avatar.startsWith('data:'))
const favorites = computed(() => (store.state.products || []).filter((product) => store.state.favoriteIds.includes(product.id)))
const availableCoupons = computed(() => (store.state.coupons || []).filter((coupon) => store.state.couponIds.includes(coupon.id)))
const activeOrder = computed(() => (store.state.orders || []).find((order) => ['paid','making','ready'].includes(order.status)))
const levelProgress = computed(() => user.value ? Math.min(100, Math.round(user.value.points / (user.value.nextLevelPoints || 1200) * 100)) : 0)
onShow(() => { if (user.value) { store.loadOrders().catch(() => {}); store.loadFavorites().catch(() => {}) } })

function openProduct(product) { uni.navigateTo({ url: `/pages/item-detail/index?id=${product.id}` }) }
function quickAdd(product) { product.options.length ? openProduct(product) : (store.addToCart(product.id), uni.showToast({ title: '已加入购物车', icon: 'success' })) }
function showFeature(message) { uni.showToast({ title: message, icon: 'none' }) }

// —— 吃货专享服务：三个板块（健康热量 / 签到领券 / 在线客服） ——
const CALORIE_STORAGE = 'CAMPUS_CALORIE_DAY'
const CHECKIN_STORAGE = 'CAMPUS_CHECKIN_V1'
const todayKey = () => { const d = new Date(); return `${d.getFullYear()}-${('0' + (d.getMonth() + 1)).slice(-2)}-${('0' + d.getDate()).slice(-2)}` }

// 健康热量管家：按已完成订单估算（每单约 480 kcal，标注为估算值）
function openCalorie() {
  if (!user.value) return goLogin()
  const done = (store.state.orders || []).filter((o) => o.status === 'completed')
  const kcal = done.length * 480
  uni.showModal({
    title: '今日热量估算',
    content: `已完成订单 ${done.length} 单，估算摄入约 ${kcal} kcal。\n数据按每单 480 kcal 折算，仅作本地估算，不作为营养建议。`,
    showCancel: false,
    confirmText: '知道了',
  })
}

// 签到领吃货券：每天一次，本地记录并加积分；顺手把账户里的券列出来
function doCheckin() {
  if (!user.value) return goLogin()
  const today = todayKey()
  if (uni.getStorageSync(CHECKIN_STORAGE) === today) {
    uni.showModal({ title: '今天已签到', content: `已连续签到，当前积分 ${user.value.points}。明天记得再来。`, showCancel: false, confirmText: '去看看券' , success: showMyCoupons })
    return
  }
  uni.setStorageSync(CHECKIN_STORAGE, today)
  const updated = { ...user.value, points: (user.value.points || 0) + 20 }
  store.state.user = updated
  uni.setStorageSync('USER_INFO', updated)
  uni.showModal({
    title: '签到成功',
    content: `积分 +20，当前 ${updated.points}。\n吃货券可在结算时选择使用。`,
    showCancel: false,
    confirmText: '看我的券',
    success: showMyCoupons,
  })
}
function showMyCoupons() {
  store.loadMyCoupons().catch(() => {}).then(() => {
    const list = availableCoupons.value
    if (!list.length) { uni.showModal({ title: '还没有可用券', content: '去首页「吃货券」卡片领一张，满 30 减 5。', showCancel: false, confirmText: '去领券', success: () => uni.switchTab({ url: '/pages/home/index' }) }); return }
    const content = list.map((c) => `${c.name}（${c.discountCents / 100} 元${c.thresholdCents ? `，满 ${c.thresholdCents / 100} 元可用` : ''}，${c.expires} 到期）`).join('\n')
    uni.showModal({ title: `我的券 ${list.length} 张`, content, showCancel: false, confirmText: '知道了' })
  })
}

// 在线客服：校园餐厅服务台
function openService() {
  uni.showModal({
    title: '在线客服',
    content: '校园餐厅服务台 07:30–21:30。\n出餐、取餐码、退款等问题，可先在「订单记录」里查看订单状态。',
    showCancel: false,
    confirmText: '看订单',
    success: () => uni.navigateTo({ url: '/pages/my-order/index' }),
  })
}
function goLogin() {
  uni.navigateTo({ url: '/pages/login/index', fail: (err) => { console.error('navigateTo /pages/login/index fail:', err); uni.redirectTo({ url: '/pages/login/index' }) } })
}
function chooseAvatar() {
  if (!user.value) return goLogin()
  uni.chooseImage({
    count: 1,
    sizeType: ['compressed'],
    success: (res) => {
      const filePath = res.tempFilePaths && res.tempFilePaths[0]
      if (!filePath) return
      uni.showLoading({ title: '上传中' })
      store.setAvatar(filePath).then(() => { uni.hideLoading(); uni.showToast({ title: '头像已更新', icon: 'success' }) }).catch(() => uni.hideLoading())
    },
  })
}
function goMerchant() { uni.navigateTo({ url: '/pages/merchant/index' }) }
function logout() {
  uni.showModal({ title: '退出登录', content: '确定要退出当前账号吗？', confirmColor: '#0637c9', success: ({ confirm }) => {
    if (!confirm) return
    store.logout()
    uni.showToast({ title: '已退出登录', icon: 'success' })
  } })
}
</script>

<template>
  <view class="page-shell my-page">
    <view class="profile-hero">
      <view class="brand-line"><button @click="uni.navigateTo({ url: '/pages/setting/index' })">设置</button></view>
      <view v-if="user" class="profile-row">
        <view class="avatar" @click="chooseAvatar">
          <image v-if="isCustomAvatar" class="avatar-img" :src="user.avatar" mode="aspectFill" />
          <text v-else>会</text>
          <text class="avatar-edit">✎</text>
        </view>
        <view class="profile-main"><text class="user-name">{{ user.name }}</text><text class="user-title">{{ user.title }} · LV.{{ user.level }}</text></view>
        <view class="points"><text class="points-value">{{ user.points }}</text><text class="points-label">会员积分</text></view>
      </view>
      <view v-else class="profile-row" @click="goLogin">
        <view class="avatar">登</view>
        <view class="profile-main"><text class="user-name">点击登录</text><text class="user-title">登录后同步订单、收藏与购物车</text></view>
        <view class="points"><text class="login-arrow">›</text><text class="points-label">去登录</text></view>
      </view>
      <template v-if="user">
        <view class="level-bar"><view :style="{ width: `${levelProgress}%` }" /></view>
        <text class="level-copy">距离下一等级还需 {{ Math.max(0, user.nextLevelPoints - user.points) }} 积分</text>
      </template>
    </view>

    <view class="quick-panel card">
      <view class="quick-item divider" @click="uni.navigateTo({ url: '/pages/my-order/index' })"><text class="quick-number">{{ store.state.orders.length }}</text><text>全部订单</text></view>
      <view class="quick-item divider" @click="showFeature('优惠券可在提交订单时选择')"><text class="quick-number">{{ availableCoupons.length }}</text><text>优惠券</text></view>
      <view class="quick-item divider" @click="showFeature('收藏餐品可在本页下方查看')"><text class="quick-number">{{ favorites.length }}</text><text>我的收藏</text></view>
      <view class="quick-item" @click="showFeature('会员等级信息已展示在页面顶部')"><text class="quick-number">{{ store.state.user ? store.state.user.level : 0 }}</text><text>会员等级</text></view>
    </view>

    <view v-if="activeOrder" class="section">
      <view class="section-heading"><text class="section-title">进行中的订单</text><text class="section-link" @click="uni.navigateTo({ url: '/pages/my-order/index' })">全部订单</text></view>
      <view class="active-order card" @click="uni.navigateTo({ url: `/pages/settled/index?id=${activeOrder.id}` })">
        <view class="active-symbol">{{ activeOrder.status === 'ready' ? '待取' : '制作' }}</view>
        <view class="active-main"><text class="active-main-title">{{ activeOrder.statusText }} · 取餐码 {{ activeOrder.pickupCode }}</text><text class="active-main-sub">{{ activeOrder.storeName }}</text></view>
        <text class="arrow">›</text>
      </view>
    </view>

    <view class="section">
      <view class="section-heading"><text class="section-title">吃货专享服务</text><text class="section-link" @click="uni.switchTab({ url: '/pages/shop/index' })">门店地图 ›</text></view>
      <view class="service-grid card">
        <view class="service-cell" @click="openCalorie">
          <view class="service-icon calorie">热</view>
          <text class="service-name">健康热量管家</text>
          <text class="service-desc">按订单估算摄入</text>
        </view>
        <view class="service-cell" @click="doCheckin">
          <view class="service-icon checkin">签</view>
          <text class="service-name">签到领吃货券</text>
          <text class="service-desc">{{ user ? '每日一签 +20 积分' : '登录后签到' }}</text>
        </view>
        <view class="service-cell" @click="openService">
          <view class="service-icon service">客</view>
          <text class="service-name">在线客服</text>
          <text class="service-desc">服务台 07:30–21:30</text>
        </view>
      </view>
    </view>

    <view class="section favorite-section">
      <view class="section-heading"><text class="section-title">我的常点</text><text class="section-link">{{ favorites.length }} 款收藏</text></view>
      <view v-if="favorites.length" class="favorite-list"><ProductCard v-for="product in favorites" :key="product.id" :product="product" @open="openProduct" @add="quickAdd" /></view>
      <view v-else class="empty-favorite card">暂无收藏餐品，可在餐品详情中添加收藏。</view>
    </view>

    <view v-if="user" class="section account-actions">
      <button v-if="user.role === 'merchant'" class="merchant-entry" @click="goMerchant">进入商家工作台</button>
      <button class="logout-entry" @click="logout">退出登录</button>
    </view>

    <view class="footer-mark">校园点餐 · 多门店聚合服务</view>
  </view>
</template>

<style scoped lang="scss">
.my-page{padding-bottom:60rpx}.profile-hero{padding:calc(54rpx + env(safe-area-inset-top)) 30rpx 74rpx;color:white;background:linear-gradient(145deg,#302019,#6e4c3a)}.brand-line{display:flex;align-items:center;justify-content:flex-end;color:var(--caramel-300);font-size:18rpx;letter-spacing:5rpx}.brand-line button{width:auto;height:52rpx;padding:0 20rpx;display:flex;align-items:center;justify-content:center;border:1rpx solid rgba(255,255,255,.25);border-radius:26rpx;background:transparent;color:white;font-size:19rpx;letter-spacing:1rpx}.profile-row{display:flex;align-items:center;margin-top:34rpx}.avatar{width:104rpx;height:104rpx;display:flex;align-items:center;justify-content:center;position:relative;overflow:visible;border:2rpx solid rgba(255,255,255,.45);border-radius:36rpx;background:#d4ad7e;color:#4a3025;font-size:43rpx;font-weight:800}.avatar-img{width:100%;height:100%;border-radius:34rpx}.avatar-edit{position:absolute;right:-6rpx;bottom:-6rpx;width:34rpx;height:34rpx;display:flex;align-items:center;justify-content:center;border-radius:50%;background:rgba(255,255,255,.9);color:#0637c9;font-size:20rpx;line-height:1}.profile-main{flex:1;margin-left:22rpx}.user-name,.user-title,.points text{display:block}.user-name{font-size:38rpx;font-weight:800}.user-title{margin-top:7rpx;color:rgba(255,255,255,.64);font-size:21rpx}.points{text-align:right}.points-value{font-size:38rpx;font-weight:800}.points-label{margin-top:3rpx;font-size:19rpx;color:rgba(255,255,255,.6)}.level-bar{height:8rpx;margin-top:30rpx;overflow:hidden;border-radius:8rpx;background:rgba(255,255,255,.15)}.level-bar view{height:100%;border-radius:8rpx;background:linear-gradient(90deg,#c99457,#f0d7b2)}.level-copy{display:block;margin-top:10rpx;text-align:right;font-size:18rpx;color:rgba(255,255,255,.55)}.quick-panel{display:flex;flex-wrap:wrap;margin:-38rpx 28rpx 0;padding:24rpx 8rpx;position:relative}.quick-item{position:relative;width:25%;text-align:center;font-size:20rpx;color:var(--muted)}.quick-item.divider::after{content:'';position:absolute;right:0;top:10rpx;bottom:10rpx;width:1rpx;background:var(--line)}.quick-item text{display:block}.quick-number{margin-bottom:8rpx;color:var(--brand-900);font-size:31rpx;font-weight:800}.active-order{display:flex;align-items:center;padding:23rpx}.active-symbol{width:64rpx;height:64rpx;margin-right:16rpx;display:flex;align-items:center;justify-content:center;border-radius:18rpx;background:#e4eee4;color:var(--green);font-size:19rpx;font-weight:700}.active-main{flex:1}.active-main text{display:block}.active-main-title{font-size:25rpx;font-weight:700}.active-main-sub{margin-top:6rpx;color:var(--muted);font-size:20rpx}.arrow{color:var(--brand-600);font-size:38rpx}.services{display:flex;flex-wrap:wrap;padding:8rpx 24rpx}.service-item{display:flex;flex-direction:column;align-items:flex-start;width:50%;padding:24rpx 10rpx;border-bottom:1rpx solid var(--line);color:var(--ink)}.service-item.no-border{border-bottom:0}.service-name{font-size:24rpx;font-weight:700;margin-bottom:7rpx}.service-desc{color:var(--muted);font-size:18rpx}.favorite-list{display:flex;flex-direction:column}.empty-favorite{padding:40rpx;text-align:center;color:var(--muted);font-size:22rpx}.footer-mark{padding:62rpx 20rpx 20rpx;text-align:center;color:#b3a89f;font-size:18rpx}
.profile-hero{background:linear-gradient(145deg,#0637c9,#071a62)}.avatar{background:#edcf91;color:#10266f}.active-symbol{background:var(--brand-soft);color:var(--brand)}
.account-actions{display:flex;flex-direction:column;margin-top:8rpx}.merchant-entry,.logout-entry{display:flex;align-items:center;justify-content:center;height:86rpx;border-radius:20rpx;font-size:26rpx;font-weight:700}.merchant-entry{background:var(--brand);color:#fff;margin-bottom:16rpx}.logout-entry{border:1rpx solid #d6aaa3;color:var(--danger);background:#fff}.login-arrow{font-size:40rpx}
.service-grid{display:flex;padding:22rpx 6rpx}.service-cell{display:flex;flex-direction:column;align-items:center;width:33.33%;padding:4rpx 10rpx}.service-icon{display:flex;align-items:center;justify-content:center;width:62rpx;height:62rpx;margin-bottom:12rpx;border-radius:18rpx;color:#fff;font-size:23rpx;font-weight:800}.service-icon.calorie{background:linear-gradient(145deg,#2f74ff,#0637c9)}.service-icon.checkin{background:linear-gradient(145deg,#f2761f,#d1490b)}.service-icon.service{background:linear-gradient(145deg,#5a6b8c,#33405a)}.service-name{font-size:22rpx;font-weight:700;color:var(--ink)}.service-desc{margin-top:5rpx;color:var(--muted);font-size:17rpx;text-align:center}
</style>
