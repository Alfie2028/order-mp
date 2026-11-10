// 微信小程序与各端顶部导航栏安全区与底部安全区计算工具
export function getNavLayout() {
  let statusBarHeight = 24
  let navBarHeight = 44
  let capsuleTop = 26
  let capsuleHeight = 32
  let capsuleRight = 12
  let bottomSafe = 0

  try {
    const sys = (uni.getWindowInfo && typeof uni.getWindowInfo === 'function')
      ? uni.getWindowInfo()
      : (uni.getSystemInfoSync ? uni.getSystemInfoSync() : null)

    if (sys) {
      if (typeof sys.statusBarHeight === 'number' && sys.statusBarHeight > 0) {
        statusBarHeight = sys.statusBarHeight
        capsuleTop = statusBarHeight + 6
      }
      if (sys.safeAreaInsets && typeof sys.safeAreaInsets.bottom === 'number') {
        bottomSafe = sys.safeAreaInsets.bottom
      } else if (sys.screenHeight && sys.safeArea && typeof sys.safeArea.bottom === 'number') {
        bottomSafe = Math.max(0, sys.screenHeight - sys.safeArea.bottom)
      }
    }

    // #ifdef MP-WEIXIN
    let capsule = null
    try {
      capsule = (uni.getMenuButtonBoundingClientRect && typeof uni.getMenuButtonBoundingClientRect === 'function')
        ? uni.getMenuButtonBoundingClientRect()
        : null
    } catch (err) {}

    if (capsule && capsule.top && capsule.left && capsule.height) {
      capsuleTop = capsule.top
      capsuleHeight = capsule.height
      const topGap = Math.max(4, capsule.top - statusBarHeight)
      navBarHeight = capsule.height + topGap * 2
      const winW = (sys && sys.windowWidth) ? sys.windowWidth : 375
      capsuleRight = Math.max(88, (winW - capsule.left) + 10)
    } else {
      capsuleTop = Math.max(statusBarHeight + 6, 48)
      capsuleHeight = 32
      capsuleRight = 100
      navBarHeight = 44
    }
    // #endif

    // #ifndef MP-WEIXIN
    capsuleRight = 12
    // #endif
  } catch (e) {
    // 降级兜底
    capsuleTop = 44
    capsuleRight = 100
  }

  const totalNavHeight = Math.max(capsuleTop + capsuleHeight + 8, statusBarHeight + navBarHeight)

  return {
    statusBarHeight,
    navBarHeight,
    capsuleTop,
    capsuleHeight,
    capsuleRight,
    totalNavHeight,
    bottomSafe,
  }
}
