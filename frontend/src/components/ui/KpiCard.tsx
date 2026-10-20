import React from 'react';
import { cn } from '../../utils';

interface KpiCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon?: React.ReactNode;
  badge?: React.ReactNode;
  footer?: React.ReactNode;
  valueColor?: string;
  className?: string;
}

export const KpiCard: React.FC<KpiCardProps> = ({
  title,
  value,
  subtitle,
  icon,
  badge,
  footer,
  valueColor = 'text-primary',
  className,
}) => {
  return (
    <div
      className={cn(
        'bg-surface-lowest p-5 rounded-lg border border-outline-variant/30 flex flex-col justify-between shadow-card hover:border-outline-variant/50 transition-all',
        className
      )}
    >
      <div className="flex items-start justify-between gap-2">
        <div className="flex flex-col">
          <div className="flex items-center gap-2">
            <span className="text-xs uppercase tracking-wider text-on-surface-variant font-bold">
              {title}
            </span>
            {badge}
          </div>
          <span className={cn('text-3xl font-bold font-display mt-2 tracking-tight', valueColor)}>
            {value}
          </span>
          {subtitle && (
            <p className="text-xs text-on-surface-variant mt-1 leading-snug">{subtitle}</p>
          )}
        </div>
        {icon && (
          <div className="p-2.5 rounded bg-surface-container text-primary flex items-center justify-center shrink-0">
            {icon}
          </div>
        )}
      </div>

      {footer && (
        <div className="mt-4 pt-3 border-t border-outline-variant/20 flex flex-col gap-1 text-xs">
          {footer}
        </div>
      )}
    </div>
  );
};
