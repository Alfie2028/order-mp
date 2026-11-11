<script setup>
import { computed, ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { useAppStore } from '@/store/app'
import { formatMoney } from '@/utils/format'
import { getNavLayout } from '@/utils/nav'

const store = useAppStore()
const navLayout = getNavLayout()
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
function back() {
  if (getCurrentPages().length > 1) uni.navigateBack({ fail: () => { uni.switchTab({ url: '/pages/home/index' }) } })
  else uni.switchTab({ url: '/pages/home/index' })
}
</script>

<template>
  <view class="page-shell merchant-sub">
    <view class="sub-header" :style="{ paddingTop: (navLayout.capsuleTop + 44) + 'px' }">
      <button class="top-back" :style="{ top: navLayout.capsuleTop + 'px' }" @click="back">‹</button>
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

    <view class="fab" :style="{ bottom: (navLayout.bottomSafe ? (navLayout.bottomSafe + 20) + 'px' : '') }" hover-class="hover-dim" @click="add">＋ 新增餐品</view>
  </view>
</template>

<style scoped lang="scss">
.merchant-sub { padding-bottom: 140rpx; background: #F7F8FA; }
.sub-header { position: relative; padding: calc(64rpx + var(--status-bar-height, 0px) + env(safe-area-inset-top, 0px)) 30rpx 40rpx; background: linear-gradient(135deg, #FFD21E 0%, #FFC300 70%, #FFAE00 100%); color: #222426; }
.top-back { position: absolute; left: 26rpx; top: calc(24rpx + var(--status-bar-height, 0px) + env(safe-area-inset-top, 0px)); width: 62rpx; height: 62rpx; display: flex; align-items: center; justify-content: center; border-radius: 50%; background: rgba(0, 0, 0, .08); color: #222426; font-size: 46rpx; line-height: 1; }
.eyebrow, .title, .subtitle { display: block; }
.eyebrow { font-size: 17rpx; letter-spacing: 5rpx; color: #8C5E00; }
.title { margin-top: 12rpx; font-size: 42rpx; font-weight: 900; color: #222426; }
.subtitle { margin-top: 8rpx; font-size: 21rpx; color: rgba(34, 36, 38, .75); }
.filter { white-space: nowrap; background: #fff; border-bottom: 1rpx solid #F0F0F2; }
.filter-inner { display: flex; padding: 16rpx 24rpx; }
.filter button { display: flex; align-items: center; justify-content: center; min-width: 108rpx; height: 60rpx; margin-right: 12rpx; padding: 0 22rpx; border-radius: 30rpx; background: #F3F4F7; color: #8E929E; font-size: 22rpx; font-weight: 600; }
.filter button.active { background: #222426; color: #FFC300; font-weight: 800; }
.list { padding: 22rpx 24rpx; }
.product-card { display: flex; margin-bottom: 18rpx; padding: 20rpx; border-radius: 20rpx; }
.product-card.off { opacity: .55; }
.thumb { width: 148rpx; height: 148rpx; margin-right: 18rpx; border-radius: 16rpx; background: #F4F5F8; flex-shrink: 0; }
.info { flex: 1; min-width: 0; margin-right: 18rpx; }
.name-row { display: flex; align-items: center; }
.name { margin-right: 10rpx; font-size: 27rpx; font-weight: 800; color: #222426; }
.tag { padding: 3rpx 12rpx; border-radius: 10rpx; background: #E6F8EE; color: #07C160; font-size: 19rpx; font-weight: 700; }
.tag.off { background: #F3F4F7; color: #8E929E; }
.subtitle { display: block; margin-top: 6rpx; font-size: 20rpx; color: #8E929E; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.meta { display: block; margin-top: 8rpx; font-size: 19rpx; color: #B37D00; font-weight: 600; }
.price-row { display: flex; align-items: baseline; margin-top: 8rpx; }
.price { margin-right: 12rpx; color: #FF4B3E; font-size: 28rpx; font-weight: 900; }
.orig { font-size: 20rpx; color: #B5B8C0; text-decoration: line-through; }
.actions { display: flex; flex-direction: column; align-self: center; }
.act { display: flex; align-items: center; justify-content: center; min-width: 92rpx; height: 52rpx; margin-bottom: 10rpx; padding: 0 16rpx; border-radius: 26rpx; background: #FFF9E6; color: #8C5E00; font-size: 21rpx; font-weight: 700; }
.act.warn { background: #FFF0ED; color: #FF7700; }
.act.danger { background: #FFEBEE; color: #FF4B3E; }
.fab { position: fixed; left: 50%; transform: translateX(-50%); bottom: calc(40rpx + constant(safe-area-inset-bottom)); bottom: calc(40rpx + env(safe-area-inset-bottom)); padding: 22rpx 60rpx; border-radius: 46rpx; background: #FFC300; color: #222426; font-size: 28rpx; font-weight: 800; box-shadow: 0 8rpx 24rpx rgba(255, 195, 0, .45); }
</style>
