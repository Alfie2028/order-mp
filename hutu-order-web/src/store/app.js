import { computed, reactive } from 'vue'
import { COUPONS as CATALOG_COUPONS, PRODUCTS as CATALOG_PRODUCTS, STALLS as CATALOG_STALLS, STORES as CATALOG_STORES } from '@/data/catalog'
import { get, post, put, del, upload, BASE_URL } from '@/utils/request'

// 兼容微信小程序 iOS 端老 JavaScriptCore（缺失 ES2020 Promise.allSettled）
const allSettled = (promises) => Promise.all(promises.map((p) => Promise.resolve(p).then(
  (value) => ({ status: 'fulfilled', value }),
  (reason) => ({ status: 'rejected', reason }),
)))
// 兼容 iOS 端对 "YYYY-MM-DDTHH:MM:SS" 字符串 new Date 解析失败的问题（手动按 UTC 解析）
const parseDate = (str) => {
  if (!str) return Date.now()
  const m = String(str).replace(/[TZ]/g, ' ').trim().split(/[- :.]/)
  if (m.length < 6) return Date.now()
  return Date.UTC(+m[0], +m[1] - 1, +m[2], +m[3] || 0, +m[4] || 0, +m[5] || 0)
}
// 图片地址解析：静态资源走原样；上传图片（/uploads/）拼 BASE_URL，兼容内网穿透换域名；
// 统一附加 imageVersion 版本号参数，图片加载失败后置位即可强制重绘重试
function resolveImage(src) {
  if (!src) return ''
  const t = src.startsWith('/static/') || src.startsWith('http://') || src.startsWith('https://') || src.startsWith('data:') ? src : BASE_URL + src
  if (t.startsWith('data:')) return t
  const v = typeof state !== 'undefined' && state && typeof state.imageVersion !== 'undefined' ? state.imageVersion : 0
  return t + (t.includes('?') ? `&v=${v}` : `?v=${v}`)
}
// 把 resolve 后的完整图片 URL 还原成相对路径，避免把临时域名写入数据库
function stripBaseUrl(src) {
  if (!src) return ''
  if (src.startsWith(BASE_URL)) return src.slice(BASE_URL.length)
  return src
}

const STORAGE_KEY = 'CAMPUS_ORDERING_V11'

// 档口展示名覆盖：后端旧名（学生餐厅等）统一展示为新档口名
const kStoreNames = { 'henau-canteen': '农大温馨家园', 'nongda-road': '农大路美食档口', 'suqiao-town': '苏桥老街档口' }

// ---- 字段映射：后端 snake_case -> 前端 camelCase，静态 catalog 补齐展示字段 ----
function mapStore(s) {
  const stat = CATALOG_STORES.find((x) => x.id === s.id) || {}
  return { ...stat, id: s.id, name: kStoreNames[s.id] || s.name, shortName: kStoreNames[s.id] || s.short_name || s.name, tag: stat.tag || (s.id === 'henau-canteen' ? '校内' : '校外'), address: s.address, distance: s.distance, hours: s.hours, status: s.status, waitMinutes: s.wait_minutes, latitude: s.latitude, longitude: s.longitude, image: resolveImage(s.image) }
}
function mapStall(s) {
  const stat = CATALOG_STALLS.find((x) => x.id === s.id) || {}
  return { ...stat, id: s.id, storeId: s.store_id, name: s.name, shortName: s.short_name, description: s.description, code: s.code, isActive: s.is_active !== false }
}
function mapProduct(p) {
  const stat = CATALOG_PRODUCTS.find((x) => x.id === p.id) || {}
  return { ...stat, id: p.id, stallId: p.stall_id, name: p.name, subtitle: p.subtitle, priceCents: p.price_cents, originalPriceCents: p.original_price_cents, badge: p.badge, sales: p.sales, image: resolveImage(p.image), options: JSON.parse(p.options || '[]'), isActive: p.is_active !== false }
}
function mapCoupon(c) {
  return { id: c.id, name: c.name, thresholdCents: c.threshold_cents, discountCents: c.discount_cents, expires: c.expires, isActive: c.is_active !== false }
}
function mapUser(u) {
  return { id: u.id, name: u.username || u.email, role: u.role, title: u.role === 'merchant' ? '商家' : '标准会员', avatar: resolveImage(u.avatar || '/uploads/catalog/avatar/default.png'), points: u.points || 0, level: 3, nextLevelPoints: 1200 }
}
function mapOrder(o) {
  return {
    dbId: o.id,               // 后端数据库自增 id，接口调用用
    id: o.order_no,           // 订单号，前端展示/导航用
    storeId: o.store_id,
    storeName: (CATALOG_STORES.find((s) => s.id === o.store_id) || {}).name || '',
    mode: o.mode,
    status: o.status,
    statusText: o.status_text,
    pickupCode: o.pickup_code,
    createdAt: parseDate(o.created_at),
    remark: o.remark,
    items: (o.items || []).map((it) => {
      const stat = state.products.find((p) => p.id === it.product_id) || CATALOG_PRODUCTS.find((p) => p.id === it.product_id) || {}
      return { productId: it.product_id, name: it.name, quantity: it.quantity, unitPriceCents: it.unit_price_cents, selectedOptions: JSON.parse(it.options || '[]'), stallName: stat.stallName || '', image: resolveImage(stat.image || ''), fallback: stat.fallback || it.name }
    }),
    subtotalCents: o.subtotal_cents,
    discountCents: o.discount_cents,
    totalCents: o.total_cents,
    couponName: o.coupon_name,
  }
}

const cartKey = (productId, options) => `${productId}:${options.map((option) => option.id).sort().join('-')}`
function mapCartItem(c) {
  const stat = state.products.find((p) => p.id === c.product_id) || CATALOG_PRODUCTS.find((p) => p.id === c.product_id) || {}
  const options = JSON.parse(c.options || '[]')
  const extras = options.reduce((sum, option) => sum + Number(option.extraCents || 0), 0)
  return { id: c.id, key: cartKey(c.product_id, options), productId: c.product_id, name: stat.name || '', stallName: stat.stallName || '', image: resolveImage(stat.image || ''), fallback: stat.fallback || '', selectedOptions: options, unitPriceCents: (stat.priceCents || 0) + extras, quantity: c.quantity }
}

const withRemoteImage = (item) => ({ ...item, image: resolveImage(item.image), tag: item.tag || (item.id === 'henau-canteen' ? '校内' : '校外') })

const initialState = () => ({
  initialized: false,
  imageVersion: 0,
  stores: CATALOG_STORES.map(withRemoteImage),
  stalls: CATALOG_STALLS,
  products: CATALOG_PRODUCTS.map(withRemoteImage),
  coupons: CATALOG_COUPONS,
  currentStoreId: CATALOG_STORES[0].id,
  selectedStallId: CATALOG_STALLS[0].id,
  orderMode: 'pickup',
  cart: [],
  orders: [],
  merchantOrders: [],
  merchantProducts: [],
  merchantStalls: [],
  merchantCoupons: [],
  dashboard: null,
  myReviews: [],
  merchantReviews: [],
  favoriteIds: [],
  couponIds: [],
  user: null,
})

const state = reactive(initialState())

function persist() {
  if (!state.initialized) return
  uni.setStorageSync(STORAGE_KEY, { currentStoreId: state.currentStoreId, selectedStallId: state.selectedStallId, orderMode: state.orderMode, cart: state.cart, favoriteIds: state.favoriteIds, couponIds: state.couponIds })
}

const isLoggedIn = () => !!state.user

// ---- 数据拉取 ----
let catalogPromise = null
function loadCatalog() {
  if (catalogPromise) return catalogPromise
  catalogPromise = allSettled([get('/api/catalog/stores'), get('/api/catalog/stalls'), get('/api/catalog/products'), get('/api/catalog/coupons')]).then(([s, st, p, c]) => {
    state.imageVersion = 1
    if (s.status === 'fulfilled') state.stores = s.value.map(mapStore)
    if (st.status === 'fulfilled') state.stalls = st.value.map(mapStall)
    if (p.status === 'fulfilled') state.products = p.value.map(mapProduct)
    if (c.status === 'fulfilled') state.coupons = c.value.map(mapCoupon)
    if (p.status !== 'fulfilled') state.products = state.products.map((item) => ({ ...item, image: resolveImage(item.image.replace(/[?&]v=\d+/, '')) }))
  }).catch(() => {
    state.imageVersion = 1
    state.products = state.products.map((item) => ({ ...item, image: resolveImage(item.image.replace(/[?&]v=\d+/, '')) }))
  })
  return catalogPromise
}
function loadOrders() {
  return loadCatalog().then(() => get('/api/orders')).then((list) => { state.orders = list.map(mapOrder) })
}
function loadFavorites() {
  return get('/api/favorites').then((ids) => { state.favoriteIds = ids })
}
function loadCart() {
  return loadCatalog().then(() => get('/api/cart')).then((list) => { state.cart = list.map(mapCartItem); persist() })
}
function loadMyCoupons() {
  if (!isLoggedIn()) return Promise.resolve()
  return get('/api/coupons/mine').then((list) => { state.couponIds = list.map((c) => c.id); persist() }).catch(() => {})
}
function loadMerchantOrders(status = '') {
  return get('/api/merchant/orders', status ? { status } : {}).then((list) => { state.merchantOrders = list.map(mapOrder) })
}
function loadMerchantProducts(stallId = '') {
  return get('/api/merchant/products', stallId ? { stall_id: stallId } : {}).then((list) => { state.merchantProducts = list.map(mapProduct) })
}
function loadMerchantStalls() {
  return get('/api/merchant/stalls').then((list) => { state.merchantStalls = list.map(mapStall) })
}
function loadMerchantCoupons() {
  return get('/api/merchant/coupons').then((list) => { state.merchantCoupons = list.map(mapCoupon) })
}
function loadDashboard() {
  return get('/api/merchant/dashboard').then((data) => { state.dashboard = data })
}

export function initializeStore() {
  if (state.initialized) return
  const saved = uni.getStorageSync(STORAGE_KEY)
  if (saved && typeof saved === 'object') Object.assign(state, initialState(), saved)
  const token = uni.getStorageSync('TOKEN')
  const userInfo = uni.getStorageSync('USER_INFO')
  if (token && userInfo) state.user = userInfo
  state.initialized = true
  loadCatalog().then(() => {
    if (isLoggedIn()) {
      loadOrders().catch(() => {})
      loadFavorites().catch(() => {})
      loadCart().catch(() => {})
      loadMyCoupons().catch(() => {})
    }
  })
}

export function useAppStore() {
  initializeStore()
  const currentStore = computed(() => state.stores.find((store) => store.id === state.currentStoreId) || state.stores[0])
  const cartCount = computed(() => state.cart.reduce((sum, item) => sum + item.quantity, 0))
  const cartSubtotal = computed(() => state.cart.reduce((sum, item) => sum + item.unitPriceCents * item.quantity, 0))

  function setStore(storeId) {
    if (!state.stores.some((store) => store.id === storeId)) return
    if (state.currentStoreId !== storeId && state.cart.length) state.cart = []
    state.currentStoreId = storeId
    persist()
  }
  function setOrderMode(mode) { state.orderMode = mode === 'dineIn' ? 'dineIn' : 'pickup'; persist() }
  function setStall(stallId) { if (state.stalls.some((stall) => stall.id === stallId)) { state.selectedStallId = stallId; persist() } }

  // ---- 购物车：登录走后端，未登录本地 ----
  function addToCart(productId, selectedOptions = [], quantity = 1) {
    const product = state.products.find((item) => item.id === productId)
    if (!product) return Promise.resolve()
    const options = selectedOptions.map((option) => ({ id: option.id, name: option.name, groupName: option.groupName, extraCents: Number(option.extraCents || 0) }))
    if (isLoggedIn()) {
      return post('/api/cart', { product_id: productId, quantity, options: JSON.stringify(options) }).then(loadCart).catch(() => {})
    }
    const key = cartKey(productId, options)
    const existing = state.cart.find((item) => item.key === key)
    if (existing) existing.quantity += quantity
    else state.cart.push({ key, productId, name: product.name, stallName: product.stallName, image: product.image, fallback: product.fallback, selectedOptions: options, unitPriceCents: product.priceCents + options.reduce((sum, option) => sum + option.extraCents, 0), quantity })
    persist()
    return Promise.resolve()
  }
  function updateCartQuantity(key, quantity) {
    if (isLoggedIn()) {
      const item = state.cart.find((entry) => entry.key === key)
      if (!item) return Promise.resolve()
      if (quantity <= 0) return del(`/api/cart/${item.id}`).then(loadCart).catch(() => {})
      return put(`/api/cart/${item.id}`, { quantity }).then(loadCart).catch(() => {})
    }
    const item = state.cart.find((entry) => entry.key === key)
    if (!item) return Promise.resolve()
    if (quantity <= 0) state.cart = state.cart.filter((entry) => entry.key !== key)
    else item.quantity = quantity
    persist()
    return Promise.resolve()
  }
  function clearCart() {
    if (isLoggedIn()) return del('/api/cart').then(() => { state.cart = []; persist() }).catch(() => {})
    state.cart = []
    persist()
    return Promise.resolve()
  }

  // ---- 收藏 ----
  function toggleFavorite(productId) {
    if (!isLoggedIn()) { uni.navigateTo({ url: '/pages/login/index' }); return Promise.resolve() }
    return post(`/api/favorites/toggle/${productId}`).then((res) => {
      if (res.favorited) { if (!state.favoriteIds.includes(productId)) state.favoriteIds = [...state.favoriteIds, productId] }
      else state.favoriteIds = state.favoriteIds.filter((id) => id !== productId)
      persist()
    }).catch(() => {})
  }

  // ---- 优惠券 ----
  function claimCoupon(couponId) {
    if (!isLoggedIn()) { uni.navigateTo({ url: '/pages/login/index' }); return Promise.resolve(null) }
    return post(`/api/coupons/${couponId}/claim`).then((coupon) => {
      const mapped = mapCoupon(coupon)
      if (!state.couponIds.includes(mapped.id)) state.couponIds = [...state.couponIds, mapped.id]
      persist()
      return mapped
    })
  }

  // ---- 认证 ----
  function sendCode(email, purpose = 'register') {
    return post('/api/auth/send-code', { email, purpose })
  }
  function login(email, password) {
    return post('/api/auth/login', { email, password }).then((data) => {
      uni.setStorageSync('TOKEN', data.access_token)
      state.user = mapUser(data.user)
      uni.setStorageSync('USER_INFO', state.user)
      return mergeLocalCart().then(() => allSettled([loadOrders(), loadFavorites(), loadCart(), loadMyCoupons()]))
    })
  }
  function register(email, code, password) {
    return post('/api/auth/register', { email, code, password }).then((data) => {
      uni.setStorageSync('TOKEN', data.access_token)
      state.user = mapUser(data.user)
      uni.setStorageSync('USER_INFO', state.user)
      return mergeLocalCart().then(() => allSettled([loadOrders(), loadFavorites(), loadCart(), loadMyCoupons()]))
    })
  }
  function loginByCode(email, code) {
    return post('/api/auth/login-by-code', { email, code }).then((data) => {
      uni.setStorageSync('TOKEN', data.access_token)
      state.user = mapUser(data.user)
      uni.setStorageSync('USER_INFO', state.user)
      return mergeLocalCart().then(() => allSettled([loadOrders(), loadFavorites(), loadCart(), loadMyCoupons()]))
    })
  }
  function logout() {
    uni.removeStorageSync('TOKEN')
    uni.removeStorageSync('USER_INFO')
    state.user = null
    state.orders = []
    state.merchantOrders = []
    state.merchantProducts = []
    state.merchantStalls = []
    state.merchantCoupons = []
    state.dashboard = null
    state.myReviews = []
    state.merchantReviews = []
    state.favoriteIds = []
    state.cart = []
    persist()
  }
  // 设置头像：上传图片，后端 Base64 存入数据库，返回更新后的用户
  function setAvatar(filePath) {
    return upload('/api/auth/avatar', filePath).then((user) => {
      state.user = mapUser(user)
      uni.setStorageSync('USER_INFO', state.user)
      return state.user
    })
  }
  // 登录后把本地（无 id）购物车合并到后端
  function mergeLocalCart() {
    const local = state.cart.filter((item) => item.id === undefined)
    if (!local.length) return loadCart()
    const tasks = local.map((item) => post('/api/cart', { product_id: item.productId, quantity: item.quantity, options: JSON.stringify(item.selectedOptions) }))
    state.cart = []
    return allSettled(tasks).then(() => loadCart())
  }

  // ---- 订单 ----
  function createOrder({ couponId = '', remark = '', pickupTime = '尽快取餐' } = {}) {
    if (!state.cart.length) return Promise.resolve(null)
    const stallId = state.cart[0] ? ((state.products.find((p) => p.id === state.cart[0].productId) || {}).stallId || state.selectedStallId) : state.selectedStallId
    const items = state.cart.map((item) => ({ product_id: item.productId, name: item.name, quantity: item.quantity, unit_price_cents: item.unitPriceCents, options: JSON.stringify(item.selectedOptions) }))
    return post('/api/orders', { store_id: currentStore.value.id, stall_id: stallId, mode: state.orderMode, remark, coupon_id: couponId, items }).then((o) => {
      const order = mapOrder(o)
      state.orders.unshift(order)
      if (order.discountCents > 0) state.couponIds = state.couponIds.filter((id) => id !== couponId)
      if (state.user) state.user.points += Math.floor(order.totalCents / 100)
      return clearCart().then(() => order)
    })
  }
  const findOrder = (orderId) => state.orders.find((order) => order.id === orderId)
  function payOrder(orderId) {
    const order = findOrder(orderId)
    if (!order) return Promise.reject(new Error('订单不存在'))
    return post(`/api/pay/orders/${order.dbId}/pay`).then((res) => {
      if (res.paid) { order.status = 'paid'; order.statusText = '已支付' }
      persist()
      return res
    })
  }
  function completeOrder(orderId) {
    const order = findOrder(orderId)
    if (!order) return Promise.reject(new Error('订单不存在'))
    return post(`/api/orders/${order.dbId}/complete`).then((o) => {
      const mapped = mapOrder(o)
      const idx = state.orders.findIndex((x) => x.id === orderId)
      if (idx >= 0) state.orders[idx] = mapped
      persist()
      return mapped
    })
  }
  function refreshOrder(orderId) {
    const order = findOrder(orderId)
    if (!order) return Promise.reject(new Error('订单不存在'))
    return get(`/api/orders/${order.dbId}`).then((o) => {
      const mapped = mapOrder(o)
      const idx = state.orders.findIndex((x) => x.id === orderId)
      if (idx >= 0) state.orders[idx] = mapped
      persist()
      return mapped
    })
  }

  // ---- 评价 ----
  function submitReview(orderId, rating, content) {
    return post('/api/reviews', { order_id: orderId, rating, content }).then((review) => {
      if (!state.myReviews.some((r) => r.order_id === orderId)) state.myReviews = [...state.myReviews, review]
      return review
    })
  }
  function loadMyReviews() {
    return get('/api/reviews/mine').then((list) => { state.myReviews = list.map((r) => ({ ...r, createdAt: parseDate(r.created_at) })) })
  }
  function loadMerchantReviews() {
    return get('/api/reviews').then((list) => { state.merchantReviews = list.map((r) => ({ ...r, createdAt: parseDate(r.created_at) })) })
  }

  // ---- 商家端 ----
  function acceptOrder(orderId) {
    const order = (state.merchantOrders || []).find((o) => o.id === orderId)
    if (!order) return Promise.reject(new Error('订单不存在'))
    return post(`/api/merchant/orders/${order.dbId}/accept`).then((o) => {
      const mapped = mapOrder(o)
      const idx = state.merchantOrders.findIndex((x) => x.id === orderId)
      if (idx >= 0) state.merchantOrders[idx] = mapped
      return mapped
    })
  }
  function readyOrder(orderId) {
    const order = (state.merchantOrders || []).find((o) => o.id === orderId)
    if (!order) return Promise.reject(new Error('订单不存在'))
    return post(`/api/merchant/orders/${order.dbId}/ready`).then((o) => {
      const mapped = mapOrder(o)
      const idx = state.merchantOrders.findIndex((x) => x.id === orderId)
      if (idx >= 0) state.merchantOrders[idx] = mapped
      return mapped
    })
  }

  // ---- 商家经营：餐品 ----
  function saveProduct(payload) {
    const body = {
      stall_id: payload.stallId,
      name: payload.name,
      subtitle: payload.subtitle || '',
      price_cents: Number(payload.priceCents) || 0,
      original_price_cents: Number(payload.originalPriceCents) || 0,
      badge: payload.badge || '',
      image: stripBaseUrl(payload.image),
      options: JSON.stringify(payload.options || []),
    }
    if (payload.id) return put(`/api/merchant/products/${payload.id}`, body)
    return post('/api/merchant/products', body)
  }
  function deleteProduct(id) { return del(`/api/merchant/products/${id}`) }
  function toggleProduct(id) { return post(`/api/merchant/products/${id}/toggle`) }

  // ---- 商家经营：档口 ----
  function saveStall(payload) {
    const body = {
      store_id: 'henau-canteen',
      name: payload.name,
      short_name: payload.shortName || '',
      description: payload.description || '',
      code: Number(payload.code) || 0,
    }
    if (payload.id) return put(`/api/merchant/stalls/${payload.id}`, body)
    return post('/api/merchant/stalls', body)
  }
  function toggleStall(id) { return post(`/api/merchant/stalls/${id}/toggle`) }

  // ---- 商家经营：优惠券 ----
  function saveCoupon(payload) {
    const body = {
      name: payload.name,
      threshold_cents: Number(payload.thresholdCents) || 0,
      discount_cents: Number(payload.discountCents) || 0,
      expires: payload.expires || '',
    }
    return post('/api/merchant/coupons', body)
  }
  function toggleCoupon(id) { return post(`/api/merchant/coupons/${id}/toggle`) }

  // ---- 商家经营：营业状态 / 上传 ----
  function toggleStoreStatus() {
    return post('/api/merchant/store/toggle').then((res) => {
      const store = state.stores.find((s) => s.id === res.id)
      if (store) store.status = res.status
      return res
    })
  }
  function uploadImage() {
    return new Promise((resolve, reject) => {
      uni.chooseImage({
        count: 1,
        sizeType: ['compressed'],
        success: (res) => {
          const filePath = res.tempFilePaths && res.tempFilePaths[0]
          if (!filePath) { reject(new Error('未选择图片')); return }
          upload('/api/merchant/upload', filePath).then((data) => resolve(data.url)).catch(reject)
        },
        fail: reject,
      })
    })
  }

  // ---- 再来一单 ----
  function reorder(orderId) {
    const order = findOrder(orderId)
    if (!order) return
    state.currentStoreId = order.storeId
    state.orderMode = order.mode
    state.cart = []
    const firstProduct = state.products.find((product) => product.id === order.items[0]?.productId)
    if (firstProduct) state.selectedStallId = firstProduct.stallId
    order.items.forEach((item) => addToCart(item.productId, item.selectedOptions, item.quantity))
    persist()
  }

  function resetStore() { const keepUser = state.user; Object.assign(state, initialState(), { initialized: true }); state.user = keepUser; persist() }

  return { state, currentStore, cartCount, cartSubtotal, loadCatalog, loadOrders, loadFavorites, loadCart, loadMyCoupons, claimCoupon, loadMerchantOrders, loadMerchantProducts, loadMerchantStalls, loadMerchantCoupons, loadDashboard, loadMerchantReviews, saveProduct, deleteProduct, toggleProduct, saveStall, toggleStall, saveCoupon, toggleCoupon, toggleStoreStatus, uploadImage, setAvatar, resolveImage, setStore, setOrderMode, setStall, addToCart, updateCartQuantity, clearCart, toggleFavorite, sendCode, login, register, loginByCode, logout, createOrder, findOrder, payOrder, completeOrder, refreshOrder, submitReview, loadMyReviews, acceptOrder, readyOrder, reorder, resetStore }
}
