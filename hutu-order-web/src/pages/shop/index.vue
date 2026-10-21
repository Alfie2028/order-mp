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
    callout: { content: store.name, display: isSelected ? 'ALWAYS' : 'BYCLICK', padding: 7, borderRadius: 5, color: '#35231b', bgColor: '#ffffff' },
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
    const color = isCampus ? '#0637c9' : '#0637c9'
    const pin = document.createElement('div')
    pin.style.cssText = `position:absolute;left:${px - size / 2}px;top:${py - size / 2}px;width:${size}px;height:${size}px;border-radius:50%;background:${color};border:2px solid #fff;box-shadow:0 1px 5px rgba(0,0,0,.35);cursor:pointer`
    if (p.store) pin.addEventListener('click', () => { if (!dragState.moved) select(p.store) })
    pinsEl.appendChild(pin)
    if (isCampus || selected) {
      const label = document.createElement('div')
      label.textContent = p.title
      label.style.cssText = `position:absolute;left:${px}px;top:${py - size / 2 - 20}px;transform:translateX(-50%);max-width:150px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;background:rgba(255,255,255,.95);color:#35231b;font-size:11px;line-height:1;padding:3px 6px;border-radius:5px;box-shadow:0 1px 4px rgba(0,0,0,.2)`
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
  tilesEl.style.cssText = 'position:absolute;inset:0;overflow:hidden;background:#e6ebf6'
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
    uni.showModal({ title: '切换档口', content: '切换档口将清空当前购物车，是否继续？', confirmColor: '#0637c9', success: ({ confirm }) => confirm && apply() })
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
    uni.showModal({ title: '切换档口', content: '切换档口将清空当前购物车，是否继续？', confirmColor: '#0637c9', success: ({ confirm }) => confirm && apply() })
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
        <view><text class="sheet-title">选择档口</text></view>
        <view class="service-status"><text class="status-dot"></text><text>营业中</text></view>
      </view>
      <view class="search-box"><text class="search-symbol">⌕</text><input v-model="keyword" placeholder="搜索档口名称或地址" confirm-type="search" /><text v-if="keyword" class="clear" @click="keyword = ''">×</text></view>
      <view class="result-title"><text>附近档口</text><text class="result-count">{{ filteredStores.length }} 家</text></view>
      <scroll-view scroll-y class="store-list">
        <view v-for="store in filteredStores" :key="store.id" class="store-item card" :class="{ selected: store.id === state.currentStoreId }" @click="select(store)">
          <image class="store-cover" :src="store.image" mode="aspectFill" />
          <view class="store-main">
            <view class="store-row"><view class="store-name-wrap"><text class="store-name">{{ store.name }}</text></view><text class="store-distance">{{ formatDistance(store.distance) }}</text></view>
            <text class="store-address">{{ store.address }}</text>
            <view class="store-meta"><text :class="store.status">{{ store.status === 'open' ? '营业中' : '客流较多' }}</text><text>约 {{ store.waitMinutes }} 分钟</text></view>
            <text class="store-hours">{{ store.hours }}</text>
            <view class="store-footer">
              <view class="service-row"><text v-for="service in store.services" :key="service" class="chip">{{ service }}</text></view>
              <text class="enter-btn" @click.stop="enterStore(store)">进店点餐 ›</text>
            </view>
          </view>
          <text v-if="store.id === state.currentStoreId" class="selected-mark">✓ 已选择</text>
        </view>
      </scroll-view>
    </view>
  </view>
</template>

<style scoped lang="scss">
.shop-page{height:100vh;overflow:hidden;padding:0;background:var(--oat-50);display:flex;flex-direction:column}
.map-wrap{position:relative;flex:0 0 auto;overflow:hidden;background:#e6ebf6}.map-box{width:100%;height:100%}.vanilla-map{overflow:hidden}
.zoom-control{position:absolute;z-index:3;right:24rpx;top:24rpx;display:flex;flex-direction:column}.zoom-btn{width:60rpx;height:60rpx;margin-bottom:8rpx;display:flex;align-items:center;justify-content:center;border:1rpx solid rgba(6,55,201,.12);border-radius:14rpx;background:#fff;box-shadow:0 6rpx 18rpx rgba(16,38,111,.16);color:#0637c9;font-size:32rpx;line-height:1;font-weight:700}
.recenter-button{position:absolute;z-index:3;right:24rpx;bottom:32rpx;width:68rpx;height:68rpx;padding:0;display:flex;align-items:center;justify-content:center;border:1rpx solid rgba(6,55,201,.1);border-radius:50%;background:#fff;box-shadow:0 8rpx 24rpx rgba(16,38,111,.17)}.recenter-button image{width:32rpx;height:32rpx}
.shop-content{position:relative;z-index:4;flex:1 1 auto;min-height:0;margin-top:-26rpx;padding:12rpx 28rpx calc(24rpx + env(safe-area-inset-bottom));border-radius:32rpx 32rpx 0 0;background:var(--oat-50);box-shadow:0 -10rpx 35rpx rgba(34,48,42,.08);display:flex;flex-direction:column}.store-list{flex:1;min-height:0}.drag-zone{flex:0 0 auto;display:flex;align-items:center;justify-content:center;height:52rpx}.sheet-handle{width:68rpx;height:7rpx;border-radius:5rpx;background:#d6d2ca}.sheet-heading{display:flex;align-items:center;justify-content:space-between;margin:0 2rpx 19rpx}.sheet-heading text{display:block}.sheet-title{font-size:31rpx;font-weight:700}.service-status{display:flex;align-items:center;padding:10rpx 15rpx;border-radius:24rpx;color:var(--brand);background:var(--brand-soft);font-size:19rpx;font-weight:600}.status-dot{width:10rpx;height:10rpx;margin-right:8rpx;border-radius:50%;background:var(--brand)}
.search-box{display:flex;align-items:center;height:76rpx;padding:0 23rpx;border:1rpx solid var(--line);border-radius:22rpx;background:#fff;box-shadow:0 6rpx 20rpx rgba(16,38,111,.04)}.search-box input{flex:1;margin-right:14rpx;font-size:23rpx}.search-symbol{margin-right:14rpx;font-size:24rpx;color:var(--brand)}.clear{font-size:34rpx;color:var(--muted)}
.result-title{display:flex;justify-content:space-between;margin:24rpx 2rpx 14rpx;font-size:27rpx;font-weight:700}.result-count{color:var(--muted);font-size:20rpx;font-weight:400}
.store-item{position:relative;display:flex;margin-bottom:14rpx;padding:18rpx;border-radius:22rpx;box-shadow:0 12rpx 32rpx rgba(16,38,111,.1)}.store-item.selected{border:1rpx solid rgba(6,55,201,.28);background:linear-gradient(135deg,#fff 60%,#edf2ff)}.store-cover{width:138rpx;height:166rpx;margin-right:18rpx;flex:0 0 138rpx;border-radius:17rpx;background:#e6e9f1}.store-main{min-width:0;flex:1}.store-row{display:flex;justify-content:space-between;align-items:center}.store-name-wrap{display:flex;align-items:center;min-width:0;flex:1}.store-name{min-width:0;font-size:24rpx;font-weight:700;line-height:1.3}.tag-badge{margin-left:12rpx;padding:2rpx 10rpx;font-size:18rpx;border-radius:8rpx;font-weight:600;white-space:nowrap;flex:none}.tag-badge.inside{background:#edf2ff;color:#0637c9;border:1rpx solid rgba(6,55,201,.2)}.tag-badge.outside{background:#fff4ea;color:#d96a00;border:1rpx solid rgba(217,106,0,.2)}.store-distance{flex:none;color:var(--brand);font-size:19rpx;font-weight:600}.store-address{display:block;margin-top:7rpx;color:var(--muted);font-size:18rpx;line-height:1.35}.store-meta{display:flex;margin-top:9rpx;color:var(--muted);font-size:17rpx}.store-meta text{margin-right:13rpx}.store-meta .open{color:var(--brand);font-weight:700}.store-meta .busy{color:var(--danger);font-weight:700}.store-hours{display:block;margin-top:5rpx;color:#858891;font-size:16rpx}.store-footer{display:flex;align-items:center;justify-content:space-between;margin-top:12rpx}.service-row{display:flex}.service-row .chip{min-height:32rpx;margin-right:7rpx;padding:0 9rpx;color:#40527d;background:#f0f3fa;font-size:15rpx}.enter-btn{flex:none;padding:9rpx 18rpx;border-radius:26rpx;color:#fff;background:var(--brand);font-size:20rpx;font-weight:700;box-shadow:0 6rpx 14rpx rgba(6,55,201,.2)}.selected-mark{position:absolute;left:20rpx;top:20rpx;padding:8rpx 16rpx;border-radius:14rpx;color:#fff;background:var(--brand);font-size:20rpx;font-weight:800;box-shadow:0 6rpx 16rpx rgba(6,55,201,.3)}
</style>
