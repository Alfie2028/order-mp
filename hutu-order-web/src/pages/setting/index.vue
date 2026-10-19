<script setup>
import { CAMPUS } from '@/data/catalog'
import { useAppStore } from '@/store/app'

const store = useAppStore()
function reset() {
  uni.showModal({ title: '恢复默认设置', content: '购物车、订单和偏好将恢复初始状态。', confirmColor: '#0637c9', success: ({ confirm }) => {
    if (!confirm) return
    store.resetStore()
    uni.showToast({ title: '已恢复初始状态', icon: 'success' })
  } })
}
function toast(text) { uni.showToast({ title: text, icon: 'none' }) }
</script>

<template>
  <view class="page-shell setting-page">
    <view class="setting-header"><button class="top-back" @click="uni.navigateBack()">‹</button><text class="header-title">设置</text><text class="header-sub">管理账户、通知与使用偏好</text></view>
    <view class="section">
      <view class="section-heading"><text class="section-title">基础设置</text></view>
      <view class="settings card">
        <view class="setting-row"><view><text class="row-title">默认位置</text><text class="row-copy">{{ CAMPUS.name }} · {{ CAMPUS.campus }}</text></view><text class="tag">已启用</text></view>
        <view class="setting-row"><view><text class="row-title">数据管理</text><text class="row-copy">购物车、订单与偏好设置</text></view><text class="tag">本地保存</text></view>
        <view class="setting-row last"><view><text class="row-title">服务范围</text><text class="row-copy">点餐、餐厅查询与订单管理</text></view><text class="safe">✓</text></view>
      </view>
    </view>
    <view class="section">
      <view class="section-heading"><text class="section-title">偏好设置</text></view>
      <view class="settings card">
        <button class="setting-row" @click="toast('消息提醒已开启')"><view><text class="row-title">订单消息提醒</text><text class="row-copy">制作与取餐状态通知</text></view><text class="arrow">›</text></button>
        <button class="setting-row" @click="toast('隐私与权限由系统设置统一管理')"><view><text class="row-title">隐私与权限</text><text class="row-copy">位置、通知与数据使用</text></view><text class="arrow">›</text></button>
        <button class="setting-row last" @click="toast('当前已是最新版本')"><view><text class="row-title">关于</text><text class="row-copy">校园点餐 v3.0.0</text></view><text class="arrow">›</text></button>
      </view>
    </view>
    <view class="section"><button class="reset-button" @click="reset">恢复默认设置</button><text class="reset-tip">购物车、订单与偏好将恢复初始状态</text></view>
  </view>
</template>

<style scoped lang="scss">
.setting-page{padding-bottom:60rpx}.setting-header{position:relative;padding:calc(92rpx + env(safe-area-inset-top)) 30rpx 56rpx;background:linear-gradient(145deg,#35231b,#684736);color:#fff}.top-back{position:absolute;left:26rpx;top:calc(22rpx + env(safe-area-inset-top));width:66rpx;height:66rpx;display:flex;align-items:center;justify-content:center;border-radius:50%;background:rgba(255,255,255,.12);color:white;font-size:48rpx;line-height:1}.setting-header text{display:block}.header-title{margin-top:14rpx;font-size:47rpx;font-weight:800}.header-sub{margin-top:9rpx;font-size:23rpx;color:rgba(255,255,255,.6)}.settings{padding:0 24rpx}.setting-row{display:flex;align-items:center;justify-content:space-between;width:100%;min-height:106rpx;border:0;border-bottom:1rpx solid var(--line);background:transparent;text-align:left;color:var(--ink)}.setting-row.last{border-bottom:0}.row-title,.row-copy{display:block}.row-title{font-size:26rpx;font-weight:700}.row-copy{margin-top:7rpx;color:var(--muted);font-size:20rpx}.tag{padding:7rpx 12rpx;border-radius:10rpx;background:var(--oat-100);color:var(--brand-700);font-size:18rpx}.safe{color:var(--green);font-size:31rpx}.arrow{font-size:36rpx;color:var(--muted)}.reset-button{display:flex;align-items:center;justify-content:center;width:100%;height:90rpx;border:1rpx solid #d6aaa3;border-radius:45rpx;color:var(--danger);font-size:26rpx;font-weight:700}.reset-tip{display:block;margin-top:15rpx;text-align:center;color:var(--muted);font-size:19rpx}
.setting-header{background:linear-gradient(145deg,#0637c9,#071a62)}
</style>
