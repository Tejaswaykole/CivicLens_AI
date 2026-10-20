import React from 'react';
import { Card } from '../components/ui/Card';
import { PriorityBadge } from '../components/ui/Badges';
import { MOCK_COMPLAINTS } from '../mock/data';
import { Sparkles, Brain, CheckCircle, ShieldAlert, Cpu } from 'lucide-react';

export const AIExplainabilityPage: React.FC = () => {
  return (
    <div className="flex flex-col gap-6">
      <div className="bg-surface-container p-6 rounded-lg border border-outline-variant/30 shadow-card">
        <div className="flex items-center gap-2">
          <Brain className="w-6 h-6 text-secondary" />
          <h1 className="text-2xl font-bold font-display text-primary">AI Explainability & Audit</h1>
        </div>
        <p className="text-xs text-on-surface-variant max-w-2xl mt-1">
          Detailed transparency breakdown of computer vision detections, text grievance NLP
          urgency scoring, and Human-in-the-Loop decision governance.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card title="HITL Threshold" subtitle="Policy Rule Engine">
          <div className="flex items-center gap-3">
            <ShieldAlert className="w-8 h-8 text-secondary" />
            <div>
              <span className="text-xl font-bold font-display text-primary">75.0%</span>
              <p className="text-[11px] text-on-surface-variant mt-0.5">
                Model confidence &lt; 75% or sensitive civic class forces mandatory human officer
                sign-off.
              </p>
            </div>
          </div>
        </Card>

        <Card title="Computer Vision" subtitle="Image Triage Engine">
          <div className="flex items-center gap-3">
            <Cpu className="w-8 h-8 text-primary" />
            <div>
              <span className="text-xl font-bold font-display text-primary">94.2%</span>
              <p className="text-[11px] text-on-surface-variant mt-0.5">
                Pothole, arterial obstruction, and electrical hazard classification accuracy.
              </p>
            </div>
          </div>
        </Card>

        <Card title="Human Concurrence" subtitle="Officer Alignment">
          <div className="flex items-center gap-3">
            <CheckCircle className="w-8 h-8 text-emerald-700" />
            <div>
              <span className="text-xl font-bold font-display text-primary">98.1%</span>
              <p className="text-[11px] text-on-surface-variant mt-0.5">
                Municipal officers concur with or escalate AI-suggested priority classifications.
              </p>
            </div>
          </div>
        </Card>
      </div>

      <Card
        title="Recent Algorithmic Classifications & Reasoning Log"
        subtitle="Immutable explainability trace for simulated inference decisions"
      >
        <div className="divide-y divide-outline-variant/20">
          {MOCK_COMPLAINTS.map((c) => (
            <div key={c.id} className="py-4 flex flex-col gap-2">
              <div className="flex items-center justify-between">
                <span className="font-mono text-xs font-bold text-primary">{c.trackingNumber}</span>
                <PriorityBadge priority={c.aiAssessment.suggestedPriority} isAiSuggested />
              </div>

              <h3 className="text-sm font-semibold text-primary">{c.title}</h3>

              <div className="p-3 rounded bg-surface-container-low border border-outline-variant/30 text-xs flex flex-col gap-1">
                <span className="font-semibold text-secondary flex items-center gap-1">
                  <Sparkles className="w-3.5 h-3.5" /> Explainability Rationale:
                </span>
                <p className="text-on-surface-variant text-[11px]">
                  {c.aiAssessment.urgencyReasoning}
                </p>
                <div className="flex items-center gap-2 mt-1">
                  <span className="text-[10px] text-on-surface-variant font-medium">
                    Features detected:
                  </span>
                  {c.aiAssessment.detectedCategories.map((cat, idx) => (
                    <span
                      key={idx}
                      className="px-1.5 py-0.5 rounded bg-surface-lowest border border-outline-variant/30 text-[10px]"
                    >
                      {cat}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
};
