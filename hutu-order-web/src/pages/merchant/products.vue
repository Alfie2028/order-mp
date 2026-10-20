<script setup>
import { computed, ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { useAppStore } from '@/store/app'
import { formatMoney } from '@/utils/format'

const store = useAppStore()
const filterStall = ref('')

const products = computed(() => store.state.merchantProducts || [])
const stalls = computed(() => store.state.merchantStalls || [])
const filtered = computed(() => {
  if (!filterStall.value) return products.value
  return products.value.filter((p) => p.stallId === filterStall.value)
})
function stallName(id) { const s = stalls.value.find((x) => x.id === id); return s ? s.name : '未分档口' }

function load() {
  store.loadMerchantStalls().catch(() => {})
  store.loadMerchantProducts().catch(() => {})
}

onShow(() => {
  if (!store.state.user || store.state.user.role !== 'merchant') { uni.redirectTo({ url: '/pages/login/index' }); return }
  load()
})

function add() { uni.navigateTo({ url: '/pages/merchant/product-edit' }) }
function edit(id) { uni.navigateTo({ url: '/pages/merchant/product-edit?id=' + id }) }
async function toggle(p) {
  await store.toggleProduct(p.id)
  uni.showToast({ title: p.isActive ? '已下架' : '已上架', icon: 'none' })
  store.loadMerchantProducts().catch(() => {})
}
function remove(p) {
  uni.showModal({
    title: '删除餐品',
    content: `确定删除「${p.name}」？历史订单不受影响。`,
    success: async (res) => {
      if (!res.confirm) return
      await store.deleteProduct(p.id)
      uni.showToast({ title: '已删除', icon: 'success' })
      store.loadMerchantProducts().catch(() => {})
    },
  })
}
function back() { uni.navigateBack() }
</script>

<template>
  <view class="page-shell merchant-sub">
    <view class="sub-header">
      <button class="top-back" @click="back">‹</button>
      <text class="title">餐品管理</text>
      <text class="subtitle">上新品、下架、改价、编辑配料</text>
    </view>

    <scroll-view scroll-x class="filter">
      <view class="filter-inner">
        <button :class="{ active: filterStall === '' }" @click="filterStall = ''">全部</button>
        <button v-for="s in stalls" :key="s.id" :class="{ active: filterStall === s.id }" @click="filterStall = s.id">{{ s.name }}</button>
      </view>
    </scroll-view>

    <view class="list">
      <view v-for="p in filtered" :key="p.id" class="product-card card" :class="{ off: !p.isActive }">
        <image class="thumb" :src="store.resolveImage(p.image || '/uploads/catalog/product/product-lemon-tea.png')" mode="aspectFill" />
        <view class="info">
          <view class="name-row"><text class="name">{{ p.name }}</text><text class="tag" :class="{ off: !p.isActive }">{{ p.isActive ? '在售' : '已下架' }}</text></view>
          <text class="subtitle">{{ p.subtitle }}</text>
          <text class="meta">{{ stallName(p.stallId) }} · 已售 {{ p.sales }}</text>
          <view class="price-row">
            <text class="price">{{ formatMoney(p.priceCents) }}</text>
            <text v-if="p.originalPriceCents" class="orig">{{ formatMoney(p.originalPriceCents) }}</text>
          </view>
        </view>
        <view class="actions">
          <button class="act" @click="edit(p.id)">编辑</button>
          <button class="act" :class="{ warn: p.isActive }" @click="toggle(p)">{{ p.isActive ? '下架' : '上架' }}</button>
          <button class="act danger" @click="remove(p)">删除</button>
        </view>
      </view>
    </view>

    <view class="fab" hover-class="hover-dim" @click="add">＋ 新增餐品</view>
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
.filter { white-space: nowrap; background: #fff; border-bottom: 1rpx solid var(--line); }
.filter-inner { display: flex; padding: 16rpx 24rpx; }
.filter button { display: flex; align-items: center; justify-content: center; min-width: 108rpx; height: 56rpx; margin-right: 10rpx; padding: 0 18rpx; border-radius: 28rpx; background: var(--oat-100); color: var(--muted); font-size: 22rpx; }
.filter button.active { background: var(--brand-800); color: #fff; font-weight: 700; }
.list { padding: 22rpx 28rpx; }
.product-card { display: flex; margin-bottom: 18rpx; padding: 20rpx; }
.product-card.off { opacity: .55; }
.thumb { width: 148rpx; height: 148rpx; margin-right: 18rpx; border-radius: 16rpx; background: var(--oat-100); flex-shrink: 0; }
.info { flex: 1; min-width: 0; margin-right: 18rpx; }
.name-row { display: flex; align-items: center; }
.name { margin-right: 10rpx; font-size: 27rpx; font-weight: 700; }
.tag { padding: 3rpx 12rpx; border-radius: 10rpx; background: #e3eee4; color: var(--green); font-size: 19rpx; }
.tag.off { background: #eee9e4; color: var(--muted); }
.subtitle { display: block; margin-top: 6rpx; font-size: 20rpx; color: var(--muted); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.meta { display: block; margin-top: 8rpx; font-size: 19rpx; color: var(--muted); }
.price-row { display: flex; align-items: baseline; margin-top: 8rpx; }
.price { margin-right: 12rpx; color: var(--danger); font-size: 28rpx; font-weight: 800; }
.orig { font-size: 20rpx; color: var(--muted); text-decoration: line-through; }
.actions { display: flex; flex-direction: column; align-self: center; }
.act { display: flex; align-items: center; justify-content: center; min-width: 92rpx; height: 52rpx; margin-bottom: 10rpx; padding: 0 16rpx; border-radius: 26rpx; background: var(--oat-100); color: var(--brand-700); font-size: 21rpx; }
.act.warn { background: #f7ead7; color: #98642f; }
.act.danger { background: #fbe7e2; color: var(--danger); }
.fab { position: fixed; left: 50%; transform: translateX(-50%); bottom: calc(40rpx + env(safe-area-inset-bottom)); padding: 22rpx 60rpx; border-radius: 46rpx; background: linear-gradient(135deg, var(--brand), var(--brand-dark)); color: #fff; font-size: 28rpx; font-weight: 700; box-shadow: 0 12rpx 26rpx rgba(6,55,201,.3); }
</style>
