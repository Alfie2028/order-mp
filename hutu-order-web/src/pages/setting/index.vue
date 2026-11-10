<script setup>
import { CAMPUS } from '@/data/catalog'
import { useAppStore } from '@/store/app'

const store = useAppStore()
function reset() {
  uni.showModal({ title: '恢复默认设置', content: '购物车、订单和偏好将恢复初始状态。', confirmColor: '#FF4B3E', success: ({ confirm }) => {
    if (!confirm) return
    store.resetStore()
    uni.showToast({ title: '已恢复初始状态', icon: 'success' })
  } })
}
function toast(text) { uni.showToast({ title: text, icon: 'none' }) }
function goBack() {
  if (getCurrentPages().length > 1) uni.navigateBack({ fail: () => { uni.switchTab({ url: '/pages/home/index' }) } })
  else uni.switchTab({ url: '/pages/home/index' })
}
</script>

<template>
  <view class="page-shell setting-page">
    <view class="setting-header">
      <button class="top-back" @click="goBack">‹</button>
      <text class="header-title">系统设置</text>
      <text class="header-sub">美团校园 · 管理账户、通知与偏好</text>
    </view>
    <view class="section">
      <view class="section-heading"><text class="section-title">基础设置</text></view>
      <view class="settings card">
        <view class="setting-row">
          <view><text class="row-title">当前校区</text><text class="row-copy">{{ CAMPUS.name }} · {{ CAMPUS.campus }}</text></view>
          <text class="tag">已定位</text>
        </view>
        <view class="setting-row">
          <view><text class="row-title">数据缓存</text><text class="row-copy">购物车、点单历史与神券</text></view>
          <text class="tag">本地同步</text>
        </view>
        <view class="setting-row last">
          <view><text class="row-title">服务范围</text><text class="row-copy">点餐、档口查询与订单送达</text></view>
          <text class="safe">✓</text>
        </view>
      </view>
    </view>
    <view class="section">
      <view class="section-heading"><text class="section-title">偏好设置</text></view>
      <view class="settings card">
        <button class="setting-row" @click="toast('订单制作与出餐通知已开启')">
          <view><text class="row-title">出餐取餐通知</text><text class="row-copy">制作完成与取餐码提醒</text></view>
          <text class="arrow">›</text>
        </button>
        <button class="setting-row" @click="toast('隐私权限由系统安全统一管理')">
          <view><text class="row-title">隐私与权限</text><text class="row-copy">定位、通知与相册权限</text></view>
          <text class="arrow">›</text>
        </button>
        <button class="setting-row last" @click="toast('当前已是最新版本')">
          <view><text class="row-title">关于我们</text><text class="row-copy">美团校园点餐 v3.2.0</text></view>
          <text class="arrow">›</text>
        </button>
      </view>
    </view>
    <view class="section">
      <button class="reset-button" @click="reset">恢复默认设置</button>
      <text class="reset-tip">恢复后购物车与本地缓存将被清除</text>
    </view>
  </view>
</template>

<style scoped lang="scss">
.setting-page { padding-bottom: 60rpx; background: #F7F8FA; }
.setting-header {
  position: relative;
  padding: calc(64rpx + env(safe-area-inset-top)) 30rpx 56rpx;
  background: linear-gradient(135deg, #FFD21E 0%, #FFC300 70%, #FFAE00 100%);
  color: #222426;
}
.top-back {
  position: absolute;
  left: 26rpx;
  top: calc(22rpx + env(safe-area-inset-top));
  width: 66rpx;
  height: 66rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: rgba(0, 0, 0, .08);
  color: #222426;
  font-size: 48rpx;
  line-height: 1;
}
.header-title { margin-top: 14rpx; font-size: 44rpx; font-weight: 900; color: #222426; display: block; }
.header-sub { margin-top: 8rpx; font-size: 22rpx; color: rgba(34, 36, 38, .75); display: block; }

.settings { padding: 4rpx 24rpx; }
.setting-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  min-height: 104rpx;
  border: 0;
  border-bottom: 1rpx solid #F0F0F2;
  background: transparent;
  text-align: left;
  color: #222426;
}
.setting-row.last { border-bottom: 0; }
.row-title { font-size: 26rpx; font-weight: 800; color: #222426; display: block; }
.row-copy { margin-top: 6rpx; color: #8E929E; font-size: 20rpx; display: block; }
.tag {
  padding: 6rpx 14rpx;
  border-radius: 12rpx;
  background: #FFF7DB;
  color: #8C5E00;
  font-size: 19rpx;
  font-weight: 700;
}
.safe { color: #07C160; font-size: 28rpx; font-weight: 900; }
.arrow { font-size: 34rpx; color: #8E929E; }

.reset-button {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 88rpx;
  border: 2rpx solid #FFCDD2;
  border-radius: 44rpx;
  color: #FF4B3E;
  background: #fff;
  font-size: 27rpx;
  font-weight: 800;
}
.reset-tip {
  display: block;
  margin-top: 14rpx;
  text-align: center;
  color: #8E929E;
  font-size: 20rpx;
}
</style>
