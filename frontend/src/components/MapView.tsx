import React, { useState } from 'react';

interface MapViewProps {
    origin?: string;
    destination?: string;
}

export const MapView: React.FC<MapViewProps> = ({ origin, destination }) => {
    const [isFullScreen, setIsFullScreen] = useState(false);
    const [userLocation, setUserLocation] = useState<string>(origin || '');
    const [locationStatus, setLocationStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle');


    if (!destination) return null;

    const detectLocation = () => {
        if (!navigator.geolocation) {
            setLocationStatus('error');
            return;
        }
        setLocationStatus('loading');
        navigator.geolocation.getCurrentPosition(
            async (position) => {
                const { latitude, longitude } = position.coords;

                try {
                    const resp = await fetch(
                        `https://nominatim.openstreetmap.org/reverse?lat=${latitude}&lon=${longitude}&format=json`
                    );
                    const data = await resp.json();
                    const city = data.address?.city || data.address?.town || data.address?.village || data.address?.state || '';
                    const area = data.address?.suburb || data.address?.neighbourhood || '';
                    setUserLocation(area ? `${area}, ${city}` : city);
                    setLocationStatus('success');
                } catch {
                    setUserLocation(`${latitude.toFixed(4)}, ${longitude.toFixed(4)}`);
                    setLocationStatus('success');
                }
            },
            () => {
                setLocationStatus('error');
            },
            { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
        );
    };

    const effectiveOrigin = userLocation || origin || '';
    const mapQuery = encodeURIComponent(destination);
    const directionsUrl = `https://www.google.com/maps/dir/?api=1&origin=${encodeURIComponent(effectiveOrigin)}&destination=${mapQuery}&travelmode=driving`;

    // Map embed URL — show route if we have both origin and destination
    const embedUrl = effectiveOrigin
        ? `https://maps.google.com/maps?saddr=${encodeURIComponent(effectiveOrigin)}&daddr=${mapQuery}&output=embed`
        : `https://maps.google.com/maps?q=${mapQuery}&t=&z=13&ie=UTF8&iwloc=&output=embed`;

    return (
        <>
            {/* Compact Map Card */}
            <div className="glass-card overflow-hidden flex flex-col">
                <div className="flex items-center gap-3 px-6 py-4 border-b border-border bg-surface-1/50">
                    <div className="w-8 h-8 rounded-lg bg-cyan-accent/10 border border-cyan-accent/20 flex items-center justify-center">
                        <svg className="w-4 h-4 text-cyan-accent" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                            <path d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
                        </svg>
                    </div>
                    <h3 className="text-sm font-semibold text-text-primary">Route Map</h3>
                </div>
                
                {/* Mini map preview */}
                <div className="h-48 w-full relative bg-surface-2">
                    <div className="absolute inset-0 z-10 shadow-[inset_0_0_20px_rgba(6,8,15,0.8)] pointer-events-none" />
                    <iframe
                        title="Google Map Preview"
                        width="100%"
                        height="100%"
                        style={{ border: 0, filter: 'invert(90%) hue-rotate(180deg) contrast(100%) grayscale(20%)' }}
                        loading="lazy"
                        allowFullScreen
                        referrerPolicy="no-referrer-when-downgrade"
                        src={`https://maps.google.com/maps?q=${mapQuery}&t=&z=12&ie=UTF8&iwloc=&output=embed`}
                    />
                </div>
                
                {/* Buttons */}
                <div className="p-4 border-t border-border bg-surface-1/30 space-y-2">
                    <button
                        onClick={() => setIsFullScreen(true)}
                        className="flex items-center justify-center gap-2 w-full py-3 bg-cyan-accent/10 hover:bg-cyan-accent/20 border border-cyan-accent/30 rounded-xl text-cyan-accent font-semibold transition-colors shadow-[0_0_15px_rgba(34,211,238,0.1)] hover:shadow-[0_0_25px_rgba(34,211,238,0.2)] cursor-pointer text-sm"
                    >
                        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                            <path d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
                        </svg>
                        Open Full Map
                    </button>
                </div>
            </div>

            {/* Full Screen Map Overlay */}
            {isFullScreen && (
                <div className="map-overlay">
                    {/* Top Bar */}
                    <div className="map-top-bar">
                        <div className="flex items-center gap-3 flex-1 min-w-0">
                            <div className="map-logo">
                                <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                                    <rect width="24" height="24" rx="6" fill="url(#mg)" />
                                    <path d="M7 12L12 7L17 12L12 17L7 12Z" fill="white" fillOpacity="0.9" />
                                    <defs><linearGradient id="mg" x1="0" y1="0" x2="24" y2="24"><stop stopColor="#818cf8"/><stop offset="1" stopColor="#22d3ee"/></linearGradient></defs>
                                </svg>
                            </div>
                            <span className="text-sm font-semibold text-text-primary truncate">
                                TravelAI Navigator
                            </span>
                        </div>
                        <button
                            onClick={() => setIsFullScreen(false)}
                            className="map-close-btn"
                            aria-label="Close map"
                        >
                            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                                <path d="M6 18L18 6M6 6l12 12" />
                            </svg>
                        </button>
                    </div>

                    {/* Location Bar */}
                    <div className="map-location-bar">
                        <div className="map-location-row">
                            <div className="map-location-dots">
                                <div className="w-3 h-3 rounded-full bg-emerald-accent border-2 border-emerald-accent/30" />
                                <div className="w-px h-6 bg-text-muted/30" />
                                <div className="w-3 h-3 rounded-full bg-red-400 border-2 border-red-400/30" />
                            </div>
                            <div className="flex-1 space-y-2 min-w-0">
                                <div className="map-location-input">
                                    <input
                                        type="text"
                                        value={effectiveOrigin}
                                        onChange={(e) => setUserLocation(e.target.value)}
                                        placeholder="Enter origin or use current location"
                                        className="map-input"
                                    />
                                    <button onClick={detectLocation} className="map-locate-btn" title="Use current location">
                                        {locationStatus === 'loading' ? (
                                            <div className="w-4 h-4 border-2 border-cyan-accent border-t-transparent rounded-full animate-spin" />
                                        ) : (
                                            <svg className={`w-4 h-4 ${locationStatus === 'success' ? 'text-emerald-accent' : 'text-cyan-accent'}`} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                                                <circle cx="12" cy="12" r="3" />
                                                <path d="M12 2v4m0 12v4M2 12h4m12 0h4" />
                                            </svg>
                                        )}
                                    </button>
                                </div>
                                <div className="map-location-input">
                                    <input
                                        type="text"
                                        value={destination}
                                        readOnly
                                        className="map-input text-red-400/90"
                                    />
                                    <div className="px-2">
                                        <svg className="w-4 h-4 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                                            <path d="M17.657 16.657L13.414 20.9a2 2 0 01-2.828 0l-4.243-4.243a8 8 0 1111.314 0z" />
                                            <circle cx="12" cy="11" r="3" />
                                        </svg>
                                    </div>
                                </div>
                            </div>
                        </div>
                        {locationStatus === 'error' && (
                            <p className="text-xs text-red-400 mt-2 pl-7">
                                Could not detect location. Please type your origin manually.
                            </p>
                        )}
                    </div>

                    {/* Full Screen Map */}
                    <div className="map-canvas">
                        <iframe
                            title="Google Map Full"
                            width="100%"
                            height="100%"
                            style={{ border: 0, filter: 'invert(90%) hue-rotate(180deg) contrast(100%) grayscale(15%)' }}
                            loading="lazy"
                            allowFullScreen
                            referrerPolicy="no-referrer-when-downgrade"
                            src={embedUrl}
                        />
                    </div>

                    {/* Bottom Navigation Bar */}
                    <div className="map-bottom-bar">
                        <a
                            href={directionsUrl}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="map-nav-btn"
                        >
                            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                                <path d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
                            </svg>
                            Start Navigation
                        </a>
                        <button
                            onClick={() => setIsFullScreen(false)}
                            className="map-back-btn"
                        >
                            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                                <path d="M10 19l-7-7m0 0l7-7m-7 7h18" />
                            </svg>
                            Back to Itinerary
                        </button>
                    </div>
                </div>
            )}
        </>
    );
};
