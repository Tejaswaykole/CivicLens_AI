import React, { useState } from 'react';
import { KpiCard } from '../ui/KpiCard';
import { Card } from '../ui/Card';
import { PriorityBadge, StatusBadge } from '../ui/Badges';
import { Button } from '../ui/Button';
import { SearchAndFilter } from '../ui/SearchAndFilter';
import { ConfirmationDialog } from '../ui/ConfirmationDialog';
import { MOCK_COMPLAINTS } from '../../mock/data';
import type { Complaint } from '../../types';
import {
  Inbox,
  AlertTriangle,
  CheckCircle2,
  Brain,
  Download,
  Calendar,
  MapPin,
  ShieldCheck,
  Eye,
} from 'lucide-react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  PieChart,
  Pie,
  Cell,
  Legend,
} from 'recharts';

export const SystemAdminDashboard: React.FC = () => {
  const [complaints] = useState<Complaint[]>(MOCK_COMPLAINTS);
  const [search, setSearch] = useState('');
  const [category, setCategory] = useState('ALL');
  const [selectedComplaint, setSelectedComplaint] = useState<Complaint | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);

  // Filter complaints
  const filteredComplaints = complaints.filter((c) => {
    const matchesSearch =
      c.title.toLowerCase().includes(search.toLowerCase()) ||
      c.trackingNumber.toLowerCase().includes(search.toLowerCase()) ||
      c.wardZone.toLowerCase().includes(search.toLowerCase());
    const matchesCategory = category === 'ALL' || c.category === category;
    return matchesSearch && matchesCategory;
  });

  const categories = Array.from(new Set(complaints.map((c) => c.category)));

  // Simulated chart data based on System Overview Stitch design
  const departmentWorkloadData = [
    { name: 'PWD', complaints: 4820, resolved: 4120 },
    { name: 'DJB', complaints: 3910, resolved: 3200 },
    { name: 'MCD', complaints: 3540, resolved: 2950 },
    { name: 'BSES', complaints: 2010, resolved: 1580 },
  ];

  const priorityDistData = [
    { name: 'Critical', value: 942, color: '#ba1a1a' },
    { name: 'High', value: 3120, color: '#78526f' },
    { name: 'Medium', value: 6840, color: '#282B4A' },
    { name: 'Low', value: 3378, color: '#77767e' },
  ];

  return (
    <div className="flex flex-col gap-6">
      {/* Top Advisory Banner */}
      <div className="bg-surface-container p-6 rounded-lg shadow-card flex flex-col lg:flex-row lg:items-center justify-between gap-4 border border-outline-variant/30">
        <div>
          <div className="flex items-center gap-2.5 flex-wrap">
            <h1 className="text-2xl font-bold font-display text-primary">System Overview</h1>
            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded bg-amber-100 text-amber-900 text-xs font-bold uppercase tracking-wider">
              <span className="w-1.5 h-1.5 rounded-full bg-secondary" />
              Simulated Operational Telemetry
            </span>
          </div>
          <p className="text-xs text-on-surface-variant max-w-2xl mt-1 leading-relaxed">
            Monitor public grievances, review AI-assisted prioritization, and oversee system
            accountability across NCT municipal jurisdictions.
          </p>
        </div>

        <div className="flex items-center gap-2 flex-wrap shrink-0">
          <div className="flex items-center bg-surface-lowest px-3 py-1.5 rounded text-xs text-on-surface border border-outline-variant/40 shadow-xs">
            <Calendar className="w-3.5 h-3.5 mr-1.5 text-primary" />
            <span>Oct 1 - Oct 31, 2024</span>
          </div>
          <div className="flex items-center bg-surface-lowest px-3 py-1.5 rounded text-xs text-on-surface border border-outline-variant/40 shadow-xs">
            <MapPin className="w-3.5 h-3.5 mr-1.5 text-secondary" />
            <span>All NCT Zones (12)</span>
          </div>
          <Button size="sm" icon={<Download className="w-3.5 h-3.5" />}>
            Export Ledger
          </Button>
        </div>
      </div>

      {/* Statutory Administrative Advisory Banner */}
      <div className="bg-surface-container-high/60 p-4 rounded-lg flex items-start gap-3 border border-outline-variant/30 text-xs">
        <ShieldCheck className="w-5 h-5 text-secondary shrink-0 mt-0.5" />
        <div className="flex flex-col sm:flex-row sm:items-center justify-between w-full gap-2">
          <p className="text-on-surface-variant leading-relaxed">
            <strong className="font-semibold text-primary">Governance Note:</strong> AI
            recommendations support human decision-making and do not replace authorized review. All
            algorithmic priority outputs require municipal officer concurrence prior to field
            execution.
          </p>
          <span className="text-[10px] text-secondary font-bold uppercase tracking-wider shrink-0 bg-surface-container px-2 py-0.5 rounded">
            SOP v4.1 Compliant
          </span>
        </div>
      </div>

      {/* 4 Compact Operational KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
        <KpiCard
          title="Total Complaints"
          value="14,280"
          subtitle="Monthly municipal ingress"
          icon={<Inbox className="w-5 h-5" />}
          footer={
            <div className="flex items-center justify-between text-on-surface-variant">
              <span className="text-secondary font-semibold">+8.4% vs last month</span>
              <span>PWD: 4.8k • DJB: 3.9k</span>
            </div>
          }
        />

        <KpiCard
          title="Awaiting Human Review"
          value="84"
          subtitle="Confidence < 75% or sensitive class"
          valueColor="text-secondary"
          badge={
            <span className="px-1.5 py-0.5 rounded bg-secondary text-white text-[10px] font-bold">
              HITL QUEUE
            </span>
          }
          icon={<Brain className="w-5 h-5 text-secondary" />}
          footer={
            <div className="flex items-center gap-1 text-on-surface-variant">
              <AlertTriangle className="w-3.5 h-3.5 text-secondary" />
              <span>Mandatory municipal concurrences pending</span>
            </div>
          }
        />

        <KpiCard
          title="Critical & High Hazards"
          value="942"
          subtitle="Direct risk to life or arterial flow"
          valueColor="text-error"
          icon={<AlertTriangle className="w-5 h-5 text-error" />}
          footer={
            <div className="flex items-center justify-between text-on-surface-variant">
              <span className="text-error font-bold">126 Critical Hazards</span>
              <span>816 High Urgent</span>
            </div>
          }
        />

        <KpiCard
          title="Resolved This Month"
          value="11,850"
          subtitle="With citizen closure audit"
          icon={<CheckCircle2 className="w-5 h-5 text-primary" />}
          footer={
            <div className="flex items-center justify-between text-on-surface-variant">
              <span className="text-primary font-bold">83.0% Velocity</span>
              <span className="text-secondary font-bold">96.2% SLA Compliance</span>
            </div>
          }
        />
      </div>

      {/* Analytics Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Chart: Inflow by Department */}
        <Card
          className="lg:col-span-8"
          title="Department Intake & Resolution Breakdown"
          subtitle="Cumulative cases received vs. field closures"
        >
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={departmentWorkloadData}>
                <XAxis dataKey="name" stroke="#77767e" fontSize={11} />
                <YAxis stroke="#77767e" fontSize={11} />
                <Tooltip />
                <Bar dataKey="complaints" name="Total Ingress" fill="#282B4A" radius={[4, 4, 0, 0]} />
                <Bar dataKey="resolved" name="Resolved" fill="#78526f" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>

        {/* Right Chart: Priority Distribution */}
        <Card
          className="lg:col-span-4"
          title="AI Triage Class Distribution"
          subtitle="Classified severity categories across all zones"
        >
          <div className="h-64 w-full flex items-center justify-center">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={priorityDistData}
                  dataKey="value"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  innerRadius={50}
                  outerRadius={75}
                  paddingAngle={3}
                >
                  {priorityDistData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend iconSize={8} wrapperStyle={{ fontSize: 11 }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </Card>
      </div>

      {/* Complaints Ledger Table */}
      <Card
        title="Municipal Grievance Ledger & HITL Triage"
        subtitle="Live inspection records, algorithmic confidence scores, and officer decisions"
        action={
          <SearchAndFilter
            searchQuery={search}
            onSearchChange={setSearch}
            selectedCategory={category}
            onCategoryChange={setCategory}
            categories={categories}
          />
        }
      >
        <div className="overflow-x-auto -mx-5">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="bg-surface-container text-on-surface-variant uppercase tracking-wider text-[10px] font-bold border-y border-outline-variant/30">
                <th className="py-3 px-4">Tracking ID & Title</th>
                <th className="py-3 px-3">Department</th>
                <th className="py-3 px-3">AI Recommendation</th>
                <th className="py-3 px-3">Officer Status</th>
                <th className="py-3 px-3">Status</th>
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-outline-variant/20">
              {filteredComplaints.map((c) => (
                <tr key={c.id} className="hover:bg-surface-low/60 transition-colors">
                  <td className="py-3 px-4 max-w-xs">
                    <span className="font-mono font-semibold text-primary block">
                      {c.trackingNumber}
                    </span>
                    <span className="font-medium text-on-surface truncate block" title={c.title}>
                      {c.title}
                    </span>
                    <span className="text-[11px] text-on-surface-variant block mt-0.5">
                      {c.wardZone}
                    </span>
                  </td>
                  <td className="py-3 px-3">
                    <span className="font-semibold text-primary">{c.departmentName}</span>
                  </td>
                  <td className="py-3 px-3">
                    <div className="flex flex-col gap-1">
                      <PriorityBadge
                        priority={c.aiAssessment.suggestedPriority}
                        isAiSuggested
                      />
                      <span className="text-[10px] text-on-surface-variant">
                        Confidence: {(c.aiAssessment.confidenceScore * 100).toFixed(0)}%
                      </span>
                    </div>
                  </td>
                  <td className="py-3 px-3">
                    {c.humanConfirmation ? (
                      <div className="flex flex-col">
                        <PriorityBadge
                          priority={c.humanConfirmation.confirmedPriority}
                          isHumanConfirmed
                        />
                        <span className="text-[10px] text-on-surface-variant mt-0.5">
                          {c.humanConfirmation.confirmedByOfficerName}
                        </span>
                      </div>
                    ) : (
                      <span className="text-[11px] text-secondary font-medium italic">
                        Pending Officer Review
                      </span>
                    )}
                  </td>
                  <td className="py-3 px-3">
                    <StatusBadge status={c.status} />
                  </td>
                  <td className="py-3 px-4 text-right">
                    <div className="flex items-center justify-end gap-1.5">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => setSelectedComplaint(c)}
                        title="View details"
                      >
                        <Eye className="w-3.5 h-3.5" />
                      </Button>
                      <Button
                        size="sm"
                        variant="primary"
                        onClick={() => {
                          setSelectedComplaint(c);
                          setDialogOpen(true);
                        }}
                      >
                        Triage
                      </Button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      {/* Confirmation Dialog Demo */}
      <ConfirmationDialog
        isOpen={dialogOpen}
        title="Confirm Algorithmic Priority Concurrence"
        description={`Are you sure you want to officially concur with AI-suggested priority for ${selectedComplaint?.trackingNumber}? This action records an immutable audit entry in the municipal ledger.`}
        confirmLabel="Concur & Dispatch"
        onConfirm={() => {
          setDialogOpen(false);
          alert(`Priority concurred for ${selectedComplaint?.trackingNumber}`);
        }}
        onCancel={() => setDialogOpen(false)}
      />
    </div>
  );
};
