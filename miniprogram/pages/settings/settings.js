const { getConfig, updateConfig, resetData } = require('../../utils/api')

Page({
  data: {
    keywords: [],
    keywordInput: '',
    cities: [],
    cityInput: '',
    enablePush: true,
    saving: false,
    showResetDialog: false,
  },

  onLoad() {
    this.loadConfig()
  },

  loadConfig() {
    getConfig().then(cfg => {
      this.setData({
        keywords: cfg.keywords || [],
        cities: cfg.cities || [],
        enablePush: cfg.enable_push !== false,
      })
    }).catch(err => {
      const msg = err.message === '请求超时' ? '请求超时' : '加载配置失败'
      wx.showToast({ title: msg, icon: 'none' })
    })
  },

  onKeywordInput(e) {
    this.setData({ keywordInput: e.detail.value })
  },

  addKeyword() {
    const kw = this.data.keywordInput.trim()
    if (!kw) return
    if (this.data.keywords.includes(kw)) {
      wx.showToast({ title: '关键词已存在', icon: 'none' })
      return
    }
    this.setData({
      keywords: [...this.data.keywords, kw],
      keywordInput: '',
    })
  },

  removeKeyword(e) {
    const idx = e.currentTarget.dataset.index
    const keywords = [...this.data.keywords]
    keywords.splice(idx, 1)
    this.setData({ keywords })
  },

  onCityInput(e) {
    this.setData({ cityInput: e.detail.value })
  },

  addCity() {
    const city = this.data.cityInput.trim()
    if (!city) return
    if (this.data.cities.includes(city)) {
      wx.showToast({ title: '城市已存在', icon: 'none' })
      return
    }
    this.setData({
      cities: [...this.data.cities, city],
      cityInput: '',
    })
  },

  removeCity(e) {
    const idx = e.currentTarget.dataset.index
    const cities = [...this.data.cities]
    cities.splice(idx, 1)
    this.setData({ cities })
  },

  onPushToggle(e) {
    this.setData({ enablePush: e.detail.value })
  },

  onSave() {
    this.setData({ saving: true })
    updateConfig({
      keywords: this.data.keywords,
      cities: this.data.cities,
      enable_push: this.data.enablePush,
    })
      .then(() => {
        wx.showToast({ title: '保存成功', icon: 'success' })
      })
      .catch(err => {
        const msg = err.message === '请求超时' ? '请求超时' : '保存失败'
        wx.showToast({ title: msg, icon: 'none' })
      })
      .finally(() => this.setData({ saving: false }))
  },

  onReset() {
    this.setData({ showResetDialog: true })
  },

  onDialogConfirm() {
    this.setData({ showResetDialog: false })
    resetData()
      .then(() => {
        wx.showToast({ title: '已重置', icon: 'success' })
      })
      .catch(err => {
        const msg = err.message === '请求超时' ? '请求超时' : '重置失败'
        wx.showToast({ title: msg, icon: 'none' })
      })
  },

  onDialogCancel() {
    this.setData({ showResetDialog: false })
  },
})
