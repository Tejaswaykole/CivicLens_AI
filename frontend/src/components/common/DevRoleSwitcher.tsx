import React from 'react';
import { useRolePreview } from '../../context/useRolePreview';
import type { UserRole } from '../../types';
import { ShieldCheck, UserCheck, Wrench, User as UserIcon } from 'lucide-react';

export const DevRoleSwitcher: React.FC = () => {
  const { currentRole, setRole, isDevMode } = useRolePreview();

  // Must not be exposed in non-development environments
  if (!isDevMode) return null;

  const roles: { id: UserRole; label: string; icon: React.ReactNode }[] = [
    {
      id: 'system_admin',
      label: 'System Admin',
      icon: <ShieldCheck className="w-3.5 h-3.5 text-primary" />,
    },
    {
      id: 'grievance_officer',
      label: 'Grievance Officer',
      icon: <UserCheck className="w-3.5 h-3.5 text-secondary" />,
    },
    {
      id: 'department_officer',
      label: 'Dept Officer',
      icon: <Wrench className="w-3.5 h-3.5 text-amber-700" />,
    },
    {
      id: 'citizen',
      label: 'Citizen',
      icon: <UserIcon className="w-3.5 h-3.5 text-emerald-700" />,
    },
  ];

  return (
    <div
      role="region"
      aria-label="Development Role Previewer"
      className="fixed bottom-3 right-4 z-50 bg-surface-container-high/95 backdrop-blur-md border border-outline-variant/60 rounded-lg p-2 shadow-floating flex items-center gap-2 text-xs"
    >
      <div className="flex items-center gap-1.5 px-2 py-0.5 rounded bg-surface-container font-medium text-[11px] text-on-surface-variant border border-outline-variant/40">
        <span className="w-1.5 h-1.5 rounded-full bg-secondary animate-pulse" />
        <span className="font-semibold uppercase tracking-wider text-[10px]">Dev Preview</span>
      </div>

      <div className="flex items-center gap-1">
        {roles.map((r) => {
          const isActive = currentRole === r.id;
          return (
            <button
              key={r.id}
              onClick={() => setRole(r.id)}
              className={`flex items-center gap-1.5 px-2.5 py-1 rounded transition-colors text-[11px] font-medium ${
                isActive
                  ? 'bg-primary text-white shadow-sm font-semibold'
                  : 'bg-surface-lowest text-on-surface hover:bg-surface-low border border-outline-variant/30'
              }`}
              title={`Switch preview to ${r.label}`}
            >
              {r.icon}
              <span>{r.label}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
};
