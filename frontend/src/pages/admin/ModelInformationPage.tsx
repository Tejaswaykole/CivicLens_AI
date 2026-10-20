import React from 'react';
import { Card } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { Cpu, Layers, CheckCircle, RefreshCw } from 'lucide-react';

export const ModelInformationPage: React.FC = () => {
  const models = [
    {
      name: 'CivicVision-YOLOv8-Ensemble',
      version: 'v2.4.1-pilot',
      type: 'Computer Vision (Object Detection & Severity)',
      accuracy: '94.2% mAP@50',
      inferenceTime: '42ms',
      lastTrained: 'Oct 12, 2024',
      status: 'Active (Production Pipeline)',
      description: 'Detects pothole dimensions, fallen trees, garbage overflow, and low-hanging electrical wires.',
    },
    {
      name: 'CivicNLP-RoBERTa-Urgency',
      version: 'v1.8.0-hi-en',
      type: 'Multilingual Text Classifier (Hindi / Hinglish / English)',
      accuracy: '91.8% F1-Macro',
      inferenceTime: '28ms',
      lastTrained: 'Oct 05, 2024',
      status: 'Active (Production Pipeline)',
      description: 'Analyzes citizen grievance narratives, extracts location landmarks, and scores public hazard indicators.',
    },
    {
      name: 'HITL-Threshold-Policy-Engine',
      version: 'v4.1.0',
      type: 'Deterministic Governance Rules Engine',
      accuracy: '100% Policy Adherence',
      inferenceTime: '< 2ms',
      lastTrained: 'Rule Base Locked',
      status: 'Enforced',
      description: 'Guarantees any prediction with confidence < 75% or hazard tag forces mandatory human officer review.',
    },
  ];

  return (
    <div className="flex flex-col gap-6">
      {/* Header Banner */}
      <div className="bg-surface-container p-6 rounded-lg border border-outline-variant/30 shadow-card flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <Cpu className="w-6 h-6 text-primary" />
            <h1 className="text-2xl font-bold font-display text-primary">Model Governance & Inventory</h1>
          </div>
          <p className="text-xs text-on-surface-variant max-w-xl mt-1">
            Technical specifications, versioning history, latency, and illustrative accuracy benchmarks
            for all active grievance triage models.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <span className="px-2 py-0.5 rounded bg-tertiary-fixed text-on-tertiary-fixed text-[10px] font-bold uppercase tracking-wider">
            Illustrative Benchmark Records
          </span>
          <Button size="sm" variant="outline" icon={<RefreshCw className="w-3.5 h-3.5" />} onClick={() => alert('Simulated model telemetry refreshed.')}>
            Refresh Telemetry
          </Button>
        </div>
      </div>

      {/* Model Cards */}
      <div className="grid grid-cols-1 gap-4">
        {models.map((m, idx) => (
          <Card key={idx} className="flex flex-col gap-3">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-3 border-b border-outline-variant/20 gap-2">
              <div className="flex items-center gap-2.5">
                <div className="w-9 h-9 rounded bg-primary/10 text-primary flex items-center justify-center shrink-0">
                  <Layers className="w-5 h-5" />
                </div>
                <div>
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="text-sm font-bold font-display text-primary">{m.name}</span>
                    <span className="px-1.5 py-0.5 rounded bg-surface-container font-mono text-[10px] font-bold text-secondary">
                      {m.version}
                    </span>
                    <span className="px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 text-[10px] font-semibold flex items-center gap-1">
                      <CheckCircle className="w-3 h-3" /> {m.status}
                    </span>
                  </div>
                  <span className="text-xs text-on-surface-variant mt-0.5 block">{m.type}</span>
                </div>
              </div>

              <div className="text-xs text-on-surface-variant flex items-center gap-3 self-start sm:self-auto">
                <span>Latency: <strong className="text-primary">{m.inferenceTime}</strong></span>
                <span>•</span>
                <span>Updated: <strong>{m.lastTrained}</strong></span>
              </div>
            </div>

            <p className="text-xs text-on-surface leading-relaxed">{m.description}</p>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-3 border-t border-outline-variant/20 bg-surface-container-low/40 -mx-5 -mb-5 px-5 py-3 rounded-b-lg text-xs">
              <div>
                <span className="text-[10px] uppercase font-bold text-outline block">Benchmark Metric</span>
                <span className="font-semibold text-primary">{m.accuracy}</span>
              </div>
              <div>
                <span className="text-[10px] uppercase font-bold text-outline block">Serving Target</span>
                <span className="font-semibold text-primary">NCT Delhi Cluster</span>
              </div>
              <div>
                <span className="text-[10px] uppercase font-bold text-outline block">Model Weight Format</span>
                <span className="font-mono text-[11px] text-on-surface">ONNX / TensorRT</span>
              </div>
              <div>
                <span className="text-[10px] uppercase font-bold text-outline block">Drift Monitor</span>
                <span className="font-semibold text-emerald-700">Healthy (&lt; 1.2% Drift)</span>
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
};
