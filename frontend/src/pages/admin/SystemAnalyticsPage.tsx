import React, { useState } from 'react';
import { Card } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { KpiCard } from '../../components/ui/KpiCard';
import { BarChart3, TrendingUp, Calendar, Download, MapPin } from 'lucide-react';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
} from 'recharts';

export const SystemAnalyticsPage: React.FC = () => {
  const [timeRange, setTimeRange] = useState<'7d' | '30d' | '90d'>('30d');

  // Intake Velocity Data
  const intakeVelocityData = [
    { day: 'Day 1', ingress: 420, resolved: 380 },
    { day: 'Day 5', ingress: 480, resolved: 440 },
    { day: 'Day 10', ingress: 530, resolved: 510 },
    { day: 'Day 15', ingress: 610, resolved: 580 },
    { day: 'Day 20', ingress: 590, resolved: 570 },
    { day: 'Day 25', ingress: 640, resolved: 620 },
    { day: 'Day 30', ingress: 580, resolved: 590 },
  ];

  // SLA Compliance by Zone
  const zonalComplianceData = [
    { zone: 'South Zone', slaMet: 96.4, slaBreached: 3.6 },
    { zone: 'Central Zone', slaMet: 94.8, slaBreached: 5.2 },
    { zone: 'West Zone', slaMet: 92.1, slaBreached: 7.9 },
    { zone: 'North Zone', slaMet: 93.5, slaBreached: 6.5 },
    { zone: 'East Zone', slaMet: 91.2, slaBreached: 8.8 },
  ];

  return (
    <div className="flex flex-col gap-6">
      {/* Header Banner */}
      <div className="bg-surface-container p-6 rounded-lg border border-outline-variant/30 shadow-card flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <BarChart3 className="w-6 h-6 text-primary" />
            <h1 className="text-2xl font-bold font-display text-primary">System Analytics & SLA Telemetry</h1>
          </div>
          <p className="text-xs text-on-surface-variant max-w-xl mt-1">
            Real-time ingress velocity, statutory SLA compliance ratios, and resolution efficiency across all 12 NCT municipal zones.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <div className="flex items-center bg-surface-lowest p-1 rounded border border-outline-variant/40 text-xs">
            <button
              onClick={() => setTimeRange('7d')}
              className={`px-2.5 py-1 rounded transition-colors ${
                timeRange === '7d' ? 'bg-primary text-white font-bold' : 'text-on-surface-variant'
              }`}
            >
              7D
            </button>
            <button
              onClick={() => setTimeRange('30d')}
              className={`px-2.5 py-1 rounded transition-colors ${
                timeRange === '30d' ? 'bg-primary text-white font-bold' : 'text-on-surface-variant'
              }`}
            >
              30D
            </button>
            <button
              onClick={() => setTimeRange('90d')}
              className={`px-2.5 py-1 rounded transition-colors ${
                timeRange === '90d' ? 'bg-primary text-white font-bold' : 'text-on-surface-variant'
              }`}
            >
              90D
            </button>
          </div>

          <Button size="sm" icon={<Download className="w-3.5 h-3.5" />} onClick={() => alert('Exporting SLA analytics report')}>
            Export Report
          </Button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
        <KpiCard
          title="Overall SLA Adherence"
          value="94.6%"
          subtitle="Grievances resolved within statutory hours"
          icon={<TrendingUp className="w-5 h-5 text-emerald-700" />}
          footer={<span className="text-emerald-700 font-bold">+1.8% vs previous month</span>}
        />
        <KpiCard
          title="Avg Turnaround Time"
          value="18.4 hrs"
          subtitle="Down from 26.2 hrs prior to AI triage"
          icon={<Calendar className="w-5 h-5 text-primary" />}
          footer={<span className="text-primary font-bold">Benchmark: 24.0 hrs</span>}
        />
        <KpiCard
          title="Citizen Satisfaction"
          value="4.5 / 5.0"
          subtitle="Based on verified post-resolution audits"
          valueColor="text-secondary"
          icon={<TrendingUp className="w-5 h-5 text-secondary" />}
          footer={<span className="text-secondary font-bold">1,842 Citizen Ratings</span>}
        />
        <KpiCard
          title="Zonal Coverage"
          value="12 Zones"
          subtitle="100% NCT Delhi wards connected"
          icon={<MapPin className="w-5 h-5 text-primary" />}
          footer={<span className="text-on-surface-variant">272 Wards Active</span>}
        />
      </div>

      {/* Intake Velocity Chart */}
      <Card
        title="Ingress vs Resolution Velocity Dynamics"
        subtitle="Daily complaint registration compared against verified field crew closures"
      >
        <div className="h-72 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={intakeVelocityData}>
              <XAxis dataKey="day" stroke="#77767e" fontSize={11} />
              <YAxis stroke="#77767e" fontSize={11} />
              <Tooltip />
              <Legend wrapperStyle={{ fontSize: 11 }} />
              <Area type="monotone" dataKey="ingress" name="Grievance Ingress" stroke="#282B4A" fill="#282B4A" fillOpacity={0.2} />
              <Area type="monotone" dataKey="resolved" name="Field Closures" stroke="#78526f" fill="#78526f" fillOpacity={0.3} />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </Card>

      {/* SLA Compliance by Zone Chart */}
      <Card
        title="Statutory SLA Compliance Ratio by Municipal Zone"
        subtitle="Percentage of grievances resolved within mandated turnaround timeframes"
      >
        <div className="h-64 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={zonalComplianceData}>
              <XAxis dataKey="zone" stroke="#77767e" fontSize={11} />
              <YAxis domain={[80, 100]} stroke="#77767e" fontSize={11} />
              <Tooltip />
              <Legend wrapperStyle={{ fontSize: 11 }} />
              <Bar dataKey="slaMet" name="SLA Met %" fill="#282B4A" radius={[3, 3, 0, 0]} />
              <Bar dataKey="slaBreached" name="Breached SLA %" fill="#ba1a1a" radius={[3, 3, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </Card>
    </div>
  );
};
