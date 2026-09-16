import React from 'react';
import { AlertTriangle, RotateCcw } from 'lucide-react';

export const ErrorState: React.FC<{
  title?: string;
  message?: string;
  onRetry?: () => void;
}> = ({
  title = 'Failed to load data',
  message = 'An error occurred while calculating analytical dimensions.',
  onRetry
}) => {
  return (
    <div className="flex flex-col items-center justify-center p-12 text-center bg-rose-50/40 rounded-xl border border-rose-200 shadow-xs">
      <div className="p-3 bg-rose-100 rounded-full text-rose-600 mb-3">
        <AlertTriangle className="w-6 h-6" />
      </div>
      <h3 className="text-sm font-bold text-slate-900">{title}</h3>
      <p className="text-xs text-slate-600 mt-1 max-w-md">{message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="mt-4 inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-white bg-slate-900 rounded-lg hover:bg-slate-800 transition-colors"
        >
          <RotateCcw className="w-3.5 h-3.5" />
          <span>Try Again</span>
        </button>
      )}
    </div>
  );
};
