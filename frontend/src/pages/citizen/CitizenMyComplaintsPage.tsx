import React, { useState } from 'react';
import { Card } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { StatusBadge } from '../../components/ui/Badges';
import { useAppData } from '../../context/useAppData';
import { useRolePreview } from '../../context/useRolePreview';
import { formatDateTime } from '../../utils';
import {
  FileText,
  Clock,
  CheckCircle2,
  Star,
  MapPin,
} from 'lucide-react';

export const CitizenMyComplaintsPage: React.FC = () => {
  const { complaints, submitResolutionFeedback } = useAppData();
  const { currentUser } = useRolePreview();

  // Show only this citizen's records or Pooja Sharma's demo records
  const myComplaints = complaints.filter(
    (c) => c.citizenName === currentUser.name || c.citizenName === 'Pooja Sharma'
  );

  const [feedbackComplaintId, setFeedbackComplaintId] = useState<string | null>(null);
  const [rating, setRating] = useState(5);
  const [feedbackComment, setFeedbackComment] = useState('');

  const handleOpenFeedback = (id: string) => {
    setFeedbackComplaintId(id);
    setRating(5);
    setFeedbackComment('');
  };

  const handleSubmitFeedback = (e: React.FormEvent) => {
    e.preventDefault();
    if (!feedbackComplaintId) return;

    submitResolutionFeedback(
      feedbackComplaintId,
      rating,
      feedbackComment || 'Citizen confirmed satisfactory field resolution.'
    );

    setFeedbackComplaintId(null);
  };

  return (
    <div className="flex flex-col gap-6 max-w-4xl mx-auto">
      {/* Header Banner */}
      <div className="bg-surface-container p-6 rounded-lg border border-outline-variant/30 shadow-card flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <FileText className="w-6 h-6 text-primary" />
            <h1 className="text-2xl font-bold font-display text-primary">My Registered Grievances</h1>
          </div>
          <p className="text-xs text-on-surface-variant max-w-xl mt-1">
            Track status, engineer dispatches, and resolution audit proof for complaints lodged under your account.
          </p>
        </div>

        <span className="px-2.5 py-1 rounded bg-secondary text-white text-xs font-bold uppercase tracking-wider">
          {myComplaints.length} Lodged Dockets
        </span>
      </div>

      {/* Complaints Dossiers */}
      <div className="flex flex-col gap-4">
        {myComplaints.map((c) => (
          <Card key={c.id} className="flex flex-col gap-3">
            <div className="flex items-center justify-between pb-3 border-b border-outline-variant/20 flex-wrap gap-2">
              <div className="flex items-center gap-2">
                <span className="font-mono text-xs font-bold text-primary">{c.trackingNumber}</span>
                <StatusBadge status={c.status} />
              </div>
              <span className="text-xs text-on-surface-variant flex items-center gap-1">
                <Clock className="w-3.5 h-3.5 text-outline" /> Submitted: {formatDateTime(c.createdAt)}
              </span>
            </div>

            <h3 className="text-sm font-bold font-display text-primary">{c.title}</h3>
            <p className="text-xs text-on-surface-variant">{c.description}</p>

            <div className="p-3 rounded bg-surface-container-low border border-outline-variant/30 flex flex-col gap-2 text-xs">
              <div className="flex items-center justify-between flex-wrap gap-2 text-on-surface-variant text-[11px]">
                <span className="flex items-center gap-1">
                  <MapPin className="w-3.5 h-3.5 text-secondary" /> {c.locationAddress}
                </span>
                <span>Line Agency: <strong className="text-primary">{c.departmentName}</strong></span>
              </div>

              {/* Progress Timeline snippet */}
              <div className="mt-1 pt-2 border-t border-outline-variant/20 flex flex-col gap-1.5">
                <span className="text-[10px] uppercase font-bold text-outline">Latest Activity</span>
                <div className="flex items-start gap-2">
                  <span className="w-2 h-2 rounded-full bg-secondary mt-1 shrink-0" />
                  <div>
                    <span className="font-semibold text-primary block">
                      {c.statusHistory[c.statusHistory.length - 1]?.title}
                    </span>
                    <span className="text-[11px] text-on-surface-variant">
                      {c.statusHistory[c.statusHistory.length - 1]?.note}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* Resolution Verification & Feedback */}
            {c.status === 'resolved' && (
              <div className="p-3 rounded bg-emerald-50 border border-emerald-200 text-emerald-950 flex flex-col gap-2 text-xs">
                <div className="flex items-center justify-between">
                  <span className="font-semibold flex items-center gap-1 text-emerald-900">
                    <CheckCircle2 className="w-4 h-4 text-emerald-700" /> Resolution Completed
                  </span>

                  {!c.resolutionFeedback && (
                    <Button
                      size="sm"
                      variant="primary"
                      icon={<Star className="w-3 h-3" />}
                      onClick={() => handleOpenFeedback(c.id)}
                    >
                      Rate Resolution
                    </Button>
                  )}
                </div>

                {c.resolutionNotes && (
                  <p className="text-[11px] text-on-surface">
                    <strong>Engineer Closure Note:</strong> {c.resolutionNotes}
                  </p>
                )}

                {c.resolutionFeedback && (
                  <div className="p-2 rounded bg-white/80 border border-emerald-200 flex flex-col gap-1 text-[11px]">
                    <div className="flex items-center gap-1 font-semibold text-emerald-900">
                      <span>Citizen Rating:</span>
                      <div className="flex items-center text-amber-500">
                        {Array.from({ length: c.resolutionFeedback.rating }).map((_, i) => (
                          <Star key={i} className="w-3 h-3 fill-amber-400 text-amber-400" />
                        ))}
                      </div>
                    </div>
                    <span className="text-on-surface italic">
                      "{c.resolutionFeedback.comments}"
                    </span>
                  </div>
                )}
              </div>
            )}
          </Card>
        ))}
      </div>

      {/* Feedback Modal */}
      {feedbackComplaintId && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-primary/40 backdrop-blur-sm">
          <div className="bg-surface-lowest w-full max-w-md rounded-lg shadow-floating border border-outline-variant/40 p-6 flex flex-col gap-4 text-xs">
            <h3 className="text-base font-bold font-display text-primary">
              Citizen Resolution Verification
            </h3>
            <p className="text-on-surface-variant">
              Confirm whether the municipal repair in your neighborhood was completed satisfactorily.
            </p>

            <form onSubmit={handleSubmitFeedback} className="flex flex-col gap-3">
              <div>
                <label className="block font-semibold text-primary mb-1">Satisfaction Rating</label>
                <div className="flex items-center gap-2">
                  {[1, 2, 3, 4, 5].map((s) => (
                    <button
                      type="button"
                      key={s}
                      onClick={() => setRating(s)}
                      className={`p-1.5 rounded transition-colors ${
                        rating >= s ? 'text-amber-500' : 'text-gray-300'
                      }`}
                    >
                      <Star className={`w-6 h-6 ${rating >= s ? 'fill-amber-400' : ''}`} />
                    </button>
                  ))}
                  <span className="font-semibold text-primary ml-2">{rating} / 5 Stars</span>
                </div>
              </div>

              <div>
                <label className="block font-semibold text-primary mb-1">Feedback Comments</label>
                <textarea
                  rows={3}
                  value={feedbackComment}
                  onChange={(e) => setFeedbackComment(e.target.value)}
                  placeholder="Share details on road surface condition, water clarity, or crew response..."
                  className="w-full px-3 py-2 rounded border border-outline-variant/60 bg-surface-lowest"
                />
              </div>

              <div className="flex items-center justify-end gap-2 pt-2 border-t border-outline-variant/20">
                <Button size="sm" variant="outline" type="button" onClick={() => setFeedbackComplaintId(null)}>
                  Cancel
                </Button>
                <Button size="sm" variant="primary" type="submit">
                  Submit Citizen Feedback
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
