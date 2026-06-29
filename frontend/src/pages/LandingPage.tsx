import { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Navbar } from '../components/Navbar';
import { Footer } from '../components/Footer';
import { PlanningProgress } from '../components/PlanningProgress';
import { ConversationView } from '../components/ConversationView';

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000';

type AppStage = 'home' | 'enhancing' | 'enhanced' | 'planning' | 'result';

interface EnhancedData {
  destination: string;
  origin: string;
  start_date: string;
  end_date: string;
  num_travellers: number | string;
  budget_inr: number | string;
  transport_mode: string;
  interests: string[];
  enhanced_prompt: string;
  trip_title: string;
}

const suggestions = [
  '🏖️ Take me to Goa for 3 days, budget ₹15,000',
  '🏔️ Plan a Manali trip for 5 days with trekking and adventure',
  '🕌 Heritage tour of Rajasthan, 7 days, ₹40,000 budget',
  '🍜 Street food crawl across Delhi for a weekend',
];

export default function LandingPage() {
  const navigate = useNavigate();
  const [stage, setStage] = useState<AppStage>('home');
  const [userPrompt, setUserPrompt] = useState('');
  const [enhanced, setEnhanced] = useState<EnhancedData | null>(null);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState('');
  const [isEditingParams, setIsEditingParams] = useState(false);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  const isLoggedIn = !!localStorage.getItem('voyagr_token');
  const userName = localStorage.getItem('voyagr_name') || '';

  // Auto-focus input
  useEffect(() => {
    if (stage === 'home' && inputRef.current) {
      inputRef.current.focus();
    }
  }, [stage]);

  // Step 1: Enhance the prompt
  const handleEnhance = async (prompt: string) => {
    if (!prompt.trim()) return;
    setUserPrompt(prompt);
    setStage('enhancing');
    setError('');

    try {
      const res = await fetch(`${API}/api/plan/enhance`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt }),
      });

      if (!res.ok) throw new Error('Failed to enhance prompt');
      const data = await res.json();
      setEnhanced(data);
      setStage('enhanced');
    } catch (e: any) {
      setError(e.message || 'Something went wrong');
      setStage('home');
    }
  };

  // Step 2: Generate the itinerary
  const handleGenerate = async () => {
    if (!enhanced) return;
    setStage('planning');
    setError('');

    try {
      const token = localStorage.getItem('voyagr_token');
      const headers: any = { 'Content-Type': 'application/json' };
      if (token) headers['Authorization'] = `Bearer ${token}`;

      const res = await fetch(`${API}/api/plan/stream`, {
        method: 'POST',
        headers,
        body: JSON.stringify({
          ...enhanced,
          num_travellers: Number(enhanced.num_travellers) || 1,
          budget_inr: Number(enhanced.budget_inr) || 0,
          user_prompt: userPrompt,
        }),
      });

      if (!res.ok) throw new Error('Failed to start planning');

      const reader = res.body?.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (reader) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (!line.startsWith('data: ')) continue;
          try {
            const data = JSON.parse(line.slice(6));

            if (data.status === 'error') {
              setError(data.message);
              setStage('home');
              return;
            }

            if (data.status === 'complete' && data.result) {
              setResult(data.result);
              setStage('result');
            }
          } catch {
            // Skip malformed SSE lines
          }
        }
      }
    } catch (e: any) {
      setError(e.message || 'Connection error');
      setStage('home');
    }
  };

  // Reset everything
  const handleReset = () => {
    setStage('home');
    setUserPrompt('');
    setEnhanced(null);
    setResult(null);
    setError('');
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleEnhance(userPrompt);
    }
  };

  return (
    <div style={{ minHeight: '100vh', background: 'var(--bg-primary)', display: 'flex', flexDirection: 'column' }}>
      {/* Background orbs */}
      <div className="bg-scene">
        <div className="orb orb-1" />
        <div className="orb orb-2" />
        <div className="orb orb-3" />
        <div className="noise-overlay" />
      </div>

      <Navbar userName={userName} isLoggedIn={isLoggedIn} onNewTrip={handleReset} />

      {/* Main Content */}
      <main style={{ flex: 1, position: 'relative', zIndex: 10, display: 'flex', flexDirection: 'column' }}>

        {/* HOME — ChatGPT-style input */}
        {stage === 'home' && (
          <div style={{ flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', padding: '40px 20px' }} className="animate-fade-in">
            <div style={{ textAlign: 'center', marginBottom: 40, maxWidth: 600 }}>
              <h1 style={{ fontFamily: 'var(--font-display)', fontSize: 'clamp(28px, 5vw, 48px)', fontWeight: 800, lineHeight: 1.1, marginBottom: 12 }}>
                Where do you want to go?
              </h1>
              <p style={{ fontSize: 15, color: 'var(--text-secondary)', maxWidth: 480, margin: '0 auto' }}>
                Tell me about your dream trip in plain English. I'll craft the perfect itinerary.
              </p>
            </div>

            {/* Input box */}
            <div style={{ width: '100%', maxWidth: 640 }}>
              <div className="glass-card" style={{ padding: 16, borderColor: 'var(--border-hover)' }}>
                <textarea
                  ref={inputRef}
                  value={userPrompt}
                  onChange={(e) => setUserPrompt(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="e.g. Plan a 4-day trip to Udaipur, ₹20,000 budget, love lakes and palaces..."
                  rows={3}
                  style={{
                    width: '100%', background: 'transparent', border: 'none', outline: 'none',
                    color: 'var(--text-primary)', fontSize: 15, lineHeight: 1.6, resize: 'none',
                    fontFamily: 'var(--font-body)',
                  }}
                />
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 8 }}>
                  <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>
                    Press Enter to search • Shift+Enter for new line
                  </span>
                  <button
                    onClick={() => handleEnhance(userPrompt)}
                    disabled={!userPrompt.trim()}
                    style={{
                      padding: '8px 20px', background: 'var(--accent)', color: '#000',
                      border: 'none', borderRadius: 'var(--radius-md)', fontWeight: 700,
                      fontSize: 13, cursor: 'pointer', transition: 'all 0.2s',
                      opacity: userPrompt.trim() ? 1 : 0.4,
                      fontFamily: 'var(--font-body)',
                    }}
                  >
                    ✨ Plan Trip
                  </button>
                </div>
              </div>

              {/* Error display */}
              {error && (
                <div style={{
                  marginTop: 12, padding: '10px 14px', background: 'rgba(248,113,113,0.1)',
                  border: '1px solid rgba(248,113,113,0.3)', borderRadius: 'var(--radius-sm)',
                  color: 'var(--error)', fontSize: 13,
                }}>
                  {error}
                </div>
              )}

              {/* Suggestion chips */}
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, marginTop: 16, justifyContent: 'center' }}>
                {suggestions.map((s) => (
                  <button
                    key={s}
                    onClick={() => { setUserPrompt(s); handleEnhance(s); }}
                    style={{
                      padding: '8px 14px', background: 'var(--bg-card)', border: '1px solid var(--border)',
                      borderRadius: 'var(--radius-full)', color: 'var(--text-secondary)', fontSize: 12,
                      cursor: 'pointer', transition: 'all 0.2s', fontFamily: 'var(--font-body)',
                    }}
                    onMouseEnter={(e) => { e.currentTarget.style.borderColor = 'var(--accent)'; e.currentTarget.style.color = 'var(--accent)'; }}
                    onMouseLeave={(e) => { e.currentTarget.style.borderColor = 'var(--border)'; e.currentTarget.style.color = 'var(--text-secondary)'; }}
                  >
                    {s}
                  </button>
                ))}
              </div>

              {/* Free trial notice */}
              {!isLoggedIn && (
                <p style={{ textAlign: 'center', marginTop: 20, fontSize: 12, color: 'var(--text-muted)' }}>
                  🎁 1 free trip generation •{' '}
                  <span style={{ color: 'var(--accent)', cursor: 'pointer', fontWeight: 600 }} onClick={() => navigate('/signup')}>
                    Sign up free
                  </span>{' '}
                  for unlimited access
                </p>
              )}
            </div>
          </div>
        )}

        {/* ENHANCING — loading state */}
        {stage === 'enhancing' && (
          <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 40 }} className="animate-fade-in">
            <div style={{ textAlign: 'center' }}>
              <div style={{
                width: 48, height: 48, borderRadius: '50%',
                border: '3px solid var(--border)', borderTopColor: 'var(--accent)',
                animation: 'spin 0.8s linear infinite', margin: '0 auto 16px',
              }} />
              <p style={{ fontSize: 15, fontWeight: 600, color: 'var(--text-primary)' }}>Understanding your request...</p>
              <p style={{ fontSize: 13, color: 'var(--text-muted)', marginTop: 6 }}>AI is enhancing your travel prompt</p>
            </div>
          </div>
        )}

        {/* ENHANCED — show extracted params for confirmation */}
        {stage === 'enhanced' && enhanced && (
          <div style={{ flex: 1, display: 'flex', justifyContent: 'center', padding: '40px 20px' }} className="animate-fade-in-up">
            <div style={{ width: '100%', maxWidth: 640 }}>
              {/* User's original prompt */}
              <div className="chat-user-msg" style={{ marginBottom: 20 }}>
                <div className="avatar">👤</div>
                <div className="msg-text">{userPrompt}</div>
              </div>

              {/* AI enhanced understanding */}
              <div className="chat-ai-msg">
                <div className="avatar">✨</div>
                <div className="msg-content">
                  <p style={{ fontSize: 14, color: 'var(--text-primary)', marginBottom: 12 }}>
                    Here's what I understood. Ready to plan?
                  </p>

                  {/* Enhanced params card */}
                  <div className="glass-card" style={{ padding: 20, marginBottom: 16 }}>
                    <h3 style={{ fontFamily: 'var(--font-display)', fontSize: 18, fontWeight: 700, marginBottom: 4, color: 'var(--accent)' }}>
                      {enhanced.trip_title}
                    </h3>
                    <p style={{ fontSize: 13, color: 'var(--text-secondary)', marginBottom: 16, lineHeight: 1.6 }}>
                      {enhanced.enhanced_prompt}
                    </p>

                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: 12 }}>
                      {isEditingParams ? (
                        <>
                          <div style={{ background: 'var(--bg-elevated)', borderRadius: 'var(--radius-sm)', padding: '10px 12px' }}>
                            <div style={{ fontSize: 10, color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em' }}>📍 Destination</div>
                            <input type="text" value={enhanced.destination} onChange={(e) => setEnhanced({...enhanced, destination: e.target.value})} style={{ width: '100%', background: 'transparent', border: '1px solid var(--border)', color: 'var(--text-primary)', fontSize: 13, marginTop: 4, padding: 4, borderRadius: 4, outline: 'none' }} />
                          </div>
                          <div style={{ background: 'var(--bg-elevated)', borderRadius: 'var(--radius-sm)', padding: '10px 12px' }}>
                            <div style={{ fontSize: 10, color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em' }}>🏠 From</div>
                            <input type="text" value={enhanced.origin} onChange={(e) => setEnhanced({...enhanced, origin: e.target.value})} style={{ width: '100%', background: 'transparent', border: '1px solid var(--border)', color: 'var(--text-primary)', fontSize: 13, marginTop: 4, padding: 4, borderRadius: 4, outline: 'none' }} />
                          </div>
                          <div style={{ background: 'var(--bg-elevated)', borderRadius: 'var(--radius-sm)', padding: '10px 12px' }}>
                            <div style={{ fontSize: 10, color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em' }}>👥 Travellers</div>
                            <input type="number" value={enhanced.num_travellers} onChange={(e) => setEnhanced({...enhanced, num_travellers: e.target.value === '' ? '' : parseInt(e.target.value) || ''})} min="1" style={{ width: '100%', background: 'transparent', border: '1px solid var(--border)', color: 'var(--text-primary)', fontSize: 13, marginTop: 4, padding: 4, borderRadius: 4, outline: 'none' }} />
                          </div>
                          <div style={{ background: 'var(--bg-elevated)', borderRadius: 'var(--radius-sm)', padding: '10px 12px' }}>
                            <div style={{ fontSize: 10, color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em' }}>💰 Budget (₹)</div>
                            <input type="number" value={enhanced.budget_inr} onChange={(e) => setEnhanced({...enhanced, budget_inr: e.target.value === '' ? '' : parseInt(e.target.value) || ''})} style={{ width: '100%', background: 'transparent', border: '1px solid var(--border)', color: 'var(--text-primary)', fontSize: 13, marginTop: 4, padding: 4, borderRadius: 4, outline: 'none' }} />
                          </div>
                          <div style={{ background: 'var(--bg-elevated)', borderRadius: 'var(--radius-sm)', padding: '10px 12px' }}>
                            <div style={{ fontSize: 10, color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em' }}>✈️ Transport</div>
                            <select value={enhanced.transport_mode} onChange={(e) => setEnhanced({...enhanced, transport_mode: e.target.value})} style={{ width: '100%', background: 'var(--bg-card)', border: '1px solid var(--border)', color: 'var(--text-primary)', fontSize: 13, marginTop: 4, padding: 4, borderRadius: 4, outline: 'none' }}>
                              <option value="Flight">Flight</option>
                              <option value="Train">Train</option>
                              <option value="Car">Car</option>
                            </select>
                          </div>
                        </>
                      ) : (
                        [
                          { label: 'Destination', value: enhanced.destination, icon: '📍' },
                          { label: 'From', value: enhanced.origin || 'Flexible', icon: '🏠' },
                          { label: 'Dates', value: `${enhanced.start_date} → ${enhanced.end_date}`, icon: '📅' },
                          { label: 'Travellers', value: String(enhanced.num_travellers), icon: '👥' },
                          { label: 'Budget', value: `₹${enhanced.budget_inr.toLocaleString('en-IN')}`, icon: '💰' },
                          { label: 'Transport', value: enhanced.transport_mode, icon: enhanced.transport_mode === 'Flight' ? '✈️' : enhanced.transport_mode === 'Train' ? '🚆' : '🚗' },
                        ].map((p) => (
                          <div key={p.label} style={{ background: 'var(--bg-elevated)', borderRadius: 'var(--radius-sm)', padding: '10px 12px' }}>
                            <div style={{ fontSize: 10, color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                              {p.icon} {p.label}
                            </div>
                            <div style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-primary)', marginTop: 2 }}>
                              {p.value}
                            </div>
                          </div>
                        ))
                      )}
                    </div>

                    {/* Interests */}
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginTop: 14 }}>
                      {enhanced.interests.map((i) => (
                        <span key={i} style={{
                          padding: '4px 10px', background: 'var(--accent-muted)', border: '1px solid rgba(200,255,0,0.2)',
                          borderRadius: 'var(--radius-full)', fontSize: 11, fontWeight: 600, color: 'var(--accent)',
                          textTransform: 'capitalize',
                        }}>
                          {i}
                        </span>
                      ))}
                    </div>
                  </div>

                  {/* Action buttons */}
                  <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap' }}>
                    <button
                      onClick={() => setStage('home')}
                      style={{
                        padding: '13px 20px', background: 'transparent',
                        border: '1px solid var(--border)', borderRadius: 'var(--radius-md)',
                        color: 'var(--text-secondary)', fontWeight: 600, fontSize: 13,
                        cursor: 'pointer', fontFamily: 'var(--font-body)',
                      }}
                    >
                      ← Back
                    </button>
                    <button
                      onClick={handleGenerate}
                      style={{
                        flex: 1, padding: '13px 20px', background: 'var(--accent)', color: '#000',
                        border: 'none', borderRadius: 'var(--radius-md)', fontWeight: 700,
                        fontSize: 14, cursor: 'pointer', transition: 'all 0.2s',
                        fontFamily: 'var(--font-body)',
                      }}
                    >
                      🚀 Generate Itinerary
                    </button>
                    <button
                      onClick={() => {
                        if (isEditingParams) {
                          setIsEditingParams(false);
                        } else {
                          setIsEditingParams(true);
                        }
                      }}
                      style={{
                        padding: '13px 20px', background: 'transparent',
                        border: '1px solid var(--border)', borderRadius: 'var(--radius-md)',
                        color: 'var(--text-secondary)', fontWeight: 600, fontSize: 13,
                        cursor: 'pointer', fontFamily: 'var(--font-body)',
                      }}
                    >
                      {isEditingParams ? '✅ Save' : '✏️ Edit'}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* PLANNING — progress view */}
        {stage === 'planning' && (
          <div style={{ flex: 1, display: 'flex', justifyContent: 'center', padding: '40px 20px' }} className="animate-fade-in">
            <div style={{ width: '100%', maxWidth: 640 }}>
              {/* User prompt */}
              <div className="chat-user-msg" style={{ marginBottom: 20 }}>
                <div className="avatar">👤</div>
                <div className="msg-text">{userPrompt}</div>
              </div>

              <div className="chat-ai-msg">
                <div className="avatar">✨</div>
                <div className="msg-content">
                  <PlanningProgress />
                </div>
              </div>
            </div>
          </div>
        )}

        {/* RESULT — conversational itinerary */}
        {stage === 'result' && result && (
          <div style={{ flex: 1, padding: '20px 20px 40px' }} className="animate-fade-in-up">
            <ConversationView
              userPrompt={userPrompt}
              result={result}
              onBack={() => setStage('enhanced')}
              onNewTrip={handleReset}
            />
          </div>
        )}
      </main>

      {stage === 'home' && <Footer />}
    </div>
  );
}
