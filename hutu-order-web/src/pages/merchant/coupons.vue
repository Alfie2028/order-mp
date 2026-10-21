<script setup>
import { computed, reactive, ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { useAppStore } from '@/store/app'

const store = useAppStore()
const yuan = (cents) => (cents / 100).toFixed(2).replace(/\.?0+$/, '')
const coupons = computed(() => store.state.merchantCoupons || [])
const editing = ref(false)
const form = reactive({ name: '', thresholdYuan: '', discountYuan: '', expires: '' })

function load() { store.loadMerchantCoupons().catch(() => {}) }
onShow(() => {
  if (!store.state.user || store.state.user.role !== 'merchant') { uni.redirectTo({ url: '/pages/login/index' }); return }
  load()
})

function add() { form.name = ''; form.thresholdYuan = ''; form.discountYuan = ''; form.expires = ''; editing.value = true }
function cancel() { editing.value = false }
async function save() {
  if (!form.name.trim()) { uni.showToast({ title: '请填写券名', icon: 'none' }); return }
  const discount = Math.round(Number(form.discountYuan) * 100)
  if (!discount || discount <= 0) { uni.showToast({ title: '请填写优惠金额', icon: 'none' }); return }
  await store.saveCoupon({
    name: form.name.trim(),
    thresholdCents: form.thresholdYuan ? Math.round(Number(form.thresholdYuan) * 100) : 0,
    discountCents: discount,
    expires: form.expires.trim(),
  })
  editing.value = false
  uni.showToast({ title: '已创建', icon: 'success' })
  load()
}
async function toggle(c) {
  await store.toggleCoupon(c.id)
  uni.showToast({ title: c.isActive ? '已停用' : '已启用', icon: 'none' })
  load()
}
function back() {
  if (getCurrentPages().length > 1) uni.navigateBack({ fail: () => { uni.switchTab({ url: '/pages/home/index' }) } })
  else uni.switchTab({ url: '/pages/home/index' })
}
</script>

<template>
  <view class="page-shell merchant-sub">
    <view class="sub-header">
      <button class="top-back" @click="back">‹</button>
      <text class="title">优惠券管理</text>
      <text class="subtitle">满减券创建与停用，用户端下单可选</text>
    </view>

    <view class="list">
      <view v-for="c in coupons" :key="c.id" class="coupon-card card" :class="{ off: !c.isActive }">
        <view class="left">
          <text class="discount">¥{{ yuan(c.discountCents) }}</text>
          <text class="threshold">{{ c.thresholdCents > 0 ? `满 ¥${yuan(c.thresholdCents)} 可用` : '无门槛' }}</text>
        </view>
        <view class="mid">
          <text class="name">{{ c.name }}</text>
          <text class="expires">{{ c.expires ? `有效期至 ${c.expires}` : '长期有效' }}</text>
        </view>
        <view class="right">
          <button class="act" :class="{ warn: c.isActive }" @click="toggle(c)">{{ c.isActive ? '停用' : '启用' }}</button>
        </view>
      </view>
    </view>

    <view class="fab" hover-class="hover-dim" @click="add">＋ 新增优惠券</view>

    <view v-if="editing" class="mask" @click="cancel">
      <view class="sheet card" @click.stop>
        <text class="sheet-title">新增优惠券</text>
        <view class="sheet-field"><text>券名</text><input v-model="form.name" placeholder="如 满30减5" maxlength="20" /></view>
        <view class="sheet-field"><text>门槛(元)</text><input v-model="form.thresholdYuan" type="digit" placeholder="0 表示无门槛" /></view>
        <view class="sheet-field"><text>优惠(元)</text><input v-model="form.discountYuan" type="digit" placeholder="如 5" /></view>
        <view class="sheet-field"><text>有效期</text><input v-model="form.expires" placeholder="如 2026-12-31" maxlength="10" /></view>
        <view class="sheet-actions">
          <button class="sheet-btn" @click="cancel">取消</button>
          <button class="sheet-btn primary last" @click="save">创建</button>
        </view>
      </view>
    </view>
  </view>
</template>

<style scoped lang="scss">
.merchant-sub { padding-bottom: 140rpx; }
.sub-header { padding: calc(70rpx + env(safe-area-inset-top)) 30rpx 36rpx; background: linear-gradient(145deg, #0637c9, #071a62); color: #fff; }
.top-back { position: absolute; left: 26rpx; top: calc(24rpx + env(safe-area-inset-top)); width: 62rpx; height: 62rpx; display: flex; align-items: center; justify-content: center; border-radius: 50%; background: rgba(255,255,255,.12); color: #fff; font-size: 46rpx; line-height: 1; }
.eyebrow, .title, .subtitle { display: block; }
.eyebrow { font-size: 17rpx; letter-spacing: 5rpx; color: #edcf91; }
.title { margin-top: 12rpx; font-size: 42rpx; font-weight: 800; }
.subtitle { margin-top: 8rpx; font-size: 21rpx; color: rgba(255,255,255,.65); }
.list { padding: 24rpx 28rpx; }
.coupon-card { display: flex; align-items: center; margin-bottom: 18rpx; padding: 24rpx; }
.coupon-card.off { opacity: .55; }
.left { width: 180rpx; flex-shrink: 0; margin-right: 20rpx; border-right: 1rpx dashed var(--line); }
.discount { display: block; color: var(--danger); font-size: 40rpx; font-weight: 800; }
.threshold { display: block; margin-top: 4rpx; font-size: 19rpx; color: var(--muted); }
.mid { flex: 1; min-width: 0; margin-right: 20rpx; }
.name { display: block; font-size: 27rpx; font-weight: 700; }
.expires { display: block; margin-top: 8rpx; font-size: 19rpx; color: var(--muted); }
.right { display: flex; flex-direction: column; align-items: flex-end; }
.act { display: flex; align-items: center; justify-content: center; min-width: 92rpx; height: 52rpx; border-radius: 26rpx; background: var(--oat-100); color: var(--brand-700); font-size: 21rpx; }
.act.warn { background: #f7ead7; color: #98642f; }
.fab { position: fixed; left: 50%; transform: translateX(-50%); bottom: calc(40rpx + env(safe-area-inset-bottom)); padding: 22rpx 60rpx; border-radius: 46rpx; background: linear-gradient(135deg, var(--brand), var(--brand-dark)); color: #fff; font-size: 28rpx; font-weight: 700; box-shadow: 0 12rpx 26rpx rgba(6,55,201,.3); }
.mask { position: fixed; left: 0; top: 0; right: 0; bottom: 0; background: rgba(0,0,0,.45); z-index: 50; display: flex; align-items: flex-end; }
.sheet { width: 100%; border-radius: 32rpx 32rpx 0 0; padding: 32rpx 30rpx calc(30rpx + env(safe-area-inset-bottom)); }
.sheet-title { display: block; font-size: 32rpx; font-weight: 800; margin-bottom: 10rpx; }
.sheet-field { display: flex; align-items: center; min-height: 92rpx; border-bottom: 1rpx solid var(--line); }
.sheet-field text { width: 130rpx; margin-right: 16rpx; font-size: 24rpx; font-weight: 600; }
.sheet-field input { flex: 1; font-size: 24rpx; }
.sheet-actions { display: flex; margin-top: 30rpx; }
.sheet-btn { display: flex; align-items: center; justify-content: center; flex: 1; height: 84rpx; margin-right: 20rpx; border-radius: 42rpx; background: var(--oat-100); color: var(--ink); font-size: 27rpx; font-weight: 700; }
.sheet-btn.last { margin-right: 0; }
.sheet-btn.primary { background: var(--brand); color: #fff; }
</style>
