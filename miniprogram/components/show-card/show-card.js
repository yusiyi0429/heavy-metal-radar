const { PLATFORMS, STATUS_MAP } = require('../../utils/constants')

Component({
  properties: {
    show: {
      type: Object,
      value: {},
    },
  },

  computed: {},

  methods: {
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

    platformLabel() {
      const p = PLATFORMS[this.data.show.platform]
      return p ? p.label : this.data.show.platform
    },

    platformEmoji() {
      const p = PLATFORMS[this.data.show.platform]
      return p ? p.emoji : ''
    },

    statusInfo() {
      return STATUS_MAP[this.data.show.status] || { label: '未知', color: '#888' }
    },
  },
})
