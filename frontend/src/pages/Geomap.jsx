import { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Circle } from 'react-leaflet';
import L from 'leaflet';
import api from '../api/axios';
import { MapPin, ShieldAlert, Filter } from 'lucide-react';
import { Link } from 'react-router-dom';

// Custom Map Markers
const createCustomIcon = (color) => {
  return new L.Icon({
    iconUrl: `https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-${color}.png`,
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
    shadowSize: [41, 41]
  });
};

const icons = {
  high: createCustomIcon('red'),
  medium: createCustomIcon('gold'),
  low: createCustomIcon('green'),
};

export default function Geomap() {
  const [meters, setMeters] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');

  // Base coordinate for the demo (Noida/Delhi area)
  const BASE_LAT = 28.6200;
  const BASE_LNG = 77.3800;

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [metersRes, alertsRes] = await Promise.all([
          api.get('/meters'),
          api.get('/alerts')
        ]);
        
        const fetchedMeters = metersRes.data.data;
        const fetchedAlerts = alertsRes.data.data;

        // Map alerts to meters for risk calculation
        const meterAlertMap = {};
        fetchedAlerts.forEach(alert => {
          if (alert.meter && alert.meter._id) {
            meterAlertMap[alert.meter._id] = alert.theftProbabilityScore;
          }
        });

        // Add dummy coordinates around the base location for MVP visualization
        const mappedMeters = fetchedMeters.map((meter, index) => {
          // Scatter within ~5km radius
          const latOffset = (Math.random() - 0.5) * 0.08;
          const lngOffset = (Math.random() - 0.5) * 0.08;
          
          const riskScore = meterAlertMap[meter._id] || 0.1; // Default low risk if no alert
          
          let riskLevel = 'low';
          if (riskScore >= 0.70) riskLevel = 'high';
          else if (riskScore >= 0.30) riskLevel = 'medium';

          return {
            ...meter,
            lat: BASE_LAT + latOffset,
            lng: BASE_LNG + lngOffset,
            riskScore,
            riskLevel
          };
        });

        setMeters(mappedMeters);
        setAlerts(fetchedAlerts);
      } catch (err) {
        console.error('Fetch map data error:', err);
      } finally {
        setLoading(false);
      }
    };
    
    fetchData();
  }, []);

  const filteredMeters = meters.filter(m => filter === 'all' || m.riskLevel === filter);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="flex flex-col items-center gap-4">
          <div className="w-10 h-10 border-2 border-brand-500 border-t-transparent rounded-full animate-spin" />
          <p className="text-sm text-white/40">Loading Geographic Network…</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 flex flex-col h-[calc(100vh-120px)]">
      {/* ─── Header & Filters ────────────────────────────── */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            <MapPin className="text-cyan-400" /> Geographic Map View
          </h1>
          <p className="text-sm text-white/40 mt-1">
            Real-time geospatial monitoring of high-risk consumers
          </p>
        </div>

        <div className="flex items-center gap-2 flex-wrap glass-card p-2 rounded-xl">
          <Filter className="w-4 h-4 text-white/30 ml-2" />
          {['all', 'high', 'medium', 'low'].map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all duration-200 capitalize ${
                filter === f
                  ? 'bg-brand-500/20 text-brand-400 border border-brand-500/30'
                  : 'bg-white/[0.04] text-white/40 border border-transparent hover:text-white/60'
              }`}
            >
              {f === 'high' && <span className="text-red-400 mr-1">🔴</span>}
              {f === 'medium' && <span className="text-orange-400 mr-1">🟡</span>}
              {f === 'low' && <span className="text-green-400 mr-1">🟢</span>}
              {f} Risk
            </button>
          ))}
        </div>
      </div>

      {/* ─── Leaflet Map Container ───────────────────────── */}
      <div className="flex-1 glass-card rounded-2xl overflow-hidden relative border border-white/[0.06] shadow-2xl">
        <MapContainer 
          center={[BASE_LAT, BASE_LNG]} 
          zoom={13} 
          style={{ height: '100%', width: '100%', backgroundColor: '#0f172a' }}
        >
          {/* Dark themed map tiles */}
          <TileLayer
            url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
          />

          {/* DTR / Substation Marker (Center) */}
          <Circle 
            center={[BASE_LAT, BASE_LNG]} 
            pathOptions={{ color: '#06b6d4', fillColor: '#06b6d4', fillOpacity: 0.1 }} 
            radius={4000} 
          />
          <Marker position={[BASE_LAT, BASE_LNG]} icon={createCustomIcon('blue')}>
            <Popup className="custom-popup">
              <div className="p-1">
                <h3 className="font-bold text-gray-800">Main Feeder Line</h3>
                <p className="text-xs text-gray-500">Noida Sector 62 Substation</p>
                <p className="text-xs font-semibold text-brand-500 mt-1">Monitoring {meters.length} downstream meters</p>
              </div>
            </Popup>
          </Marker>

          {/* Consumer Markers */}
          {filteredMeters.map(meter => (
            <Marker 
              key={meter._id} 
              position={[meter.lat, meter.lng]} 
              icon={icons[meter.riskLevel]}
            >
              <Popup>
                <div className="p-1 min-w-[180px]">
                  <div className="flex justify-between items-start border-b pb-2 mb-2">
                    <div>
                      <h3 className="font-bold text-gray-900">{meter.consumerName || 'Unknown Consumer'}</h3>
                      <p className="text-xs font-mono text-gray-500">ID: {meter.location}</p>
                    </div>
                    {meter.riskLevel === 'high' && (
                      <ShieldAlert className="w-5 h-5 text-red-500" />
                    )}
                  </div>
                  
                  <div className="space-y-1 mb-3">
                    <p className="text-xs flex justify-between">
                      <span className="text-gray-500">Risk Score:</span>
                      <span className={`font-bold ${meter.riskLevel === 'high' ? 'text-red-500' : meter.riskLevel === 'medium' ? 'text-orange-500' : 'text-green-500'}`}>
                        {(meter.riskScore * 100).toFixed(0)}%
                      </span>
                    </p>
                    <p className="text-xs flex justify-between">
                      <span className="text-gray-500">Avg Usage:</span>
                      <span className="font-medium text-gray-700">{meter.baselineConsumption} kWh</span>
                    </p>
                  </div>

                  <Link 
                    to={`/meters/${meter._id}`}
                    className="block w-full text-center bg-brand-500 hover:bg-brand-600 text-white text-xs font-bold py-1.5 rounded transition-colors"
                  >
                    View Details
                  </Link>
                </div>
              </Popup>
            </Marker>
          ))}
        </MapContainer>
        
        {/* Map Overlay Stats */}
        <div className="absolute bottom-6 right-6 z-[400] glass-card p-4 rounded-xl border border-white/[0.1] bg-surface-900/90 backdrop-blur-md">
          <h4 className="text-xs font-bold text-white/70 uppercase tracking-wider mb-3">Live Feed Map Stats</h4>
          <div className="space-y-2">
            <div className="flex items-center justify-between gap-6">
              <div className="flex items-center gap-2 text-xs text-white/80">
                <div className="w-2.5 h-2.5 rounded-full bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.5)]"></div>
                High Risk
              </div>
              <span className="text-sm font-bold text-red-400">{meters.filter(m => m.riskLevel === 'high').length}</span>
            </div>
            <div className="flex items-center justify-between gap-6">
              <div className="flex items-center gap-2 text-xs text-white/80">
                <div className="w-2.5 h-2.5 rounded-full bg-amber-500 shadow-[0_0_8px_rgba(245,158,11,0.5)]"></div>
                Medium Risk
              </div>
              <span className="text-sm font-bold text-amber-400">{meters.filter(m => m.riskLevel === 'medium').length}</span>
            </div>
            <div className="flex items-center justify-between gap-6">
              <div className="flex items-center gap-2 text-xs text-white/80">
                <div className="w-2.5 h-2.5 rounded-full bg-green-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]"></div>
                Low Risk
              </div>
              <span className="text-sm font-bold text-green-400">{meters.filter(m => m.riskLevel === 'low').length}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
