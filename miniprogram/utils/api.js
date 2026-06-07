const app = getApp()

function request(path, method = 'GET', data = null) {
  return new Promise((resolve, reject) => {
    wx.request({
      url: app.globalData.baseUrl + path,
      method,
      data,
      header: { 'Content-Type': 'application/json' },
      success(res) {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(res.data)
        } else {
          reject(res)
        }
      },
      fail(err) {
        reject(err)
      },
    })
  })
}

function getShows(params = {}) {
  const qs = Object.keys(params)
    .filter(k => params[k] !== undefined && params[k] !== '')
    .map(k => `${k}=${encodeURIComponent(params[k])}`)
    .join('&')
  return request(`/api/shows${qs ? '?' + qs : ''}`)
}

function getConfig() {
  return request('/api/config')
}

function updateConfig(updates) {
  return request('/api/config', 'PUT', updates)
}

function triggerFetch() {
  return request('/api/fetch', 'POST')
}

function triggerNotify() {
  return request('/api/notify', 'POST')
}

function resetData() {
  return request('/api/reset', 'POST')
}

function healthCheck() {
  return request('/api/health')
}

module.exports = {
  getShows,
  getConfig,
  updateConfig,
  triggerFetch,
  triggerNotify,
  resetData,
  healthCheck,
}
