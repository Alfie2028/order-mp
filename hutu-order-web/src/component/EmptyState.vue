<template>
  <view class="empty-state">
    <image class="empty-mascot" src="/static/image/kangaroo.png" mode="aspectFit" />
    <view class="empty-title">{{ title }}</view>
    <view class="empty-desc">{{ description }}</view>
    <button v-if="action || actionText" class="empty-action" @click="$emit('action')">{{ action || actionText }}</button>
  </view>
</template>
<script setup>
defineProps({ title: { type: String, default: '暂无内容' }, description: { type: String, default: '' }, action: { type: String, default: '' }, actionText: { type: String, default: '' } })
defineEmits(['action'])
</script>
<style scoped>
.empty-state { padding: 90rpx 40rpx; text-align: center; }
.empty-mascot { width: 140rpx; height: 140rpx; margin: 0 auto 20rpx; opacity: .85; }
.empty-title { font-size: 30rpx; font-weight: 800; color: #222426; }
.empty-desc { margin-top: 10rpx; color: #8E929E; font-size: 23rpx; }
.empty-action {
  display: inline-flex;
  margin-top: 30rpx;
  padding: 16rpx 40rpx;
  border-radius: 36rpx;
  color: #222426;
  background: #FFC300;
  font-size: 24rpx;
  font-weight: 800;
  box-shadow: 0 4rpx 14rpx rgba(255, 195, 0, .4);
}
</style>
