const CACHE_NAME = 'presupuesto-acapulco-v1';

// Recursos estáticos que se cachean en la instalación
const STATIC_ASSETS = [
  '/static/css/style.css',
  '/static/js/configurador.js',
  '/offline',
];

// INSTALACIÓN: guarda los recursos estáticos en caché
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(STATIC_ASSETS))
  );
  self.skipWaiting();
});

// ACTIVACIÓN: elimina cachés de versiones anteriores
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(
        keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k))
      )
    )
  );
  self.clients.claim();
});

// FETCH: estrategia según el tipo de recurso
self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);

  // Solo interceptamos peticiones GET al mismo origen
  if (event.request.method !== 'GET' || url.origin !== location.origin) return;

  // Archivos estáticos → caché primero, luego red (cache-first)
  if (url.pathname.startsWith('/static/')) {
    event.respondWith(
      caches.match(event.request).then((cached) => {
        if (cached) return cached;
        return fetch(event.request).then((response) => {
          const clone = response.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(event.request, clone));
          return response;
        });
      })
    );
    return;
  }

  // Páginas dinámicas → red primero, caché de respaldo (network-first)
  event.respondWith(
    fetch(event.request).catch(() =>
      caches.match(event.request).then((cached) => cached || caches.match('/offline'))
    )
  );
});
