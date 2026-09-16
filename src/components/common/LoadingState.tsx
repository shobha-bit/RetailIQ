import React from 'react';
import { Loader2 } from 'lucide-react';

export const LoadingState: React.FC<{ message?: string }> = ({ message = 'Loading retail analytics...' }) => {
  return (
    <div className="flex flex-col items-center justify-center p-12 text-center bg-white rounded-xl border border-slate-200/90 shadow-xs">
      <Loader2 className="w-8 h-8 text-blue-600 animate-spin mb-3" />
      <p className="text-sm font-semibold text-slate-700">{message}</p>
      <p className="text-xs text-slate-400 mt-1">Aggregating real-time transactions & inventory state</p>
    </div>
  );
};
