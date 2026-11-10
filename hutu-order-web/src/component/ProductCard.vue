<template>
  <view class="product-card" :class="{ 'sold-out': !product.isActive }" @click="$emit('open', product)">
    <view class="product-image-wrap">
      <image v-if="!imageFailed" class="product-image" :src="product.image" mode="aspectFit" @error="imageFailed = true" />
      <view v-else class="product-fallback">{{ product.fallback }}</view>
      <text v-if="product.badge" class="badge">{{ product.badge }}</text>
      <text v-if="!product.isActive" class="sold-tag">售罄</text>
    </view>
    <view class="product-info">
      <view class="product-name">{{ product.name }}</view>
      <view class="product-desc">{{ product.subtitle }}</view>
      <view class="product-sales">{{ product.stallName }}</view>
      <view class="product-bottom">
        <view class="price-wrap">
          <text class="price">{{ formatMoney(product.priceCents) }}</text>
          <text v-if="product.originalPriceCents" class="original">{{ formatMoney(product.originalPriceCents) }}</text>
        </view>
        <button class="add-button" :class="{ disabled: !product.isActive }" aria-label="加入购物车" @click.stop="$emit('add', product)">
          <text class="plus-icon">＋</text>
        </button>
      </view>
    </view>
  </view>
</template>
<script setup>
import { ref } from 'vue'
import { formatMoney } from '@/utils/format'
defineProps({ product: { type: Object, required: true } })
defineEmits(['open', 'add'])
const imageFailed = ref(false)
</script>
<style scoped lang="scss">
.product-card {
  display: flex;
  margin-bottom: 16rpx;
  padding: 18rpx 16rpx;
  border: 1rpx solid rgba(0, 0, 0, .04);
  border-radius: 20rpx;
  background: #fff;
  box-shadow: 0 4rpx 14rpx rgba(0, 0, 0, .03);
  transition: all .15s ease;
}
.product-image-wrap {
  position: relative;
  flex: 0 0 156rpx;
  height: 166rpx;
  margin-right: 16rpx;
  border-radius: 16rpx;
  overflow: hidden;
  background: #f8f8fa;
}
.product-image { width: 100%; height: 100%; transform: scale(1.04); }
.product-fallback {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  color: #c78800;
  font-size: 24rpx;
  font-weight: 700;
  letter-spacing: 2rpx;
  background: linear-gradient(145deg, #FFF6DD, #FFE9B8);
}
.badge {
  position: absolute;
  left: 0;
  top: 0;
  padding: 4rpx 10rpx;
  border-radius: 0 0 10rpx 0;
  color: #fff;
  background: linear-gradient(135deg, #FF6040, #FF3824);
  font-size: 16rpx;
  font-weight: 700;
}
.sold-tag {
  position: absolute;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  padding: 8rpx 16rpx;
  border-radius: 8rpx;
  color: #fff;
  background: rgba(30, 30, 32, .75);
  font-size: 22rpx;
  font-weight: 700;
  letter-spacing: 2rpx;
}
.product-card.sold-out .product-image { opacity: .5; }
.product-info { min-width: 0; flex: 1; display: flex; flex-direction: column; }
.product-name { font-size: 28rpx; font-weight: 800; color: #222426; }
.product-desc {
  margin-top: 6rpx;
  color: #8E929E;
  font-size: 20rpx;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
  overflow: hidden;
}
.product-sales { margin-top: 6rpx; color: #A5A8B2; font-size: 18rpx; }
.product-bottom { display: flex; align-items: flex-end; justify-content: space-between; margin-top: auto; }
.price-wrap { display: flex; align-items: baseline; }
.price { font-size: 32rpx; font-weight: 800; color: #FF4B3E; }
.original { margin-left: 10rpx; color: #BBB; text-decoration: line-through; font-size: 20rpx; }

/* 圆形添加按钮 (Meituan Style Round Add Button) */
.add-button {
  flex: 0 0 54rpx;
  width: 54rpx;
  height: 54rpx;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  color: #222426;
  background: #FFC300;
  box-shadow: 0 4rpx 12rpx rgba(255, 195, 0, .45);
  font-size: 32rpx;
  font-weight: 900;
  line-height: 1;
  transition: transform .1s ease;
}
.add-button:active { transform: scale(.92); }
.add-button.disabled { background: #E0E2E7; color: #9AA0A8; box-shadow: none; }
.plus-icon { display: block; line-height: 1; font-weight: 900; transform: translateY(-1rpx); }
</style>
