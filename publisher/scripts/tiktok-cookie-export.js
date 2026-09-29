// Export TikTok session cookies from the Playwriter-connected Chrome profile
// to /tmp/tiktok_cookies.json (sandboxed write), for the TikTok publisher.
//
// Run from a Playwriter session whose browser profile is logged in to the
// GutKitchen TikTok account:
//   playwriter -s <session> -e 'state.page = context.pages().find(p => p.url().includes("tiktok.com")); await import("<repo>/publisher/scripts/tiktok-cookie-export.js")'
// then move the file into $SOCIAL_INFLUENCE_STATE_DIR (default ~/.social-influence).
//
// Cookies never enter the repo; the file is gitignored and lives outside it.

const cdp = await getCDPSession({ page: state.page })
const { cookies } = await cdp.send('Network.getCookies', {
  urls: ['https://www.tiktok.com', 'https://www.tiktok.com/'],
})
const fs = require('node:fs')
fs.writeFileSync('/tmp/tiktok_cookies.json', JSON.stringify(cookies, null, 2))
const names = cookies.map(c => c.name)
console.log(`exported ${cookies.length} cookies -> /tmp/tiktok_cookies.json`)
console.log('sessionid present:', names.includes('sessionid'))