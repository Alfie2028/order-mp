// 请求层：统一封装 uni.request，处理 BASE_URL / token / 响应解包
// 内网穿透后把 BASE_URL 改成公网域名（如 https://xxx.free.bufpay.com 的穿透地址）
const BASE_URL = 'https://campus-order.learnshare.uk'

function request(path, { method = 'GET', data = {} } = {}) {
  const token = uni.getStorageSync('TOKEN')
  return new Promise((resolve, reject) => {
    uni.request({
      url: BASE_URL + path,
      method,
      data,
      header: {
        'Content-Type': 'application/json',
        'Bypass-Tunnel-Reminder': 'true',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      success: (res) => {
        const body = res.data
        if (body && body.code === 0) {
          resolve(body.data)
        } else {
          const msg = (body && body.msg) || '请求失败'
          uni.showToast({ title: msg, icon: 'none' })
          reject(new Error(msg))
        }
      },
      fail: (err) => {
        uni.showToast({ title: '网络连接失败', icon: 'none' })
        reject(err)
      },
    })
  })
}

export const get = (path, data) => request(path, { method: 'GET', data })
export const post = (path, data) => request(path, { method: 'POST', data })
export const put = (path, data) => request(path, { method: 'PUT', data })
export const del = (path, data) => request(path, { method: 'DELETE', data })

// 文件上传：uni.uploadFile 封装，字段名固定为 file（后端 UploadFile = File(...)）
export function upload(path, filePath) {
  const token = uni.getStorageSync('TOKEN')
  return new Promise((resolve, reject) => {
    uni.uploadFile({
      url: BASE_URL + path,
      filePath,
      name: 'file',
      header: {
        'Bypass-Tunnel-Reminder': 'true',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      success: (res) => {
        try {
          const body = JSON.parse(res.data)
          if (body && body.code === 0) resolve(body.data)
          else {
            const msg = (body && body.msg) || '上传失败'
            uni.showToast({ title: msg, icon: 'none' })
            reject(new Error(msg))
          }
        } catch (err) {
          uni.showToast({ title: '上传失败', icon: 'none' })
          reject(err)
        }
      },
      fail: (err) => {
        uni.showToast({ title: '网络连接失败', icon: 'none' })
        reject(err)
      },
    })
  })
}

export default request
export { BASE_URL }
