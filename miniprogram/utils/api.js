const DEFAULT_TIMEOUT = 15000

let _baseUrl = ''

function getBaseUrl() {
  if (_baseUrl) return _baseUrl
  const app = getApp()
  _baseUrl = app ? app.globalData.baseUrl : 'http://localhost:5001'
  return _baseUrl
}

function request(path, method = 'GET', data = null, options = {}) {
  return new Promise((resolve, reject) => {
    const baseUrl = getBaseUrl()
    let timer = null
    let completed = false

    const req = wx.request({
      url: baseUrl + path,
      method,
      data,
      header: { 'Content-Type': 'application/json' },
      timeout: options.timeout || DEFAULT_TIMEOUT,
      success(res) {
        if (completed) return
        completed = true
        clearTimeout(timer)
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(res.data)
        } else {
          const err = new Error(`HTTP ${res.statusCode}`)
          err.statusCode = res.statusCode
          err.data = res.data
          reject(err)
        }
      },
      fail(err) {
        if (completed) return
        completed = true
        clearTimeout(timer)
        reject(err)
      },
    })

    timer = setTimeout(() => {
      if (completed) return
      completed = true
      req && req.abort && req.abort()
      reject(new Error('请求超时'))
    }, options.timeout || DEFAULT_TIMEOUT)
  })
}

// 带 loading 的请求封装
function requestWithLoading(path, method, data, msg = '加载中...') {
  wx.showLoading({ title: msg, mask: true })
  return request(path, method, data).finally(() => {
    wx.hideLoading()
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
  request,
  requestWithLoading,
  getShows,
  getConfig,
  updateConfig,
  triggerFetch,
  triggerNotify,
  resetData,
  healthCheck,
}
