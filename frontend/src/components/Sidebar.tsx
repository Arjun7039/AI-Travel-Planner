import { Link, useLocation } from 'react-router-dom';
import { Plane, MessageSquare, Compass, Bookmark, Sparkles, Plus, LogOut, LogIn, Menu, X } from 'lucide-react';
import { useState } from 'react';

export function Sidebar() {
  const location = useLocation();
  const [isOpen, setIsOpen] = useState(false);
  
  const token = localStorage.getItem('voyagr_token');
  const userName = localStorage.getItem('voyagr_name') || 'Guest Explorer';

  const menuItems = [
    { name: 'Chats', icon: MessageSquare, path: '/plan' },
    { name: 'Trips', icon: Compass, path: '/' },
    { name: 'Explore', icon: Sparkles, path: '/#destinations' },
    { name: 'Saved', icon: Bookmark, path: '/#saved' },
  ];

  const handleSignOut = () => {
    localStorage.removeItem('voyagr_token');
    localStorage.removeItem('voyagr_name');
    window.location.href = '/';
  };

  const handleNavigationClick = () => {
    setIsOpen(false);
  };

  return (
    <>
      {/* Mobile top bar toggle button */}
      <div className="md:hidden fixed top-4 left-4 z-40">
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="p-2.5 rounded-xl border border-border bg-card/85 backdrop-blur-md text-foreground cursor-pointer transition hover:bg-neutral-800"
        >
          {isOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
        </button>
      </div>

      {/* Backdrop for mobile */}
      {isOpen && (
        <div
          onClick={() => setIsOpen(false)}
          className="md:hidden fixed inset-0 z-30 bg-black/60 backdrop-blur-sm"
        />
      )}

      {/* Sidebar Container */}
      <aside
        className={`fixed top-0 bottom-0 left-0 z-35 w-64 border-r border-border bg-[#0a0a0a]/95 backdrop-blur-xl flex flex-col justify-between py-6 px-4 transition-transform duration-300 md:translate-x-0 ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        {/* Top: Branding and New Chat */}
        <div className="flex flex-col gap-8">
          <Link
            to="/"
            onClick={handleNavigationClick}
            className="flex items-center gap-2.5 px-3 py-1 font-bold text-xl text-foreground"
            style={{ fontFamily: 'var(--font-display)' }}
          >
            <span className="inline-flex h-8 w-8 items-center justify-center rounded-lg bg-accent text-[#0d0d0d]">
              <Plane className="h-4.5 w-4.5" />
            </span>
            voyagr
          </Link>

          {/* New Chat Button */}
          <Link
            to="/plan"
            onClick={handleNavigationClick}
            className="flex items-center justify-center gap-2.5 px-4 py-3 rounded-xl bg-accent text-[#0d0d0d] font-bold text-sm uppercase tracking-wide cursor-pointer transition duration-300 hover:bg-accent-hover hover:scale-[1.02] active:scale-95 shadow-lg shadow-accent/10"
          >
            <Plus className="h-4.5 w-4.5 stroke-[2.5]" />
            New Trip Plan
          </Link>

          {/* Menu Items */}
          <nav className="flex flex-col gap-1.5 mt-2">
            <span className="text-[10px] uppercase tracking-wider font-extrabold text-neutral-500 px-3 mb-2">
              Discover
            </span>
            {menuItems.map((item) => {
              const isActive = location.pathname === item.path;
              return (
                <Link
                  key={item.name}
                  to={item.path}
                  onClick={handleNavigationClick}
                  className={`flex items-center gap-3 px-3 py-3 rounded-xl text-sm font-medium transition duration-200 cursor-pointer ${
                    isActive
                      ? 'bg-neutral-900 text-accent font-semibold border-l-2 border-accent'
                      : 'text-neutral-400 hover:text-foreground hover:bg-neutral-900/60'
                  }`}
                >
                  <item.icon className={`h-4.5 w-4.5 ${isActive ? 'text-accent' : 'text-neutral-400'}`} />
                  {item.name}
                </Link>
              );
            })}
          </nav>
        </div>

        {/* Bottom Profile and Session Status */}
        <div className="flex flex-col gap-4 border-t border-border/60 pt-6 px-1">
          {token ? (
            <div className="flex flex-col gap-3">
              {/* User Identity info block */}
              <div className="flex items-center gap-3 px-2">
                <div className="h-9 w-9 rounded-full bg-accent/20 border border-accent/40 flex items-center justify-center font-bold text-accent">
                  {userName.charAt(0).toUpperCase()}
                </div>
                <div className="flex flex-col min-w-0">
                  <span className="text-xs font-semibold text-foreground truncate" style={{ fontFamily: 'var(--font-display)' }}>
                    {userName}
                  </span>
                  <span className="text-[10px] text-neutral-500 font-medium">Premium Member</span>
                </div>
              </div>

              {/* Logout button */}
              <button
                onClick={handleSignOut}
                className="w-full flex items-center gap-2.5 px-3 py-2.5 rounded-xl text-xs font-semibold text-neutral-400 cursor-pointer transition hover:text-red-400 hover:bg-red-500/10"
              >
                <LogOut className="h-4.5 w-4.5" />
                Sign Out
              </button>
            </div>
          ) : (
            <div className="flex flex-col gap-2.5">
              <Link
                to="/login"
                onClick={handleNavigationClick}
                className="w-full flex items-center justify-center gap-2 px-4 py-3 rounded-xl border border-border bg-neutral-900/40 text-neutral-200 text-xs font-bold uppercase tracking-wider hover:bg-neutral-800 transition duration-200"
              >
                <LogIn className="h-4 w-4" />
                Sign In
              </Link>
              <Link
                to="/signup"
                onClick={handleNavigationClick}
                className="w-full flex items-center justify-center py-3 rounded-xl bg-accent text-[#0d0d0d] text-xs font-bold uppercase tracking-wider hover:bg-accent-hover transition duration-200"
              >
                Get Started
              </Link>
            </div>
          )}
        </div>
      </aside>
    </>
  );
}
