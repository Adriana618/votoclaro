// Cache version — bump this to force all browsers to refresh on next visit.
// The activate event will delete old caches automatically.
const CACHE_VERSION = '2';
const CACHE_NAME = `votoclaro-v${CACHE_VERSION}`;

// Pages to pre-cache for offline support
const PRECACHE = ['/', '/simulador', '/quiz', '/filtros', '/sabias-que', '/aprende'];

self.addEventListener('install', (event) => {
  // Skip waiting so new SW activates immediately
  self.skipWaiting();
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(PRECACHE))
  );
});

self.addEventListener('activate', (event) => {
  // Delete ALL old caches when a new version activates
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(
        keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key))
      )
    ).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);

  // Never cache API calls
  if (url.pathname.startsWith('/api') || url.hostname !== self.location.hostname) {
    return;
  }

  // Network-first strategy: try network, fall back to cache if offline
  event.respondWith(
    fetch(event.request)
      .then((response) => {
        // Cache successful GET responses for offline use
        if (response.ok && event.request.method === 'GET') {
          const clone = response.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(event.request, clone));
        }
        return response;
      })
      .catch(() => {
        // Offline: serve from cache
        return caches.match(event.request).then((cached) => cached || caches.match('/'));
      })
  );
});
