const CACHE_NAME = 'pulau-gabriel-v7';
const ASSETS = [
  './',
  './index.html',
  './manifest.json',
  './assets/icon-192.png',
  './assets/icon-512.png',
  './assets/gabriel-avatar.jpg',
  './assets/treasure-chest.jpg',
  './assets/island-map.jpg',
  './assets/island-daring.jpg',
  './assets/island-english.jpg',
  './assets/island-living_english.jpg',
  './assets/island-pjok.jpg',
  './assets/island-homeroom.jpg'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(ASSETS)).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

// Network-first (no-store for HTML & quests_data.js) so curriculum updates always show up immediately on Android & Mac
self.addEventListener('fetch', (event) => {
  if (event.request.method !== 'GET') return;
  const url = event.request.url || '';
  const isDataOrHtml = url.includes('quests_data.js') || url.endsWith('/') || url.includes('index.html');
  const fetchPromise = isDataOrHtml
    ? fetch(event.request, { cache: 'no-store' })
    : fetch(event.request);
  event.respondWith(
    fetchPromise
      .then((response) => {
        const clone = response.clone();
        caches.open(CACHE_NAME).then((cache) => cache.put(event.request, clone));
        return response;
      })
      .catch(() => caches.match(event.request))
  );
});
