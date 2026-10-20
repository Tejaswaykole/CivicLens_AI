import React, { useState } from 'react';
import { Card } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { PriorityBadge } from '../../components/ui/Badges';
import { useAppData } from '../../context/useAppData';
import { useRolePreview } from '../../context/useRolePreview';
import { CheckCircle2, AlertTriangle, ShieldCheck, Check } from 'lucide-react';
import type { Complaint } from '../../types';

export const OfficerHITLReviewPage: React.FC = () => {
  const { complaints, concurComplaint, overrideComplaintPriority } = useAppData();
  const { currentUser } = useRolePreview();

  const hitlQueue = complaints.filter((c) => c.aiAssessment.requiresHITLReview);
  const [selectedComplaint, setSelectedComplaint] = useState<Complaint | null>(hitlQueue[0] || null);
  const [reviewReason, setReviewReason] = useState('');

  const handleConcur = (c: Complaint) => {
    concurComplaint(
      c.id,
      currentUser.id,
      currentUser.name,
      'Officer concurred during batch HITL review queue.'
    );
  };

  return (
    <div className="flex flex-col gap-6">
      {/* Header Banner */}
      <div className="bg-surface-container p-6 rounded-lg border border-outline-variant/30 shadow-card flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <ShieldCheck className="w-6 h-6 text-secondary" />
            <h1 className="text-2xl font-bold font-display text-primary">Human-in-the-Loop (HITL) Review Queue</h1>
          </div>
          <p className="text-xs text-on-surface-variant max-w-xl mt-1">
            Mandatory review queue for complaints with model confidence under 75% or flagged with acute public safety hazards.
          </p>
        </div>

        <span className="px-2.5 py-1 rounded bg-secondary text-white text-xs font-bold uppercase tracking-wider">
          {hitlQueue.length} Dossiers Pending
        </span>
      </div>

      {hitlQueue.length === 0 ? (
        <Card className="p-12 text-center flex flex-col items-center">
          <CheckCircle2 className="w-12 h-12 text-emerald-600 mb-2" />
          <h3 className="text-base font-bold text-primary">All Mandated Reviews Completed</h3>
          <p className="text-xs text-on-surface-variant mt-1">
            There are currently no active grievances awaiting Human-in-the-Loop concurrence.
          </p>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-12 gap-6 items-start">
          {/* Left Column: Queue List */}
          <div className="md:col-span-5 flex flex-col gap-3">
            {hitlQueue.map((c) => (
              <div
                key={c.id}
                onClick={() => setSelectedComplaint(c)}
                className={`p-4 rounded-lg border transition-all cursor-pointer flex flex-col gap-2 ${
                  selectedComplaint?.id === c.id
                    ? 'bg-surface-lowest border-secondary shadow-card ring-1 ring-secondary/20'
                    : 'bg-surface-lowest border-outline-variant/30 hover:border-outline-variant/60'
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="font-mono text-xs font-bold text-primary">{c.trackingNumber}</span>
                  <PriorityBadge priority={c.aiAssessment.suggestedPriority} isAiSuggested />
                </div>
                <h4 className="text-xs font-semibold text-on-surface line-clamp-1">{c.title}</h4>
                <div className="flex items-center justify-between text-[11px] text-on-surface-variant">
                  <span>Confidence: {(c.aiAssessment.confidenceScore * 100).toFixed(0)}%</span>
                  <span className="text-secondary font-medium">Needs Concurrence</span>
                </div>
              </div>
            ))}
          </div>

          {/* Right Column: Review Workbench */}
          {selectedComplaint && (
            <Card
              className="md:col-span-7 flex flex-col gap-4"
              title={`Review Dossier: ${selectedComplaint.trackingNumber}`}
              subtitle={selectedComplaint.locationAddress}
            >
              <div className="flex flex-col gap-3 text-xs">
                <div className="p-3 rounded bg-surface-container-low border border-outline-variant/30 flex flex-col gap-1">
                  <span className="font-semibold text-primary">Description</span>
                  <p className="text-on-surface-variant leading-relaxed">{selectedComplaint.description}</p>
                </div>

                <div className="p-3 rounded bg-amber-50 border border-amber-200 text-amber-950 flex flex-col gap-1">
                  <span className="font-semibold text-amber-900 flex items-center gap-1">
                    <AlertTriangle className="w-3.5 h-3.5" /> Mandated Review Trigger:
                  </span>
                  <p className="text-[11px] leading-relaxed">
                    Confidence {(selectedComplaint.aiAssessment.confidenceScore * 100).toFixed(0)}% is below 75% SOP threshold. {selectedComplaint.aiAssessment.urgencyReasoning}
                  </p>
                </div>

                <div>
                  <label className="block font-semibold text-primary mb-1">Officer Justification / Notes</label>
                  <textarea
                    rows={3}
                    value={reviewReason}
                    onChange={(e) => setReviewReason(e.target.value)}
                    placeholder="Enter concurrence notes or override justification..."
                    className="w-full px-3 py-2 rounded border border-outline-variant/60 bg-surface-lowest text-xs"
                  />
                </div>

                <div className="flex items-center justify-end gap-2 pt-3 border-t border-outline-variant/20">
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => {
                      if (!reviewReason) {
                        alert('Please enter a review reason to override.');
                        return;
                      }
                      overrideComplaintPriority(
                        selectedComplaint.id,
                        'high',
                        currentUser.id,
                        currentUser.name,
                        reviewReason
                      );
                      setReviewReason('');
                    }}
                  >
                    Override to High
                  </Button>
                  <Button
                    size="sm"
                    variant="primary"
                    icon={<Check className="w-3.5 h-3.5" />}
                    onClick={() => {
                      handleConcur(selectedComplaint);
                      setReviewReason('');
                    }}
                  >
                    Concur Priority & Dispatch
                  </Button>
                </div>
              </div>
            </Card>
          )}
        </div>
      )}
    </div>
  );
};
