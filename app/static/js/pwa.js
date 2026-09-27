// ── Notificaciones Push ──────────────────────────────────────────────────────

async function requestNotificationPermission() {
  if (!('Notification' in window)) return 'unsupported';
  if (Notification.permission === 'granted') return 'granted';
  return await Notification.requestPermission();
}

function showNotification(title, body) {
  if (Notification.permission !== 'granted') return;
  navigator.serviceWorker.ready.then((reg) => {
    reg.showNotification(title, {
      body,
      icon: '/static/icons/icon.svg',
      badge: '/static/icons/icon.svg',
      vibrate: [200, 100, 200],
      tag: 'presupuesto-notif',
    });
  });
}

// Dispara notificación si la página acaba de guardar una cotización
document.addEventListener('DOMContentLoaded', () => {
  const successAlert = document.querySelector('.alert-success');
  if (successAlert && successAlert.textContent.includes('guardada')) {
    requestNotificationPermission().then((perm) => {
      if (perm === 'granted') {
        showNotification(
          '✅ Cotización guardada',
          'Tu presupuesto de construcción quedó guardado en PresupuestoAcapulco.'
        );
      }
    });
  }
});

// ── Geolocalización ──────────────────────────────────────────────────────────

function initGeolocation() {
  const btn    = document.getElementById('btn-geolocate');
  const result = document.getElementById('geo-result');
  if (!btn) return;

  btn.addEventListener('click', () => {
    if (!navigator.geolocation) {
      result.innerHTML =
        '<i class="bi bi-exclamation-triangle me-1 text-warning"></i>' +
        'Tu navegador no soporta geolocalización.';
      return;
    }

    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span>Detectando...';

    navigator.geolocation.getCurrentPosition(
      // Permiso concedido
      (pos) => {
        const lat = pos.coords.latitude.toFixed(5);
        const lng = pos.coords.longitude.toFixed(5);
        result.innerHTML =
          '<i class="bi bi-geo-alt-fill me-1 text-accent"></i>' +
          `<strong>Ubicación detectada:</strong> ${lat}, ${lng} &mdash; ` +
          '<span class="text-muted small">Acapulco, Gro.</span>';
        btn.disabled = false;
        btn.innerHTML = '<i class="bi bi-geo-alt-fill me-1"></i>Mi ubicación';

        showNotification(
          '📍 Ubicación detectada',
          `Lat: ${lat} | Lng: ${lng} — PresupuestoAcapulco`
        );
      },
      // Permiso denegado o error
      (err) => {
        const msgs = {
          1: 'Permiso de ubicación denegado. Actívalo en la configuración del navegador.',
          2: 'No se pudo obtener la ubicación. Intenta de nuevo.',
          3: 'Tiempo de espera agotado.',
        };
        result.innerHTML =
          '<i class="bi bi-x-circle me-1 text-danger"></i>' +
          (msgs[err.code] || 'Error desconocido.');
        btn.disabled = false;
        btn.innerHTML = '<i class="bi bi-geo-alt-fill me-1"></i>Mi ubicación';
      },
      { enableHighAccuracy: true, timeout: 10000 }
    );
  });
}

document.addEventListener('DOMContentLoaded', initGeolocation);
