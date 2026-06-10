const { getConfig, getShows, triggerFetch } = require('../../utils/api')

Page({
  data: {
    shows: [],
    cities: [],
    selectedCity: '',
    cityIndex: 0,
    loading: true,
    refreshing: false,
    empty: false,
  },

  onLoad() {
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
    }).catch(() => {
      wx.showToast({ title: '加载配置失败', icon: 'none' })
    })
  },

  loadShows() {
    this.setData({ loading: true })
    const params = {}
    if (this.data.selectedCity) params.city = this.data.selectedCity

    // 同时拉全量数据（供城市列表）和筛选数据（供展示）
    return Promise.all([getShows({}), getShows(params)])
      .then(([all, filtered]) => {
        const cities = this.extractCities(all.shows || [])
        const cityIndex = Math.max(0, cities.indexOf(this.data.selectedCity))
        this.setData({
          shows: filtered.shows || [],
          empty: (filtered.shows || []).length === 0,
          cities,
          cityIndex,
        })
      })
      .catch(() => {
        wx.showToast({ title: '加载失败，请检查后端是否启动', icon: 'none' })
      })
      .finally(() => this.setData({ loading: false }))
  },

  extractCities(shows) {
    const citySet = new Set()
    shows.forEach(s => { if (s.city) citySet.add(s.city) })
    return Array.from(citySet).sort()
  },

  onCityChange(e) {
    const idx = e.detail.value
    const city = this.data.cities[idx] || ''
    this.setData({ selectedCity: city, cityIndex: idx })
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
