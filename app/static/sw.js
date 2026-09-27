const CACHE_NAME = 'presupuesto-acapulco-v2';

const STATIC_ASSETS = [
  '/static/css/style.css',
  '/static/js/configurador.js',
  '/static/js/pwa.js',
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

// PUSH: recibe notificaciones del servidor
self.addEventListener('push', (event) => {
  const data = event.data?.json() ?? {
    title: 'PresupuestoAcapulco',
    body: 'Tienes una nueva notificación.',
  };
  event.waitUntil(
    self.registration.showNotification(data.title, {
      body: data.body,
      icon: '/static/icons/icon.svg',
      badge: '/static/icons/icon.svg',
      vibrate: [200, 100, 200],
    })
  );
});

// NOTIFICATIONCLICK: abre la app al tocar la notificación
self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  event.waitUntil(
    clients.matchAll({ type: 'window' }).then((list) => {
      const existing = list.find((c) => c.url.includes('localhost') && 'focus' in c);
      return existing ? existing.focus() : clients.openWindow('/');
    })
  );
});
