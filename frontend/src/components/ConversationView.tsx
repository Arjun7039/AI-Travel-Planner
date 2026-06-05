/**
 * ConversationView — ChatGPT-style itinerary display.
 * Shows the user's prompt, then the AI response as rich markdown,
 * followed by a budget breakdown card.
 */

interface ConversationViewProps {
  userPrompt: string;
  result: {
    itinerary_markdown: string;
    trip_title: string;
    budget_breakdown: Record<string, number>;
    total_cost: number;
    within_budget: boolean;
    destination: string;
    transport_mode: string;
  };
  onBack: () => void;
  onNewTrip: () => void;
}

function parseMarkdown(md: string): string {
  if (!md) return '';
  
  let html = md
    // Headers
    .replace(/^### (.+)$/gm, '<h3>$1</h3>')
    .replace(/^## (.+)$/gm, '<h2>$1</h2>')
    .replace(/^# (.+)$/gm, '<h1>$1</h1>')
    // Bold and italic
    .replace(/\*\*\*(.+?)\*\*\*/g, '<strong><em>$1</em></strong>')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    // Unordered lists (handle • and - and *)
    .replace(/^[•\-\*]\s+(.+)$/gm, '<li>$1</li>')
    // Ordered lists  
    .replace(/^\d+\.\s+(.+)$/gm, '<li>$1</li>')
    // Blockquotes
    .replace(/^>\s+(.+)$/gm, '<blockquote>$1</blockquote>')
    // Horizontal rules
    .replace(/^---+$/gm, '<hr/>')
    // Line breaks
    .replace(/\n\n/g, '</p><p>')
    .replace(/\n/g, '<br/>');

  // Wrap consecutive <li> in <ul>
  html = html.replace(/(<li>.*?<\/li>)(\s*<br\/>)*\s*(?=<li>)/g, '$1');
  html = html.replace(/(<li>[\s\S]*?<\/li>)/g, (match) => {
    if (!match.startsWith('<ul>')) {
      return `<ul>${match}</ul>`;
    }
    return match;
  });
  // Clean up nested <ul> tags
  html = html.replace(/<\/ul>\s*<ul>/g, '');

  return `<p>${html}</p>`;
}

const budgetColors: Record<string, string> = {
  transport: '#6366f1',
  accommodation: '#0ea5e9',
  food: '#f59e0b',
  activities: '#10b981',
  miscellaneous: '#8b5cf6',
};

const budgetIcons: Record<string, string> = {
  transport: '🚗',
  accommodation: '🏨',
  food: '🍽️',
  activities: '🎯',
  miscellaneous: '📦',
};

export function ConversationView({ userPrompt, result, onBack, onNewTrip }: ConversationViewProps) {
  const budget = result.total_cost || 0;
  const breakdown = result.budget_breakdown || {};

  let waypoints: any[] = [];
  let displayMarkdown = result.itinerary_markdown || '';

  // Extract JSON waypoints
  const jsonMatch = displayMarkdown.match(/```json\s*([\s\S]*?)\s*```/);
  if (jsonMatch) {
    try {
      const parsed = JSON.parse(jsonMatch[1]);
      if (parsed.waypoints && Array.isArray(parsed.waypoints)) {
        waypoints = parsed.waypoints;
      }
    } catch (e) {
      console.error("Failed to parse waypoints JSON", e);
    }
    displayMarkdown = displayMarkdown.replace(/```json\s*[\s\S]*?\s*```/, '').trim();
  }

  return (
    <div className="conversation-layout">
      {/* Left Column: Chat & Itinerary */}
      <div className="chat-container">
        {/* Top bar */}
        <div style={{
          display: 'flex', justifyContent: 'space-between', alignItems: 'center',
          padding: '12px 0', borderBottom: '1px solid var(--border)', marginBottom: 8,
        }}>
          <div>
            <h2 style={{ fontFamily: 'var(--font-display)', fontSize: 18, fontWeight: 700 }}>
              {result.trip_title || 'Your Trip'}
            </h2>
            <div style={{ display: 'flex', gap: 12, marginTop: 4 }}>
              <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>📍 {result.destination}</span>
              <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>
                {result.transport_mode === 'Flight' ? '✈️' : result.transport_mode === 'Train' ? '🚆' : '🚗'} {result.transport_mode}
              </span>
              {result.within_budget
                ? <span style={{ fontSize: 12, color: 'var(--success)' }}>✅ Within budget</span>
                : <span style={{ fontSize: 12, color: 'var(--error)' }}>⚠️ Over budget</span>
              }
            </div>
          </div>
          <div style={{ display: 'flex', gap: 8 }}>
            <button
              onClick={onBack}
              style={{
                padding: '8px 16px', background: 'transparent', border: '1px solid var(--border)',
                borderRadius: 'var(--radius-md)', color: 'var(--text-secondary)', fontWeight: 600,
                fontSize: 12, cursor: 'pointer', fontFamily: 'var(--font-body)',
              }}
            >
              ← Back
            </button>
            <button
              onClick={onNewTrip}
              style={{
                padding: '8px 16px', background: 'var(--bg-card)', border: '1px solid var(--border)',
                borderRadius: 'var(--radius-md)', color: 'var(--text-primary)', fontWeight: 600,
                fontSize: 12, cursor: 'pointer', fontFamily: 'var(--font-body)',
              }}
            >
              + New Trip
            </button>
          </div>
        </div>

        {/* User message */}
        <div className="chat-user-msg">
          <div className="avatar">👤</div>
          <div className="msg-text">{userPrompt}</div>
        </div>

        {/* AI itinerary response */}
        <div className="chat-ai-msg">
          <div className="avatar">✨</div>
          <div className="msg-content">
            <div
              className="itinerary-md"
              dangerouslySetInnerHTML={{ __html: parseMarkdown(displayMarkdown) }}
            />
          </div>
        </div>

        {/* Budget Breakdown Card */}
        {Object.keys(breakdown).length > 0 && (
          <div className="budget-card animate-fade-in" style={{ marginTop: 8, marginLeft: 44 }}>
            <h3 style={{ fontFamily: 'var(--font-display)', fontSize: 15, fontWeight: 700, marginBottom: 16 }}>
              💰 Budget Breakdown
            </h3>
            <div style={{ fontSize: 24, fontWeight: 800, fontFamily: 'var(--font-display)', marginBottom: 4 }}>
              ₹{budget.toLocaleString('en-IN')}
            </div>
            <p style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 16 }}>Estimated total cost</p>

            <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
              {Object.entries(breakdown).map(([key, value]) => {
                const pct = budget > 0 ? Math.min(Math.round((Number(value) / budget) * 100), 100) : 0;
                const color = budgetColors[key] || '#888';
                return (
                  <div key={key}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 4 }}>
                      <span style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-primary)', textTransform: 'capitalize' }}>
                        {budgetIcons[key] || '📌'} {key}
                      </span>
                      <span style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-secondary)' }}>
                        ₹{Number(value).toLocaleString('en-IN')} ({pct}%)
                      </span>
                    </div>
                    <div className="budget-bar">
                      <div className="budget-bar-fill" style={{ width: `${pct}%`, background: color }} />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Bottom action */}
        <div style={{ textAlign: 'center', padding: '20px 0 40px', marginLeft: 44 }}>
          <button
            onClick={onNewTrip}
            style={{
              padding: '12px 28px', background: 'var(--accent)', color: '#000',
              border: 'none', borderRadius: 'var(--radius-md)', fontWeight: 700,
              fontSize: 14, cursor: 'pointer', fontFamily: 'var(--font-body)',
            }}
          >
            ✨ Plan Another Trip
          </button>
        </div>
      </div>

      {/* Right Column: Map */}
      <div className="animate-fade-in-up map-container">
        <div style={{ padding: '12px 16px', background: 'var(--bg-card)', borderBottom: '1px solid var(--border)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-primary)' }}>📍 Itinerary Map</span>
          <a 
            href={`https://www.google.com/maps/dir/?api=1&destination=${encodeURIComponent(result.destination)}`}
            target="_blank" 
            rel="noreferrer"
            style={{ fontSize: 12, fontWeight: 700, color: '#000', background: 'var(--accent)', padding: '6px 12px', borderRadius: '4px', textDecoration: 'none' }}
          >
            Google Maps ↗
          </a>
        </div>
        {waypoints.length > 0 ? (
          <iframe
            width="100%"
            style={{ flex: 1, border: 0 }}
            srcDoc={`
              <!DOCTYPE html>
              <html>
              <head>
                <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
                <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
                <style>
                  body, html, #map { height: 100%; margin: 0; padding: 0; background: #e5e3df; }
                  .custom-marker { background: #ea4335; color: #fff; border-radius: 50%; width: 24px; height: 24px; display: flex; align-items: center; justify-content: center; font-weight: bold; font-family: Roboto, Arial, sans-serif; font-size: 12px; border: 2px solid #fff; box-shadow: 0 2px 6px rgba(0,0,0,0.4); }
                  .leaflet-popup-content-wrapper { background: #fff; color: #3c4043; border-radius: 8px; font-family: Roboto, Arial, sans-serif; box-shadow: 0 2px 10px rgba(0,0,0,0.2); }
                  .leaflet-popup-tip { background: #fff; }
                </style>
              </head>
              <body>
                <div id="map"></div>
                <script>
                  var map = L.map('map', { zoomControl: false });
                  L.control.zoom({ position: 'bottomright' }).addTo(map);
                  
                  // Native Google Maps Tiles
                  L.tileLayer('http://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}', {
                      attribution: '&copy; Google',
                      maxZoom: 20
                  }).addTo(map);

                  var waypoints = ${JSON.stringify(waypoints)};
                  var cityName = ${JSON.stringify(result.destination)};
                  var bounds = L.latLngBounds();
                  
                  waypoints.forEach((wp, idx) => {
                    if(wp.lat && wp.lng) {
                      var icon = L.divIcon({
                        className: 'custom-marker',
                        html: (idx + 1),
                        iconSize: [24, 24],
                        iconAnchor: [12, 12]
                      });
                      var marker = L.marker([wp.lat, wp.lng], {icon: icon}).addTo(map);
                      
                      var dirUrl = "https://www.google.com/maps/dir/?api=1&destination=" + encodeURIComponent(wp.name + ", " + cityName);
                      var popupHtml = "<div style='text-align:center; padding: 4px;'><b>" + wp.name + "</b><br><a href='" + dirUrl + "' target='_blank' style='display:inline-block; margin-top:8px; background:#1a73e8; color:#fff; padding:6px 12px; border-radius:4px; text-decoration:none; font-weight:500; font-size:13px;'>Directions ↗</a></div>";
                      
                      marker.bindPopup(popupHtml);
                      bounds.extend([wp.lat, wp.lng]);
                    }
                  });

                  if (waypoints.length > 0 && bounds.isValid()) {
                    map.fitBounds(bounds, { padding: [50, 50] });
                  } else {
                    map.setView([20.5937, 78.9629], 5);
                  }
                </script>
              </body>
              </html>
            `}
          />
        ) : (
          <iframe
            width="100%"
            style={{ flex: 1, border: 0 }}
            loading="lazy"
            allowFullScreen
            referrerPolicy="no-referrer-when-downgrade"
            src={`https://maps.google.com/maps?q=${encodeURIComponent(result.destination)}&t=m&z=12&ie=UTF8&iwloc=&output=embed`}
          ></iframe>
        )}
      </div>
    </div>
  );
}
