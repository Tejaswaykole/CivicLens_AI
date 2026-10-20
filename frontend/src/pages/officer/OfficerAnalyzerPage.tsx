import React, { useState } from 'react';
import { Card } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { PriorityBadge } from '../../components/ui/Badges';
import { Sparkles, Brain } from 'lucide-react';
import type { ComplaintPriority } from '../../types';

export const OfficerAnalyzerPage: React.FC = () => {
  const [inputText, setInputText] = useState(
    'A high-voltage transformer behind Metro station gate 2 is sparking violently near water pipeline.'
  );
  const [selectedCategory, setSelectedCategory] = useState('Electrical Hazard');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<{
    priority: ComplaintPriority;
    confidence: number;
    reasoning: string;
    features: { feature: string; weight: number; positive: boolean }[];
  } | null>({
    priority: 'critical',
    confidence: 0.94,
    reasoning:
      'Co-occurrence of high-voltage sparking in proximity to pedestrian egress and wet infrastructure triggers immediate emergency hazard tier.',
    features: [
      { feature: 'transformer sparking', weight: 0.45, positive: true },
      { feature: 'high-voltage equipment', weight: 0.32, positive: true },
      { feature: 'metro station egress', weight: 0.22, positive: true },
      { feature: 'water pipeline proximity', weight: 0.18, positive: true },
    ],
  });

  const handleSimulateAnalysis = () => {
    setIsAnalyzing(true);
    setTimeout(() => {
      setIsAnalyzing(false);
      const isCritical = inputText.toLowerCase().includes('spark') || inputText.toLowerCase().includes('accident') || inputText.toLowerCase().includes('danger');
      const isHigh = inputText.toLowerCase().includes('water') || inputText.toLowerCase().includes('deep') || inputText.toLowerCase().includes('overflow');

      setAnalysisResult({
        priority: isCritical ? 'critical' : isHigh ? 'high' : 'medium',
        confidence: isCritical ? 0.93 : isHigh ? 0.82 : 0.76,
        reasoning: `Simulated NLP feature extraction detected ${isCritical ? 'active acute danger signals' : isHigh ? 'significant public disruption' : 'standard maintenance need'}.`,
        features: [
          { feature: 'keyword severity correlation', weight: 0.38, positive: true },
          { feature: 'category benchmark weighting', weight: 0.28, positive: true },
          { feature: 'historical ward incident density', weight: 0.16, positive: true },
        ],
      });
    }, 600);
  };

  return (
    <div className="flex flex-col gap-6 max-w-5xl mx-auto">
      {/* Header Banner */}
      <div className="bg-surface-container p-6 rounded-lg border border-outline-variant/30 shadow-card flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <Brain className="w-6 h-6 text-primary" />
            <h1 className="text-2xl font-bold font-display text-primary">Complaint Analyzer & Explainability Sandbox</h1>
          </div>
          <p className="text-xs text-on-surface-variant max-w-xl mt-1">
            Simulate and inspect how civic language and visual features influence algorithmic priority
            triage.
          </p>
        </div>

        <span className="px-2.5 py-1 rounded bg-tertiary-fixed text-on-tertiary-fixed text-xs font-bold uppercase tracking-wider">
          Illustrative Simulation Model
        </span>
      </div>

      {/* Advisory Note */}
      <div className="bg-surface-container-high/60 p-4 rounded-lg flex items-start gap-3 border border-outline-variant/30 text-xs">
        <Sparkles className="w-5 h-5 text-secondary shrink-0 mt-0.5" />
        <p className="text-on-surface-variant leading-relaxed">
          <strong className="font-semibold text-primary">Notice:</strong> This is an illustrative demonstration of explainable AI (XAI) feature attribution. No live machine learning model is executing in production.
        </p>
      </div>

      {/* Input Workbench */}
      <Card title="Simulated Grievance Narrative Input" subtitle="Enter sample text to test feature attribution weights">
        <div className="flex flex-col gap-4 text-xs">
          <div>
            <label className="block font-semibold text-primary mb-1">Grievance Description Text</label>
            <textarea
              rows={3}
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              className="w-full px-3 py-2 rounded border border-outline-variant/60 bg-surface-lowest text-xs"
            />
          </div>

          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div className="flex items-center gap-2">
              <span className="font-semibold text-primary">Civic Category:</span>
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="px-2 py-1.5 rounded border border-outline-variant/60 bg-surface-lowest text-xs"
              >
                <option value="Electrical Hazard">Electrical Hazard</option>
                <option value="Road Infrastructure">Road Infrastructure</option>
                <option value="Water & Sewage">Water & Sewage</option>
                <option value="Sanitation & Solid Waste">Sanitation & Solid Waste</option>
              </select>
            </div>

            <Button
              size="sm"
              variant="primary"
              disabled={isAnalyzing}
              onClick={handleSimulateAnalysis}
              icon={<Sparkles className="w-3.5 h-3.5" />}
            >
              {isAnalyzing ? 'Extracting Heuristics...' : 'Run Simulated Analysis'}
            </Button>
          </div>
        </div>
      </Card>

      {/* Analysis Output */}
      {analysisResult && (
        <div className="grid grid-cols-1 md:grid-cols-12 gap-6">
          <Card className="md:col-span-4" title="Triage Classification">
            <div className="flex flex-col gap-3 text-xs">
              <div className="flex items-center justify-between p-3 rounded bg-surface-container-low border border-outline-variant/20">
                <span className="font-semibold text-on-surface-variant">Predicted Priority</span>
                <PriorityBadge priority={analysisResult.priority} isAiSuggested />
              </div>
              <div className="flex items-center justify-between p-3 rounded bg-surface-container-low border border-outline-variant/20">
                <span className="font-semibold text-on-surface-variant">Simulated Confidence</span>
                <span className="font-bold text-primary text-sm">
                  {(analysisResult.confidence * 100).toFixed(0)}%
                </span>
              </div>
              <div className="p-3 rounded bg-surface-container-low border border-outline-variant/20">
                <span className="font-semibold text-primary block mb-1">Model Reasoning</span>
                <span className="text-[11px] text-on-surface-variant leading-snug">
                  {analysisResult.reasoning}
                </span>
              </div>
            </div>
          </Card>

          <Card
            className="md:col-span-8"
            title="Feature Attribution & Influential Tokens"
            subtitle="Illustrative token impact on model severity output"
          >
            <div className="flex flex-col gap-3 text-xs">
              {analysisResult.features.map((f, i) => (
                <div key={i} className="flex flex-col gap-1">
                  <div className="flex items-center justify-between">
                    <span className="font-semibold text-primary font-mono text-[11px]">{f.feature}</span>
                    <span className="text-secondary font-bold text-[11px]">
                      +{(f.weight * 100).toFixed(0)}% Impact
                    </span>
                  </div>
                  <div className="w-full bg-surface-container h-2 rounded-full overflow-hidden">
                    <div
                      className="bg-secondary h-full rounded-full"
                      style={{ width: `${Math.min(100, f.weight * 150)}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </div>
      )}
    </div>
  );
};
