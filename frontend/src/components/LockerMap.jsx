import React from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import { MapPin } from 'lucide-react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Fix for default marker icon in react-leaflet
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';
const DefaultIcon = L.icon({ iconUrl: icon, shadowUrl: iconShadow, iconSize: [25, 41], iconAnchor: [12, 41] });
L.Marker.prototype.options.icon = DefaultIcon;

const inpostIcon = new L.Icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-yellow.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});

const closestIcon = new L.Icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
  iconSize: [30, 49],
  iconAnchor: [15, 49],
  popupAnchor: [1, -40],
  shadowSize: [41, 41]
});

function ChangeView({ center }) {
  const map = useMap();
  map.setView(center, 13);
  return null;
}

function getMapCenter(results) {
  if (results?.pois?.length > 0) {
    return [results.pois[0].location.lat, results.pois[0].location.lon];
  }
  if (results?.inpost_points?.length > 0) {
    return [results.inpost_points[0].location.lat, results.inpost_points[0].location.lon];
  }
  if (results?.city_lat != null && results?.city_lon != null) {
    return [results.city_lat, results.city_lon];
  }
  return [52.2297, 21.0122]; // Last resort: Warsaw
}

export function LockerMap({ results, loading }) {
  if (!results && !loading) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center text-gray-400 p-8 text-center">
        <MapPin size={48} className="mb-4 opacity-50" />
        <p className="text-lg font-medium">Map will appear here</p>
        <p className="text-sm">Enter a natural language query to see logistics intelligence in action.</p>
      </div>
    );
  }

  const center = getMapCenter(results);

  return (
    <div className="flex-1 w-full h-full relative z-0">
      <MapContainer center={center} zoom={13} className="w-full h-full min-h-[600px] z-0">
        <TileLayer
          url="https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
        />

        {results && <ChangeView center={center} />}

        {results?.pois?.map((poi) => (
          <Marker key={poi.id} position={[poi.location.lat, poi.location.lon]}>
            <Popup>
              <strong className="block text-sm">{poi.name}</strong>
              <span className="text-xs text-gray-500 capitalize">{poi.type}</span>
            </Popup>
          </Marker>
        ))}

        {results?.inpost_points?.map((point, idx) => {
          const isClosest = idx === 0 && point.distance_m != null;
          return (
            <Marker
              key={`inpost-${idx}`}
              position={[point.location.lat, point.location.lon]}
              icon={isClosest ? closestIcon : inpostIcon}
            >
              <Popup>
                <div className="flex flex-col gap-1">
                  {isClosest && (
                    <span className="text-xs font-bold text-red-600 uppercase tracking-wide">⭐ Closest locker</span>
                  )}
                  <strong className="text-sm">{point.name}</strong>
                  <span className="text-xs text-gray-600">{point.address?.line1}</span>
                  <span className="text-xs text-gray-600">{point.address?.line2}</span>
                  <div className="flex gap-1 mt-1 flex-wrap">
                    <span className="text-xs font-semibold px-2 py-1 bg-green-100 text-green-800 rounded w-max">
                      {point.status}
                    </span>
                    {point.distance_m != null && (
                      <span className="text-xs font-semibold px-2 py-1 bg-blue-100 text-blue-800 rounded w-max">
                        📍 {point.distance_m >= 1000
                          ? `${(point.distance_m / 1000).toFixed(1)} km`
                          : `${point.distance_m} m`}
                      </span>
                    )}
                  </div>
                </div>
              </Popup>
            </Marker>
          );
        })}
      </MapContainer>

      {results && (
        <div className="absolute top-4 right-4 bg-white/90 backdrop-blur p-3 rounded-lg shadow-md border border-gray-100 z-[1000]">
          <h4 className="text-xs font-bold mb-2 uppercase tracking-wider text-gray-500">Legend</h4>
          <div className="flex flex-col gap-2">
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 bg-blue-500 rounded-full"></div>
              <span className="text-sm">{results.poi_type ? `POIs (${results.poi_type})` : 'POIs'} ({results.pois.length})</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 bg-[#FFCC00] rounded-full border border-yellow-600"></div>
              <span className="text-sm">InPost Lockers ({results.inpost_points.length})</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
