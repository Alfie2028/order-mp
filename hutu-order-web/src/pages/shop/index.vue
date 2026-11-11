<script setup>
import { computed, ref, onMounted } from 'vue'
import { CAMPUS } from '@/data/catalog'
import { useAppStore } from '@/store/app'
import { formatDistance } from '@/utils/format'

const keyword = ref('')
const latitude = ref(CAMPUS.latitude)
const longitude = ref(CAMPUS.longitude)
const { state, currentStore, setStore } = useAppStore()

// ---- 地图高度（可拖拽拉伸，随上划收缩/下划展开）----
const windowHeight = uni.getSystemInfoSync().windowHeight
const minMapHeight = Math.round(windowHeight * 0.22)
const maxMapHeight = Math.round(windowHeight * 0.72)
const mapHeightPx = ref(Math.round(windowHeight * 0.45))
let dragStartY = 0
let dragStartHeight = 0

function onDragStart(e) {
  dragStartY = e.touches[0].clientY
  dragStartHeight = mapHeightPx.value
}
function onDragMove(e) {
  const dy = dragStartY - e.touches[0].clientY // 上划为正
  mapHeightPx.value = Math.min(maxMapHeight, Math.max(minMapHeight, dragStartHeight - dy))
  // #ifdef H5
  renderVanilla()
  // #endif
}

const filteredStores = computed(() => {
  const key = keyword.value.trim()
  return key ? state.stores.filter((store) => `${store.name}${store.address}`.includes(key)) : state.stores
})

const markers = computed(() => state.stores.map((store, index) => {
  const isSelected = store.id === state.currentStoreId
  return {
    id: index,
    latitude: store.latitude,
    longitude: store.longitude,
    title: store.name,
    iconPath: isSelected ? '/static/icon/shop-location-selected.png' : '/static/icon/shop-location.png',
    width: isSelected ? 32 : 27,
    height: isSelected ? 32 : 27,
    callout: { content: store.name, display: isSelected ? 'ALWAYS' : 'BYCLICK', padding: 7, borderRadius: 5, color: '#222426', bgColor: '#ffffff' },
  }
}))

// ---- H5 端地图：原生瓦片地图（高德瓦片，国内可访问、免 key、零外部依赖）----
// #ifdef H5
const TILE = 256
let mapEl = null
let tilesEl = null
let pinsEl = null
let centerLng = CAMPUS.longitude
let centerLat = CAMPUS.latitude
let zoom = 15
let dragState = { active: false, moved: false, x: 0, y: 0 }

function lon2tileX(lon, z) { return ((lon + 180) / 360) * Math.pow(2, z) }
function lat2tileY(lat, z) {
  const r = (lat * Math.PI) / 180
  return ((1 - Math.log(Math.tan(r) + 1 / Math.cos(r)) / Math.PI) / 2) * Math.pow(2, z)
}
function tileY2lat(y, z) {
  const n = Math.PI * (1 - (2 * y) / Math.pow(2, z))
  return (Math.atan(Math.sinh(n)) * 180) / Math.PI
}
function tileUrl(x, y, z) {
  const s = ((x + y) % 4) + 1
  return `https://webrd0${s}.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=8&x=${x}&y=${y}&z=${z}`
}

function renderPins(left, top) {
  pinsEl.innerHTML = ''
  const points = [
    { lat: CAMPUS.latitude, lng: CAMPUS.longitude, title: CAMPUS.name },
    ...state.stores.map((s) => ({ lat: s.latitude, lng: s.longitude, title: s.name, store: s })),
  ]
  points.forEach((p, i) => {
    const px = lon2tileX(p.lng, zoom) * TILE - left
    const py = lat2tileY(p.lat, zoom) * TILE - top
    const isCampus = i === 0
    const selected = p.store && p.store.id === state.currentStoreId
    const size = isCampus ? 18 : selected ? 16 : 12
    const color = isCampus ? '#FF4B3E' : selected ? '#FFC300' : '#222426'
    const pin = document.createElement('div')
    pin.style.cssText = `position:absolute;left:${px - size / 2}px;top:${py - size / 2}px;width:${size}px;height:${size}px;border-radius:50%;background:${color};border:2px solid #fff;box-shadow:0 1px 5px rgba(0,0,0,.35);cursor:pointer`
    if (p.store) pin.addEventListener('click', () => { if (!dragState.moved) select(p.store) })
    pinsEl.appendChild(pin)
    if (isCampus || selected) {
      const label = document.createElement('div')
      label.textContent = p.title
      label.style.cssText = `position:absolute;left:${px}px;top:${py - size / 2 - 20}px;transform:translateX(-50%);max-width:150px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;background:rgba(255,255,255,.95);color:#222426;font-size:11px;font-weight:700;line-height:1;padding:4px 8px;border-radius:6px;box-shadow:0 2px 6px rgba(0,0,0,.15)`
      pinsEl.appendChild(label)
    }
  })
}

function renderVanilla() {
  if (!mapEl || !tilesEl) return
  const w = mapEl.clientWidth
  const h = mapEl.clientHeight
  if (!w || !h) return
  const n = Math.pow(2, zoom)
  const cx = lon2tileX(centerLng, zoom) * TILE
  const cy = lat2tileY(centerLat, zoom) * TILE
  const left = cx - w / 2
  const top = cy - h / 2
  const startTx = Math.floor(left / TILE)
  const startTy = Math.floor(top / TILE)
  const endTx = Math.floor((left + w) / TILE)
  const endTy = Math.floor((top + h) / TILE)
  const frag = document.createDocumentFragment()
  for (let ty = startTy; ty <= endTy; ty++) {
    if (ty < 0 || ty >= n) continue
    for (let tx = startTx; tx <= endTx; tx++) {
      const x = ((tx % n) + n) % n
      const img = document.createElement('img')
      img.src = tileUrl(x, ty, zoom)
      img.draggable = false
      img.style.cssText = `position:absolute;width:${TILE}px;height:${TILE}px;left:${tx * TILE - left}px;top:${ty * TILE - top}px`
      frag.appendChild(img)
    }
  }
  tilesEl.innerHTML = ''
  tilesEl.appendChild(frag)
  renderPins(left, top)
}

function setVanillaCenter(lat, lng) {
  centerLat = lat
  centerLng = lng
  renderVanilla()
}

function zoomIn() { if (zoom < 18) { zoom++; renderVanilla() } }
function zoomOut() { if (zoom > 12) { zoom--; renderVanilla() } }

function dragPoint(e) { return e.touches ? e.touches[0] : e }
function onMapTouchStart(e) {
  const t = dragPoint(e)
  dragState.active = true
  dragState.moved = false
  dragState.x = t.clientX
  dragState.y = t.clientY
}
function onMapTouchMove(e) {
  if (!dragState.active) return
  e.preventDefault()
  const t = dragPoint(e)
  const dx = t.clientX - dragState.x
  const dy = t.clientY - dragState.y
  if (Math.abs(dx) + Math.abs(dy) > 2) dragState.moved = true
  dragState.x = t.clientX
  dragState.y = t.clientY
  const scale = Math.pow(2, zoom)
  const nx = lon2tileX(centerLng, zoom) * TILE - dx
  const ny = lat2tileY(centerLat, zoom) * TILE - dy
  centerLng = (nx / TILE / scale) * 360 - 180
  centerLat = tileY2lat(ny / TILE, zoom)
  renderVanilla()
}
function onMapTouchEnd() { dragState.active = false }

function buildVanillaMap() {
  mapEl = document.getElementById('leaflet-map')
  if (!mapEl || tilesEl) return
  if (!mapEl.clientWidth || !mapEl.clientHeight) {
    requestAnimationFrame(buildVanillaMap)
    return
  }
  mapEl.style.position = 'relative'
  mapEl.style.cursor = 'grab'
  tilesEl = document.createElement('div')
  tilesEl.style.cssText = 'position:absolute;inset:0;overflow:hidden;background:#f5f6f8'
  pinsEl = document.createElement('div')
  pinsEl.style.cssText = 'position:absolute;inset:0;overflow:hidden'
  mapEl.appendChild(tilesEl)
  mapEl.appendChild(pinsEl)
  mapEl.addEventListener('touchstart', onMapTouchStart, { passive: false })
  mapEl.addEventListener('mousedown', onMapTouchStart)
  window.addEventListener('touchmove', onMapTouchMove, { passive: false })
  window.addEventListener('touchend', onMapTouchEnd)
  window.addEventListener('mousemove', (e) => { if (dragState.active) onMapTouchMove(e) })
  window.addEventListener('mouseup', onMapTouchEnd)
  window.addEventListener('resize', renderVanilla)
  renderVanilla()
}
// #endif

onMounted(() => {
  // #ifdef H5
  buildVanillaMap()
  // #endif
})

function select(store) {
  const apply = () => {
    setStore(store.id)
    latitude.value = store.latitude
    longitude.value = store.longitude
    // #ifdef H5
    setVanillaCenter(store.latitude, store.longitude)
    // #endif
  }
  if (state.cart.length && state.currentStoreId !== store.id) {
    uni.showModal({ title: '切换门店', content: '切换门店将清空当前购物车，是否继续？', confirmColor: '#222426', success: ({ confirm }) => confirm && apply() })
  } else apply()
}

function handleMarkerTap(event) {
  const markerId = Number(event.detail && event.detail.markerId != null ? event.detail.markerId : event.markerId)
  const store = state.stores[markerId]
  if (store) select(store)
}

function recenterCampus() {
  latitude.value = CAMPUS.latitude
  longitude.value = CAMPUS.longitude
  // #ifdef H5
  setVanillaCenter(CAMPUS.latitude, CAMPUS.longitude)
  // #endif
}

function goOrder() { uni.switchTab({ url: '/pages/order/index' }) }

function enterStore(store) {
  const apply = () => { setStore(store.id); goOrder() }
  if (state.cart.length && state.currentStoreId !== store.id) {
    uni.showModal({ title: '切换门店', content: '切换门店将清空当前购物车，是否继续？', confirmColor: '#222426', success: ({ confirm }) => confirm && apply() })
  } else apply()
}
</script>

<template>
  <view class="page-shell shop-page">
    <view class="map-wrap" :style="{ height: mapHeightPx + 'px' }">
      <!-- #ifdef H5 -->
      <div id="leaflet-map" class="map-box vanilla-map"></div>
      <view class="zoom-control">
        <view class="zoom-btn" @click="zoomIn">＋</view>
        <view class="zoom-btn" @click="zoomOut">－</view>
      </view>
      <!-- #endif -->
      <!-- #ifndef H5 -->
      <map
        class="map-box"
        :latitude="latitude"
        :longitude="longitude"
        :markers="markers"
        :scale="15"
        show-location
        @markertap="handleMarkerTap"
      />
      <!-- #endif -->
      <button class="recenter-button" aria-label="回到学院位置" @click="recenterCampus">
        <image src="/static/icon/local.png" mode="aspectFit" />
      </button>
    </view>

    <view class="shop-content">
      <view class="drag-zone" @touchstart="onDragStart" @touchmove="onDragMove">
        <view class="sheet-handle" />
      </view>
      <view class="sheet-heading">
        <view><text class="sheet-title">选择就近门店</text></view>
        <view class="service-status">
          <text class="status-dot" />
          <text>全城配送中</text>
        </view>
      </view>
      <view class="search-box">
        <view class="search-ico-small">
          <view class="ico-c" />
          <view class="ico-s" />
        </view>
        <input v-model="keyword" placeholder="搜索门店名称或地址" confirm-type="search" />
        <text v-if="keyword" class="clear" @click="keyword = ''">×</text>
      </view>
      <view class="result-title">
        <text>附近门店列表</text>
        <text class="result-count">{{ filteredStores.length }} 家门店</text>
      </view>
      <scroll-view scroll-y class="store-list">
        <view v-for="store in filteredStores" :key="store.id" class="store-item card" :class="{ selected: store.id === state.currentStoreId }" @click="select(store)">
          <image class="store-cover" :src="store.image" mode="aspectFill" />
          <view class="store-main">
            <view class="store-row">
              <view class="store-name-wrap">
                <text class="store-name">{{ store.name }}</text>
              </view>
              <text class="store-distance">{{ formatDistance(store.distance) }}</text>
            </view>
            <text class="store-address">{{ store.address }}</text>
            <view class="store-meta">
              <text class="open-status">{{ store.status === 'open' ? '营业中' : '客流较多' }}</text>
              <text>约 {{ store.waitMinutes }} 分钟出餐</text>
            </view>
            <text class="store-hours">{{ store.hours }}</text>
            <view class="store-footer">
              <view class="service-row">
                <text v-for="service in store.services" :key="service" class="chip">{{ service }}</text>
              </view>
              <text class="enter-btn" @click.stop="enterStore(store)">进店点餐 ›</text>
            </view>
          </view>
          <view v-if="store.id === state.currentStoreId" class="selected-mark">
            <text class="check-glyph">✓</text>
            <text>已选择</text>
          </view>
        </view>
      </scroll-view>
    </view>
  </view>
</template>

<style scoped lang="scss">
.shop-page {
  height: 100vh;
  overflow: hidden;
  padding: 0;
  background: #F7F8FA;
  display: flex;
  flex-direction: column;
}
.map-wrap {
  position: relative;
  flex: 0 0 auto;
  overflow: hidden;
  background: #ECEEF2;
}
.map-box { width: 100%; height: 100%; }
.vanilla-map { overflow: hidden; }

.zoom-control {
  position: absolute;
  z-index: 3;
  right: 24rpx;
  top: 24rpx;
  display: flex;
  flex-direction: column;
}
.zoom-btn {
  width: 60rpx;
  height: 60rpx;
  margin-bottom: 10rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: #fff;
  box-shadow: 0 4rpx 14rpx rgba(0, 0, 0, .15);
  color: #222426;
  font-size: 32rpx;
  line-height: 1;
  font-weight: 900;
}
.recenter-button {
  position: absolute;
  z-index: 3;
  right: 24rpx;
  bottom: 32rpx;
  width: 72rpx;
  height: 72rpx;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: #fff;
  box-shadow: 0 6rpx 18rpx rgba(0, 0, 0, .18);
}
.recenter-button image { width: 36rpx; height: 36rpx; }

.shop-content {
  position: relative;
  z-index: 4;
  flex: 1 1 auto;
  min-height: 0;
  margin-top: -26rpx;
  padding: 12rpx 24rpx calc(24rpx + env(safe-area-inset-bottom));
  border-radius: 32rpx 32rpx 0 0;
  background: #F7F8FA;
  box-shadow: 0 -8rpx 30rpx rgba(0, 0, 0, .08);
  display: flex;
  flex-direction: column;
}
.store-list { flex: 1; min-height: 0; }
.drag-zone {
  flex: 0 0 auto;
  display: flex;
  align-items: center;
  justify-content: center;
  height: 48rpx;
}
.sheet-handle {
  width: 72rpx;
  height: 8rpx;
  border-radius: 4rpx;
  background: #D8DADF;
}
.sheet-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin: 0 2rpx 18rpx;
}
.sheet-title { font-size: 32rpx; font-weight: 900; color: #222426; }
.service-status {
  display: flex;
  align-items: center;
  padding: 8rpx 16rpx;
  border-radius: 20rpx;
  color: #8C5E00;
  background: #FFF7DB;
  font-size: 20rpx;
  font-weight: 700;
}
.status-dot {
  width: 12rpx;
  height: 12rpx;
  margin-right: 8rpx;
  border-radius: 50%;
  background: #07C160;
}

.search-box {
  display: flex;
  align-items: center;
  height: 74rpx;
  padding: 0 24rpx;
  border: 2rpx solid #E5E6EB;
  border-radius: 37rpx;
  background: #fff;
  box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, .03);
}
.search-ico-small {
  position: relative;
  width: 26rpx;
  height: 26rpx;
  margin-right: 14rpx;
}
.ico-c {
  position: absolute;
  left: 0;
  top: 0;
  width: 18rpx;
  height: 18rpx;
  border: 3rpx solid #222426;
  border-radius: 50%;
}
.ico-s {
  position: absolute;
  right: 0;
  bottom: 0;
  width: 9rpx;
  height: 3rpx;
  transform: rotate(45deg);
  background: #222426;
}
.search-box input { flex: 1; font-size: 24rpx; color: #222426; }
.clear { font-size: 32rpx; color: #8E929E; }

.result-title {
  display: flex;
  justify-content: space-between;
  margin: 22rpx 4rpx 14rpx;
  font-size: 28rpx;
  font-weight: 900;
  color: #222426;
}
.result-count { color: #8E929E; font-size: 20rpx; font-weight: 400; }

.store-item {
  position: relative;
  display: flex;
  margin-bottom: 16rpx;
  padding: 20rpx;
  border-radius: 22rpx;
  border: 2rpx solid transparent;
  transition: all .15s ease;
}
.store-item.selected {
  border: 2rpx solid #FFC300;
  background: linear-gradient(135deg, #ffffff 60%, #FFFDF5 100%);
}
.store-cover {
  width: 140rpx;
  height: 170rpx;
  margin-right: 18rpx;
  flex: 0 0 140rpx;
  border-radius: 18rpx;
  background: #F2F3F5;
}
.store-main { min-width: 0; flex: 1; }
.store-row { display: flex; justify-content: space-between; align-items: center; }
.store-name-wrap { display: flex; align-items: center; min-width: 0; flex: 1; }
.store-name { min-width: 0; font-size: 26rpx; font-weight: 900; color: #222426; line-height: 1.3; }
.store-distance { flex: none; color: #B37D00; font-size: 20rpx; font-weight: 700; margin-left: 10rpx; }
.store-address { display: block; margin-top: 6rpx; color: #8E929E; font-size: 19rpx; line-height: 1.35; }
.store-meta { display: flex; margin-top: 8rpx; color: #666; font-size: 18rpx; }
.store-meta text { margin-right: 14rpx; }
.open-status { color: #07C160; font-weight: 700; }
.store-hours { display: block; margin-top: 6rpx; color: #8E929E; font-size: 17rpx; }
.store-footer { display: flex; align-items: center; justify-content: space-between; margin-top: 14rpx; }
.service-row { display: flex; }
.service-row .chip {
  min-height: 34rpx;
  margin-right: 8rpx;
  padding: 0 10rpx;
  color: #8C5E00;
  background: #FFF7DB;
  font-size: 16rpx;
  font-weight: 700;
}
.enter-btn {
  flex: none;
  padding: 10rpx 24rpx;
  border-radius: 28rpx;
  color: #222426;
  background: #FFC300;
  font-size: 21rpx;
  font-weight: 800;
  box-shadow: 0 4rpx 12rpx rgba(255, 195, 0, .35);
}
.selected-mark {
  position: absolute;
  left: 20rpx;
  top: 20rpx;
  display: flex;
  align-items: center;
  padding: 6rpx 14rpx;
  border-radius: 12rpx;
  color: #222426;
  background: #FFC300;
  font-size: 19rpx;
  font-weight: 800;
  box-shadow: 0 4rpx 12rpx rgba(255, 195, 0, .4);
}
.check-glyph { margin-right: 4rpx; font-weight: 900; }
</style>
