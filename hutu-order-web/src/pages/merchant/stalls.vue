<script setup>
import { computed, reactive, ref } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { useAppStore } from '@/store/app'

const store = useAppStore()
const stalls = computed(() => store.state.merchantStalls || [])
const editing = ref(false)
const form = reactive({ id: '', name: '', shortName: '', description: '' })

function load() { store.loadMerchantStalls().catch(() => {}) }
onShow(() => {
  if (!store.state.user || store.state.user.role !== 'merchant') { uni.redirectTo({ url: '/pages/login/index' }); return }
  load()
})

function add() { form.id = ''; form.name = ''; form.shortName = ''; form.description = ''; editing.value = true }
function edit(s) { form.id = s.id; form.name = s.name; form.shortName = s.shortName; form.description = s.description; editing.value = true }
function cancel() { editing.value = false }
async function save() {
  if (!form.name.trim()) { uni.showToast({ title: '请填写档口名称', icon: 'none' }); return }
  await store.saveStall({ id: form.id, name: form.name.trim(), shortName: form.shortName.trim(), description: form.description.trim() })
  editing.value = false
  uni.showToast({ title: '已保存', icon: 'success' })
  load()
}
async function toggle(s) {
  await store.toggleStall(s.id)
  uni.showToast({ title: s.isActive ? '已下架' : '已上架', icon: 'none' })
  load()
}
function back() { uni.navigateBack() }
</script>

<template>
  <view class="page-shell merchant-sub">
    <view class="sub-header">
      <button class="top-back" @click="back">‹</button>
      <text class="title">档口管理</text>
      <text class="subtitle">档口上架后，用户端点单页可见</text>
    </view>

    <view class="list">
      <view v-for="s in stalls" :key="s.id" class="stall-card card" :class="{ off: !s.isActive }">
        <view class="head">
          <text class="name">{{ s.name }}</text>
          <text class="tag" :class="{ off: !s.isActive }">{{ s.isActive ? '营业中' : '已下架' }}</text>
        </view>
        <text class="desc">{{ s.description }}</text>
        <view class="actions">
          <button class="act" @click="edit(s)">编辑</button>
          <button class="act" :class="{ warn: s.isActive }" @click="toggle(s)">{{ s.isActive ? '下架' : '上架' }}</button>
        </view>
      </view>
    </view>

    <view class="fab" hover-class="hover-dim" @click="add">＋ 新增档口</view>

    <view v-if="editing" class="mask" @click="cancel">
      <view class="sheet card" @click.stop>
        <text class="sheet-title">{{ form.id ? '编辑档口' : '新增档口' }}</text>
        <view class="sheet-field"><text>名称</text><input v-model="form.name" placeholder="档口名称" maxlength="20" /></view>
        <view class="sheet-field"><text>简称</text><input v-model="form.shortName" placeholder="如 盖饭" maxlength="10" /></view>
        <view class="sheet-field"><text>描述</text><input v-model="form.description" placeholder="如 现点现炒，荤素搭配" maxlength="40" /></view>
        <view class="sheet-actions">
          <button class="sheet-btn" @click="cancel">取消</button>
          <button class="sheet-btn primary last" @click="save">保存</button>
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
.stall-card { margin-bottom: 18rpx; padding: 24rpx; }
.stall-card.off { opacity: .55; }
.head { display: flex; align-items: center; }
.name { flex: 1; margin-right: 14rpx; font-size: 28rpx; font-weight: 700; }
.tag { padding: 4rpx 14rpx; border-radius: 12rpx; background: #e3eee4; color: var(--green); font-size: 20rpx; }
.tag.off { background: #eee9e4; color: var(--muted); }
.desc { display: block; margin-top: 14rpx; font-size: 21rpx; color: var(--muted); }
.actions { display: flex; justify-content: flex-end; margin-top: 18rpx; }
.act { display: flex; align-items: center; justify-content: center; min-width: 108rpx; height: 56rpx; margin-right: 12rpx; border-radius: 28rpx; background: var(--oat-100); color: var(--brand-700); font-size: 22rpx; }
.act.warn { background: #f7ead7; color: #98642f; }
.fab { position: fixed; left: 50%; transform: translateX(-50%); bottom: calc(40rpx + env(safe-area-inset-bottom)); padding: 22rpx 60rpx; border-radius: 46rpx; background: linear-gradient(135deg, var(--brand), var(--brand-dark)); color: #fff; font-size: 28rpx; font-weight: 700; box-shadow: 0 12rpx 26rpx rgba(6,55,201,.3); }
.mask { position: fixed; left: 0; top: 0; right: 0; bottom: 0; background: rgba(0,0,0,.45); z-index: 50; display: flex; align-items: flex-end; }
.sheet { width: 100%; border-radius: 32rpx 32rpx 0 0; padding: 32rpx 30rpx calc(30rpx + env(safe-area-inset-bottom)); }
.sheet-title { display: block; font-size: 32rpx; font-weight: 800; margin-bottom: 10rpx; }
.sheet-field { display: flex; align-items: center; min-height: 92rpx; border-bottom: 1rpx solid var(--line); }
.sheet-field text { width: 110rpx; margin-right: 16rpx; font-size: 24rpx; font-weight: 600; }
.sheet-field input { flex: 1; font-size: 24rpx; }
.sheet-actions { display: flex; margin-top: 30rpx; }
.sheet-btn { display: flex; align-items: center; justify-content: center; flex: 1; height: 84rpx; margin-right: 20rpx; border-radius: 42rpx; background: var(--oat-100); color: var(--ink); font-size: 27rpx; font-weight: 700; }
.sheet-btn.last { margin-right: 0; }
.sheet-btn.primary { background: var(--brand); color: #fff; }
</style>
