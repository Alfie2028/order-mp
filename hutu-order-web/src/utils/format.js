export function formatMoney(cents = 0) {
  return `¥${(Number(cents || 0) / 100).toFixed(2)}`
}

export function formatDistance(meters = 0) {
  return meters < 1000 ? `${Math.round(meters)}m` : `${(meters / 1000).toFixed(1)}km`
}

export function formatDateTime(timestamp) {
  const date = new Date(timestamp)
  const pad = (value) => ('0' + value).slice(-2)
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())} ${pad(date.getHours())}:${pad(date.getMinutes())}`
}

export function createOrderNo() {
  const now = new Date()
  const stamp = `${now.getFullYear()}${('0' + (now.getMonth() + 1)).slice(-2)}${('0' + now.getDate()).slice(-2)}`
  return `XC${stamp}${String(now.getTime()).slice(-6)}`
}
