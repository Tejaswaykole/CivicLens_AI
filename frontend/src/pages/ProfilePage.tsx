import React from 'react';
import { Card } from '../components/ui/Card';
import { useRolePreview } from '../context/useRolePreview';
import { Mail, Shield, MapPin, Building, Key } from 'lucide-react';

export const ProfilePage: React.FC = () => {
  const { currentUser, currentRole } = useRolePreview();

  return (
    <div className="flex flex-col gap-6 max-w-4xl mx-auto">
      <div className="bg-surface-container p-6 rounded-lg border border-outline-variant/30 shadow-card">
        <h1 className="text-2xl font-bold font-display text-primary">Official Profile & Credentials</h1>
        <p className="text-xs text-on-surface-variant max-w-xl mt-1">
          Municipal administrative credentials, jurisdictional assignment, and access controls.
        </p>
      </div>

      <Card title="Personnel Record">
        <div className="flex flex-col sm:flex-row items-center gap-6 pb-6 border-b border-outline-variant/20">
          <div className="w-20 h-20 rounded-full bg-secondary text-white font-display font-bold text-2xl flex items-center justify-center border-4 border-surface shadow-sm">
            {currentUser.avatarInitials}
          </div>
          <div className="flex flex-col text-center sm:text-left">
            <h2 className="text-lg font-bold font-display text-primary">{currentUser.name}</h2>
            <p className="text-xs text-secondary font-medium">
              {currentUser.designation || currentUser.role.replace('_', ' ').toUpperCase()}
            </p>
            <p className="text-xs text-on-surface-variant mt-1 flex items-center justify-center sm:justify-start gap-1">
              <Mail className="w-3.5 h-3.5" /> {currentUser.email}
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-4 text-xs">
          <div className="p-3 rounded bg-surface-container-low border border-outline-variant/30 flex items-start gap-2.5">
            <Shield className="w-4 h-4 text-primary shrink-0 mt-0.5" />
            <div>
              <span className="font-semibold text-primary block">Designated Role</span>
              <span className="text-on-surface-variant capitalize">{currentRole.replace('_', ' ')}</span>
            </div>
          </div>

          <div className="p-3 rounded bg-surface-container-low border border-outline-variant/30 flex items-start gap-2.5">
            <MapPin className="w-4 h-4 text-secondary shrink-0 mt-0.5" />
            <div>
              <span className="font-semibold text-primary block">Jurisdiction Zone / Ward</span>
              <span className="text-on-surface-variant">{currentUser.wardOrZone || 'NCT All Zones'}</span>
            </div>
          </div>

          <div className="p-3 rounded bg-surface-container-low border border-outline-variant/30 flex items-start gap-2.5">
            <Building className="w-4 h-4 text-primary shrink-0 mt-0.5" />
            <div>
              <span className="font-semibold text-primary block">Assigned Authority</span>
              <span className="text-on-surface-variant">Government of NCT of Delhi</span>
            </div>
          </div>

          <div className="p-3 rounded bg-surface-container-low border border-outline-variant/30 flex items-start gap-2.5">
            <Key className="w-4 h-4 text-secondary shrink-0 mt-0.5" />
            <div>
              <span className="font-semibold text-primary block">Security Protocol</span>
              <span className="text-on-surface-variant">NIC 2FA Token Enforced</span>
            </div>
          </div>
        </div>
      </Card>
    </div>
  );
};
