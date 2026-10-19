const map = L.map('map').setView([25.42, -100.97], 9);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '&copy; OpenStreetMap contributors'
}).addTo(map);

const resumen = document.getElementById('resumen');
const lista = document.getElementById('lista-resultados');
const btnGeo = document.getElementById('btn-geolocalizacion');

let userLocation = null;
let userMarker = null;

function haversineDistance(lat1, lon1, lat2, lon2) {
  const R = 6371;
  const dLat = (lat2 - lat1) * Math.PI / 180;
  const dLon = (lon2 - lon1) * Math.PI / 180;
  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
    Math.sin(dLon / 2) * Math.sin(dLon / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return R * c;
}

function setUserLocation(lat, lon) {
  userLocation = { lat, lon };

  if (userMarker) {
    map.removeLayer(userMarker);
  }

  userMarker = L.circleMarker([lat, lon], {
    radius: 8,
    color: '#0c6bdb',
    fillColor: '#0c6bdb',
    fillOpacity: 0.9
  }).addTo(map);

  userMarker.bindPopup('Tu ubicación actual').openPopup();
  map.setView([lat, lon], 12);
}

function obtenerGeolocalizacion() {
  if (!navigator.geolocation) {
    resumen.textContent = 'Tu navegador no soporta geolocalización.';
    return;
  }

  navigator.geolocation.getCurrentPosition(
    (position) => {
      const { latitude, longitude } = position.coords;
      setUserLocation(latitude, longitude);
      resumen.textContent = `Ubicación actual detectada: ${latitude.toFixed(4)}, ${longitude.toFixed(4)}.`;
    },
    () => {
      resumen.textContent = 'No se pudo acceder a tu ubicación actual.';
    },
    { enableHighAccuracy: true, timeout: 10000 }
  );
}

btnGeo.addEventListener('click', obtenerGeolocalizacion);

fetch('/api/edificios')
  .then((response) => response.json())
  .then((data) => {
    const resultados = data.results || [];
    resumen.textContent = `Se encontraron ${resultados.length} edificios con distancia >= 10 km.`;

    if (!resultados.length) {
      lista.innerHTML = '<p>No se encontraron resultados.</p>';
      return;
    }

    resultados.forEach((item) => {
      const latEdificio = item.edificio_lat;
      const lonEdificio = item.edificio_lon;
      const latCp = item.cp_lat;
      const lonCp = item.cp_lon;

      const edificioMarker = L.marker([latEdificio, lonEdificio]).addTo(map);
      edificioMarker.bindPopup(`
        <strong>${item.nombre}</strong><br>
        CCT: ${item.cct}<br>
        CP: ${item.codigo_postal}<br>
        Distancia edificio-CP: ${item.distancia_km} km<br>
        <a href="${item.google_maps}" target="_blank">Ver ruta en Google Maps</a>
      `);

      const cpMarker = L.marker([latCp, lonCp]).addTo(map);
      cpMarker.bindPopup(`<strong>CP ${item.codigo_postal}</strong>`);

      L.polyline(
        [[latEdificio, lonEdificio], [latCp, lonCp]],
        { color: '#d62828', weight: 2, opacity: 0.9 }
      ).addTo(map);

      let distanciaDesdeUsuario = 'N/A';
      if (userLocation) {
        const d = haversineDistance(userLocation.lat, userLocation.lon, latEdificio, lonEdificio);
        distanciaDesdeUsuario = `${d.toFixed(2)} km`;
      }

      const itemCard = document.createElement('div');
      itemCard.className = 'item';
      itemCard.innerHTML = `
        <strong>${item.nombre}</strong>
        <div class="meta">CCT: ${item.cct}</div>
        <div class="meta">CP: ${item.codigo_postal}</div>
        <div class="meta">Distancia edificio-CP: ${item.distancia_km} km</div>
        <div class="meta">Distancia desde mi ubicación: ${distanciaDesdeUsuario}</div>
        <a href="${item.google_maps}" target="_blank">Ver ruta en Google Maps</a>
      `;
      lista.appendChild(itemCard);
    });

    const bounds = resultados.reduce((acc, item) => {
      acc.push([item.edificio_lat, item.edificio_lon]);
      acc.push([item.cp_lat, item.cp_lon]);
      return acc;
    }, []);

    map.fitBounds(bounds);
  })
  .catch((error) => {
    console.error('Error al cargar los datos:', error);
    resumen.textContent = 'Ocurrió un error al cargar los datos.';
    lista.innerHTML = '<p>No se pudieron cargar los resultados.</p>';
  });
