import { Link } from 'react-router-dom';
import { Plane } from 'lucide-react';
import heroImg from '../assets/hero.png';

interface AuthShellProps {
  title: string;
  subtitle: string;
  children: React.ReactNode;
  footer: React.ReactNode;
}

export function AuthShell({ title, subtitle, children, footer }: AuthShellProps) {
  return (
    <div className="min-h-screen grid lg:grid-cols-2 bg-[#0d0d0d]">
      {/* Visual side */}
      <div className="relative hidden lg:block">
        <img src={heroImg} alt="" className="absolute inset-0 h-full w-full object-cover" />
        <div className="absolute inset-0 bg-gradient-to-br from-accent/30 via-neutral-950/40 to-neutral-950/80" />
        <div className="relative h-full flex flex-col justify-between p-12 text-white">
          <Link to="/" className="flex items-center gap-2.5 text-xl font-bold" style={{ fontFamily: 'var(--font-display)' }}>
            <span className="inline-flex h-9 w-9 items-center justify-center rounded-lg bg-accent text-[#0d0d0d]">
              <Plane className="h-4.5 w-4.5" />
            </span>
            voyagr
          </Link>
          <div className="max-w-md">
            <h2 className="text-4xl font-bold leading-tight" style={{ fontFamily: 'var(--font-display)', textWrap: 'balance' }}>
              "Voyagr planned my honeymoon in 30 seconds. It was better than any agent."
            </h2>
            <p className="mt-4 opacity-90 text-accent font-semibold">— Amelia & Ravi, Santorini 2026</p>
          </div>
        </div>
      </div>

      {/* Form side */}
      <div className="flex items-center justify-center p-6 sm:p-12 bg-[#0d0d0d]">
        <div className="w-full max-w-md">
          <Link to="/" className="lg:hidden flex items-center gap-2.5 text-xl font-bold mb-8" style={{ fontFamily: 'var(--font-display)' }}>
            <span className="inline-flex h-9 w-9 items-center justify-center rounded-lg bg-accent text-[#0d0d0d]">
              <Plane className="h-4.5 w-4.5" />
            </span>
            voyagr
          </Link>
          <h1 className="text-3xl font-bold text-neutral-100" style={{ fontFamily: 'var(--font-display)' }}>{title}</h1>
          <p className="mt-2 text-sm text-neutral-400 font-medium">{subtitle}</p>
          <div className="mt-8 space-y-4">{children}</div>
          <div className="mt-8 text-xs text-neutral-500 font-semibold">{footer}</div>
        </div>
      </div>
    </div>
  );
}

interface FieldProps {
  label: string;
  type?: string;
  placeholder?: string;
  name?: string;
  value?: string;
  onChange?: (e: React.ChangeEvent<HTMLInputElement>) => void;
}

export function Field({ label, type = 'text', placeholder, name, value, onChange }: FieldProps) {
  return (
    <label className="block space-y-1.5">
      <span className="text-[10px] uppercase tracking-wider font-extrabold text-neutral-500">{label}</span>
      <input
        type={type}
        name={name}
        placeholder={placeholder}
        value={value}
        onChange={onChange}
        className="w-full rounded-xl border border-border/80 px-4 py-3 text-xs font-semibold outline-none bg-neutral-950/40 text-neutral-200 transition focus:border-accent/40 focus:ring-2 focus:ring-accent/10"
      />
    </label>
  );
}
