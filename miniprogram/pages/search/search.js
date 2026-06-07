const { getShows } = require('../../utils/api')

Page({
  data: {
    query: '',
    shows: [],
    onlyOnSale: false,
    searched: false,
  },

  onSearch() {
    const params = { keyword: this.data.query }
    this.setData({ searched: true })

    getShows(params)
      .then(data => {
        let shows = data.shows || []
        if (this.data.onlyOnSale) {
          shows = shows.filter(s => s.status === 'on_sale')
        }
        this.setData({ shows })
      })
      .catch(() => {
        wx.showToast({ title: '搜索失败', icon: 'none' })
      })
  },

  onInput(e) {
    this.setData({ query: e.detail.value })
  },

  onToggleFilter(e) {
    this.setData({ onlyOnSale: e.detail.value })
    if (this.data.searched) {
      this.onSearch()
    }
  },
})
