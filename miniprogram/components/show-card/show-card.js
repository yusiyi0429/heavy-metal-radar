const { PLATFORMS, STATUS_MAP } = require('../../utils/constants')

Component({
  properties: {
    show: {
      type: Object,
      value: {},
    },
  },

  data: {
    statusLabel: '',
    statusColor: '#888',
    platformLabelText: '',
    platformEmojiText: '',
  },

  lifetimes: {
    attached() {
      const show = this.properties.show || {}
      this._updateDerived(show)
    },
  },

  observers: {
    'show': function (show) {
      this._updateDerived(show)
    },
  },

  methods: {
    _updateDerived(show) {
      if (!show) return
      const p = PLATFORMS[show.platform]
      const s = STATUS_MAP[show.status]
      this.setData({
        statusLabel: s ? s.label : '未知',
        statusColor: s ? s.color : '#888',
        platformLabelText: p ? p.label : (show.platform || ''),
        platformEmojiText: p ? p.emoji : '',
      })
    },

    onBuy() {
      const url = this.data.show.url
      if (url) {
        wx.setClipboardData({
          data: url,
          success() {
            wx.showToast({ title: '链接已复制，请在浏览器打开', icon: 'none' })
          },
        })
      }
    },
  },
})
