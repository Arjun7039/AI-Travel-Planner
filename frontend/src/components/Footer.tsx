/**
 * Footer — Simple footer with branding.
 */

export function Footer() {
  return (
    <footer style={{
      padding: '20px 24px',
      borderTop: '1px solid var(--border)',
      textAlign: 'center',
      position: 'relative',
      zIndex: 10,
    }}>
      <p style={{ fontSize: 12, color: 'var(--text-muted)' }}>
        Built with ✨ LangGraph + Groq + React — Multi-Agent AI Travel Planner
      </p>
      <p style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 4, opacity: 0.6 }}>
        © 2026 Voyagr AI. Open Source Project.
      </p>
    </footer>
  );
}
