<script setup>
import { ref, onUnmounted } from 'vue'
import { useAppStore } from '@/store/app'

const store = useAppStore()
const mode = ref('login') // login / register / code-login
const email = ref('')
const password = ref('')
const code = ref('')
const submitting = ref(false)
const sending = ref(false)
const countdown = ref(0)
let timer = null

function startCountdown() {
  countdown.value = 60
  if (timer) clearInterval(timer)
  timer = setInterval(() => {
    countdown.value--
    if (countdown.value <= 0) { clearInterval(timer); timer = null }
  }, 1000)
}

onUnmounted(() => { if (timer) clearInterval(timer) })

async function sendCode() {
  const addr = email.value.trim()
  if (!addr || !addr.includes('@')) { uni.showToast({ title: '请输入正确的邮箱', icon: 'none' }); return }
  if (countdown.value > 0 || sending.value) return
  sending.value = true
  try {
    const purpose = mode.value === 'register' ? 'register' : 'login'
    await store.sendCode(addr, purpose)
    startCountdown()
    uni.showToast({ title: '验证码已发送', icon: 'none' })
  } catch (e) {
    // 错误提示已由请求层统一 toast
  } finally {
    sending.value = false
  }
}

async function submit() {
  if (submitting.value) return
  const addr = email.value.trim()
  if (!addr || !addr.includes('@')) { uni.showToast({ title: '请输入正确的邮箱', icon: 'none' }); return }
  if (mode.value !== 'login') {
    if (!code.value) { uni.showToast({ title: '请输入验证码', icon: 'none' }); return }
  }
  if (mode.value !== 'code-login') {
    if (password.value.length < 6) { uni.showToast({ title: '密码至少 6 位', icon: 'none' }); return }
  }
  submitting.value = true
  uni.showLoading({ title: mode.value === 'register' ? '注册中' : '登录中' })
  try {
    if (mode.value === 'login') await store.login(addr, password.value)
    else if (mode.value === 'register') await store.register(addr, code.value, password.value)
    else await store.loginByCode(addr, code.value)
    uni.hideLoading()
    uni.showToast({ title: mode.value === 'register' ? '注册成功' : '登录成功', icon: 'success' })
    setTimeout(() => {
      if (store.state.user && store.state.user.role === 'merchant') {
        uni.redirectTo({ url: '/pages/merchant/index' })
      } else {
        const pages = getCurrentPages()
        if (pages.length > 1) uni.navigateBack()
        else uni.switchTab({ url: '/pages/my/index' })
      }
    }, 400)
  } catch (e) {
    uni.hideLoading()
  } finally {
    submitting.value = false
  }
}

function switchMode(next) {
  if (next === mode.value) return
  mode.value = next
  password.value = ''
  code.value = ''
}
</script>

<template>
  <view class="page-shell login-page">
    <view class="login-header">
      <button class="top-back" @click="uni.navigateBack()">‹</button>
      <text class="title">{{ mode === 'login' ? '登录' : mode === 'register' ? '注册' : '验证码登录' }}</text>
      <text class="subtitle">{{ mode === 'register' ? '创建账户，开启校园点餐' : '登录后同步订单、收藏与购物车' }}</text>
    </view>

    <view class="form-card card">
      <view class="mode-tabs">
        <button class="tab-left" :class="{ active: mode === 'login' }" @click="switchMode('login')">登录</button>
        <button :class="{ active: mode === 'register' }" @click="switchMode('register')">注册</button>
      </view>

      <view class="field">
        <text>邮箱</text>
        <input v-model="email" placeholder="请输入邮箱" maxlength="80" @confirm="submit" />
      </view>

      <view v-if="mode !== 'code-login'" class="field">
        <text>密码</text>
        <input v-model="password" password placeholder="请输入密码（至少 6 位）" maxlength="30" @confirm="submit" />
      </view>

      <view v-if="mode !== 'login'" class="field">
        <text>验证码</text>
        <input v-model="code" placeholder="6 位验证码" maxlength="6" type="number" @confirm="submit" />
        <button class="code-btn" :class="{ disabled: countdown > 0 || sending }" @click="sendCode">
          {{ sending ? '发送中' : countdown > 0 ? countdown + 's' : '获取验证码' }}
        </button>
      </view>

      <button class="submit-button" :class="{ disabled: submitting }" @click="submit">
        {{ mode === 'login' ? '登录' : mode === 'register' ? '注册并登录' : '验证码登录' }}
      </button>

      <view class="switch-line">
        <text @click="switchMode(mode === 'login' ? 'code-login' : 'login')">
          {{ mode === 'login' ? '使用验证码登录' : mode === 'code-login' ? '使用密码登录' : '' }}
        </text>
      </view>
    </view>

    <view class="tips">
      <text class="tip-title">演示账号</text>
      <text class="tip-line">用户端：test@example.com / 123456</text>
      <text class="tip-line">商家端：merchant@example.com / 123456</text>
    </view>
  </view>
</template>

<style scoped lang="scss">
.login-page { padding-bottom: 60rpx; }
.login-header { position: relative; padding: calc(92rpx + env(safe-area-inset-top)) 30rpx 70rpx; background: linear-gradient(145deg, #0637c9, #071a62); color: #fff; }
.top-back { position: absolute; left: 26rpx; top: calc(22rpx + env(safe-area-inset-top)); width: 66rpx; height: 66rpx; display: flex; align-items: center; justify-content: center; border-radius: 50%; background: rgba(255,255,255,.12); color: #fff; font-size: 48rpx; line-height: 1; }
.eyebrow, .title, .subtitle { display: block; }
.eyebrow { font-size: 18rpx; letter-spacing: 5rpx; color: #edcf91; }
.title { margin-top: 14rpx; font-size: 47rpx; font-weight: 800; }
.subtitle { margin-top: 9rpx; font-size: 22rpx; color: rgba(255,255,255,.65); }
.form-card { margin: -40rpx 28rpx 0; position: relative; padding: 30rpx 28rpx; }
.mode-tabs { display: flex; padding: 8rpx; border-radius: 20rpx; background: var(--oat-50); }
.mode-tabs button { display: flex; flex: 1; align-items: center; justify-content: center; height: 74rpx; border-radius: 16rpx; color: var(--muted); font-size: 26rpx; }
.mode-tabs .tab-left { margin-right: 12rpx; }
.mode-tabs button.active { background: var(--brand-800); color: #fff; font-weight: 700; }
.field { display: flex; align-items: center; min-height: 100rpx; border-bottom: 1rpx solid var(--line); }
.field > text { width: 96rpx; flex-shrink: 0; margin-right: 16rpx; font-weight: 600; font-size: 25rpx; }
.field input { flex: 1; margin-right: 16rpx; font-size: 25rpx; }
.code-btn { flex-shrink: 0; height: 60rpx; line-height: 60rpx; padding: 0 8rpx; margin: 0; border-radius: 12rpx; background: transparent; color: var(--brand); font-size: 24rpx; }
.code-btn.disabled { color: var(--muted); }
.submit-button { display: flex; align-items: center; justify-content: center; width: 100%; height: 88rpx; margin-top: 30rpx; border-radius: 20rpx; background: var(--brand); color: #fff; font-size: 28rpx; font-weight: 700; }
.submit-button.disabled { opacity: .5; }
.switch-line { margin-top: 22rpx; text-align: center; }
.switch-line text { font-size: 23rpx; color: var(--brand); }
.tips { margin: 34rpx 28rpx 0; padding: 26rpx; border: 1rpx dashed #d8cec2; border-radius: 18rpx; }
.tips text { display: block; }
.tip-title { font-size: 23rpx; font-weight: 700; color: var(--ink); }
.tip-line { margin-top: 10rpx; font-size: 21rpx; color: var(--muted); }
</style>
