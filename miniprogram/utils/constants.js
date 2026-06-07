const PLATFORMS = {
  showstart: { label: '秀动', emoji: '🎸' },
  damai: { label: '大麦', emoji: '🎫' },
}

const STATUS_MAP = {
  on_sale: { label: '售票中', color: '#2ecc71' },
  upcoming: { label: '即将开票', color: '#f39c12' },
  sold_out: { label: '已售罄', color: '#888' },
}

module.exports = { PLATFORMS, STATUS_MAP }
