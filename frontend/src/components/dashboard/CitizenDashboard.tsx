import React, { useState } from 'react';
import { Card } from '../ui/Card';
import { StatusBadge } from '../ui/Badges';
import { Button } from '../ui/Button';
import { MOCK_COMPLAINTS } from '../../mock/data';
import {
  FileText,
  Clock,
  CheckCircle2,
  AlertCircle,
  PlusCircle,
  MessageSquare,
  Shield,
} from 'lucide-react';

export const CitizenDashboard: React.FC = () => {
  const [complaints] = useState(
    MOCK_COMPLAINTS.filter((c) => c.citizenName === 'Pooja Sharma' || c.id === 'cmp_1001')
  );

  return (
    <div className="flex flex-col gap-6">
      {/* 4 Citizen KPI Summary Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-surface-container p-4 rounded-lg flex flex-col justify-between h-28 border border-outline-variant/30 shadow-card">
          <div className="flex items-center justify-between text-on-surface-variant">
            <span className="text-[11px] font-bold uppercase tracking-wider">Total Submitted</span>
            <FileText className="w-4 h-4 text-primary" />
          </div>
          <div>
            <div className="text-2xl font-bold font-display text-primary leading-none">5</div>
            <div className="text-[11px] text-on-surface-variant mt-1">All-time logged via portal</div>
          </div>
        </div>

        <div className="bg-surface-container p-4 rounded-lg flex flex-col justify-between h-28 border border-outline-variant/30 shadow-card">
          <div className="flex items-center justify-between text-on-surface-variant">
            <span className="text-[11px] font-bold uppercase tracking-wider">Under Review</span>
            <Clock className="w-4 h-4 text-secondary" />
          </div>
          <div>
            <div className="text-2xl font-bold font-display text-secondary leading-none">1</div>
            <div className="text-[11px] text-on-surface-variant mt-1">Assessing jurisdiction</div>
          </div>
        </div>

        <div className="bg-surface-container p-4 rounded-lg flex flex-col justify-between h-28 border border-outline-variant/30 shadow-card">
          <div className="flex items-center justify-between text-on-surface-variant">
            <span className="text-[11px] font-bold uppercase tracking-wider">In Progress</span>
            <AlertCircle className="w-4 h-4 text-primary" />
          </div>
          <div>
            <div className="text-2xl font-bold font-display text-primary leading-none">2</div>
            <div className="text-[11px] text-on-surface-variant mt-1">Field crews dispatched</div>
          </div>
        </div>

        <div className="bg-surface-container p-4 rounded-lg flex flex-col justify-between h-28 border border-outline-variant/30 shadow-card">
          <div className="flex items-center justify-between text-on-surface-variant">
            <span className="text-[11px] font-bold uppercase tracking-wider">Resolved</span>
            <CheckCircle2 className="w-4 h-4 text-secondary" />
          </div>
          <div>
            <div className="text-2xl font-bold font-display text-secondary leading-none">2</div>
            <div className="text-[11px] text-on-surface-variant mt-1">With photo proof & sign-off</div>
          </div>
        </div>
      </div>

      {/* Prominent Citizen Action / CTA Banner */}
      <div className="bg-midnight-indigo text-white p-6 rounded-lg shadow-card flex flex-col lg:flex-row lg:items-center justify-between gap-6 relative overflow-hidden">
        <div className="space-y-1.5 max-w-2xl relative z-10">
          <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-white/10 text-white/90 text-xs font-semibold">
            <Shield className="w-3.5 h-3.5" />
            24/7 Citizen Grievance Redressal
          </div>
          <h2 className="text-xl font-bold font-display text-white tracking-tight">
            Have a civic issue in your neighborhood?
          </h2>
          <p className="text-xs text-white/70 leading-relaxed">
            Report potholes, broken streetlights, overflowing waste dumps, or water contamination in
            less than 2 minutes. Receive real-time SMS & WhatsApp updates directly from municipal
            engineers.
          </p>
        </div>

        <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2.5 shrink-0 relative z-10">
          <Button
            size="md"
            variant="secondary"
            icon={<PlusCircle className="w-4 h-4" />}
            onClick={() => alert('New complaint submission modal (Phase 2 feature)')}
          >
            Submit New Complaint
          </Button>
          <Button
            size="md"
            variant="outline"
            className="bg-white/10 text-white border-white/20 hover:bg-white/20"
            icon={<MessageSquare className="w-4 h-4" />}
            onClick={() => alert('WhatsApp Grievance Assistant')}
          >
            WhatsApp Grievance
          </Button>
        </div>
      </div>

      {/* Main Grievances Ledger & Timeline */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left: My Registered Grievances */}
        <div className="lg:col-span-8 flex flex-col gap-4">
          <Card
            title="My Registered Grievances"
            subtitle="Track progress, engineer dispatches, and estimated time to resolve"
          >
            <div className="divide-y divide-outline-variant/20">
              {complaints.map((c) => (
                <div key={c.id} className="py-4 flex flex-col gap-2">
                  <div className="flex items-center justify-between">
                    <span className="font-mono text-xs font-bold text-primary">
                      {c.trackingNumber}
                    </span>
                    <StatusBadge status={c.status} />
                  </div>

                  <h3 className="text-sm font-bold text-primary">{c.title}</h3>
                  <p className="text-xs text-on-surface-variant">{c.description}</p>

                  <div className="flex items-center justify-between pt-2 text-xs text-on-surface-variant">
                    <span>{c.departmentName}</span>
                    <span className="text-secondary font-medium">
                      Location: {c.locationAddress}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </div>

        {/* Right: Citizen Charter & Help */}
        <div className="lg:col-span-4 flex flex-col gap-4">
          <Card title="Civic Service Level Agreement" subtitle="Guaranteed redressal windows">
            <div className="flex flex-col gap-3 text-xs">
              <div className="p-3 rounded bg-surface-container-low border border-outline-variant/20">
                <span className="font-semibold text-primary block">Hazard / Safety Urgent</span>
                <span className="text-[11px] text-on-surface-variant block mt-0.5">
                  Resolution commitment: Within 12 Hours
                </span>
              </div>
              <div className="p-3 rounded bg-surface-container-low border border-outline-variant/20">
                <span className="font-semibold text-primary block">Potholes & Road Damage</span>
                <span className="text-[11px] text-on-surface-variant block mt-0.5">
                  Resolution commitment: Within 48 Hours
                </span>
              </div>
              <div className="p-3 rounded bg-surface-container-low border border-outline-variant/20">
                <span className="font-semibold text-primary block">Garbage & Sanitation</span>
                <span className="text-[11px] text-on-surface-variant block mt-0.5">
                  Resolution commitment: Within 24 Hours
                </span>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
};
