import React from 'react';
import { ArrowUpRight, ArrowDownRight, Minus, LucideIcon } from 'lucide-react';

export interface KPICardProps {
  id: string;
  title: string;
  value: string | number;
  change?: number | null; // percentage change, e.g. 12.4 or -3.2, or null for neutral state
  changePeriod?: string;
  subtitle?: string;
  target?: string;
  icon?: LucideIcon;
  variant?: 'default' | 'accent' | 'success' | 'warning';
  sparklineData?: number[];
}

export const KPICard: React.FC<KPICardProps> = ({
  id,
  title,
  value,
  change,
  changePeriod = 'vs last period',
  subtitle,
  target,
  icon: Icon,
  variant = 'default',
  sparklineData
}) => {
  const isPositive = typeof change === 'number' && change > 0;
  const isNegative = typeof change === 'number' && change < 0;
  const isNeutral = typeof change === 'number' && change === 0;

  const bgStyles = {
    default: 'bg-white border-slate-200/90 text-slate-900',
    accent: 'bg-gradient-to-br from-white to-blue-50/40 border-blue-200/80 text-slate-900',
    success: 'bg-gradient-to-br from-white to-emerald-50/40 border-emerald-200/80 text-slate-900',
    warning: 'bg-gradient-to-br from-white to-amber-50/40 border-amber-200/80 text-slate-900'
  };

  return (
    <div
      id={id}
      className={`relative p-4 sm:p-5 rounded-xl border shadow-xs transition-all hover:shadow-sm flex flex-col justify-between h-full min-w-0 ${bgStyles[variant]}`}
    >
      <div>
        <div className="flex items-start justify-between gap-2 mb-2">
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-700 truncate" title={title}>
            {title}
          </span>
          {Icon && (
            <div className="p-1.5 rounded-lg bg-slate-100/90 text-slate-700 shrink-0">
              <Icon className="w-4 h-4" />
            </div>
          )}
        </div>

        <div className="flex items-baseline gap-2 mb-2">
          <span className="text-xl sm:text-2xl font-bold tracking-tight text-slate-900 font-display whitespace-nowrap overflow-hidden text-ellipsis" title={String(value)}>
            {value}
          </span>
        </div>
      </div>

      <div className="mt-auto pt-1">
        {typeof change === 'number' && (
          <div className="flex items-center gap-1.5 text-xs flex-wrap">
            <span
              className={`inline-flex items-center gap-0.5 px-1.5 py-0.5 rounded font-semibold ${
                isPositive
                  ? 'bg-emerald-50 text-emerald-700'
                  : isNegative
                  ? 'bg-rose-50 text-rose-700'
                  : 'bg-slate-100 text-slate-600'
              }`}
            >
              {isPositive && <ArrowUpRight className="w-3.5 h-3.5" />}
              {isNegative && <ArrowDownRight className="w-3.5 h-3.5" />}
              {isNeutral && <Minus className="w-3.5 h-3.5" />}
              {Math.abs(change).toFixed(2)}%
            </span>
            <span className="text-slate-600 font-medium">{changePeriod}</span>
          </div>
        )}

        {change === null && (
          <div className="flex items-center gap-2 text-xs">
            <span className="inline-flex items-center px-1.5 py-0.5 rounded font-semibold bg-slate-100 text-slate-500">
              —
            </span>
            {changePeriod && <span className="text-slate-600">{changePeriod}</span>}
          </div>
        )}

        {subtitle && !change && (
          <div className="text-xs text-slate-600 mt-0.5">{subtitle}</div>
        )}

        {target && (
          <div className="mt-2.5 pt-2 border-t border-slate-100 flex items-center justify-between text-xs text-slate-600">
            <span>Target benchmark:</span>
            <span className="font-semibold text-slate-700">{target}</span>
          </div>
        )}

        {sparklineData && sparklineData.length > 0 && (
          <div className="mt-2.5 flex items-end gap-1 h-6 pt-1">
            {sparklineData.map((val, idx) => {
              const max = Math.max(...sparklineData, 1);
              const heightPct = Math.max(15, Math.round((val / max) * 100));
              return (
                <div
                  key={idx}
                  className="flex-1 bg-blue-200 hover:bg-blue-500 rounded-xs transition-colors"
                  style={{ height: `${heightPct}%` }}
                  title={`Value: ${val}`}
                />
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};
