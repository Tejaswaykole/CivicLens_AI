import React, { useState } from 'react';
import { Card } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { PriorityBadge } from '../../components/ui/Badges';
import { Sliders, Sparkles, RefreshCw } from 'lucide-react';
import type { ComplaintPriority } from '../../types';

export const OfficerWhatIfSimulatorPage: React.FC = () => {
  const [arterialRoad, setArterialRoad] = useState(true);
  const [monsoonWaterlogging, setMonsoonWaterlogging] = useState(false);
  const [schoolProximity, setSchoolProximity] = useState(true);
  const [nightIlluminationFailure, setNightIlluminationFailure] = useState(false);

  // Compute simulated dynamic score
  let score = 25;
  if (arterialRoad) score += 30;
  if (monsoonWaterlogging) score += 25;
  if (schoolProximity) score += 20;
  if (nightIlluminationFailure) score += 15;

  const getSimulatedPriority = (s: number): ComplaintPriority => {
    if (s >= 75) return 'critical';
    if (s >= 55) return 'high';
    if (s >= 35) return 'medium';
    return 'low';
  };

  const priority = getSimulatedPriority(score);

  return (
    <div className="flex flex-col gap-6 max-w-5xl mx-auto">
      {/* Header Banner */}
      <div className="bg-surface-container p-6 rounded-lg border border-outline-variant/30 shadow-card flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <Sliders className="w-6 h-6 text-primary" />
            <h1 className="text-2xl font-bold font-display text-primary">Illustrative What-If Triage Simulator</h1>
          </div>
          <p className="text-xs text-on-surface-variant max-w-xl mt-1">
            Simulate how environmental parameters and location attributes impact heuristic triage scoring.
          </p>
        </div>

        <span className="px-2.5 py-1 rounded bg-tertiary-fixed text-on-tertiary-fixed text-xs font-bold uppercase tracking-wider">
          Illustrative Simulation Tool
        </span>
      </div>

      {/* Advisory Banner */}
      <div className="bg-surface-container-high/60 p-4 rounded-lg flex items-start gap-3 border border-outline-variant/30 text-xs">
        <Sparkles className="w-5 h-5 text-secondary shrink-0 mt-0.5" />
        <p className="text-on-surface-variant leading-relaxed">
          <strong className="font-semibold text-primary">Statutory Transparency Notice:</strong> This interactive simulator demonstrates rule-weight combinations. Changing inputs here simulates parameter testing for training and does not alter production grievance records.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-12 gap-6">
        {/* Sliders / Toggles */}
        <Card className="md:col-span-7" title="Environmental & Contextual Parameter Toggles">
          <div className="flex flex-col gap-4 text-xs">
            <div className="flex items-center justify-between p-3 rounded bg-surface-container-low border border-outline-variant/20">
              <div>
                <span className="font-semibold text-primary block">Primary Arterial Corridor</span>
                <span className="text-[11px] text-on-surface-variant">Arterial vs residential road (+30 weight)</span>
              </div>
              <input
                type="checkbox"
                checked={arterialRoad}
                onChange={(e) => setArterialRoad(e.target.checked)}
                className="w-4 h-4 accent-primary"
              />
            </div>

            <div className="flex items-center justify-between p-3 rounded bg-surface-container-low border border-outline-variant/20">
              <div>
                <span className="font-semibold text-primary block">Active Monsoon Waterlogging</span>
                <span className="text-[11px] text-on-surface-variant">Submerged road / drain overflow (+25 weight)</span>
              </div>
              <input
                type="checkbox"
                checked={monsoonWaterlogging}
                onChange={(e) => setMonsoonWaterlogging(e.target.checked)}
                className="w-4 h-4 accent-primary"
              />
            </div>

            <div className="flex items-center justify-between p-3 rounded bg-surface-container-low border border-outline-variant/20">
              <div>
                <span className="font-semibold text-primary block">Hospital or School Zone Proximity</span>
                <span className="text-[11px] text-on-surface-variant">Within 200m of pedestrian sensitive zone (+20 weight)</span>
              </div>
              <input
                type="checkbox"
                checked={schoolProximity}
                onChange={(e) => setSchoolProximity(e.target.checked)}
                className="w-4 h-4 accent-primary"
              />
            </div>

            <div className="flex items-center justify-between p-3 rounded bg-surface-container-low border border-outline-variant/20">
              <div>
                <span className="font-semibold text-primary block">Total Night Illumination Failure</span>
                <span className="text-[11px] text-on-surface-variant">Unlit road hazard after sunset (+15 weight)</span>
              </div>
              <input
                type="checkbox"
                checked={nightIlluminationFailure}
                onChange={(e) => setNightIlluminationFailure(e.target.checked)}
                className="w-4 h-4 accent-primary"
              />
            </div>

            <Button
              size="sm"
              variant="outline"
              className="self-start mt-2"
              icon={<RefreshCw className="w-3 h-3" />}
              onClick={() => {
                setArterialRoad(false);
                setMonsoonWaterlogging(false);
                setSchoolProximity(false);
                setNightIlluminationFailure(false);
              }}
            >
              Reset Parameters
            </Button>
          </div>
        </Card>

        {/* Dynamic Simulated Outcome */}
        <Card className="md:col-span-5 flex flex-col justify-between" title="Calculated Triage Severity">
          <div className="flex flex-col gap-4 text-xs">
            <div className="p-4 rounded-lg bg-surface-container flex flex-col items-center justify-center text-center gap-2">
              <span className="text-[10px] uppercase font-bold text-outline">Simulated Outcome</span>
              <PriorityBadge priority={priority} />
              <div className="text-2xl font-bold font-display text-primary mt-1">
                {score} / 100
              </div>
              <span className="text-[11px] text-on-surface-variant">Composite Severity Index</span>
            </div>

            <div className="p-3 rounded bg-surface-container-low border border-outline-variant/20 text-[11px] text-on-surface leading-snug">
              <strong>Evaluation Logic:</strong>{' '}
              {score >= 75
                ? 'High cumulative hazard index mandates Immediate Emergency Field Response (SLA < 12h).'
                : score >= 55
                ? 'Public safety disruption elevated to High Priority (SLA < 24h).'
                : 'Routine triage band assigned according to standard line agency protocols.'}
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
};
