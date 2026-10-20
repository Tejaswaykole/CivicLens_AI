import React from 'react';
import type { ComplaintPriority, ComplaintStatus } from '../../types';
import { cn } from '../../utils';
import { AlertCircle, Clock, CheckCircle2, ShieldAlert, Sparkles, UserCheck } from 'lucide-react';

interface PriorityBadgeProps {
  priority: ComplaintPriority;
  isAiSuggested?: boolean;
  isHumanConfirmed?: boolean;
  className?: string;
}

export const PriorityBadge: React.FC<PriorityBadgeProps> = ({
  priority,
  isAiSuggested,
  isHumanConfirmed,
  className,
}) => {
  const styles: Record<ComplaintPriority, { bg: string; text: string; border: string }> = {
    critical: {
      bg: 'bg-red-50 text-red-700',
      text: 'text-red-700',
      border: 'border-red-200',
    },
    high: {
      bg: 'bg-amber-50 text-amber-800',
      text: 'text-amber-800',
      border: 'border-amber-200',
    },
    medium: {
      bg: 'bg-blue-50 text-blue-700',
      text: 'text-blue-700',
      border: 'border-blue-200',
    },
    low: {
      bg: 'bg-gray-100 text-gray-700',
      text: 'text-gray-700',
      border: 'border-gray-200',
    },
  };

  const style = styles[priority] || styles.medium;

  return (
    <span
      className={cn(
        'inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded text-xs font-semibold border',
        style.bg,
        style.border,
        className
      )}
    >
      {priority === 'critical' && <ShieldAlert className="w-3 h-3 text-red-600 shrink-0" />}
      {priority === 'high' && <AlertCircle className="w-3 h-3 text-amber-600 shrink-0" />}
      <span className="uppercase tracking-wider font-bold text-[10px]">{priority}</span>

      {isAiSuggested && (
        <span
          className="inline-flex items-center gap-0.5 ml-1 px-1 rounded bg-secondary/15 text-secondary text-[9px] font-bold tracking-tight"
          title="AI-suggested priority"
        >
          <Sparkles className="w-2.5 h-2.5" /> AI
        </span>
      )}

      {isHumanConfirmed && (
        <span
          className="inline-flex items-center gap-0.5 ml-1 px-1 rounded bg-primary/10 text-primary text-[9px] font-bold tracking-tight"
          title="Human officer confirmed priority"
        >
          <UserCheck className="w-2.5 h-2.5" /> Officer
        </span>
      )}
    </span>
  );
};

interface StatusBadgeProps {
  status: ComplaintStatus;
  className?: string;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, className }) => {
  const statusConfig: Record<
    ComplaintStatus,
    { label: string; bg: string; text: string; icon: React.ReactNode }
  > = {
    submitted: {
      label: 'Submitted',
      bg: 'bg-surface-container text-on-surface-variant border-outline-variant/30',
      text: 'text-on-surface-variant',
      icon: <Clock className="w-3 h-3" />,
    },
    in_review: {
      label: 'In Review (HITL)',
      bg: 'bg-secondary/10 text-secondary border-secondary/30',
      text: 'text-secondary',
      icon: <Clock className="w-3 h-3" />,
    },
    triaged: {
      label: 'Triaged',
      bg: 'bg-purple-50 text-purple-700 border-purple-200',
      text: 'text-purple-700',
      icon: <CheckCircle2 className="w-3 h-3" />,
    },
    assigned: {
      label: 'Assigned to Dept',
      bg: 'bg-blue-50 text-blue-700 border-blue-200',
      text: 'text-blue-700',
      icon: <Clock className="w-3 h-3" />,
    },
    in_progress: {
      label: 'Field Crew Dispatched',
      bg: 'bg-amber-50 text-amber-800 border-amber-200',
      text: 'text-amber-800',
      icon: <Clock className="w-3 h-3" />,
    },
    resolved: {
      label: 'Verified & Resolved',
      bg: 'bg-emerald-50 text-emerald-800 border-emerald-200',
      text: 'text-emerald-800',
      icon: <CheckCircle2 className="w-3 h-3" />,
    },
    rejected: {
      label: 'Rejected',
      bg: 'bg-red-50 text-red-700 border-red-200',
      text: 'text-red-700',
      icon: <AlertCircle className="w-3 h-3" />,
    },
  };

  const config = statusConfig[status] || statusConfig.submitted;

  return (
    <span
      className={cn(
        'inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded text-xs font-medium border',
        config.bg,
        className
      )}
    >
      {config.icon}
      <span>{config.label}</span>
    </span>
  );
};
