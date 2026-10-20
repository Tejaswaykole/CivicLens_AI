import React, { useState } from 'react';
import { KpiCard } from '../ui/KpiCard';
import { Card } from '../ui/Card';
import { PriorityBadge, StatusBadge } from '../ui/Badges';
import { Button } from '../ui/Button';
import { SearchAndFilter } from '../ui/SearchAndFilter';
import { MOCK_COMPLAINTS } from '../../mock/data';
import type { Complaint, ComplaintPriority } from '../../types';
import {
  Inbox,
  AlertOctagon,
  CheckCircle,
  Clock,
  Sparkles,
  ShieldCheck,
} from 'lucide-react';

export const OfficerConsoleDashboard: React.FC = () => {
  const [complaints, setComplaints] = useState<Complaint[]>(MOCK_COMPLAINTS);
  const [activeTab, setActiveTab] = useState<'all' | 'hitl' | 'hazards'>('hitl');
  const [search, setSearch] = useState('');
  const [category, setCategory] = useState('ALL');

  const filtered = complaints.filter((c) => {
    if (activeTab === 'hitl' && !c.aiAssessment.requiresHITLReview) return false;
    if (activeTab === 'hazards' && c.effectivePriority !== 'critical') return false;
    const matchesSearch =
      c.title.toLowerCase().includes(search.toLowerCase()) ||
      c.trackingNumber.toLowerCase().includes(search.toLowerCase());
    const matchesCategory = category === 'ALL' || c.category === category;
    return matchesSearch && matchesCategory;
  });

  const categories = Array.from(new Set(complaints.map((c) => c.category)));

  const handleConcur = (complaintId: string, priority: ComplaintPriority) => {
    setComplaints((prev) =>
      prev.map((c) => {
        if (c.id === complaintId) {
          return {
            ...c,
            status: 'triaged',
            effectivePriority: priority,
            humanConfirmation: {
              confirmedPriority: priority,
              confirmedByOfficerId: 'usr_go_02',
              confirmedByOfficerName: 'Rajesh Varma',
              confirmedAt: new Date().toISOString(),
              status: 'concurred',
            },
          };
        }
        return c;
      })
    );
  };

  return (
    <div className="flex flex-col gap-6">
      {/* Header Banner */}
      <div className="bg-surface-container p-6 rounded-lg shadow-card flex flex-col sm:flex-row sm:items-center justify-between gap-4 border border-outline-variant/30">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold font-display text-primary">
              Grievance Officer Console
            </h1>
            <span className="px-2 py-0.5 rounded bg-secondary text-white text-[10px] font-bold uppercase tracking-wider">
              Shift Active
            </span>
          </div>
          <p className="text-xs text-on-surface-variant max-w-xl mt-1">
            Human-in-the-Loop triage console. Concur with AI severity ratings, verify jurisdiction,
            and route verified work orders to field departments.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Button
            size="sm"
            variant="outline"
            onClick={() => setActiveTab('hitl')}
            className={activeTab === 'hitl' ? 'bg-secondary text-white border-secondary' : ''}
          >
            HITL Queue ({complaints.filter((c) => c.aiAssessment.requiresHITLReview).length})
          </Button>
          <Button
            size="sm"
            variant="outline"
            onClick={() => setActiveTab('hazards')}
            className={activeTab === 'hazards' ? 'bg-red-700 text-white border-red-700' : ''}
          >
            Critical Hazards ({complaints.filter((c) => c.effectivePriority === 'critical').length})
          </Button>
        </div>
      </div>

      {/* 4 Shift KPI Metrics */}
      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
        <KpiCard
          title="Queue Inflow (Shift)"
          value="3,842"
          subtitle="Grievances logged past 24 hrs"
          icon={<Inbox className="w-5 h-5 text-primary" />}
          footer={
            <div className="flex items-center justify-between text-on-surface-variant">
              <span>Bot: 1,890 • IVR: 1,540 • Portal: 412</span>
            </div>
          }
        />

        <KpiCard
          title="HITL Review Queue"
          value={complaints.filter((c) => c.aiAssessment.requiresHITLReview).length}
          subtitle="Confidence < 75% or sensitive category"
          valueColor="text-secondary"
          badge={
            <span className="px-1.5 py-0.5 rounded bg-secondary text-white text-[10px] font-bold">
              Active Mandate
            </span>
          }
          icon={<Clock className="w-5 h-5 text-secondary" />}
          footer={
            <div className="flex items-center justify-between text-secondary font-medium">
              <span>Mandatory officer verification required</span>
            </div>
          }
        />

        <KpiCard
          title="Critical & High Hazards"
          value="187"
          subtitle="Arterial disruptions & safety risks"
          valueColor="text-error"
          icon={<AlertOctagon className="w-5 h-5 text-error" />}
          footer={
            <div className="flex items-center justify-between text-error font-medium">
              <span>48 Critical • 139 High Urgent</span>
            </div>
          }
        />

        <KpiCard
          title="Verified Resolved (7D)"
          value="1,264"
          subtitle="Digital sign-off with citizen audit"
          icon={<CheckCircle className="w-5 h-5 text-primary" />}
          footer={
            <div className="flex items-center justify-between text-on-surface-variant">
              <span>91.8% CSAT • 94.6% SLA Met</span>
            </div>
          }
        />
      </div>

      {/* HITL Triage Workbench */}
      <Card
        title="Active Triage Dossiers"
        subtitle="Review evidence, inspect model confidence scores, and approve field dispatch"
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
        <div className="flex flex-col gap-4">
          {filtered.map((c) => (
            <div
              key={c.id}
              className="p-4 rounded-lg bg-surface-lowest border border-outline-variant/40 hover:border-outline-variant/80 transition-all flex flex-col lg:flex-row lg:items-center justify-between gap-4"
            >
              <div className="flex flex-col gap-1.5 flex-1">
                <div className="flex items-center gap-2 flex-wrap">
                  <span className="font-mono text-xs font-bold text-primary">
                    {c.trackingNumber}
                  </span>
                  <PriorityBadge
                    priority={c.aiAssessment.suggestedPriority}
                    isAiSuggested
                  />
                  {c.humanConfirmation && (
                    <PriorityBadge
                      priority={c.humanConfirmation.confirmedPriority}
                      isHumanConfirmed
                    />
                  )}
                  <StatusBadge status={c.status} />
                </div>

                <h3 className="text-sm font-bold text-primary">{c.title}</h3>
                <p className="text-xs text-on-surface-variant line-clamp-2">{c.description}</p>

                {/* AI Reasoning cardlet */}
                <div className="mt-2 p-2.5 rounded bg-surface-container/60 border border-outline-variant/20 flex items-start gap-2 text-xs">
                  <Sparkles className="w-4 h-4 text-secondary shrink-0 mt-0.5" />
                  <div className="flex flex-col">
                    <span className="font-semibold text-primary">
                      AI Model Urgency Reasoning (Confidence:{' '}
                      {(c.aiAssessment.confidenceScore * 100).toFixed(0)}%):
                    </span>
                    <span className="text-on-surface-variant text-[11px] mt-0.5">
                      {c.aiAssessment.urgencyReasoning}
                    </span>
                  </div>
                </div>

                <div className="flex items-center gap-3 text-[11px] text-on-surface-variant mt-1">
                  <span>Location: {c.locationAddress}</span>
                  <span>•</span>
                  <span>Dept: {c.departmentName}</span>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex items-center gap-2 shrink-0 self-end lg:self-center">
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => handleConcur(c.id, 'high')}
                >
                  Set High
                </Button>
                <Button
                  size="sm"
                  variant="primary"
                  icon={<ShieldCheck className="w-3.5 h-3.5" />}
                  onClick={() => handleConcur(c.id, c.aiAssessment.suggestedPriority)}
                >
                  Concur & Dispatch
                </Button>
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
};
