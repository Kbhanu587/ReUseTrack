const VERSION = 'reusetrack-v1';
const OFFLINE_URL = '/offline/';
const CORE = [
    OFFLINE_URL,
    '/static/accounts/app.css',
    '/static/accounts/icons/icon-192.png',
    '/static/accounts/icons/icon-512.png'
];

self.addEventListener('install', function (event) {
    event.waitUntil(
        caches.open(VERSION)
            .then(function (cache) { return cache.addAll(CORE); })
            .then(function () { return self.skipWaiting(); })
    );
});

self.addEventListener('activate', function (event) {
    event.waitUntil(
        caches.keys()
            .then(function (keys) {
                return Promise.all(
                    keys.filter(function (k) { return k !== VERSION; })
                        .map(function (k) { return caches.delete(k); })
                );
            })
            .then(function () { return self.clients.claim(); })
    );
});

self.addEventListener('fetch', function (event) {
    var req = event.request;
    if (req.method !== 'GET') return;
    var url = new URL(req.url);

    if (req.mode === 'navigate') {
        event.respondWith(
            fetch(req).catch(function () { return caches.match(OFFLINE_URL); })
        );
        return;
    }

    if (url.origin === self.location.origin && url.pathname.indexOf('/static/') === 0) {
        event.respondWith(
            fetch(req)
                .then(function (res) {
                    var copy = res.clone();
                    caches.open(VERSION).then(function (cache) { cache.put(req, copy); });
                    return res;
                })
                .catch(function () { return caches.match(req); })
        );
    }
});