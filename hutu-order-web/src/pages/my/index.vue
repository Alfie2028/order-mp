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

function openCalorie() {
  if (!user.value) return goLogin()
  const done = (store.state.orders || []).filter((o) => o.status === 'completed')
  const kcal = done.length * 480
  uni.showModal({
    title: '今日热量估算',
    content: `已完成订单 ${done.length} 单，估算摄入约 ${kcal} kcal。\n数据按每单 480 kcal 折算，仅作本地估算，不作为营养建议。`,
    showCancel: false,
    confirmText: '知道了',
    confirmColor: '#222426',
  })
}

function doCheckin() {
  if (!user.value) return goLogin()
  const today = todayKey()
  if (uni.getStorageSync(CHECKIN_STORAGE) === today) {
    uni.showModal({ title: '今天已签到', content: `已连续签到，当前积分 ${user.value.points}。明天记得再来。`, showCancel: false, confirmText: '去看看券', confirmColor: '#222426', success: showMyCoupons })
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
    confirmColor: '#222426',
    success: showMyCoupons,
  })
}

function showMyCoupons() {
  store.loadMyCoupons().catch(() => {}).then(() => {
    const list = availableCoupons.value
    if (!list.length) {
      uni.showModal({
        title: '还没有可用券',
        content: '去首页「吃货券」卡片领一张，满 30 减 5。',
        showCancel: false,
        confirmText: '去领券',
        confirmColor: '#222426',
        success: () => uni.switchTab({ url: '/pages/home/index' }),
      })
      return
    }
    const content = list.map((c) => `${c.name}（${c.discountCents / 100} 元${c.thresholdCents ? `，满 ${c.thresholdCents / 100} 元可用` : ''}，${c.expires} 到期）`).join('\n')
    uni.showModal({ title: `我的券 ${list.length} 张`, content, showCancel: false, confirmText: '知道了', confirmColor: '#222426' })
  })
}

const SERVICE_PHONE = '4008001234'
const SERVICE_PHONE_TEXT = '400-800-1234'
const SERVICE_HOURS = '07:30–21:30'
function openService() {
  uni.showModal({
    title: '美团校园客服中心',
    content: `客服热线 ${SERVICE_PHONE_TEXT}\n受理时间 ${SERVICE_HOURS}（节假日正常）\n出餐、取餐码、退款等问题均可来电咨询。`,
    confirmText: '拨打',
    cancelText: '暂不',
    confirmColor: '#222426',
    success: ({ confirm }) => {
      if (!confirm) return
      uni.makePhoneCall({
        phoneNumber: SERVICE_PHONE,
        fail: (err) => {
          console.log('[客服] 拨号未完成:', err)
          uni.showToast({ title: '已取消拨号', icon: 'none' })
        },
      })
    },
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
  uni.showModal({ title: '退出登录', content: '确定要退出当前账号吗？', confirmColor: '#FF4B3E', success: ({ confirm }) => {
    if (!confirm) return
    store.logout()
    uni.showToast({ title: '已退出登录', icon: 'success' })
  } })
}
</script>

<template>
  <view class="page-shell my-page">
    <!-- 美团经典黄色顶部个人中心 (Meituan Classic Yellow Profile Hero) -->
    <view class="profile-hero">
      <view class="brand-line">
        <view class="header-logo-badge">
          <image class="header-kangaroo" src="/static/image/kangaroo.png" mode="aspectFit" />
          <text>美团会员</text>
        </view>
        <button class="setting-btn" @click="uni.navigateTo({ url: '/pages/setting/index' })">设置</button>
      </view>

      <view v-if="user" class="profile-row">
        <view class="avatar" @click="chooseAvatar">
          <image v-if="isCustomAvatar" class="avatar-img" :src="user.avatar" mode="aspectFill" />
          <image v-else class="avatar-img" src="/static/image/kangaroo.png" mode="aspectFit" />
          <view class="avatar-edit-badge">
            <view class="pencil-ico" />
          </view>
        </view>
        <view class="profile-main">
          <text class="user-name">{{ user.name }}</text>
          <view class="vip-tag">
            <text class="vip-star">★</text>
            <text>{{ user.title }} · LV.{{ user.level }}</text>
          </view>
        </view>
        <view class="points">
          <text class="points-value">{{ user.points }}</text>
          <text class="points-label">吃货积分</text>
        </view>
      </view>

      <view v-else class="profile-row" @click="goLogin">
        <view class="avatar">
          <image class="avatar-img" src="/static/image/kangaroo.png" mode="aspectFit" />
        </view>
        <view class="profile-main">
          <text class="user-name">点击登录 / 注册</text>
          <text class="user-title">登录后同步订单、优惠券与收藏</text>
        </view>
        <view class="points">
          <text class="login-arrow">›</text>
          <text class="points-label">去登录</text>
        </view>
      </view>

      <template v-if="user">
        <view class="level-bar">
          <view class="level-fill" :style="{ width: `${levelProgress}%` }" />
        </view>
        <text class="level-copy">距离下一等级还需 {{ Math.max(0, user.nextLevelPoints - user.points) }} 积分</text>
      </template>
    </view>

    <!-- 快捷数据金刚卡 (Quick Panel Card) -->
    <view class="quick-panel card">
      <view class="quick-item divider" @click="uni.navigateTo({ url: '/pages/my-order/index' })">
        <text class="quick-number">{{ store.state.orders.length }}</text>
        <text class="quick-text">全部订单</text>
      </view>
      <view class="quick-item divider" @click="showFeature('优惠券可在提交订单时选择')">
        <text class="quick-number">{{ availableCoupons.length }}</text>
        <text class="quick-text">美团神券</text>
      </view>
      <view class="quick-item divider" @click="showFeature('收藏餐品可在本页下方查看')">
        <text class="quick-number">{{ favorites.length }}</text>
        <text class="quick-text">常点收藏</text>
      </view>
      <view class="quick-item" @click="showFeature('会员等级信息已展示在页面顶部')">
        <text class="quick-number">{{ store.state.user ? store.state.user.level : 0 }}</text>
        <text class="quick-text">会员成长</text>
      </view>
    </view>

    <!-- 进行中的订单 -->
    <view v-if="activeOrder" class="section">
      <view class="section-heading">
        <text class="section-title">进行中的订单</text>
        <text class="section-link" @click="uni.navigateTo({ url: '/pages/my-order/index' })">查看全部 ›</text>
      </view>
      <view class="active-order card" @click="uni.navigateTo({ url: `/pages/settled/index?id=${activeOrder.id}` })">
        <view class="active-symbol">{{ activeOrder.status === 'ready' ? '待取' : '制作' }}</view>
        <view class="active-main">
          <text class="active-main-title">{{ activeOrder.statusText }} · 取餐码 {{ activeOrder.pickupCode }}</text>
          <text class="active-main-sub">{{ activeOrder.storeName }} · 预计准时送达</text>
        </view>
        <text class="arrow">›</text>
      </view>
    </view>

    <!-- 吃货专享服务 (Meituan Style Exclusive Services) -->
    <view class="section">
      <view class="section-heading">
        <text class="section-title">吃货专享服务</text>
        <text class="section-link" @click="uni.switchTab({ url: '/pages/shop/index' })">门店地图 ›</text>
      </view>
      <view class="service-grid card">
        <view class="service-cell" @click="openCalorie">
          <view class="service-icon calorie">
            <view class="service-glyph flame-glyph" />
          </view>
          <text class="service-name">热量管家</text>
          <text class="service-desc">按订单估算摄入</text>
        </view>
        <view class="service-cell" @click="doCheckin">
          <view class="service-icon checkin">
            <view class="service-glyph gift-glyph" />
          </view>
          <text class="service-name">签到领神券</text>
          <text class="service-desc">{{ user ? '每日签到 +20积分' : '登录后签到' }}</text>
        </view>
        <view class="service-cell" @click="openService">
          <view class="service-icon service">
            <view class="service-glyph phone-glyph" />
          </view>
          <text class="service-name">在线客服</text>
          <text class="service-desc">{{ SERVICE_PHONE_TEXT }}</text>
        </view>
      </view>
    </view>

    <!-- 我的常点 (Favorites) -->
    <view class="section favorite-section">
      <view class="section-heading">
        <text class="section-title">我的常点</text>
        <text class="section-link">{{ favorites.length }} 款收藏</text>
      </view>
      <view v-if="favorites.length" class="favorite-list">
        <ProductCard v-for="product in favorites" :key="product.id" :product="product" @open="openProduct" @add="quickAdd" />
      </view>
      <view v-else class="empty-favorite card">暂无收藏餐品，在餐品详情中点击红心可添加到这里。</view>
    </view>

    <!-- 商家工作台与退出登录 -->
    <view v-if="user" class="section account-actions">
      <button v-if="user.role === 'merchant'" class="merchant-entry" @click="goMerchant">进入商家工作台</button>
      <button class="logout-entry" @click="logout">退出登录</button>
    </view>

    <view class="footer-mark">美团校园点餐 · 随时随地准时达</view>
  </view>
</template>

<style scoped lang="scss">
.my-page {
  padding-bottom: 60rpx;
  background: #F7F8FA;
}

/* ---- 顶部美团黄个人信息区 ---- */
.profile-hero {
  padding: calc(48rpx + env(safe-area-inset-top)) 30rpx 70rpx;
  color: #222426;
  background: linear-gradient(135deg, #FFD21E 0%, #FFC300 60%, #FFAE00 100%);
  position: relative;
}
.brand-line {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.header-logo-badge {
  display: flex;
  align-items: center;
  padding: 4rpx 14rpx 4rpx 8rpx;
  border-radius: 20rpx;
  background: rgba(0, 0, 0, .08);
  font-size: 20rpx;
  font-weight: 800;
  color: #222426;
}
.header-kangaroo {
  width: 32rpx;
  height: 32rpx;
  margin-right: 8rpx;
}
.setting-btn {
  width: auto;
  height: 52rpx;
  padding: 0 22rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1rpx solid rgba(0, 0, 0, .15);
  border-radius: 26rpx;
  background: rgba(255, 255, 255, .35);
  color: #222426;
  font-size: 20rpx;
  font-weight: 700;
}

.profile-row {
  display: flex;
  align-items: center;
  margin-top: 30rpx;
}
.avatar {
  width: 110rpx;
  height: 110rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  border: 4rpx solid #fff;
  border-radius: 50%;
  background: #fff;
  box-shadow: 0 6rpx 16rpx rgba(0, 0, 0, .1);
}
.avatar-img {
  width: 100%;
  height: 100%;
  border-radius: 50%;
}
.avatar-edit-badge {
  position: absolute;
  right: -4rpx;
  bottom: -4rpx;
  width: 36rpx;
  height: 36rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: #222426;
  border: 2rpx solid #fff;
}
.pencil-ico {
  width: 14rpx;
  height: 14rpx;
  border: 2rpx solid #FFC300;
  transform: rotate(45deg);
}

.profile-main {
  flex: 1;
  margin-left: 22rpx;
}
.user-name {
  font-size: 38rpx;
  font-weight: 900;
  color: #222426;
  display: block;
}
.user-title {
  margin-top: 6rpx;
  color: rgba(34, 36, 38, .75);
  font-size: 21rpx;
  display: block;
}
.vip-tag {
  display: inline-flex;
  align-items: center;
  margin-top: 8rpx;
  padding: 4rpx 14rpx;
  border-radius: 18rpx;
  background: #222426;
  color: #FFC300;
  font-size: 19rpx;
  font-weight: 800;
}
.vip-star {
  color: #FFC300;
  font-size: 20rpx;
  margin-right: 6rpx;
}

.points { text-align: right; }
.points-value { font-size: 40rpx; font-weight: 900; color: #222426; display: block; }
.points-label { margin-top: 4rpx; font-size: 20rpx; color: rgba(34, 36, 38, .75); font-weight: 600; display: block; }
.login-arrow { font-size: 44rpx; color: #222426; font-weight: 900; line-height: 1; display: block; }

.level-bar {
  height: 8rpx;
  margin-top: 26rpx;
  overflow: hidden;
  border-radius: 4rpx;
  background: rgba(0, 0, 0, .1);
}
.level-fill {
  height: 100%;
  border-radius: 4rpx;
  background: #222426;
}
.level-copy {
  display: block;
  margin-top: 8rpx;
  text-align: right;
  font-size: 18rpx;
  color: rgba(34, 36, 38, .75);
  font-weight: 600;
}

/* ---- 快捷卡片 ---- */
.quick-panel {
  display: flex;
  flex-wrap: wrap;
  margin: -36rpx 24rpx 0;
  padding: 24rpx 6rpx;
  position: relative;
  z-index: 5;
}
.quick-item {
  position: relative;
  width: 25%;
  text-align: center;
}
.quick-item.divider::after {
  content: '';
  position: absolute;
  right: 0;
  top: 12rpx;
  bottom: 12rpx;
  width: 1rpx;
  background: #EBECEF;
}
.quick-number {
  display: block;
  margin-bottom: 6rpx;
  color: #222426;
  font-size: 34rpx;
  font-weight: 900;
}
.quick-text {
  font-size: 21rpx;
  color: #666666;
  font-weight: 600;
}

/* ---- 进行中的订单 ---- */
.active-order {
  display: flex;
  align-items: center;
  padding: 24rpx;
  border: 1rpx solid rgba(255, 195, 0, .3);
  background: #FFFDF7;
}
.active-symbol {
  width: 68rpx;
  height: 68rpx;
  margin-right: 18rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 20rpx;
  background: #FFC300;
  color: #222426;
  font-size: 21rpx;
  font-weight: 900;
}
.active-main { flex: 1; }
.active-main-title { font-size: 26rpx; font-weight: 900; color: #222426; display: block; }
.active-main-sub { margin-top: 6rpx; color: #8E929E; font-size: 20rpx; display: block; }
.arrow { color: #8E929E; font-size: 36rpx; }

/* ---- 吃货服务网格 ---- */
.service-grid {
  display: flex;
  padding: 24rpx 10rpx;
}
.service-cell {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 33.33%;
  padding: 6rpx 10rpx;
}
.service-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 72rpx;
  height: 72rpx;
  margin-bottom: 12rpx;
  border-radius: 24rpx;
}
.service-icon.calorie {
  background: linear-gradient(135deg, #FF7700, #FF5500);
}
.service-icon.checkin {
  background: linear-gradient(135deg, #FFC300, #FFAA00);
}
.service-icon.service {
  background: linear-gradient(135deg, #333333, #222222);
}

.service-glyph {
  position: relative;
}
.flame-glyph {
  width: 24rpx;
  height: 32rpx;
  background: #fff;
  border-radius: 50% 50% 30% 30%;
  transform: rotate(-10deg);
}
.gift-glyph {
  width: 28rpx;
  height: 28rpx;
  border: 4rpx solid #222426;
  border-radius: 6rpx;
  background: #FFC300;
}
.phone-glyph {
  width: 24rpx;
  height: 30rpx;
  border: 4rpx solid #fff;
  border-radius: 6rpx;
}

.service-name { font-size: 24rpx; font-weight: 800; color: #222426; }
.service-desc { margin-top: 6rpx; color: #8E929E; font-size: 18rpx; text-align: center; }

/* ---- 收藏列表 ---- */
.favorite-list { display: flex; flex-direction: column; }
.empty-favorite { padding: 44rpx; text-align: center; color: #8E929E; font-size: 22rpx; }

/* ---- 底部按钮 ---- */
.account-actions { display: flex; flex-direction: column; margin-top: 14rpx; }
.merchant-entry, .logout-entry {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 88rpx;
  border-radius: 44rpx;
  font-size: 27rpx;
  font-weight: 800;
}
.merchant-entry {
  background: #FFC300;
  color: #222426;
  margin-bottom: 18rpx;
  box-shadow: 0 6rpx 16rpx rgba(255, 195, 0, .35);
}
.logout-entry {
  border: 2rpx solid #FFCDD2;
  color: #FF4B3E;
  background: #fff;
}

.footer-mark {
  padding: 60rpx 20rpx 24rpx;
  text-align: center;
  color: #B5B8C0;
  font-size: 19rpx;
}
</style>
