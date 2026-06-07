const { getConfig, getShows, triggerFetch } = require('../../utils/api')

Page({
  data: {
    shows: [],
    cities: [],
    selectedCity: '',
    loading: false,
    refreshing: false,
    empty: false,
  },

  onLoad() {
    this.loadConfig()
    this.loadShows()
  },

  onPullDownRefresh() {
    this.setData({ refreshing: true })
    this.loadShows().finally(() => {
      wx.stopPullDownRefresh()
      this.setData({ refreshing: false })
    })
  },

  loadConfig() {
    getConfig().then(cfg => {
      this.setData({ cities: cfg.cities || [], selectedCity: '' })
    }).catch(() => {})
  },

  loadShows() {
    this.setData({ loading: true })
    const params = {}
    if (this.data.selectedCity) params.city = this.data.selectedCity

    return getShows(params)
      .then(data => {
        this.setData({
          shows: data.shows || [],
          empty: (data.shows || []).length === 0,
        })
      })
      .catch(() => {
        wx.showToast({ title: '加载失败，请检查后端是否启动', icon: 'none' })
      })
      .finally(() => this.setData({ loading: false }))
  },

  onCityChange(e) {
    const idx = e.detail.value
    const city = this.data.cities[idx] || ''
    this.setData({ selectedCity: city })
    this.loadShows()
  },

  onRefresh() {
    this.setData({ loading: true })
    triggerFetch()
      .then(data => {
        const count = data.new_count || 0
        wx.showToast({ title: `发现 ${count} 场新演出`, icon: 'none' })
        return this.loadShows()
      })
      .catch(() => {
        wx.showToast({ title: '抓取失败', icon: 'none' })
        this.setData({ loading: false })
      })
  },
})
