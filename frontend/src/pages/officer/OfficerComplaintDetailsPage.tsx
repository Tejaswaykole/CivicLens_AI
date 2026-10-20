import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { PriorityBadge, StatusBadge } from '../../components/ui/Badges';
import { useAppData } from '../../context/useAppData';
import { useRolePreview } from '../../context/useRolePreview';
import { formatDateTime } from '../../utils';
import type { ComplaintPriority } from '../../types';
import {
  ArrowLeft,
  Sparkles,
  MapPin,
  Calendar,
  Clock,
  User,
  CheckCircle2,
  AlertTriangle,
} from 'lucide-react';

export const OfficerComplaintDetailsPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { complaints, concurComplaint, overrideComplaintPriority } = useAppData();
  const { currentUser } = useRolePreview();

  const complaint = complaints.find((c) => c.id === id);

  // Triage state
  const [selectedOverridePriority, setSelectedOverridePriority] = useState<ComplaintPriority>('high');
  const [reviewReason, setReviewReason] = useState('');
  const [isOverrideModalOpen, setIsOverrideModalOpen] = useState(false);
  const [isConcurModalOpen, setIsConcurModalOpen] = useState(false);

  if (!complaint) {
    return (
      <div className="p-8 text-center">
        <h2 className="text-lg font-bold text-primary">Complaint record not found</h2>
        <Button size="sm" variant="outline" className="mt-4" onClick={() => navigate(-1)}>
          Go Back
        </Button>
      </div>
    );
  }

  const handleConcur = () => {
    concurComplaint(
      complaint.id,
      currentUser.id,
      currentUser.name,
      reviewReason || 'Concurred with AI model priority triage assessment.'
    );
    setIsConcurModalOpen(false);
    setReviewReason('');
  };

  const handleOverride = () => {
    if (!reviewReason) {
      alert('Statutory mandate requires an officer review reason when overriding AI priority.');
      return;
    }
    overrideComplaintPriority(
      complaint.id,
      selectedOverridePriority,
      currentUser.id,
      currentUser.name,
      reviewReason
    );
    setIsOverrideModalOpen(false);
    setReviewReason('');
  };

  return (
    <div className="flex flex-col gap-6 max-w-5xl mx-auto">
      {/* Top Navigation & Status Banner */}
      <div className="flex items-center justify-between">
        <Button
          size="sm"
          variant="outline"
          icon={<ArrowLeft className="w-4 h-4" />}
          onClick={() => navigate(-1)}
        >
          Back to Inbox
        </Button>

        <div className="flex items-center gap-2">
          <span className="text-xs text-on-surface-variant">Dossier ID:</span>
          <span className="font-mono font-bold text-xs bg-surface-container px-2 py-1 rounded text-primary">
            {complaint.trackingNumber}
          </span>
          <StatusBadge status={complaint.status} />
        </div>
      </div>

      {/* Main Dossier Header */}
      <div className="bg-surface-container p-6 rounded-lg border border-outline-variant/30 shadow-card flex flex-col gap-3">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <h1 className="text-xl font-bold font-display text-primary">{complaint.title}</h1>
          <div className="flex items-center gap-2 shrink-0">
            <span className="text-xs text-on-surface-variant">Effective Priority:</span>
            <PriorityBadge priority={complaint.effectivePriority} />
          </div>
        </div>
        <p className="text-xs text-on-surface leading-relaxed">{complaint.description}</p>

        <div className="flex items-center gap-4 text-xs text-on-surface-variant flex-wrap pt-2 border-t border-outline-variant/20">
          <span className="flex items-center gap-1">
            <MapPin className="w-3.5 h-3.5 text-secondary" /> {complaint.locationAddress} ({complaint.wardZone})
          </span>
          <span>•</span>
          <span className="flex items-center gap-1">
            <Calendar className="w-3.5 h-3.5 text-outline" /> Logged: {formatDateTime(complaint.createdAt)}
          </span>
          <span>•</span>
          <span className="flex items-center gap-1">
            <User className="w-3.5 h-3.5 text-outline" /> Citizen: {complaint.citizenName} ({complaint.citizenContactMasked})
          </span>
        </div>
      </div>

      {/* 2-Column AI vs Human Priority Card */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Left: AI Assessment */}
        <Card
          title="AI-Suggested Priority Evaluation"
          subtitle="Model prediction & automated computer vision heuristics"
          className="border-primary/20"
        >
          <div className="flex flex-col gap-3 text-xs">
            <div className="flex items-center justify-between p-3 rounded bg-surface-container-low border border-outline-variant/30">
              <div>
                <span className="text-[10px] uppercase font-bold text-outline block">
                  Algorithm Suggested Priority
                </span>
                <div className="mt-1">
                  <PriorityBadge priority={complaint.aiAssessment.suggestedPriority} isAiSuggested />
                </div>
              </div>
              <div className="text-right">
                <span className="text-[10px] uppercase font-bold text-outline block">Confidence</span>
                <span className="font-bold text-primary text-sm">
                  {(complaint.aiAssessment.confidenceScore * 100).toFixed(0)}%
                </span>
              </div>
            </div>

            <div className="p-3 rounded bg-surface-container-low border border-outline-variant/30 flex flex-col gap-1.5">
              <span className="font-semibold text-secondary flex items-center gap-1">
                <Sparkles className="w-3.5 h-3.5" /> Urgency Explanation:
              </span>
              <p className="text-on-surface-variant leading-relaxed text-[11px]">
                {complaint.aiAssessment.urgencyReasoning}
              </p>
            </div>

            {complaint.aiAssessment.requiresHITLReview && (
              <div className="p-3 rounded bg-amber-50 border border-amber-200 text-amber-900 flex items-start gap-2">
                <AlertTriangle className="w-4 h-4 text-amber-700 shrink-0 mt-0.5" />
                <div className="flex flex-col">
                  <strong className="font-semibold text-[11px]">HITL Review Mandated:</strong>
                  <span className="text-[10px] mt-0.5">
                    Triggered because confidence is below 75% or sensitive civic class is present.
                  </span>
                </div>
              </div>
            )}
          </div>
        </Card>

        {/* Right: Human Confirmation Workbench */}
        <Card
          title="Human-Confirmed Priority & Concurrence"
          subtitle="Official municipal officer review status"
          className="border-secondary/20"
        >
          <div className="flex flex-col gap-3 text-xs">
            {complaint.humanConfirmation ? (
              <div className="p-4 rounded bg-emerald-50 border border-emerald-200 text-emerald-950 flex flex-col gap-2">
                <div className="flex items-center justify-between">
                  <span className="font-bold uppercase tracking-wider text-[10px] text-emerald-800">
                    Decision Concurred / Overridden
                  </span>
                  <PriorityBadge
                    priority={complaint.humanConfirmation.confirmedPriority}
                    isHumanConfirmed
                  />
                </div>
                <div>
                  <span className="text-on-surface font-semibold block">
                    Reviewed By: {complaint.humanConfirmation.confirmedByOfficerName}
                  </span>
                  <span className="text-[11px] text-on-surface-variant block">
                    Timestamp: {formatDateTime(complaint.humanConfirmation.confirmedAt)}
                  </span>
                </div>
                {complaint.humanConfirmation.officerNotes && (
                  <div className="p-2 rounded bg-white/80 border border-emerald-200 mt-1">
                    <strong className="text-[10px] uppercase text-emerald-900 block font-semibold">
                      Officer Review Notes:
                    </strong>
                    <span className="text-[11px] text-on-surface">
                      {complaint.humanConfirmation.officerNotes}
                    </span>
                  </div>
                )}
              </div>
            ) : (
              <div className="p-4 rounded bg-surface-container border border-outline-variant/30 flex flex-col gap-3">
                <div className="flex items-center gap-2 text-secondary font-semibold">
                  <Clock className="w-4 h-4" />
                  <span>Pending Authorized Human Triage</span>
                </div>
                <p className="text-[11px] text-on-surface-variant leading-relaxed">
                  As the active Grievance Officer, review the algorithmic reasoning above and either
                  concur with the suggested priority or override with an operational justification.
                </p>

                <div className="flex items-center gap-2 pt-2 border-t border-outline-variant/20">
                  <Button
                    size="sm"
                    variant="primary"
                    icon={<CheckCircle2 className="w-3.5 h-3.5" />}
                    onClick={() => setIsConcurModalOpen(true)}
                  >
                    Concur Priority
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    icon={<AlertTriangle className="w-3.5 h-3.5" />}
                    onClick={() => setIsOverrideModalOpen(true)}
                  >
                    Override Priority
                  </Button>
                </div>
              </div>
            )}
          </div>
        </Card>
      </div>

      {/* Status History Audit Trail */}
      <Card
        title="Dossier Status History & Lifecycle Audit"
        subtitle="Chronological record of status transitions and officer actions"
      >
        <div className="relative pl-6 border-l-2 border-outline-variant/40 space-y-4 my-2 text-xs">
          {complaint.statusHistory.map((h) => (
            <div key={h.id} className="relative group">
              <div className="absolute -left-[31px] top-1 w-3.5 h-3.5 rounded-full bg-secondary border-2 border-surface-lowest" />
              <div className="flex items-center justify-between">
                <span className="font-semibold text-primary">{h.title}</span>
                <span className="text-[10px] text-on-surface-variant font-mono">
                  {formatDateTime(h.timestamp)}
                </span>
              </div>
              <p className="text-[11px] text-on-surface-variant mt-0.5">{h.note}</p>
              <span className="text-[10px] text-secondary font-medium block mt-1">
                Action by: {h.actor}
              </span>
            </div>
          ))}
        </div>
      </Card>

      {/* Concur Modal */}
      {isConcurModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-primary/40 backdrop-blur-sm">
          <div className="bg-surface-lowest w-full max-w-md rounded-lg shadow-floating border border-outline-variant/40 p-6 flex flex-col gap-4 text-xs">
            <h3 className="text-base font-bold font-display text-primary">
              Concur with AI Priority ({complaint.aiAssessment.suggestedPriority.toUpperCase()})
            </h3>
            <p className="text-on-surface-variant">
              Confirm that you agree with the model priority triage assessment and authorize department dispatch.
            </p>
            <div>
              <label className="block font-semibold text-primary mb-1">Officer Notes (Optional)</label>
              <textarea
                rows={3}
                value={reviewReason}
                onChange={(e) => setReviewReason(e.target.value)}
                placeholder="Concurred based on verified street hazard evidence..."
                className="w-full px-3 py-2 rounded border border-outline-variant/60 bg-surface-lowest"
              />
            </div>
            <div className="flex items-center justify-end gap-2 pt-2 border-t border-outline-variant/20">
              <Button size="sm" variant="outline" onClick={() => setIsConcurModalOpen(false)}>
                Cancel
              </Button>
              <Button size="sm" variant="primary" onClick={handleConcur}>
                Record Concurrence
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* Override Modal */}
      {isOverrideModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-primary/40 backdrop-blur-sm">
          <div className="bg-surface-lowest w-full max-w-md rounded-lg shadow-floating border border-outline-variant/40 p-6 flex flex-col gap-4 text-xs">
            <h3 className="text-base font-bold font-display text-primary">
              Override Algorithmic Priority
            </h3>
            <p className="text-on-surface-variant">
              Statutory mandate requires an official review reason when overriding AI triage output.
            </p>
            <div>
              <label className="block font-semibold text-primary mb-1">New Mandated Priority</label>
              <select
                value={selectedOverridePriority}
                onChange={(e) => setSelectedOverridePriority(e.target.value as ComplaintPriority)}
                className="w-full px-3 py-2 rounded border border-outline-variant/60 bg-surface-lowest"
              >
                <option value="critical">Critical (Immediate Danger)</option>
                <option value="high">High (Urgent Public Disruption)</option>
                <option value="medium">Medium (Standard Triage)</option>
                <option value="low">Low (Routine Maintenance)</option>
              </select>
            </div>
            <div>
              <label className="block font-semibold text-primary mb-1">
                Officer Review Reason <span className="text-error">*</span>
              </label>
              <textarea
                rows={3}
                required
                value={reviewReason}
                onChange={(e) => setReviewReason(e.target.value)}
                placeholder="Explain why the algorithmic score was adjusted..."
                className="w-full px-3 py-2 rounded border border-outline-variant/60 bg-surface-lowest"
              />
            </div>
            <div className="flex items-center justify-end gap-2 pt-2 border-t border-outline-variant/20">
              <Button size="sm" variant="outline" onClick={() => setIsOverrideModalOpen(false)}>
                Cancel
              </Button>
              <Button size="sm" variant="danger" onClick={handleOverride}>
                Submit Override
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
