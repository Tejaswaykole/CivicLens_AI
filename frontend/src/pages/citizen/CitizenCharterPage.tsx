import { Card } from '../../components/ui/Card';
import { ShieldCheck, Clock } from 'lucide-react';

export const CitizenCharterPage: React.FC = () => {
  const commitments = [
    {
      category: 'Critical Hazard & Life Safety (Fallen Wires, Gas Leaks, Cave-ins)',
      sla: '4 to 12 Hours',
      level: 'Emergency Dispatch',
      badge: 'bg-red-100 text-red-800',
    },
    {
      category: 'Potable Water Contamination & Acute Sewer Blockages',
      sla: '24 Hours',
      level: 'High Priority',
      badge: 'bg-amber-100 text-amber-800',
    },
    {
      category: 'Pothole Repairs, Crater Patching & Arterial Obstructions',
      sla: '48 Hours',
      level: 'Medium Triage',
      badge: 'bg-blue-100 text-blue-800',
    },
    {
      category: 'Streetlight Luminaires, Parks & Routine Sanitation',
      sla: '72 Hours',
      level: 'Routine Schedule',
      badge: 'bg-gray-100 text-gray-800',
    },
  ];

  return (
    <div className="flex flex-col gap-6 max-w-4xl mx-auto">
      {/* Header Banner */}
      <div className="bg-surface-container p-6 rounded-lg border border-outline-variant/30 shadow-card flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <ShieldCheck className="w-6 h-6 text-primary" />
            <h1 className="text-2xl font-bold font-display text-primary">Citizen Grievance Charter</h1>
          </div>
          <p className="text-xs text-on-surface-variant max-w-xl mt-1">
            Statutory redressal commitments, line agency escalation guidelines, and citizen rights.
          </p>
        </div>

        <span className="px-2.5 py-1 rounded bg-secondary text-white text-xs font-bold uppercase tracking-wider">
          SOP v4.1 Mandate
        </span>
      </div>

      <div className="grid grid-cols-1 gap-4">
        {commitments.map((c, i) => (
          <Card key={i}>
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
              <div className="flex flex-col">
                <span className="font-bold text-primary text-sm">{c.category}</span>
                <span className="text-on-surface-variant text-[11px] mt-0.5">
                  Authorized Line Agencies: PWD, DJB, MCD, DISCOM
                </span>
              </div>
              <div className="flex items-center gap-3 self-start sm:self-auto">
                <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${c.badge}`}>
                  {c.level}
                </span>
                <span className="font-bold font-display text-primary text-base flex items-center gap-1">
                  <Clock className="w-4 h-4 text-secondary" /> {c.sla}
                </span>
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
};
