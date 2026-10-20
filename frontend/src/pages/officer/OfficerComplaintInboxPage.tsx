import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { PriorityBadge, StatusBadge } from '../../components/ui/Badges';
import { SearchAndFilter } from '../../components/ui/SearchAndFilter';
import { EmptyState } from '../../components/ui/States';
import { useAppData } from '../../context/useAppData';
import { formatDateTime } from '../../utils';
import { Inbox, Eye, ArrowUpDown } from 'lucide-react';
import type { ComplaintPriority } from '../../types';

export const OfficerComplaintInboxPage: React.FC = () => {
  const { complaints } = useAppData();
  const navigate = useNavigate();

  const [search, setSearch] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('ALL');
  const [priorityFilter, setPriorityFilter] = useState<string>('ALL');
  const [statusFilter, setStatusFilter] = useState<string>('ALL');
  const [sortField, setSortField] = useState<'date' | 'priority'>('date');
  const [sortAsc, setSortAsc] = useState(false);

  const categories = Array.from(new Set(complaints.map((c) => c.category)));

  // Filter & Sort Logic
  const filtered = complaints
    .filter((c) => {
      const matchesSearch =
        c.title.toLowerCase().includes(search.toLowerCase()) ||
        c.trackingNumber.toLowerCase().includes(search.toLowerCase()) ||
        c.locationAddress.toLowerCase().includes(search.toLowerCase()) ||
        c.citizenName.toLowerCase().includes(search.toLowerCase());
      const matchesCategory = selectedCategory === 'ALL' || c.category === selectedCategory;
      const matchesPriority = priorityFilter === 'ALL' || c.effectivePriority === priorityFilter;
      const matchesStatus = statusFilter === 'ALL' || c.status === statusFilter;
      return matchesSearch && matchesCategory && matchesPriority && matchesStatus;
    })
    .sort((a, b) => {
      if (sortField === 'date') {
        const d1 = new Date(a.createdAt).getTime();
        const d2 = new Date(b.createdAt).getTime();
        return sortAsc ? d1 - d2 : d2 - d1;
      } else {
        const order: Record<ComplaintPriority, number> = { critical: 4, high: 3, medium: 2, low: 1 };
        const p1 = order[a.effectivePriority] || 0;
        const p2 = order[b.effectivePriority] || 0;
        return sortAsc ? p1 - p2 : p2 - p1;
      }
    });

  return (
    <div className="flex flex-col gap-6">
      {/* Header Banner */}
      <div className="bg-surface-container p-6 rounded-lg border border-outline-variant/30 shadow-card flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <Inbox className="w-6 h-6 text-primary" />
            <h1 className="text-2xl font-bold font-display text-primary">Master Complaint Inbox</h1>
          </div>
          <p className="text-xs text-on-surface-variant max-w-xl mt-1">
            Review live municipal grievances, inspect algorithmic triage confidence, and navigate to
            detailed dossier views for human concurrence or escalation.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Button
            size="sm"
            variant="outline"
            icon={<ArrowUpDown className="w-3.5 h-3.5" />}
            onClick={() => {
              setSortField(sortField === 'date' ? 'priority' : 'date');
              setSortAsc(!sortAsc);
            }}
          >
            Sort: {sortField === 'date' ? 'Date' : 'Severity'} ({sortAsc ? 'Asc' : 'Desc'})
          </Button>
        </div>
      </div>

      {/* Filter Toolbar */}
      <Card>
        <div className="flex flex-col gap-3">
          <SearchAndFilter
            searchQuery={search}
            onSearchChange={setSearch}
            selectedCategory={selectedCategory}
            onCategoryChange={setSelectedCategory}
            categories={categories}
            placeholder="Search tracking ID, citizen, road name, or description..."
            onReset={() => {
              setSearch('');
              setSelectedCategory('ALL');
              setPriorityFilter('ALL');
              setStatusFilter('ALL');
            }}
          />

          <div className="flex items-center gap-2 flex-wrap pt-2 border-t border-outline-variant/20 text-xs">
            <span className="text-[11px] font-bold uppercase text-outline">Priority:</span>
            {['ALL', 'critical', 'high', 'medium', 'low'].map((p) => (
              <button
                key={p}
                onClick={() => setPriorityFilter(p)}
                className={`px-2.5 py-1 rounded capitalize text-xs transition-colors ${
                  priorityFilter === p
                    ? 'bg-primary text-white font-semibold'
                    : 'bg-surface-container-low text-on-surface hover:bg-surface-container'
                }`}
              >
                {p}
              </button>
            ))}

            <span className="text-[11px] font-bold uppercase text-outline ml-3">Status:</span>
            {['ALL', 'submitted', 'in_review', 'triaged', 'assigned', 'in_progress', 'resolved'].map((s) => (
              <button
                key={s}
                onClick={() => setStatusFilter(s)}
                className={`px-2.5 py-1 rounded text-xs transition-colors ${
                  statusFilter === s
                    ? 'bg-secondary text-white font-semibold'
                    : 'bg-surface-container-low text-on-surface hover:bg-surface-container'
                }`}
              >
                {s.replace('_', ' ')}
              </button>
            ))}
          </div>
        </div>
      </Card>

      {/* Inbox List Table */}
      <Card
        title="Grievance Dossiers"
        subtitle={`Displaying ${filtered.length} of ${complaints.length} records`}
      >
        {filtered.length === 0 ? (
          <EmptyState
            title="No complaints matching criteria"
            description="Try modifying search keywords or clearing active priority/status filters."
            actionLabel="Reset All Filters"
            onAction={() => {
              setSearch('');
              setSelectedCategory('ALL');
              setPriorityFilter('ALL');
              setStatusFilter('ALL');
            }}
          />
        ) : (
          <div className="overflow-x-auto -mx-5">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="bg-surface-container text-on-surface-variant uppercase tracking-wider text-[10px] font-bold border-y border-outline-variant/30">
                  <th className="py-3 px-4">Tracking ID & Title</th>
                  <th className="py-3 px-3">Category & Dept</th>
                  <th className="py-3 px-3">AI-Suggested Priority</th>
                  <th className="py-3 px-3">Human-Confirmed Priority</th>
                  <th className="py-3 px-3">Current Status</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-outline-variant/20">
                {filtered.map((c) => (
                  <tr key={c.id} className="hover:bg-surface-low/50 transition-colors">
                    <td className="py-3 px-4 max-w-sm">
                      <div className="flex items-center gap-2">
                        <span className="font-mono font-bold text-primary">{c.trackingNumber}</span>
                        {c.aiAssessment.requiresHITLReview && (
                          <span className="px-1.5 py-0.5 rounded bg-secondary text-white text-[9px] font-bold uppercase">
                            HITL
                          </span>
                        )}
                      </div>
                      <span className="font-semibold text-on-surface truncate block mt-0.5" title={c.title}>
                        {c.title}
                      </span>
                      <span className="text-[11px] text-on-surface-variant block mt-0.5">
                        {c.locationAddress} • {formatDateTime(c.createdAt)}
                      </span>
                    </td>
                    <td className="py-3 px-3">
                      <span className="font-semibold text-primary block">{c.category}</span>
                      <span className="text-[11px] text-on-surface-variant block">{c.departmentName}</span>
                    </td>
                    <td className="py-3 px-3">
                      <PriorityBadge priority={c.aiAssessment.suggestedPriority} isAiSuggested />
                      <span className="text-[10px] text-on-surface-variant block mt-1">
                        Confidence: {(c.aiAssessment.confidenceScore * 100).toFixed(0)}%
                      </span>
                    </td>
                    <td className="py-3 px-3">
                      {c.humanConfirmation ? (
                        <div>
                          <PriorityBadge priority={c.humanConfirmation.confirmedPriority} isHumanConfirmed />
                          <span className="text-[10px] text-on-surface-variant block mt-1">
                            By {c.humanConfirmation.confirmedByOfficerName}
                          </span>
                        </div>
                      ) : (
                        <span className="text-[11px] text-secondary font-medium italic">
                          Awaiting Review
                        </span>
                      )}
                    </td>
                    <td className="py-3 px-3">
                      <StatusBadge status={c.status} />
                    </td>
                    <td className="py-3 px-4 text-right">
                      <Button
                        size="sm"
                        variant="primary"
                        icon={<Eye className="w-3.5 h-3.5" />}
                        onClick={() => navigate(`/app/officer/complaints/${c.id}`)}
                      >
                        Inspect Dossier
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>
    </div>
  );
};
