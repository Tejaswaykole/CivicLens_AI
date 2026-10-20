import React from 'react';
import { AlertCircle, Inbox, Loader2 } from 'lucide-react';
import { Button } from './Button';

export const LoadingState: React.FC<{ message?: string }> = ({
  message = 'Loading civic records...',
}) => {
  return (
    <div className="flex flex-col items-center justify-center p-12 text-center">
      <Loader2 className="w-8 h-8 text-primary animate-spin mb-3" />
      <p className="text-sm text-on-surface-variant font-medium">{message}</p>
    </div>
  );
};

export const EmptyState: React.FC<{
  title?: string;
  description?: string;
  actionLabel?: string;
  onAction?: () => void;
}> = ({
  title = 'No records found',
  description = 'There are no active records matching the current filter criteria.',
  actionLabel,
  onAction,
}) => {
  return (
    <div className="flex flex-col items-center justify-center p-12 text-center bg-surface-container/30 rounded-lg border border-dashed border-outline-variant/60">
      <Inbox className="w-10 h-10 text-outline mb-3" />
      <h3 className="text-base font-bold text-primary font-display">{title}</h3>
      <p className="text-xs text-on-surface-variant max-w-sm mt-1">{description}</p>
      {actionLabel && onAction && (
        <Button size="sm" variant="outline" className="mt-4" onClick={onAction}>
          {actionLabel}
        </Button>
      )}
    </div>
  );
};

export const ErrorState: React.FC<{
  message?: string;
  onRetry?: () => void;
}> = ({ message = 'An error occurred while loading civic records.', onRetry }) => {
  return (
    <div className="flex flex-col items-center justify-center p-10 text-center bg-error-container/20 rounded-lg border border-error/20">
      <AlertCircle className="w-9 h-9 text-error mb-2" />
      <h3 className="text-sm font-bold text-error">Unable to complete request</h3>
      <p className="text-xs text-on-surface-variant max-w-sm mt-1">{message}</p>
      {onRetry && (
        <Button size="sm" variant="outline" className="mt-3" onClick={onRetry}>
          Retry Request
        </Button>
      )}
    </div>
  );
};
