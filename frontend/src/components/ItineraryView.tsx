import React, { useState } from 'react';

/**
 * Normalizes any shape of itinerary data into a consistent format.
 */
function normalizeItinerary(data: any): any[] | null {
    if (!data) return null;
    if (typeof data === 'string') {
        const cleaned = data.replace(/```json\s*/g, '').replace(/```\s*/g, '').trim();
        try { return normalizeItinerary(JSON.parse(cleaned)); } catch { return null; }
    }
    if (data && typeof data === 'object' && !Array.isArray(data) && data.days) {
        return normalizeItinerary(data.days);
    }
    if (Array.isArray(data)) {
        if (data.length > 0 && data[0].activities) return data;
        if (data.length === 1 && data[0].raw_itinerary) {
            return normalizeItinerary(data[0].raw_itinerary);
        }
        if (data.length > 0 && data[0].day !== undefined) return data;
    }
    return null;
}

const categoryIcons: Record<string, string> = {
    sightseeing: '🏛️',
    food: '🍽️',
    transport: '🚗',
    shopping: '🛍️',
    adventure: '🏔️',
    culture: '🎭',
    relaxation: '🧘',
    nightlife: '🌙',
};

const categoryColors: Record<string, string> = {
    sightseeing: '#818cf8',
    food: '#f97316',
    transport: '#3b82f6',
    shopping: '#ec4899',
    adventure: '#22c55e',
    culture: '#a855f7',
    relaxation: '#14b8a6',
    nightlife: '#eab308',
};

function WeatherCard({ weather }: { weather: any }) {
    if (!weather || (!weather.condition && !weather.temp_high)) return null;
    const condition = (weather.condition || '').toLowerCase();
    let icon = '☀️';
    if (condition.includes('rain')) icon = '🌧️';
    else if (condition.includes('cloud')) icon = '⛅';
    else if (condition.includes('storm') || condition.includes('thunder')) icon = '⛈️';
    else if (condition.includes('snow')) icon = '❄️';
    else if (condition.includes('fog') || condition.includes('mist') || condition.includes('haze')) icon = '🌫️';
    else if (condition.includes('clear') || condition.includes('sunny')) icon = '☀️';

    return (
        <div className="weather-card">
            <div className="flex items-center gap-3">
                <span className="text-2xl">{icon}</span>
                <div>
                    <p className="text-sm font-semibold text-text-primary">
                        {weather.temp_high !== undefined ? `${weather.temp_high}°` : '--'}
                        <span className="text-text-muted font-normal"> / {weather.temp_low !== undefined ? `${weather.temp_low}°` : '--'}</span>
                    </p>
                    <p className="text-xs text-text-secondary capitalize">{weather.condition || 'Pleasant'}</p>
                </div>
            </div>
            <div className="flex items-center gap-4 text-xs text-text-muted mt-2">
                {weather.humidity !== undefined && (
                    <span className="flex items-center gap-1">💧 {weather.humidity}%</span>
                )}
                {weather.rain_probability !== undefined && weather.rain_probability > 0 && (
                    <span className="flex items-center gap-1">🌧️ {weather.rain_probability}%</span>
                )}
                {weather.wind_speed_kmh !== undefined && (
                    <span className="flex items-center gap-1">💨 {weather.wind_speed_kmh} km/h</span>
                )}
            </div>
            {weather.advice && (
                <p className="text-xs text-cyan-accent/80 mt-2 leading-relaxed">
                    💡 {weather.advice}
                </p>
            )}
        </div>
    );
}

function HotelCard({ hotel }: { hotel: any }) {
    if (!hotel || !hotel.name) return null;
    return (
        <div className="hotel-card">
            <div className="flex items-start gap-3">
                <div className="w-10 h-10 rounded-lg bg-purple-500/10 border border-purple-500/20 flex items-center justify-center text-lg flex-shrink-0">
                    🏨
                </div>
                <div className="flex-1 min-w-0">
                    <h6 className="text-sm font-semibold text-text-primary truncate">{hotel.name}</h6>
                    <div className="flex items-center gap-2 mt-1">
                        {hotel.stars && (
                            <span className="text-xs text-yellow-400">
                                {'★'.repeat(Math.min(hotel.stars, 5))}{'☆'.repeat(Math.max(0, 5 - hotel.stars))}
                            </span>
                        )}
                        {hotel.area && (
                            <span className="text-xs text-text-muted">📍 {hotel.area}</span>
                        )}
                    </div>
                    {hotel.check_in && (
                        <p className="text-xs text-text-muted mt-1">Check-in: {hotel.check_in}</p>
                    )}
                    <a
                        href={`https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(hotel.name + ' ' + (hotel.area || ''))}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-1 mt-2 text-xs font-semibold text-accent hover:text-accent-hover transition-colors cursor-pointer"
                    >
                        🗺️ Open Google Map
                    </a>
                </div>
                {hotel.price_per_night !== undefined && hotel.price_per_night > 0 && (
                    <div className="text-right flex-shrink-0">
                        <p className="text-sm font-bold text-emerald-accent">₹{Number(hotel.price_per_night).toLocaleString('en-IN')}</p>
                        <p className="text-[10px] text-text-muted">per night</p>
                    </div>
                )}
            </div>
        </div>
    );
}

function LocalExperienceCard({ experience }: { experience: any }) {
    if (!experience || !experience.title) return null;
    return (
        <div className="local-experience-card">
            <div className="flex items-start gap-3">
                <span className="text-lg">✨</span>
                <div>
                    <p className="text-xs font-semibold text-amber-400 uppercase tracking-wider mb-1">Local Gem</p>
                    <h6 className="text-sm font-semibold text-text-primary">{experience.title}</h6>
                    {experience.description && (
                        <p className="text-xs text-text-secondary mt-1 leading-relaxed">{experience.description}</p>
                    )}
                    {experience.estimated_cost_inr > 0 && (
                        <span className="inline-block text-[10px] text-emerald-accent/80 mt-1">
                            ₹{Number(experience.estimated_cost_inr).toLocaleString('en-IN')}
                        </span>
                    )}
                    <a
                        href={`https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(experience.title)}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-1 mt-2 text-[11px] font-semibold text-accent hover:text-accent-hover transition-colors cursor-pointer block"
                    >
                        🗺️ Open Google Map
                    </a>
                </div>
            </div>
        </div>
    );
}

export const ItineraryView: React.FC<{ itinerary: any }> = ({ itinerary }) => {
    const [expandedDays, setExpandedDays] = useState<Set<number>>(new Set([0]));

    if (!itinerary) return null;
    const days = normalizeItinerary(itinerary);

    if (!days || days.length === 0) {
        const rawText = typeof itinerary === 'string'
            ? itinerary
            : (itinerary?.[0]?.raw_itinerary || JSON.stringify(itinerary, null, 2));
        return (
            <div className="glass-card p-6">
                <h3 className="text-xl font-bold text-text-primary mb-4">Your Itinerary</h3>
                <div className="text-sm text-text-secondary leading-relaxed whitespace-pre-wrap font-sans">
                    {rawText}
                </div>
            </div>
        );
    }

    const toggleDay = (idx: number) => {
        setExpandedDays(prev => {
            const next = new Set(prev);
            if (next.has(idx)) next.delete(idx);
            else next.add(idx);
            return next;
        });
    };

    const totalCost = days.reduce((sum: number, d: any) => sum + (d.day_total_cost || 0), 0);

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-accent/10 border border-accent/20 flex items-center justify-center">
                        <svg className="w-5 h-5 text-accent" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                            <path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                        </svg>
                    </div>
                    <div>
                        <h3 className="text-2xl font-bold text-text-primary">Your Itinerary</h3>
                        <p className="text-xs text-text-muted">{days.length} days planned{totalCost > 0 ? ` • ₹${totalCost.toLocaleString('en-IN')} estimated` : ''}</p>
                    </div>
                </div>
                <button
                    onClick={() => {
                        if (expandedDays.size === days.length) setExpandedDays(new Set());
                        else setExpandedDays(new Set(days.map((_: any, i: number) => i)));
                    }}
                    className="text-xs text-accent hover:text-accent-hover transition-colors cursor-pointer"
                >
                    {expandedDays.size === days.length ? 'Collapse All' : 'Expand All'}
                </button>
            </div>

            {/* Days */}
            <div className="relative">
                {/* Timeline line */}
                <div className="absolute left-6 top-8 bottom-0 w-px bg-gradient-to-b from-accent/40 via-cyan-accent/30 to-transparent" />

                <div className="space-y-6">
                    {days.map((dayData: any, idx: number) => {
                        const isExpanded = expandedDays.has(idx);
                        return (
                            <div key={idx} className="relative pl-16">
                                {/* Day marker */}
                                <div className="absolute left-0 top-4 w-12 h-12 rounded-full bg-surface-2 border-2 border-accent/40 flex items-center justify-center shadow-[0_0_15px_rgba(129,140,248,0.2)] z-10">
                                    <span className="text-sm font-bold text-text-primary">D{dayData.day || idx + 1}</span>
                                </div>

                                {/* Day Card */}
                                <div className="glass-card overflow-hidden">
                                    {/* Day Header — clickable */}
                                    <button
                                        onClick={() => toggleDay(idx)}
                                        className="w-full flex items-center justify-between p-5 hover:bg-surface-1/30 transition-colors cursor-pointer"
                                    >
                                        <div className="text-left">
                                            <h4 className="text-lg font-bold text-text-primary">
                                                Day {dayData.day || idx + 1}
                                                {dayData.date && <span className="text-xs text-text-muted font-normal ml-2">{dayData.date}</span>}
                                            </h4>
                                            {dayData.theme && (
                                                <p className="text-accent text-sm font-medium mt-0.5">{dayData.theme}</p>
                                            )}
                                        </div>
                                        <div className="flex items-center gap-3">
                                            {dayData.day_total_cost > 0 && (
                                                <span className="text-xs font-mono text-emerald-accent/80 bg-emerald-accent/5 px-2 py-1 rounded">
                                                    ₹{Number(dayData.day_total_cost).toLocaleString('en-IN')}
                                                </span>
                                            )}
                                            <svg
                                                className={`w-4 h-4 text-text-muted transition-transform duration-300 ${isExpanded ? 'rotate-180' : ''}`}
                                                fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}
                                            >
                                                <path d="M19 9l-7 7-7-7" />
                                            </svg>
                                        </div>
                                    </button>

                                    {/* Expanded Content */}
                                    {isExpanded && (
                                        <div className="border-t border-border">
                                            {/* Weather + Hotel row */}
                                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 p-4">
                                                <WeatherCard weather={dayData.weather} />
                                                <HotelCard hotel={dayData.hotel} />
                                            </div>

                                            {/* Activities */}
                                            <div className="px-4 pb-4 space-y-3">
                                                {(dayData.activities || []).map((activity: any, actIdx: number) => {
                                                    const cat = activity.category || 'sightseeing';
                                                    const catColor = categoryColors[cat] || '#818cf8';
                                                    const catIcon = categoryIcons[cat] || '📍';

                                                    return (
                                                        <div key={actIdx} className="activity-card group">
                                                            <div className="absolute top-0 left-0 w-1 h-full rounded-l transition-colors" style={{ background: catColor }} />

                                                            <div className="flex flex-col sm:flex-row gap-3 pl-3">
                                                                {/* Time */}
                                                                <div className="sm:w-24 flex-shrink-0">
                                                                    <div className="inline-flex items-center gap-1.5 px-2 py-1 rounded-md bg-surface-3 border border-border text-xs font-semibold text-text-secondary">
                                                                        <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                                                                        {activity.time || 'TBD'}
                                                                    </div>
                                                                </div>

                                                                {/* Content */}
                                                                <div className="flex-1 min-w-0">
                                                                    <div className="flex items-center gap-2 mb-1">
                                                                        <span className="text-base">{catIcon}</span>
                                                                        <h5 className="text-sm font-semibold text-text-primary">
                                                                            {activity.title || 'Activity'}
                                                                        </h5>
                                                                        <span
                                                                            className="text-[10px] font-medium px-1.5 py-0.5 rounded uppercase tracking-wider"
                                                                            style={{ background: `${catColor}15`, color: catColor, border: `1px solid ${catColor}25` }}
                                                                        >
                                                                            {cat}
                                                                        </span>
                                                                    </div>

                                                                    {activity.description && (
                                                                        <p className="text-xs text-text-secondary leading-relaxed mb-2">
                                                                            {activity.description}
                                                                        </p>
                                                                    )}

                                                                    {/* Location */}
                                                                    {activity.location && (
                                                                        <div className="flex flex-col items-start gap-1 mb-1.5">
                                                                            <p className="text-[11px] text-text-muted flex items-center gap-1">
                                                                                <span>📍</span> {activity.location}
                                                                            </p>
                                                                            <a
                                                                                href={`https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(activity.location + (activity.title ? ' ' + activity.title : ''))}`}
                                                                                target="_blank"
                                                                                rel="noopener noreferrer"
                                                                                className="inline-flex items-center gap-1 text-[11px] font-semibold text-accent hover:text-accent-hover transition-colors cursor-pointer"
                                                                            >
                                                                                🗺️ Open Google Map
                                                                            </a>
                                                                        </div>
                                                                    )}

                                                                    {/* Tips */}
                                                                    {activity.tips && (
                                                                        <div className="text-[11px] text-cyan-accent/70 bg-cyan-accent/5 border border-cyan-accent/10 rounded-lg px-2.5 py-1.5 mb-2">
                                                                            💡 <span className="font-medium">Tip:</span> {activity.tips}
                                                                        </div>
                                                                    )}

                                                                    {/* Cost */}
                                                                    {activity.estimated_cost_inr > 0 && (
                                                                        <div className="inline-flex items-center gap-1 text-[11px] font-medium text-emerald-accent/80 bg-emerald-accent/5 px-2 py-0.5 rounded">
                                                                            ₹{Number(activity.estimated_cost_inr).toLocaleString('en-IN')}
                                                                        </div>
                                                                    )}
                                                                    {activity.estimated_cost_inr === 0 && (
                                                                        <div className="inline-flex items-center gap-1 text-[11px] font-medium text-emerald-accent/60 bg-emerald-accent/5 px-2 py-0.5 rounded">
                                                                            Free
                                                                        </div>
                                                                    )}
                                                                </div>
                                                            </div>
                                                        </div>
                                                    );
                                                })}
                                            </div>

                                            {/* Local Experience */}
                                            {dayData.local_experience && dayData.local_experience.title && (
                                                <div className="px-4 pb-4">
                                                    <LocalExperienceCard experience={dayData.local_experience} />
                                                </div>
                                            )}
                                        </div>
                                    )}
                                </div>
                            </div>
                        );
                    })}
                </div>
            </div>
        </div>
    );
};
