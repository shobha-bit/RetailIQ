import React from 'react';
import { PackageOpen } from 'lucide-react';

export const EmptyState: React.FC<{
  title?: string;
  message?: string;
  action?: React.ReactNode;
}> = ({
  title = 'No records available',
  message = 'Try changing your active filters or uploading a new dataset to view insights.',
  action
}) => {
  return (
    <div className="flex flex-col items-center justify-center p-12 text-center bg-slate-50/60 rounded-xl border border-dashed border-slate-300">
      <div className="p-3 bg-white rounded-full text-slate-400 shadow-xs mb-3 border border-slate-200">
        <PackageOpen className="w-6 h-6" />
      </div>
      <h3 className="text-sm font-bold text-slate-800">{title}</h3>
      <p className="text-xs text-slate-500 mt-1 max-w-sm">{message}</p>
      {action && <div className="mt-4">{action}</div>}
    </div>
  );
};
