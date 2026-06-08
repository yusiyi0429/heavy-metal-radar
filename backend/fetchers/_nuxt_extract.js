#!/usr/bin/env node
// Extract Showstart NUXT SSR data from HTML piped to stdin.
// Usage: curl ... | node _nuxt_extract.js

const fs = require('fs');

let html = '';
process.stdin.setEncoding('utf-8');
process.stdin.on('data', (chunk) => (html += chunk));
process.stdin.on('end', () => {
  const m = html.match(/window\.__NUXT__=\((.+)\);\s*<\/script>/);
  if (!m) {
    console.log('[]');
    process.exit(0);
  }
  try {
    const nuxt = eval('(' + m[1] + ')');
    const items =
      (nuxt.data && nuxt.data[0] && nuxt.data[0].listData) || [];
    const out = items.map((i) => ({
      showId: String(i.id || ''),
      title: i.title || '',
      artist: i.performers || i.title || '',
      city: i.cityName || '',
      venue: i.siteName || '',
      date: i.showTime || '',
      status: i.soldOut ? 'sold_out' : 'on_sale',
      url: 'https://www.showstart.com/event/' + (i.id || ''),
    }));
    console.log(JSON.stringify(out));
  } catch (e) {
    console.error('NUXT eval error:', e.message);
    console.log('[]');
  }
});
