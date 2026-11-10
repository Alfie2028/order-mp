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
function goBack() {
  if (getCurrentPages().length > 1) uni.navigateBack({ fail: () => { uni.switchTab({ url: '/pages/home/index' }) } })
  else uni.switchTab({ url: '/pages/home/index' })
}
</script>

<template>
  <view class="page-shell login-page">
    <view class="login-header">
      <button class="top-back" @click="goBack">‹</button>
      <view class="mascot-wrap">
        <image class="mascot-img" src="/static/image/kangaroo.png" mode="aspectFit" />
      </view>
      <text class="title">{{ mode === 'login' ? '美团校园 · 登录' : mode === 'register' ? '美团校园 · 注册' : '验证码快捷登录' }}</text>
      <text class="subtitle">{{ mode === 'register' ? '创建账户，开启美好校园生活' : '登录后同步订单、神券、收藏与购物车' }}</text>
    </view>

    <view class="form-card card">
      <view class="mode-tabs">
        <button class="tab-left" :class="{ active: mode === 'login' }" @click="switchMode('login')">账号密码</button>
        <button :class="{ active: mode === 'register' }" @click="switchMode('register')">新用户注册</button>
      </view>

      <view class="field">
        <text class="field-label">邮箱</text>
        <input v-model="email" placeholder="请输入校园邮箱或常用邮箱" maxlength="80" @confirm="submit" />
      </view>

      <view v-if="mode !== 'code-login'" class="field">
        <text class="field-label">密码</text>
        <input v-model="password" password placeholder="请输入密码（至少 6 位）" maxlength="30" @confirm="submit" />
      </view>

      <view v-if="mode !== 'login'" class="field">
        <text class="field-label">验证码</text>
        <input v-model="code" placeholder="6 位验证码" maxlength="6" type="number" @confirm="submit" />
        <button class="code-btn" :class="{ disabled: countdown > 0 || sending }" @click="sendCode">
          {{ sending ? '发送中' : countdown > 0 ? countdown + 's' : '获取验证码' }}
        </button>
      </view>

      <button class="submit-button" :class="{ disabled: submitting }" @click="submit">
        {{ mode === 'login' ? '立即登录' : mode === 'register' ? '注册并登录' : '验证码登录' }}
      </button>

      <view class="switch-line">
        <text @click="switchMode(mode === 'login' ? 'code-login' : 'login')">
          {{ mode === 'login' ? '使用邮箱验证码登录 ›' : mode === 'code-login' ? '使用密码登录 ›' : '' }}
        </text>
      </view>
    </view>

    <view class="tips">
      <text class="tip-title">美团校园 · 演示说明</text>
      <text class="tip-line">普通用户：test@example.com / 123456</text>
      <text class="tip-line">入驻商家：merchant@example.com / 123456</text>
      <text class="tip-line">验证码由系统代发，请留意邮件通知</text>
    </view>
  </view>
</template>

<style scoped lang="scss">
.login-page { padding-bottom: 60rpx; background: #F7F8FA; }
.login-header {
  position: relative;
  padding: calc(72rpx + env(safe-area-inset-top)) 30rpx 70rpx;
  background: linear-gradient(135deg, #FFD21E 0%, #FFC300 70%, #FFAE00 100%);
  color: #222426;
  text-align: center;
}
.top-back {
  position: absolute;
  left: 26rpx;
  top: calc(22rpx + env(safe-area-inset-top));
  width: 68rpx;
  height: 68rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: rgba(0, 0, 0, .08);
  color: #222426;
  font-size: 48rpx;
  line-height: 1;
}
.mascot-wrap {
  display: flex;
  justify-content: center;
  margin-bottom: 12rpx;
}
.mascot-img {
  width: 130rpx;
  height: 130rpx;
}
.title {
  display: block;
  font-size: 42rpx;
  font-weight: 900;
  color: #222426;
}
.subtitle {
  display: block;
  margin-top: 8rpx;
  font-size: 22rpx;
  color: rgba(34, 36, 38, .75);
}

.form-card {
  margin: -36rpx 24rpx 0;
  position: relative;
  padding: 36rpx 30rpx;
  border-radius: 28rpx;
}
.mode-tabs {
  display: flex;
  padding: 8rpx;
  border-radius: 20rpx;
  background: #F3F4F7;
  margin-bottom: 16rpx;
}
.mode-tabs button {
  display: flex;
  flex: 1;
  align-items: center;
  justify-content: center;
  height: 76rpx;
  border-radius: 16rpx;
  color: #8E929E;
  font-size: 26rpx;
  font-weight: 600;
}
.mode-tabs .tab-left { margin-right: 12rpx; }
.mode-tabs button.active {
  background: #FFC300;
  color: #222426;
  font-weight: 800;
  box-shadow: 0 4rpx 12rpx rgba(255, 195, 0, .3);
}

.field {
  display: flex;
  align-items: center;
  min-height: 104rpx;
  border-bottom: 1rpx solid #F0F0F2;
}
.field-label {
  width: 110rpx;
  flex-shrink: 0;
  font-weight: 700;
  font-size: 26rpx;
  color: #222426;
}
.field input {
  flex: 1;
  margin-right: 16rpx;
  font-size: 26rpx;
  color: #222426;
}
.code-btn {
  flex-shrink: 0;
  height: 64rpx;
  line-height: 64rpx;
  padding: 0 20rpx;
  margin: 0;
  border-radius: 32rpx;
  background: #FFF9E6;
  color: #8C5E00;
  font-size: 23rpx;
  font-weight: 700;
}
.code-btn.disabled {
  background: #F3F4F7;
  color: #8E929E;
}

.submit-button {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 90rpx;
  margin-top: 36rpx;
  border-radius: 45rpx;
  background: #FFC300;
  color: #222426;
  font-size: 30rpx;
  font-weight: 800;
  box-shadow: 0 8rpx 20rpx rgba(255, 195, 0, .4);
}
.submit-button.disabled { opacity: .5; }

.switch-line {
  margin-top: 26rpx;
  text-align: center;
}
.switch-line text {
  font-size: 24rpx;
  color: #8C5E00;
  font-weight: 700;
}

.tips {
  margin: 34rpx 24rpx 0;
  padding: 26rpx;
  border: 2rpx dashed #E5E6EB;
  border-radius: 20rpx;
  background: #fff;
}
.tip-title { font-size: 24rpx; font-weight: 800; color: #222426; display: block; }
.tip-line { margin-top: 8rpx; font-size: 21rpx; color: #8E929E; display: block; }
</style>
