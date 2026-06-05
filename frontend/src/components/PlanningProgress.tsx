/**
 * PlanningProgress — Shows the 3-agent pipeline progress during generation.
 */

const steps = [
  { id: 'research', icon: '🔍', title: 'Research Agent', desc: 'Gathering weather, attractions, and hotels...' },
  { id: 'planner', icon: '✈️', title: 'Planner Agent', desc: 'Crafting your day-by-day itinerary...' },
  { id: 'budget', icon: '💰', title: 'Budget Agent', desc: 'Validating costs and optimizing budget...' },
];

export function PlanningProgress() {
  return (
    <div>
      <p style={{ fontSize: 14, fontWeight: 600, color: 'var(--text-primary)', marginBottom: 16 }}>
        Crafting your perfect itinerary...
      </p>

      {steps.map((step, idx) => (
        <div className="progress-step animate-fade-in" key={step.id} style={{ animationDelay: `${idx * 0.5}s` }}>
          <div className="step-icon running">
            {step.icon}
          </div>
          <div className="step-info">
            <div className="step-title">{step.title}</div>
            <div className="step-desc">{step.desc}</div>
          </div>
        </div>
      ))}

      <div className="typing-indicator" style={{ marginTop: 16 }}>
        <span />
        <span />
        <span />
      </div>
      <p style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 4 }}>
        This usually takes 5-10 seconds...
      </p>
    </div>
  );
}
