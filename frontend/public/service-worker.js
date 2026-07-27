const CACHE = "geo-ops-v1"
const ASSETS = ["/oil-ops", "/assets/oil_distribution/frontend/index.html"]
self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(ASSETS)))
  self.skipWaiting()
})
self.addEventListener("activate", (e) => e.waitUntil(clients.claim()))
self.addEventListener("fetch", (e) => {
  e.respondWith(
    caches.match(e.request).then((r) => r || fetch(e.request).then((res) => {
      if (res.status === 200) {
        const copy = res.clone()
        caches.open(CACHE).then((c) => c.put(e.request, copy))
      }
      return res
    }))
  )
})
