import React, { useState, useCallback, useEffect } from 'react';
import { Sparkles, MapPin, CalendarHeart, Wallet, Users, Sun, Mountain, Utensils, Camera, Loader2, ArrowRight } from 'lucide-react';
import { PlanningProgress } from '../components/PlanningProgress';
import { ItineraryView } from '../components/ItineraryView';
import { BudgetBreakdown } from '../components/BudgetBreakdown';
import { MapView } from '../components/MapView';

type PlanView = 'form' | 'planning' | 'result';

const interests = [
  { icon: Sun, label: 'Beaches' },
  { icon: Mountain, label: 'Adventure' },
  { icon: Utensils, label: 'Food' },
  { icon: Camera, label: 'Culture' },
];

function InputBox({ icon: Icon, label, placeholder, name, type = 'text', required = false, defaultValue = '' }: {
  icon: any; label: string; placeholder: string; name: string; type?: string; required?: boolean; defaultValue?: string;
}) {
  return (
    <label className="flex items-center gap-3 rounded-2xl border border-border/80 bg-[#0d0d0d] px-4 py-3.5 transition duration-200 focus-within:border-accent/50 focus-within:ring-2 focus-within:ring-accent/10 cursor-text">
      <Icon className="h-4.5 w-4.5 text-accent" />
      <div className="flex-1 min-w-0">
        <div className="text-[9px] uppercase tracking-wider font-extrabold text-neutral-500">{label}</div>
        <input
          name={name}
          type={type}
          required={required}
          defaultValue={defaultValue}
          className="bg-transparent w-full text-xs font-semibold outline-none text-neutral-200 placeholder-neutral-600 mt-0.5"
          placeholder={placeholder}
        />
      </div>
    </label>
  );
}

export default function PlanPage() {
  const [view, setView] = useState<PlanView>('form');
  const [request, setRequest] = useState<any>(null);
  const [result, setResult] = useState<any>(null);
  const [picked, setPicked] = useState<string[]>(['Food', 'Culture']);
  const [loading, setLoading] = useState(false);

  // Read URL query parameters on load for automated search planning
  useEffect(() => {
    const searchParams = new URLSearchParams(window.location.search);
    const dest = searchParams.get('destination');
    const days = searchParams.get('days') || '5';
    const budget = searchParams.get('budget') || '50000';
    
    if (dest) {
      const today = new Date();
      const end = new Date();
      end.setDate(today.getDate() + parseInt(days));

      const data = {
        origin: '',
        destination: dest,
        start_date: today.toISOString().split('T')[0],
        end_date: end.toISOString().split('T')[0],
        num_travellers: 2,
        budget_inr: parseFloat(budget) || 50000,
        transport_mode: 'Flight',
        preferences: {
          accommodation: 'mid-range',
          activities: ['food', 'culture'],
          cuisine: ['local'],
        },
      };
      setRequest(data);
      setView('planning');
      // Clean query params so refresh goes back to form if they want
      window.history.replaceState({}, document.title, window.location.pathname);
    }
  }, []);

  const toggle = (l: string) => setPicked((p) => p.includes(l) ? p.filter(x => x !== l) : [...p, l]);

  const handlePlan = useCallback((e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    const fd = new FormData(e.target as HTMLFormElement);
    
    const startStr = fd.get('start_date') as string;
    const endStr = fd.get('end_date') as string;
    
    const data = {
      origin: fd.get('origin') as string,
      destination: fd.get('destination'),
      start_date: startStr,
      end_date: endStr,
      num_travellers: parseInt(fd.get('num_travellers') as string) || 2,
      budget_inr: parseFloat(fd.get('budget_inr') as string) || 50000,
      transport_mode: fd.get('transport_mode') || 'Flight',
      preferences: {
        accommodation: 'mid-range',
        activities: picked.map(p => p.toLowerCase()),
        cuisine: ['local'],
      },
    };
    setRequest(data);
    setView('planning');
  }, [picked]);

  return (
    <div className="flex-1 w-full max-w-7xl mx-auto px-4 md:px-8 py-8 flex flex-col justify-center min-h-[90svh]">
      
      {/* HEADER TITLE (FORM STAGE ONLY) */}
      {view === 'form' && (
        <div className="text-center mb-10 mt-6 md:mt-2">
          <span className="inline-flex items-center gap-1.5 rounded-full bg-neutral-900 border border-border/80 px-4 py-1.5 text-xs font-semibold text-accent shadow-lg shadow-accent/5">
            <Sparkles className="h-3.5 w-3.5" />
            AI Architect Suite
          </span>
          <h1 className="mt-6 text-4xl md:text-5xl font-bold tracking-tight" style={{ fontFamily: 'var(--font-display)' }}>
            Design your voyage
          </h1>
          <p className="mt-3 text-sm text-neutral-400 max-w-md mx-auto">
            Provide key parameters, and our specialized multi-agent squad will deploy and map out your custom details.
          </p>
        </div>
      )}

      {/* STAGE CONTAINER */}
      <div className="w-full">
        
        {/* VIEW 1: PRE-TRIP PARAMETERS FORM */}
        {view === 'form' && (
          <form
            onSubmit={handlePlan}
            className="glass-card p-6 md:p-10 border border-border/80 shadow-lift max-w-3xl mx-auto space-y-6"
          >
            {/* Input fields grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <InputBox icon={MapPin} label="Origin" placeholder="e.g. New Delhi" name="origin" required />
              <InputBox icon={MapPin} label="Destination" placeholder="e.g. Lisbon, Portugal" name="destination" required />
              <InputBox icon={CalendarHeart} label="Start Date" placeholder="Select date" name="start_date" type="date" required />
              <InputBox icon={CalendarHeart} label="End Date" placeholder="Select date" name="end_date" type="date" required />
              <InputBox icon={Users} label="Travelers" placeholder="2" name="num_travellers" type="number" defaultValue="2" />
              <InputBox icon={Wallet} label="Budget (₹)" placeholder="50000" name="budget_inr" type="number" defaultValue="50000" required />
            </div>

            {/* Transport selector */}
            <div className="flex flex-col gap-1.5">
              <label className="text-[10px] uppercase tracking-wider font-extrabold text-neutral-500">Preferred Transport</label>
              <select
                name="transport_mode"
                className="w-full rounded-2xl border border-border/80 px-4 py-3.5 text-xs font-semibold outline-none bg-[#0d0d0d] text-neutral-200 transition focus:border-accent/40"
              >
                <option value="Flight">✈️ Flight</option>
                <option value="Train">🚆 Train</option>
                <option value="Car">🚗 Car</option>
              </select>
            </div>

            {/* Interests checklist */}
            <div className="flex flex-col gap-2">
              <label className="text-[10px] uppercase tracking-wider font-extrabold text-neutral-500">Activity focus & interests</label>
              <div className="flex flex-wrap gap-2.5">
                {interests.map((i) => {
                  const on = picked.includes(i.label);
                  return (
                    <button
                      type="button"
                      key={i.label}
                      onClick={() => toggle(i.label)}
                      className={`inline-flex items-center gap-2 rounded-xl px-4 py-2 text-xs font-semibold border transition duration-200 cursor-pointer ${
                        on
                          ? 'bg-accent text-[#0d0d0d] border-accent shadow-md shadow-accent/5'
                          : 'bg-neutral-950/40 border-border/60 text-neutral-400 hover:border-neutral-700'
                      }`}
                    >
                      <i.icon className="h-3.5 w-3.5" />
                      {i.label}
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Notes/Optional Prompt overrides */}
            <div className="flex flex-col gap-1.5">
              <label className="text-[10px] uppercase tracking-wider font-extrabold text-neutral-500">
                Custom prompt directions <span className="text-neutral-600 font-medium">(optional override)</span>
              </label>
              <textarea
                rows={3}
                name="notes"
                placeholder="e.g. Vegetarian foodie. Cozy cafes. Jazz lounges at night. Minimal driving."
                className="w-full rounded-2xl border border-border/80 px-4 py-3 text-xs outline-none bg-[#0d0d0d] text-neutral-200 transition resize-none focus:border-accent/40"
              />
            </div>

            {/* Submit plan generation trigger */}
            <button
              type="submit"
              disabled={loading}
              className="w-full rounded-2xl bg-accent text-[#0d0d0d] py-4 font-bold text-sm uppercase tracking-wider shadow-lg shadow-accent/10 hover:bg-accent-hover transition duration-200 flex items-center justify-center gap-2 cursor-pointer active:scale-[0.98] disabled:opacity-50"
            >
              {loading ? (
                <><Loader2 className="h-4.5 w-4.5 animate-spin" /> Deploying Agents...</>
              ) : (
                <><Sparkles className="h-4.5 w-4.5 stroke-[2.5]" /> Assemble Agent Squad</>
              )}
            </button>
          </form>
        )}

        {/* VIEW 2: SSE REAL-TIME GENERATION TIMELINE */}
        {view === 'planning' && (
          <div className="max-w-2xl mx-auto mt-6 md:mt-2">
            <div className="glass-card border border-border/80 p-5 md:p-8 shadow-lift">
              <PlanningProgress
                planRequest={request}
                onComplete={(_, res) => {
                  setResult(res);
                  setView('result');
                }}
              />
            </div>
          </div>
        )}

        {/* VIEW 3: SPLIT-PANE CONVERSATIONAL RESULT DISPLAY */}
        {view === 'result' && result && (
          <div className="space-y-6 animate-fade-in mt-6 md:mt-0">
            {/* Header info bar */}
            <div className="rounded-2xl border border-border/60 bg-neutral-950/40 px-6 py-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div>
                <span className="text-[10px] font-extrabold uppercase tracking-wider text-accent">Active Voyage Plan</span>
                <h2 className="text-xl font-bold text-neutral-100" style={{ fontFamily: 'var(--font-display)' }}>
                  {request?.destination ? request.destination : 'Curated Destination'}
                </h2>
              </div>
              <button
                onClick={() => { setView('form'); setRequest(null); setResult(null); setLoading(false); }}
                className="self-start sm:self-center px-4 py-2 border border-border/80 hover:border-accent/40 rounded-xl bg-neutral-900 text-neutral-300 hover:text-accent font-semibold text-xs transition duration-200 flex items-center gap-1.5 cursor-pointer"
              >
                Plan Another Trip <ArrowRight className="h-3.5 w-3.5" />
              </button>
            </div>

            {/* Split layout: center list vs right panel widgets */}
            <div className="grid grid-cols-1 xl:grid-cols-12 gap-6 items-start">
              {/* Left pane: Conversational day breakdown itinerary */}
              <div className="xl:col-span-8">
                <ItineraryView itinerary={result?.itinerary || result} />
              </div>

              {/* Right pane: Side components (budget meter, location maps) */}
              <div className="xl:col-span-4 space-y-6">
                <BudgetBreakdown breakdown={result?.budget_breakdown} />
                <MapView origin={request?.origin} destination={request?.destination} />
              </div>
            </div>
          </div>
        )}

      </div>
    </div>
  );
}
