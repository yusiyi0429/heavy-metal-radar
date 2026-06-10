const { getShows } = require('../../utils/api')

Page({
  data: {
    query: '',
    shows: [],
    onlyOnSale: false,
    searched: false,
    searching: false,
  },

  // 防抖搜索定时器
  debounceTimer: null,

  onLoad() {
    this.debounceSearch = this._debounce(this._doSearch.bind(this), 400)
  },

  onUnload() {
    if (this.debounceTimer) {
      clearTimeout(this.debounceTimer)
    }
  },

  _debounce(fn, delay) {
    return (...args) => {
      if (this.debounceTimer) clearTimeout(this.debounceTimer)
      this.debounceTimer = setTimeout(() => fn(...args), delay)
    }
  },

  onSearch() {
    this.setData({ searched: true, searching: true })
    this._doSearch()
  },

  _doSearch() {
    const params = { keyword: this.data.query }

    getShows(params)
      .then(data => {
        let shows = data.shows || []
        if (this.data.onlyOnSale) {
          shows = shows.filter(s => s.status === 'on_sale')
        }
        this.setData({ shows, searching: false })
      })
      .catch(err => {
        const msg = err.message === '请求超时' ? '请求超时，请重试' : '搜索失败'
        wx.showToast({ title: msg, icon: 'none' })
        this.setData({ searching: false })
      })
  },

  onInput(e) {
    const value = e.detail.value
    this.setData({ query: value })
    // 输入时自动触发防抖搜索
    if (value.trim()) {
      this.debounceSearch()
    }
  },

  onToggleFilter(e) {
    this.setData({ onlyOnSale: e.detail.value })
    if (this.data.searched && this.data.query.trim()) {
      this.onSearch()
    }
  },
})
