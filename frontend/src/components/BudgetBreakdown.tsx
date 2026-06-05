import React from 'react';

interface BudgetItem {
    name: string;
    value: number;
    color: string;
    icon: React.ReactNode;
}

export const BudgetBreakdown: React.FC<{ breakdown: any }> = ({ breakdown }) => {
    if (!breakdown || (Object.keys(breakdown).length === 0)) return (
        <div className="glass-card p-6 text-center text-text-muted text-sm">
            No budget data available
        </div>
    );

    const total = breakdown.total || ((breakdown.flights || 0) + (breakdown.hotels || 0) + (breakdown.activities || 0));

    const items: BudgetItem[] = [
        {
            name: 'Transport',
            value: breakdown.flights || breakdown.transport || 0,
            color: '#6366f1',
            icon: (
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                    <path d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                </svg>
            )
        },
        {
            name: 'Hotels',
            value: breakdown.hotels || 0,
            color: '#a855f7',
            icon: (
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                    <path d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                </svg>
            )
        },
        {
            name: 'Activities',
            value: breakdown.activities || 0,
            color: '#34d399',
            icon: (
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                    <path d="M14.828 14.828a4 4 0 01-5.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
            )
        }
    ];

    return (
        <div className="glass-card p-6 md:p-8">
            <h3 className="text-lg font-bold text-text-primary flex items-center gap-3 mb-6">
                <div className="w-8 h-8 rounded-lg bg-accent/10 border border-accent/20 flex items-center justify-center">
                    <svg className="w-4 h-4 text-accent" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                        <path d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                    </svg>
                </div>
                Budget Breakdown
            </h3>

            {/* Total */}
            <div className="text-center mb-6 p-4 rounded-xl bg-surface-1/60 border border-border">
                <p className="text-xs uppercase tracking-wider text-text-muted mb-1">Total Investment</p>
                <p className="text-3xl font-extrabold text-gradient bg-gradient-to-r from-accent to-cyan-accent">
                    ₹{total.toLocaleString('en-IN')}
                </p>
            </div>

            {/* Segments */}
            <div className="space-y-3">
                {items.map((item) => {
                    const pct = total > 0 ? (item.value / total) * 100 : 0;
                    return (
                        <div key={item.name}>
                            <div className="budget-segment">
                                <div className="flex items-center gap-3">
                                    <div
                                        className="w-8 h-8 rounded-lg flex items-center justify-center"
                                        style={{
                                            background: `${item.color}15`,
                                            color: item.color,
                                            border: `1px solid ${item.color}25`
                                        }}
                                    >
                                        {item.icon}
                                    </div>
                                    <div>
                                        <p className="text-sm font-medium text-text-primary">{item.name}</p>
                                        <p className="text-xs text-text-muted">{pct.toFixed(0)}% of total</p>
                                    </div>
                                </div>
                                <span className="text-sm font-bold font-mono text-text-primary tabular-nums">
                                    ₹{item.value.toLocaleString('en-IN')}
                                </span>
                            </div>
                            <div className="budget-bar">
                                <div
                                    className="budget-bar-fill"
                                    style={{
                                        width: `${pct}%`,
                                        background: `linear-gradient(90deg, ${item.color}, ${item.color}99)`,
                                        boxShadow: `0 0 8px ${item.color}40`
                                    }}
                                />
                            </div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
};
