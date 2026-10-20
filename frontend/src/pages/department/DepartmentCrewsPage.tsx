import React, { useState } from 'react';
import { Card } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { Users, MapPin } from 'lucide-react';

export const DepartmentCrewsPage: React.FC = () => {
  const [crews, setCrews] = useState([
    {
      id: 'cr_01',
      name: 'Unit 4 (Asphalt Rapid Paver)',
      lead: 'Er. Vikram Malhotra',
      membersCount: 8,
      status: 'On Site',
      assignedWard: 'Ward 24 - Outer Ring Road',
      currentTask: 'DEL-2024-8921 (Crater patching)',
      equipment: 'Hot-mix asphalt roller, vibratory tamper',
    },
    {
      id: 'cr_02',
      name: 'Unit 2 (Storm Drainage Jetting)',
      lead: 'S. Sharma',
      membersCount: 6,
      status: 'En Route',
      assignedWard: 'Ward 18 - Janakpuri',
      currentTask: 'DEL-2024-8922 (Culvert desilting)',
      equipment: 'High-pressure suction jetter, safety winches',
    },
    {
      id: 'cr_03',
      name: 'Unit 7 (Structural Survey)',
      lead: 'K. Verma',
      membersCount: 4,
      status: 'Standby',
      assignedWard: 'Zone 4 Depot',
      currentTask: 'Depot Standby / Inspection Queue',
      equipment: 'Total station, ultrasonic pavement scanner',
    },
  ]);

  const handleToggleStatus = (id: string) => {
    setCrews((prev) =>
      prev.map((c) => {
        if (c.id === id) {
          const nextStatus = c.status === 'On Site' ? 'Standby' : 'On Site';
          return { ...c, status: nextStatus };
        }
        return c;
      })
    );
  };

  return (
    <div className="flex flex-col gap-6">
      {/* Header Banner */}
      <div className="bg-surface-container p-6 rounded-lg border border-outline-variant/30 shadow-card flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <Users className="w-6 h-6 text-primary" />
            <h1 className="text-2xl font-bold font-display text-primary">Field Crew Roster & Telemetry</h1>
          </div>
          <p className="text-xs text-on-surface-variant max-w-xl mt-1">
            Real-time crew deployment, heavy equipment assignment, and on-site task allocation across Zone 4.
          </p>
        </div>

        <span className="px-2.5 py-1 rounded bg-secondary text-white text-xs font-bold uppercase tracking-wider">
          3 Field Units Configured
        </span>
      </div>

      {/* Crew Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {crews.map((c) => (
          <Card key={c.id} className="flex flex-col justify-between">
            <div>
              <div className="flex items-start justify-between pb-3 border-b border-outline-variant/20">
                <div>
                  <h3 className="text-sm font-bold font-display text-primary">{c.name}</h3>
                  <span className="text-[11px] text-on-surface-variant block mt-0.5">
                    Lead: {c.lead} • {c.membersCount} Crew Members
                  </span>
                </div>
                <span
                  className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                    c.status === 'On Site'
                      ? 'bg-emerald-100 text-emerald-800'
                      : c.status === 'En Route'
                      ? 'bg-amber-100 text-amber-800'
                      : 'bg-gray-200 text-gray-700'
                  }`}
                >
                  {c.status}
                </span>
              </div>

              <div className="py-3 flex flex-col gap-2 text-xs">
                <div>
                  <span className="text-[10px] uppercase font-bold text-outline block">Active Assignment</span>
                  <span className="font-semibold text-primary">{c.currentTask}</span>
                </div>
                <div>
                  <span className="text-[10px] uppercase font-bold text-outline block">Zonal Location</span>
                  <span className="text-on-surface flex items-center gap-1">
                    <MapPin className="w-3.5 h-3.5 text-secondary" /> {c.assignedWard}
                  </span>
                </div>
                <div>
                  <span className="text-[10px] uppercase font-bold text-outline block">Assigned Machinery</span>
                  <span className="text-on-surface-variant text-[11px]">{c.equipment}</span>
                </div>
              </div>
            </div>

            <div className="pt-3 border-t border-outline-variant/20">
              <Button
                size="sm"
                variant="outline"
                className="w-full"
                onClick={() => handleToggleStatus(c.id)}
              >
                Toggle Status ({c.status === 'On Site' ? 'Set Standby' : 'Set On Site'})
              </Button>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
};
