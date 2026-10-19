<script setup>
import { computed, reactive, ref } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { useAppStore } from '@/store/app'
import { formatMoney } from '@/utils/format'

const store = useAppStore()
const productId = ref('')
const product = computed(() => store.state.products.find((item) => item.id === productId.value) || store.state.products[0])
const selected = reactive({})
const quantity = ref(1)
const imageFailed = ref(false)

onLoad((query) => {
  productId.value = query.id || store.state.products[0]?.id
  const current = product.value
  if (current) current.options.forEach((group) => { selected[group.id] = group.multiple ? [] : group.options[0]?.id })
})

const favorite = computed(() => store.state.favoriteIds.includes(product.value.id))
const selectedOptions = computed(() => product.value.options.reduce((acc, group) => {
  const ids = Array.isArray(selected[group.id]) ? selected[group.id] : [selected[group.id]]
  return acc.concat(group.options.filter((option) => ids.includes(option.id)).map((option) => ({ ...option, groupName: group.name })))
}, []))
const unitPrice = computed(() => product.value.priceCents + selectedOptions.value.reduce((sum, option) => sum + option.extraCents, 0))
const totalPrice = computed(() => unitPrice.value * quantity.value)

function choose(group, optionId) {
  if (!group.multiple) {
    selected[group.id] = optionId
    return
  }
  const values = selected[group.id]
  selected[group.id] = values.includes(optionId) ? values.filter((id) => id !== optionId) : [...values, optionId]
}

function isSelected(groupId, optionId) {
  const value = selected[groupId]
  return Array.isArray(value) ? value.includes(optionId) : value === optionId
}

function add(goCheckout = false) {
  if (!product.value.isActive) { uni.showToast({ title: '该商品已售罄', icon: 'none' }); return }
  store.addToCart(product.value.id, selectedOptions.value, quantity.value)
  uni.showToast({ title: '已加入购物车', icon: 'success' })
  if (goCheckout) setTimeout(() => uni.navigateTo({ url: '/pages/confirm-order/index' }), 250)
}
</script>

<template>
  <view class="page-shell detail-page">
    <view class="visual">
      <image v-if="!imageFailed" class="visual-image" :src="product.image" mode="aspectFit" @error="imageFailed = true" />
      <text v-else class="visual-fallback">{{ product.fallback }}</text>
      <button class="back-button" @click="uni.navigateBack()">‹</button>
      <button class="favorite-button" :class="{ active: favorite }" @click="store.toggleFavorite(product.id)">{{ favorite ? '♥' : '♡' }}</button>
      <view class="visual-glow" />
    </view>

    <view class="content">
      <view class="headline">
        <view class="headline-main">
          <text class="badge">{{ product.badge }}</text>
          <text class="title">{{ product.name }}</text>
          <text class="subtitle">{{ product.subtitle }}</text>
        </view>
        <view class="price-block">
          <text class="price">{{ formatMoney(unitPrice) }}</text>
          <text class="sales">{{ product.stallName }}</text>
        </view>
      </view>

      <view v-if="product.options.length" class="option-card card">
        <view v-for="(group, index) in product.options" :key="group.id" class="option-group" :class="{ last: index === product.options.length - 1 }">
          <view class="option-heading">
            <text class="option-title">{{ group.name }}</text>
            <text class="option-tip">{{ group.multiple ? '可多选' : '单选' }}</text>
          </view>
          <view class="option-grid">
            <button v-for="option in group.options" :key="option.id" class="option" :class="{ selected: isSelected(group.id, option.id) }" @click="choose(group, option.id)">
              <text>{{ option.name }}</text>
              <text v-if="option.extraCents" class="option-extra">+{{ formatMoney(option.extraCents) }}</text>
            </button>
          </view>
        </view>
      </view>

      <view class="notice card"><view><text class="notice-title">档口现制</text><text class="notice-copy">餐品将在下单后开始制作，请按预计出餐时间到餐厅取餐。</text></view></view>
    </view>

    <view class="action-bar">
      <view class="stepper">
        <button @click="quantity = Math.max(1, quantity - 1)">−</button><text>{{ quantity }}</text><button @click="quantity += 1">＋</button>
      </view>
      <button class="secondary-action" @click="add(false)">加入购物车</button>
      <button class="primary-action" @click="add(true)">去结算 · {{ formatMoney(totalPrice) }}</button>
    </view>
  </view>
</template>

<style scoped lang="scss">
.detail-page { padding-bottom: 170rpx; }
.visual { height:600rpx;position:relative;display:flex;align-items:center;justify-content:center;overflow:hidden;background:radial-gradient(circle at 50% 44%,#fff 0,#f0f4ff 52%,#d9e4ff 100%) }
.visual-image { width:88%;height:88%;position:relative;z-index:2 }
.visual-fallback { position: relative; z-index: 2; font-size: 230rpx; }
.visual-glow { position:absolute;width:380rpx;height:90rpx;bottom:58rpx;border-radius:50%;background:rgba(6,55,201,.12) }
.back-button,.favorite-button { position: fixed; top: calc(24rpx + env(safe-area-inset-top)); z-index: 4; width: 72rpx; height: 72rpx; border-radius: 50%; display: flex; align-items: center; justify-content: center; background: rgba(255,255,255,.9); color: var(--brand-900); box-shadow: 0 8rpx 24rpx rgba(53,35,27,.12); }
.back-button { left: 26rpx; font-size: 54rpx; line-height: 1; }
.favorite-button { right: 26rpx; font-size: 42rpx; }.favorite-button.active{color:var(--danger)}
.content { position: relative; z-index: 3; margin-top: -44rpx; padding: 36rpx 28rpx 0; border-radius: 40rpx 40rpx 0 0; background: var(--oat-50); }
.headline { display:flex; justify-content:space-between; }.headline-main{flex:1;min-width:0}
.badge { display:inline-block;margin-bottom:14rpx;padding:7rpx 14rpx;border-radius:7rpx;background:var(--brand);color:#fff;font-size:20rpx;font-weight:700 }
.title,.subtitle,.sales,.notice-title,.notice-copy { display:block; }.title{font-size:44rpx;font-weight:800;color:var(--brand-950)}.subtitle{margin-top:12rpx;color:#5a5f68;font-size:25rpx;line-height:1.6}
.price-block{text-align:right;padding-top:34rpx}.price{font-size:34rpx}.sales{margin-top:8rpx;font-size:20rpx;color:var(--muted)}
.option-card{margin-top:32rpx;padding:8rpx 26rpx}.option-group{padding:26rpx 0;border-bottom:1rpx solid var(--line)}.option-group.last{border-bottom:0}.option-heading{display:flex;align-items:center;justify-content:space-between;margin-bottom:18rpx}.option-title{font-weight:700;font-size:29rpx}.option-tip{font-size:21rpx;color:var(--muted)}
.option-grid{display:flex;flex-wrap:wrap;margin-right:-14rpx}.option{width:calc(50% - 14rpx);margin-right:14rpx;margin-bottom:14rpx;display:flex;align-items:center;justify-content:center;min-height:74rpx;padding:0 16rpx;border:1rpx solid var(--line);border-radius:16rpx;color:var(--ink);background:#fff;font-size:25rpx}.option.selected{border-color:var(--brand-700);background:var(--oat-100);color:var(--brand-800);font-weight:700}.option-extra{margin-left:6rpx;font-size:19rpx;color:var(--muted)}
.notice{display:flex;margin-top:22rpx;padding:24rpx;border-left:5rpx solid var(--caramel-500)}.notice-title{font-size:25rpx;font-weight:700}.notice-copy{margin-top:6rpx;font-size:22rpx;color:var(--muted);line-height:1.5}
.action-bar{position:fixed;left:0;right:0;bottom:0;z-index:20;display:flex;align-items:center;padding:18rpx 24rpx calc(18rpx + env(safe-area-inset-bottom));background:rgba(255,255,255,.96);box-shadow:0 -10rpx 30rpx rgba(53,35,27,.08)}
.stepper{display:flex;align-items:center;margin-right:12rpx}.stepper button{width:52rpx;height:52rpx;margin-right:8rpx;padding:0;display:flex;align-items:center;justify-content:center;border:1rpx solid var(--line);border-radius:50%;font-size:27rpx;line-height:1}.stepper text{min-width:28rpx;margin-right:8rpx;text-align:center;font-weight:700}.secondary-action,.primary-action{display:flex;align-items:center;justify-content:center;height:78rpx;padding:0 22rpx;border-radius:20rpx;font-size:24rpx;font-weight:700}.secondary-action{border:1rpx solid var(--brand);color:var(--brand);margin-right:12rpx}.primary-action{flex:1;background:var(--brand);color:white;white-space:nowrap}
@media screen and (min-width:760px){.action-bar{max-width:750px;margin:0 auto}}
</style>
