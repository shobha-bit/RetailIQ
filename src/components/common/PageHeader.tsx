import React from 'react';

export interface PageHeaderProps {
  id: string;
  title: string;
  description: string;
  badge?: React.ReactNode;
  actions?: React.ReactNode;
}

export const PageHeader: React.FC<PageHeaderProps> = ({
  id,
  title,
  description,
  badge,
  actions
}) => {
  return (
    <div
      id={id}
      className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-6 mb-6 border-b border-slate-200/80"
    >
      <div>
        <div className="flex items-center gap-2.5">
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight font-display">
            {title}
          </h1>
          {badge}
        </div>
        <p className="text-sm text-slate-600 mt-1 max-w-3xl leading-relaxed">
          {description}
        </p>
      </div>

      {actions && (
        <div className="flex flex-wrap items-center gap-2.5 self-start md:self-auto">
          {actions}
        </div>
      )}
    </div>
  );
};
