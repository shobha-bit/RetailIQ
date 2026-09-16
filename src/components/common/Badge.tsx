import React from 'react';

export interface BadgeProps {
  id?: string;
  children: React.ReactNode;
  variant?: 'primary' | 'success' | 'warning' | 'danger' | 'neutral' | 'purple' | 'info' | 'cyan';
  size?: 'sm' | 'md';
  dot?: boolean;
  className?: string;
}

export const Badge: React.FC<BadgeProps> = ({
  id,
  children,
  variant = 'neutral',
  size = 'md',
  dot = false,
  className = ''
}) => {
  const variantStyles = {
    primary: 'bg-blue-50 text-blue-700 border border-blue-200/60',
    success: 'bg-emerald-50 text-emerald-700 border border-emerald-200/60',
    warning: 'bg-amber-50 text-amber-700 border border-amber-200/60',
    danger: 'bg-rose-50 text-rose-700 border border-rose-200/60',
    neutral: 'bg-slate-100 text-slate-700 border border-slate-200/80',
    purple: 'bg-purple-50 text-purple-700 border border-purple-200/60',
    info: 'bg-indigo-50 text-indigo-700 border border-indigo-200/60',
    cyan: 'bg-cyan-50 text-cyan-700 border border-cyan-200/60'
  };

  const dotColors = {
    primary: 'bg-blue-500',
    success: 'bg-emerald-500',
    warning: 'bg-amber-500',
    danger: 'bg-rose-500',
    neutral: 'bg-slate-400',
    purple: 'bg-purple-500',
    info: 'bg-indigo-500',
    cyan: 'bg-cyan-500'
  };

  const sizeStyles = {
    sm: 'px-2 py-0.5 text-xs font-medium',
    md: 'px-2.5 py-1 text-xs font-semibold'
  };

  return (
    <span
      id={id}
      className={`inline-flex items-center gap-1.5 rounded-full whitespace-nowrap ${variantStyles[variant]} ${sizeStyles[size]} ${className}`}
    >
      {dot && <span className={`w-1.5 h-1.5 rounded-full ${dotColors[variant]}`} />}
      {children}
    </span>
  );
};
