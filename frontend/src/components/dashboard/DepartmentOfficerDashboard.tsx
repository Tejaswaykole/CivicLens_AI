import React, { useState } from 'react';
import { KpiCard } from '../ui/KpiCard';
import { Card } from '../ui/Card';
import { PriorityBadge, StatusBadge } from '../ui/Badges';
import { Button } from '../ui/Button';
import { MOCK_COMPLAINTS } from '../../mock/data';
import type { Complaint } from '../../types';
import {
  Wrench,
  Clock,
  AlertTriangle,
  CheckCircle2,
  Users,
  Truck,
  ArrowUpRight,
} from 'lucide-react';

export const DepartmentOfficerDashboard: React.FC = () => {
  const [complaints] = useState<Complaint[]>(
    MOCK_COMPLAINTS.filter((c) => c.departmentId === 'dept_pwd')
  );

  return (
    <div className="flex flex-col gap-6">
      {/* Header Banner */}
      <div className="bg-surface-container p-6 rounded-lg shadow-card flex flex-col sm:flex-row sm:items-center justify-between gap-4 border border-outline-variant/30">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold font-display text-primary">
              Public Works Department (PWD) Console
            </h1>
            <span className="px-2 py-0.5 rounded bg-midnight-indigo text-white text-[10px] font-bold uppercase tracking-wider">
              Zone 4
            </span>
          </div>
          <p className="text-xs text-on-surface-variant max-w-xl mt-1">
            Execution Workbench for Field Engineers. Dispatch repair crews, monitor SLA compliance
            thresholds, and upload closure evidence.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Button size="sm" variant="outline" icon={<Users className="w-3.5 h-3.5" />}>
            Crew Roster (6 Active)
          </Button>
          <Button size="sm" variant="primary" icon={<Truck className="w-3.5 h-3.5" />}>
            Dispatch Unit
          </Button>
        </div>
      </div>

      {/* 4 Execution KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
        <KpiCard
          title="Assigned Work Orders"
          value="184"
          subtitle="Active cases in Ward 18 & 24"
          icon={<Wrench className="w-5 h-5 text-primary" />}
          footer={
            <div className="flex items-center justify-between text-on-surface-variant">
              <span>Roads: 184 • Drainage: 96 • Culverts: 62</span>
            </div>
          }
        />

        <KpiCard
          title="Awaiting Crew Dispatch"
          value="48"
          subtitle="Field crew dispatch required < 24h"
          valueColor="text-secondary"
          badge={
            <span className="px-1.5 py-0.5 rounded bg-secondary text-white text-[10px] font-bold">
              Need Crew
            </span>
          }
          icon={<Clock className="w-5 h-5 text-secondary" />}
          footer={
            <div className="flex items-center justify-between text-secondary font-medium">
              <span>12 Critical Field Inspections</span>
            </div>
          }
        />

        <KpiCard
          title="Overdue Complaints"
          value="9"
          subtitle="Exceeded 48h SLA window"
          valueColor="text-error"
          icon={<AlertTriangle className="w-5 h-5 text-error" />}
          footer={
            <div className="flex items-center justify-between text-error font-medium">
              <span>Ward 14: 3 • Ward 22: 4 • Ward 31: 2</span>
            </div>
          }
        />

        <KpiCard
          title="Resolved This Month"
          value="418"
          subtitle="Verified by Grievance Officer"
          icon={<CheckCircle2 className="w-5 h-5 text-primary" />}
          footer={
            <div className="flex items-center justify-between text-on-surface-variant">
              <span>94.8% SLA Rate • 4.4 / 5.0 CSAT</span>
            </div>
          }
        />
      </div>

      {/* Main 2-Column Operational Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left Column: Work Order Ledger */}
        <div className="lg:col-span-8 flex flex-col gap-4">
          <Card
            title="Field Work Orders & Task Orders"
            subtitle="Real-time status of road patching, culvert clearance and structural fixes"
          >
            <div className="divide-y divide-outline-variant/20">
              {complaints.map((c) => (
                <div key={c.id} className="py-3.5 flex flex-col gap-2">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-xs font-bold text-primary">
                        {c.trackingNumber}
                      </span>
                      <PriorityBadge
                        priority={c.effectivePriority}
                        isHumanConfirmed={!!c.humanConfirmation}
                      />
                      <StatusBadge status={c.status} />
                    </div>
                    <span className="text-[11px] text-on-surface-variant flex items-center gap-1">
                      <Clock className="w-3 h-3 text-outline" /> Due in 12h
                    </span>
                  </div>

                  <p className="text-xs font-medium text-on-surface">{c.title}</p>
                  <p className="text-[11px] text-on-surface-variant">{c.locationAddress}</p>

                  <div className="flex items-center justify-between pt-2">
                    <span className="text-[11px] text-secondary font-medium">
                      Assigned to: {c.assignedOfficerName || 'Rapid PWD Unit'}
                    </span>
                    <Button size="sm" variant="outline" icon={<ArrowUpRight className="w-3 h-3" />}>
                      Update Crew Status
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </div>

        {/* Right Column: Crew Deployment Status */}
        <div className="lg:col-span-4 flex flex-col gap-4">
          <Card title="Field Unit Telemetry" subtitle="Active crew status and location">
            <div className="flex flex-col gap-3">
              {[
                { name: 'Unit 4 (Asphalt Paver)', lead: 'Er. Malhotra', status: 'En Route', count: '3 Tasks' },
                { name: 'Unit 2 (Drainage Jetting)', lead: 'S. Sharma', status: 'On Site', count: '2 Tasks' },
                { name: 'Unit 7 (Survey Crew)', lead: 'K. Verma', status: 'Standby', count: '0 Tasks' },
              ].map((u, i) => (
                <div
                  key={i}
                  className="p-3 rounded bg-surface-container-low border border-outline-variant/30 flex items-center justify-between text-xs"
                >
                  <div className="flex flex-col">
                    <span className="font-semibold text-primary">{u.name}</span>
                    <span className="text-[11px] text-on-surface-variant">Lead: {u.lead}</span>
                  </div>
                  <div className="text-right">
                    <span className="px-2 py-0.5 rounded bg-emerald-100 text-emerald-800 text-[10px] font-bold">
                      {u.status}
                    </span>
                    <span className="block text-[10px] text-on-surface-variant mt-1">
                      {u.count}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
};
