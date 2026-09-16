import React from 'react';

export interface ChartCardProps {
  id: string;
  title: string;
  subtitle?: string;
  badge?: React.ReactNode;
  actions?: React.ReactNode;
  children: React.ReactNode;
  className?: string;
}

export const ChartCard: React.FC<ChartCardProps> = ({
  id,
  title,
  subtitle,
  badge,
  actions,
  children,
  className = ''
}) => {
  return (
    <div
      id={id}
      className={`bg-white border border-slate-200/90 rounded-xl p-5 shadow-xs transition-shadow hover:shadow-xs ${className}`}
    >
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-4 mb-4 border-b border-slate-100">
        <div>
          <div className="flex items-center gap-2">
            <h3 className="text-base font-bold text-slate-900 tracking-tight">{title}</h3>
            {badge}
          </div>
          {subtitle && <p className="text-xs text-slate-700 mt-0.5">{subtitle}</p>}
        </div>
        {actions && <div className="flex items-center gap-2 self-start sm:self-auto">{actions}</div>}
      </div>

      <div className="w-full relative">{children}</div>
    </div>
  );
};
