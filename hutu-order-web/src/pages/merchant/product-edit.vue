<script setup>
import { reactive, computed, ref } from 'vue'
import { onLoad } from '@dcloudio/uni-app'
import { useAppStore } from '@/store/app'

const store = useAppStore()
const stalls = computed(() => store.state.merchantStalls || [])

const form = reactive({
  id: '',
  stallId: '',
  name: '',
  subtitle: '',
  priceYuan: '',
  originalYuan: '',
  badge: '',
  image: '',
  options: [],
})

let uid = 0
const genId = (prefix) => `${prefix}${Date.now()}${uid++}`

function stallName(id) { const s = stalls.value.find((x) => x.id === id); return s ? s.name : '' }

onLoad((query) => {
  if (!store.state.user || store.state.user.role !== 'merchant') { uni.redirectTo({ url: '/pages/login/index' }); return }
  if (!stalls.value.length) store.loadMerchantStalls().catch(() => {})
  if (query && query.id) {
    const p = (store.state.merchantProducts || []).find((x) => x.id === query.id)
    if (p) {
      form.id = p.id
      form.stallId = p.stallId
      form.name = p.name
      form.subtitle = p.subtitle
      form.priceYuan = (p.priceCents / 100).toFixed(2)
      form.originalYuan = p.originalPriceCents ? (p.originalPriceCents / 100).toFixed(2) : ''
      form.badge = p.badge
      form.image = p.image
      form.options = (p.options || []).map((g) => ({
        id: g.id, name: g.name, required: !!g.required, multiple: !!g.multiple,
        options: (g.options || []).map((o) => ({ id: o.id, name: o.name, extraCents: o.extraCents ? String(o.extraCents / 100) : '' })),
      }))
    }
  }
})

function onStallChange(e) { form.stallId = stalls.value[e.detail.value].id }
function chooseImage() {
  store.uploadImage().then((url) => { form.image = url }).catch(() => {})
}

function addGroup() {
  form.options.push({ id: genId('g'), name: '规格组', required: false, multiple: false, options: [] })
}
function removeGroup(i) { form.options.splice(i, 1) }
function addOption(i) {
  form.options[i].options.push({ id: genId('o'), name: '', extraCents: 0 })
}
function removeOption(i, j) { form.options[i].options.splice(j, 1) }

async function save() {
  if (!form.stallId) { uni.showToast({ title: '请选择档口', icon: 'none' }); return }
  if (!form.name.trim()) { uni.showToast({ title: '请填写餐品名称', icon: 'none' }); return }
  if (!form.priceYuan || Number(form.priceYuan) <= 0) { uni.showToast({ title: '请填写价格', icon: 'none' }); return }
  const options = form.options.map((g) => ({
    id: g.id, name: g.name, required: !!g.required, multiple: !!g.multiple,
    options: g.options.map((o) => ({ id: o.id, name: o.name, extraCents: Math.round((Number(o.extraCents) || 0) * 100) })),
  }))
  uni.showLoading({ title: '保存中' })
  try {
    await store.saveProduct({
      id: form.id,
      stallId: form.stallId,
      name: form.name.trim(),
      subtitle: form.subtitle.trim(),
      priceCents: Math.round(Number(form.priceYuan) * 100),
      originalPriceCents: form.originalYuan ? Math.round(Number(form.originalYuan) * 100) : 0,
      badge: form.badge.trim(),
      image: form.image,
      options,
    })
    uni.hideLoading()
    uni.showToast({ title: '已保存', icon: 'success' })
    setTimeout(() => uni.navigateBack(), 400)
  } catch (e) {
    uni.hideLoading()
  }
}
function back() { uni.navigateBack() }
</script>

<template>
  <view class="page-shell merchant-sub">
    <view class="sub-header">
      <button class="top-back" @click="back">‹</button>
      <text class="title">{{ form.id ? '编辑餐品' : '新增餐品' }}</text>
      <text class="subtitle">填写基本信息与配料规格，图片可选相册/拍照</text>
    </view>

    <view class="form card">
      <view class="field">
        <text class="label">档口</text>
        <picker class="picker" :range="stalls" range-key="name" @change="onStallChange">
          <view class="picker-value" :class="{ empty: !form.stallId }">{{ stallName(form.stallId) || '请选择档口' }}<text class="arrow">›</text></view>
        </picker>
      </view>
      <view class="field">
        <text class="label">名称</text>
        <input v-model="form.name" placeholder="餐品名称" maxlength="30" />
      </view>
      <view class="field">
        <text class="label">描述</text>
        <input v-model="form.subtitle" placeholder="一句话描述，如「现点现炒」" maxlength="60" />
      </view>
      <view class="field-row">
        <view class="field">
          <text class="label">价格(元)</text>
          <input v-model="form.priceYuan" type="digit" placeholder="0.00" />
        </view>
        <view class="field second">
          <text class="label">原价(元)</text>
          <input v-model="form.originalYuan" type="digit" placeholder="选填" />
        </view>
      </view>
      <view class="field">
        <text class="label">徽标</text>
        <input v-model="form.badge" placeholder="如「招牌盖饭」" maxlength="20" />
      </view>
      <view class="field image-field last">
        <text class="label">图片</text>
        <view class="image-box">
          <image v-if="form.image" class="preview" :src="store.resolveImage(form.image)" mode="aspectFill" />
          <view v-else class="preview empty">暂无图片</view>
          <button class="upload-btn" @click="chooseImage">{{ form.image ? '更换' : '上传' }}</button>
        </view>
      </view>
    </view>

    <view class="options">
      <view class="options-head"><text class="op-title">配料 / 规格</text><button class="add-group" @click="addGroup">＋ 规格组</button></view>
      <text v-if="!form.options.length" class="op-hint">暂无规格组，例如「辣度」「份量」「加料」</text>

      <view v-for="(g, i) in form.options" :key="g.id" class="group card">
        <view class="group-head">
          <input v-model="g.name" class="group-name" placeholder="规格组名称，如 辣度" maxlength="20" />
          <button class="del" @click="removeGroup(i)">删除</button>
        </view>
        <view class="group-toggles">
          <button :class="{ on: g.required }" @click="g.required = !g.required">必选</button>
          <button :class="{ on: g.multiple }" @click="g.multiple = !g.multiple">多选</button>
        </view>
        <view v-for="(o, j) in g.options" :key="o.id" class="opt-row">
          <input v-model="o.name" class="opt-name" placeholder="选项名" maxlength="15" />
          <view class="opt-price"><text>+</text><input v-model="o.extraCents" type="digit" placeholder="0" /><text>元</text></view>
          <button class="del" @click="removeOption(i, j)">×</button>
        </view>
        <button class="add-option" @click="addOption(i)">＋ 选项</button>
      </view>
    </view>

    <view class="save-wrap"><button class="primary-button" @click="save">保存</button></view>
  </view>
</template>

<style scoped lang="scss">
.merchant-sub { padding-bottom: 160rpx; }
.sub-header { padding: calc(70rpx + env(safe-area-inset-top)) 30rpx 36rpx; background: linear-gradient(145deg, #0637c9, #071a62); color: #fff; }
.top-back { position: absolute; left: 26rpx; top: calc(24rpx + env(safe-area-inset-top)); width: 62rpx; height: 62rpx; display: flex; align-items: center; justify-content: center; border-radius: 50%; background: rgba(255,255,255,.12); color: #fff; font-size: 46rpx; line-height: 1; }
.eyebrow, .title, .subtitle { display: block; }
.eyebrow { font-size: 17rpx; letter-spacing: 5rpx; color: #edcf91; }
.title { margin-top: 12rpx; font-size: 42rpx; font-weight: 800; }
.subtitle { margin-top: 8rpx; font-size: 21rpx; color: rgba(255,255,255,.65); }
.form { margin: -30rpx 28rpx 0; padding: 12rpx 26rpx; position: relative; }
.field { display: flex; align-items: center; min-height: 92rpx; border-bottom: 1rpx solid var(--line); }
.field.last { border-bottom: 0; }
.label { width: 130rpx; margin-right: 16rpx; font-weight: 600; font-size: 24rpx; flex-shrink: 0; }
.field input { flex: 1; font-size: 24rpx; }
.field-row { display: flex; }
.field-row .field { flex: 1; }
.field.second { border-left: 1rpx solid var(--line); padding-left: 20rpx; border-bottom: 0; }
.picker { flex: 1; }
.picker-value { display: flex; align-items: center; justify-content: space-between; font-size: 24rpx; }
.picker-value.empty { color: var(--muted); }
.arrow { color: var(--muted); font-size: 30rpx; }
.image-field { align-items: flex-start; padding: 22rpx 0; }
.image-box { flex: 1; display: flex; align-items: center; }
.preview { width: 128rpx; height: 128rpx; margin-right: 18rpx; border-radius: 14rpx; background: var(--oat-100); }
.preview.empty { display: flex; align-items: center; justify-content: center; color: var(--muted); font-size: 20rpx; }
.upload-btn { min-width: 120rpx; height: 60rpx; display: flex; align-items: center; justify-content: center; border-radius: 30rpx; background: var(--brand-soft); color: var(--brand-700); font-size: 22rpx; }
.options { margin: 28rpx 28rpx 0; }
.options-head { display: flex; align-items: center; justify-content: space-between; margin-bottom: 16rpx; }
.op-title { font-size: 30rpx; font-weight: 700; }
.add-group { padding: 10rpx 22rpx; border-radius: 28rpx; background: var(--brand-soft); color: var(--brand-700); font-size: 22rpx; }
.op-hint { display: block; padding: 30rpx; text-align: center; color: var(--muted); font-size: 22rpx; border: 1rpx dashed var(--line); border-radius: 18rpx; }
.group { margin-bottom: 18rpx; padding: 22rpx; }
.group-head { display: flex; align-items: center; }
.group-name { flex: 1; margin-right: 14rpx; font-size: 25rpx; font-weight: 700; }
.del { display: flex; align-items: center; justify-content: center; min-width: 72rpx; height: 52rpx; border-radius: 26rpx; background: var(--oat-100); color: var(--muted); font-size: 21rpx; }
.group-toggles { display: flex; margin-top: 14rpx; }
.group-toggles button { display: flex; align-items: center; justify-content: center; min-width: 88rpx; height: 50rpx; margin-right: 12rpx; border-radius: 25rpx; background: var(--oat-100); color: var(--muted); font-size: 21rpx; }
.group-toggles button.on { background: var(--brand-800); color: #fff; }
.opt-row { display: flex; align-items: center; margin-top: 16rpx; padding: 12rpx; border-radius: 14rpx; background: var(--oat-50); }
.opt-name { flex: 1; margin-right: 12rpx; font-size: 23rpx; }
.opt-price { display: flex; align-items: center; margin-right: 12rpx; font-size: 20rpx; color: var(--muted); }
.opt-price text { margin-right: 4rpx; }
.opt-price input { width: 80rpx; margin-right: 4rpx; text-align: right; font-size: 22rpx; }
.add-option { display: flex; align-items: center; justify-content: center; width: 100%; height: 60rpx; margin-top: 14rpx; border: 1rpx dashed var(--line); border-radius: 14rpx; color: var(--brand-600); font-size: 22rpx; }
.save-wrap { padding: 30rpx 28rpx; }
</style>
