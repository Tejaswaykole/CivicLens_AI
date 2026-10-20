import React, { useState } from 'react';
import { Card } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { useAppData } from '../../context/useAppData';
import { History, ShieldCheck, Download, Search } from 'lucide-react';
import { formatDateTime } from '../../utils';

export const AuditHistoryPage: React.FC = () => {
  const { auditLogs } = useAppData();
  const [search, setSearch] = useState('');
  const [typeFilter, setTypeFilter] = useState('ALL');

  const filtered = auditLogs.filter((log) => {
    const matchesSearch =
      log.description.toLowerCase().includes(search.toLowerCase()) ||
      log.actorName.toLowerCase().includes(search.toLowerCase()) ||
      log.details.toLowerCase().includes(search.toLowerCase());
    const matchesType = typeFilter === 'ALL' || log.eventType === typeFilter;
    return matchesSearch && matchesType;
  });

  return (
    <div className="flex flex-col gap-6">
      {/* Header Banner */}
      <div className="bg-surface-container p-6 rounded-lg border border-outline-variant/30 shadow-card flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <History className="w-6 h-6 text-primary" />
            <h1 className="text-2xl font-bold font-display text-primary">Statutory Audit Ledger</h1>
          </div>
          <p className="text-xs text-on-surface-variant max-w-xl mt-1">
            Immutable audit record of all Human-in-the-Loop priority overrides, officer concurrences,
            and administrative policy changes.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <span className="px-2 py-0.5 rounded bg-tertiary-fixed text-on-tertiary-fixed text-[10px] font-bold uppercase tracking-wider">
            Simulated Audit Telemetry
          </span>
          <Button size="sm" icon={<Download className="w-3.5 h-3.5" />} onClick={() => alert('Exporting simulated audit ledger (CSV/JSON)')}>
            Export Audit Ledger
          </Button>
        </div>
      </div>

      {/* Advisory Banner */}
      <div className="bg-surface-container-high/60 p-4 rounded-lg flex items-start gap-3 border border-outline-variant/30 text-xs">
        <ShieldCheck className="w-5 h-5 text-secondary shrink-0 mt-0.5" />
        <div>
          <strong className="font-semibold text-primary">Cryptographic Verification:</strong> All entries recorded in this ledger are simulated representation of municipal tamper-evident audit logs conforming to statutory public grievances guidelines.
        </div>
      </div>

      {/* Audit Log Table */}
      <Card
        title="Event Trace & Municipal Records"
        subtitle={`Showing ${filtered.length} entries recorded in current session`}
        action={
          <div className="flex items-center gap-2">
            <div className="relative">
              <Search className="w-3.5 h-3.5 text-outline absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                placeholder="Search audit trail..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="pl-8 pr-3 py-1.5 text-xs rounded border border-outline-variant/60 bg-surface-lowest text-on-surface focus:outline-none focus:border-primary w-52"
              />
            </div>
            <select
              value={typeFilter}
              onChange={(e) => setTypeFilter(e.target.value)}
              className="py-1.5 px-3 text-xs rounded border border-outline-variant/60 bg-surface-lowest text-on-surface focus:outline-none focus:border-primary"
            >
              <option value="ALL">All Event Types</option>
              <option value="CONCURRENCE">Concurrences</option>
              <option value="HITL_OVERRIDE">HITL Overrides</option>
              <option value="STATUS_CHANGE">Status Changes</option>
              <option value="DEPARTMENT_UPDATE">Department Changes</option>
              <option value="SYSTEM_ALERT">System Alerts</option>
            </select>
          </div>
        }
      >
        <div className="overflow-x-auto -mx-5">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="bg-surface-container text-on-surface-variant uppercase tracking-wider text-[10px] font-bold border-y border-outline-variant/30">
                <th className="py-3 px-4">Timestamp</th>
                <th className="py-3 px-3">Event Type</th>
                <th className="py-3 px-3">Description</th>
                <th className="py-3 px-3">Authorized Actor</th>
                <th className="py-3 px-4">Verification Audit</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-outline-variant/20">
              {filtered.map((log) => (
                <tr key={log.id} className="hover:bg-surface-low/50 transition-colors">
                  <td className="py-3 px-4 whitespace-nowrap text-on-surface font-mono text-[11px]">
                    {formatDateTime(log.timestamp)}
                  </td>
                  <td className="py-3 px-3">
                    <span
                      className={`inline-block px-2 py-0.5 rounded text-[9px] font-bold uppercase tracking-wider ${
                        log.eventType === 'HITL_OVERRIDE'
                          ? 'bg-amber-100 text-amber-900 border border-amber-200'
                          : log.eventType === 'CONCURRENCE'
                          ? 'bg-emerald-100 text-emerald-900 border border-emerald-200'
                          : 'bg-primary/10 text-primary border border-primary/20'
                      }`}
                    >
                      {log.eventType.replace('_', ' ')}
                    </span>
                  </td>
                  <td className="py-3 px-3">
                    <span className="font-semibold text-primary block">{log.description}</span>
                    <span className="text-[11px] text-on-surface-variant block mt-0.5">{log.details}</span>
                  </td>
                  <td className="py-3 px-3 whitespace-nowrap">
                    <span className="font-medium text-on-surface block">{log.actorName}</span>
                    <span className="text-[10px] text-on-surface-variant capitalize">{log.actorRole.replace('_', ' ')}</span>
                  </td>
                  <td className="py-3 px-4 whitespace-nowrap">
                    <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-emerald-700">
                      <ShieldCheck className="w-3.5 h-3.5" /> Immutable Hash Verified
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
};
