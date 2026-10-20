import React, { useState } from 'react';
import { Card } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { PriorityBadge, StatusBadge } from '../../components/ui/Badges';
import { SearchAndFilter } from '../../components/ui/SearchAndFilter';
import { EmptyState } from '../../components/ui/States';
import { useAppData } from '../../context/useAppData';
import { formatDateTime } from '../../utils';
import { Wrench, Clock, ArrowUpRight } from 'lucide-react';
import type { ComplaintStatus } from '../../types';

export const DepartmentWorkOrdersPage: React.FC = () => {
  const { complaints, updateComplaintStatus } = useAppData();
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [selectedComplaintId, setSelectedComplaintId] = useState<string | null>(null);
  const [updateModalStatus, setUpdateModalStatus] = useState<ComplaintStatus>('in_progress');
  const [resolutionNote, setResolutionNote] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);

  // Filter department work orders (default to PWD)
  const deptComplaints = complaints.filter(
    (c) => c.departmentId === 'dept_pwd' || c.departmentName.includes('PWD')
  );

  const filtered = deptComplaints.filter((c) => {
    const matchesSearch =
      c.title.toLowerCase().includes(search.toLowerCase()) ||
      c.trackingNumber.toLowerCase().includes(search.toLowerCase()) ||
      c.locationAddress.toLowerCase().includes(search.toLowerCase());
    const matchesStatus = statusFilter === 'ALL' || c.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const categories = Array.from(new Set(deptComplaints.map((c) => c.category)));

  const handleOpenStatusModal = (complaintId: string) => {
    setSelectedComplaintId(complaintId);
    setResolutionNote('');
    setIsModalOpen(true);
  };

  const handleSaveStatus = (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedComplaintId) return;

    updateComplaintStatus(
      selectedComplaintId,
      updateModalStatus,
      'Er. Vikram Malhotra (PWD)',
      resolutionNote || `Field crew updated status to ${updateModalStatus.replace('_', ' ')}.`
    );

    setIsModalOpen(false);
  };

  return (
    <div className="flex flex-col gap-6">
      {/* Header Banner */}
      <div className="bg-surface-container p-6 rounded-lg border border-outline-variant/30 shadow-card flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <Wrench className="w-6 h-6 text-primary" />
            <h1 className="text-2xl font-bold font-display text-primary">Department Work Orders</h1>
          </div>
          <p className="text-xs text-on-surface-variant max-w-xl mt-1">
            Track assigned field cases, deploy crew units, and update on-site resolution evidence.
          </p>
        </div>

        <span className="px-2.5 py-1 rounded bg-midnight-indigo text-white text-xs font-bold uppercase tracking-wider">
          PWD Zone 4
        </span>
      </div>

      {/* Filter Card */}
      <Card>
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <SearchAndFilter
            searchQuery={search}
            onSearchChange={setSearch}
            selectedCategory="ALL"
            onCategoryChange={() => {}}
            categories={categories}
            placeholder="Search work orders, road landmarks, or tokens..."
          />

          <div className="flex items-center gap-1.5 shrink-0 text-xs">
            <span className="font-semibold text-outline text-[11px] uppercase">Status:</span>
            {['ALL', 'assigned', 'in_progress', 'resolved'].map((s) => (
              <button
                key={s}
                onClick={() => setStatusFilter(s)}
                className={`px-2.5 py-1 rounded text-xs transition-colors ${
                  statusFilter === s
                    ? 'bg-primary text-white font-semibold'
                    : 'bg-surface-container-low text-on-surface hover:bg-surface-container'
                }`}
              >
                {s.replace('_', ' ')}
              </button>
            ))}
          </div>
        </div>
      </Card>

      {/* Work Orders List */}
      <Card
        title="Field Task Orders & Dispatches"
        subtitle={`Showing ${filtered.length} work orders in local session`}
      >
        {filtered.length === 0 ? (
          <EmptyState
            title="No work orders matching query"
            description="Clear the active status filter or search parameters."
          />
        ) : (
          <div className="divide-y divide-outline-variant/20">
            {filtered.map((c) => (
              <div key={c.id} className="py-4 flex flex-col gap-2">
                <div className="flex items-center justify-between flex-wrap gap-2">
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-xs font-bold text-primary">{c.trackingNumber}</span>
                    <PriorityBadge priority={c.effectivePriority} />
                    <StatusBadge status={c.status} />
                  </div>
                  <span className="text-xs text-on-surface-variant flex items-center gap-1">
                    <Clock className="w-3.5 h-3.5 text-outline" /> Logged: {formatDateTime(c.createdAt)}
                  </span>
                </div>

                <h3 className="text-sm font-semibold text-primary">{c.title}</h3>
                <p className="text-xs text-on-surface-variant">{c.description}</p>

                <div className="flex items-center justify-between pt-2 text-xs flex-wrap gap-2">
                  <div className="flex items-center gap-3 text-on-surface-variant text-[11px]">
                    <span>Location: <strong className="text-on-surface">{c.locationAddress}</strong></span>
                    <span>•</span>
                    <span>Assigned Unit: <strong className="text-secondary">{c.assignedCrewUnit || 'Unit 4 (Asphalt Paver)'}</strong></span>
                  </div>

                  <Button
                    size="sm"
                    variant="outline"
                    icon={<ArrowUpRight className="w-3 h-3" />}
                    onClick={() => handleOpenStatusModal(c.id)}
                  >
                    Update Progress / Close
                  </Button>
                </div>
              </div>
            ))}
          </div>
        )}
      </Card>

      {/* Update Status Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-primary/40 backdrop-blur-sm">
          <div className="bg-surface-lowest w-full max-w-md rounded-lg shadow-floating border border-outline-variant/40 p-6 flex flex-col gap-4 text-xs">
            <h3 className="text-base font-bold font-display text-primary">
              Update Work Order Progress
            </h3>

            <form onSubmit={handleSaveStatus} className="flex flex-col gap-3">
              <div>
                <label className="block font-semibold text-primary mb-1">New Operational Status</label>
                <select
                  value={updateModalStatus}
                  onChange={(e) => setUpdateModalStatus(e.target.value as ComplaintStatus)}
                  className="w-full px-3 py-2 rounded border border-outline-variant/60 bg-surface-lowest"
                >
                  <option value="in_progress">Field Crew Dispatched / In Progress</option>
                  <option value="resolved">Verified & Resolved (Closure Proof)</option>
                  <option value="assigned">Assigned / Awaiting Crew</option>
                </select>
              </div>

              <div>
                <label className="block font-semibold text-primary mb-1">Field Engineer Action Notes</label>
                <textarea
                  rows={3}
                  required
                  value={resolutionNote}
                  onChange={(e) => setResolutionNote(e.target.value)}
                  placeholder="Detail asphalt volume laid, culvert clearance completed, or test verification..."
                  className="w-full px-3 py-2 rounded border border-outline-variant/60 bg-surface-lowest"
                />
              </div>

              <div className="flex items-center justify-end gap-2 pt-2 border-t border-outline-variant/20">
                <Button size="sm" variant="outline" type="button" onClick={() => setIsModalOpen(false)}>
                  Cancel
                </Button>
                <Button size="sm" variant="primary" type="submit">
                  Record Status Update
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
