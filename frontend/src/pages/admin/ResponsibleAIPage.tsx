import React from 'react';
import { Card } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { KpiCard } from '../../components/ui/KpiCard';
import { Shield, Scale, Eye, FileCheck, CheckCircle2, RefreshCw } from 'lucide-react';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Legend } from 'recharts';

export const ResponsibleAIPage: React.FC = () => {

  // Simulated demographic parity data across Delhi municipal zones
  const demographicParityData = [
    { zone: 'Zone 1 (Central)', maleApproval: 96.2, femaleApproval: 95.8, lowIncomeTriage: 97.1 },
    { zone: 'Zone 2 (West)', maleApproval: 94.8, femaleApproval: 95.1, lowIncomeTriage: 95.9 },
    { zone: 'Zone 3 (North)', maleApproval: 93.5, femaleApproval: 94.0, lowIncomeTriage: 94.4 },
    { zone: 'Zone 4 (South)', maleApproval: 97.0, femaleApproval: 96.8, lowIncomeTriage: 96.2 },
    { zone: 'Zone 5 (East)', maleApproval: 95.4, femaleApproval: 95.6, lowIncomeTriage: 96.0 },
  ];

  return (
    <div className="flex flex-col gap-6">
      {/* Header Banner */}
      <div className="bg-surface-container p-6 rounded-lg border border-outline-variant/30 shadow-card flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <Scale className="w-6 h-6 text-primary" />
            <h1 className="text-2xl font-bold font-display text-primary">Responsible AI & Ethics Compliance</h1>
          </div>
          <p className="text-xs text-on-surface-variant max-w-xl mt-1">
            Algorithmic fairness audits, demographic parity metrics, and explainability governance conforming to statutory guidelines.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <span className="px-2 py-0.5 rounded bg-tertiary-fixed text-on-tertiary-fixed text-[10px] font-bold uppercase tracking-wider">
            Illustrative Audit Metrics
          </span>
          <Button size="sm" variant="outline" icon={<RefreshCw className="w-3.5 h-3.5" />} onClick={() => alert('Simulated fairness re-calibration completed.')}>
            Re-run Bias Audit
          </Button>
        </div>
      </div>

      {/* 4 Ethical Compliance Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
        <KpiCard
          title="Demographic Parity Score"
          value="98.4%"
          subtitle="Equitable triage velocity across all socio-economic wards"
          icon={<Scale className="w-5 h-5 text-emerald-700" />}
          footer={
            <div className="flex items-center gap-1 text-emerald-800 font-semibold text-[11px]">
              <CheckCircle2 className="w-3.5 h-3.5" /> High Equity Band (&gt; 95%)
            </div>
          }
        />

        <KpiCard
          title="HITL Safeguard Rate"
          value="100%"
          subtitle="All algorithmic outputs require officer sign-off before field dispatch"
          icon={<Shield className="w-5 h-5 text-secondary" />}
          footer={
            <div className="text-secondary font-semibold text-[11px]">
              Zero Autonomous Field Executions
            </div>
          }
        />

        <KpiCard
          title="Explainability Fidelity"
          value="94.6%"
          subtitle="Feature attribution stability on civic vision & text NLP"
          icon={<Eye className="w-5 h-5 text-primary" />}
          footer={
            <div className="text-on-surface-variant text-[11px]">
              SHAP / LIME surrogate congruence
            </div>
          }
        />

        <KpiCard
          title="Statutory SOP Alignment"
          value="v4.1"
          subtitle="Adherence to National Data Governance Framework"
          icon={<FileCheck className="w-5 h-5 text-primary" />}
          footer={
            <div className="text-emerald-700 font-semibold text-[11px]">
              Certified for Municipal Pilot
            </div>
          }
        />
      </div>

      {/* Demographic & Zonal Fairness Chart */}
      <Card
        title="Zonal Equity & Intake Parity (Simulated Evaluation)"
        subtitle="Verification that grievance severity assessment does not skew across socio-demographic jurisdictions"
        action={
          <div className="flex items-center gap-1.5 text-xs">
            <span className="text-on-surface-variant font-medium">Metric:</span>
            <span className="px-2 py-0.5 rounded bg-surface-container font-semibold text-primary">
              Statistical Parity Ratio
            </span>
          </div>
        }
      >
        <div className="h-72 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={demographicParityData}>
              <XAxis dataKey="zone" stroke="#77767e" fontSize={11} />
              <YAxis domain={[90, 100]} stroke="#77767e" fontSize={11} />
              <Tooltip />
              <Legend wrapperStyle={{ fontSize: 11 }} />
              <Bar dataKey="maleApproval" name="Standard Grievance SLA %" fill="#282B4A" radius={[3, 3, 0, 0]} />
              <Bar dataKey="femaleApproval" name="Women Safety Priority %" fill="#78526f" radius={[3, 3, 0, 0]} />
              <Bar dataKey="lowIncomeTriage" name="Under-served Wards Equity %" fill="#381932" radius={[3, 3, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </Card>
    </div>
  );
};
