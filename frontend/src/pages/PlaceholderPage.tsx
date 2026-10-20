import React from 'react';
import { Card } from '../components/ui/Card';
import { Construction } from 'lucide-react';

interface PlaceholderProps {
  title: string;
  description: string;
  phase?: string;
}

export const PlaceholderPage: React.FC<PlaceholderProps> = ({
  title,
  description,
  phase = 'Phase 2',
}) => {
  return (
    <div className="flex flex-col gap-6 max-w-4xl mx-auto">
      <div className="bg-surface-container p-6 rounded-lg border border-outline-variant/30 shadow-card">
        <h1 className="text-2xl font-bold font-display text-primary">{title}</h1>
        <p className="text-xs text-on-surface-variant max-w-xl mt-1">{description}</p>
      </div>

      <Card>
        <div className="flex flex-col items-center justify-center p-12 text-center">
          <div className="p-3 rounded-full bg-surface-container text-secondary mb-3">
            <Construction className="w-8 h-8" />
          </div>
          <h2 className="text-base font-bold font-display text-primary">{title} Module</h2>
          <p className="text-xs text-on-surface-variant max-w-sm mt-1">
            This module is reserved for {phase} implementation according to the CivicLens AI
            architecture plan.
          </p>
        </div>
      </Card>
    </div>
  );
};
