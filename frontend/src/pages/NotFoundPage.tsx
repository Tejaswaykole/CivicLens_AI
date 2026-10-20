import React from 'react';
import { Link } from 'react-router-dom';
import { Button } from '../components/ui/Button';
import { Compass, Home } from 'lucide-react';

export const NotFoundPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-surface-container-high/40 flex items-center justify-center p-4">
      <div className="w-full max-w-md bg-surface-lowest rounded-xl shadow-card border border-outline-variant/40 p-8 text-center flex flex-col items-center gap-4">
        <div className="w-16 h-16 rounded-full bg-secondary-container text-secondary flex items-center justify-center">
          <Compass className="w-8 h-8" />
        </div>

        <h1 className="text-2xl font-bold font-display text-primary">404 - Page Not Found</h1>
        <p className="text-xs text-on-surface-variant max-w-xs leading-relaxed">
          The requested administrative view or grievance docket could not be located on the
          CivicLens municipal portal.
        </p>

        <Link to="/app/dashboard" className="mt-2">
          <Button size="sm" icon={<Home className="w-3.5 h-3.5" />}>
            Return to Dashboard
          </Button>
        </Link>
      </div>
    </div>
  );
};
