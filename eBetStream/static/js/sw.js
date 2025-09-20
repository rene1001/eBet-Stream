// Service Worker pour eBetStream
const CACHE_NAME = 'ebetstream-v2';
const ASSETS_TO_CACHE = [
  '/',
  '/static/css/sport-style.css',
  '/static/js/mobile-interactions.js',
  '/static/images/Logo.png',
  '/static/images/favicon.png',
  '/static/images/apple-touch-icon.png',
  'https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css',
  'https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css',
  'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css',
  'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap',
  'https://code.jquery.com/jquery-3.7.1.min.js',
  'https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js'
];

// Installation du Service Worker
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('Mise en cache des ressources principales');
        return cache.addAll(ASSETS_TO_CACHE)
          .catch(error => {
            console.error('Erreur lors du cache des ressources:', error);
          });
      })
  );
  self.skipWaiting();
});

// Activation du Service Worker
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cache => {
          if (cache !== CACHE_NAME) {
            console.log('Suppression de l\'ancien cache :', cache);
            return caches.delete(cache);
          }
        })
      );
    })
  );
  self.clients.claim();
});

// Stratégie de mise en cache : Cache First, puis réseau
self.addEventListener('fetch', event => {
  // Ne pas mettre en cache les requêtes API, POST, ou les requêtes vers des domaines externes non listés
  if (event.request.method !== 'GET' || 
      event.request.url.includes('/api/') || 
      event.request.url.includes('sockjs') ||
      event.request.url.includes('browser-sync')) {
    return;
  }

  event.respondWith(
    caches.match(event.request)
      .then(response => {
        // Retourner la réponse mise en cache si elle existe
        if (response) {
          return response;
        }

        // Sinon, faire la requête réseau
        return fetch(event.request).then(response => {
          // Vérifier si la réponse est valide
          if (!response || response.status !== 200 || response.type !== 'basic') {
            return response;
          }

          // Mettre en cache la réponse pour les requêtes GET
          if (event.request.method === 'GET') {
            const responseToCache = response.clone();
            caches.open(CACHE_NAME)
              .then(cache => {
                cache.put(event.request, responseToCache);
              });
          }

          return response;
        });
      })
  );
});

// Gestion des notifications push
self.addEventListener('push', event => {
  const options = {
    body: event.data.text(),
    icon: '/static/images/icon-192x192.png',
    badge: '/static/images/icon-96x96.png',
    vibrate: [100, 50, 100],
    data: {
      dateOfArrival: Date.now(),
      primaryKey: 1
    }
  };

  event.waitUntil(
    self.registration.showNotification('eBetStream', options)
  );
});
