import React, { useState } from 'react';
import { Card } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { ConfirmationDialog } from '../../components/ui/ConfirmationDialog';
import { useAppData } from '../../context/useAppData';
import type { Department } from '../../types';
import { Building2, Plus, Edit2, Trash2, Clock, CheckCircle2 } from 'lucide-react';

export const DepartmentManagementPage: React.FC = () => {
  const { departments, addDepartment, updateDepartment, deleteDepartment } = useAppData();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingDept, setEditingDept] = useState<Department | null>(null);
  const [deleteCandidate, setDeleteCandidate] = useState<Department | null>(null);

  // Form states
  const [name, setName] = useState('');
  const [code, setCode] = useState('');
  const [description, setDescription] = useState('');
  const [nodalOfficer, setNodalOfficer] = useState('');
  const [contactEmail, setContactEmail] = useState('');
  const [slaHours, setSlaHours] = useState(24);

  const openCreateModal = () => {
    setEditingDept(null);
    setName('');
    setCode('');
    setDescription('');
    setNodalOfficer('');
    setContactEmail('');
    setSlaHours(24);
    setIsModalOpen(true);
  };

  const openEditModal = (dept: Department) => {
    setEditingDept(dept);
    setName(dept.name);
    setCode(dept.code);
    setDescription(dept.description);
    setNodalOfficer(dept.nodalOfficer);
    setContactEmail(dept.contactEmail);
    setSlaHours(dept.slaTargetHours);
    setIsModalOpen(true);
  };

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    if (!name || !code) return;

    if (editingDept) {
      updateDepartment(editingDept.id, {
        name,
        code,
        description,
        nodalOfficer,
        contactEmail,
        slaTargetHours: Number(slaHours),
      });
    } else {
      addDepartment({
        name,
        code,
        description,
        nodalOfficer,
        contactEmail,
        slaTargetHours: Number(slaHours),
      });
    }

    setIsModalOpen(false);
  };

  return (
    <div className="flex flex-col gap-6">
      {/* Header Banner */}
      <div className="bg-surface-container p-6 rounded-lg border border-outline-variant/30 shadow-card flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <Building2 className="w-6 h-6 text-primary" />
            <h1 className="text-2xl font-bold font-display text-primary">Department Administration</h1>
          </div>
          <p className="text-xs text-on-surface-variant max-w-xl mt-1">
            Configure line agency routing, update statutory SLA compliance thresholds, and manage
            nodal officer assignments.
          </p>
        </div>

        <Button size="sm" icon={<Plus className="w-4 h-4" />} onClick={openCreateModal}>
          Register Department
        </Button>
      </div>

      {/* Department Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {departments.map((dept) => (
          <Card key={dept.id} className="flex flex-col justify-between">
            <div>
              <div className="flex items-start justify-between pb-3 border-b border-outline-variant/20">
                <div className="flex flex-col">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-bold font-display text-primary">{dept.name}</span>
                    <span className="px-1.5 py-0.5 rounded bg-primary/10 text-primary font-mono text-[10px] font-bold">
                      {dept.code}
                    </span>
                  </div>
                  <span className="text-[11px] text-on-surface-variant mt-1 leading-snug">
                    {dept.description}
                  </span>
                </div>
                <div className="flex items-center gap-1">
                  <button
                    onClick={() => openEditModal(dept)}
                    className="p-1 rounded text-outline hover:text-primary transition-colors"
                    title="Edit department SLA"
                  >
                    <Edit2 className="w-3.5 h-3.5" />
                  </button>
                  <button
                    onClick={() => setDeleteCandidate(dept)}
                    className="p-1 rounded text-outline hover:text-error transition-colors"
                    title="Remove department"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3 py-3 text-xs">
                <div>
                  <span className="text-[10px] uppercase font-bold text-outline block">
                    Nodal Officer
                  </span>
                  <span className="font-semibold text-primary">{dept.nodalOfficer}</span>
                  <span className="text-[11px] text-on-surface-variant block mt-0.5">
                    {dept.contactEmail}
                  </span>
                </div>
                <div>
                  <span className="text-[10px] uppercase font-bold text-outline block">
                    Statutory SLA Target
                  </span>
                  <span className="font-semibold text-secondary flex items-center gap-1">
                    <Clock className="w-3.5 h-3.5" /> {dept.slaTargetHours} Hours
                  </span>
                </div>
              </div>
            </div>

            <div className="pt-3 border-t border-outline-variant/20 flex items-center justify-between text-xs bg-surface-container-low/50 -mx-5 -mb-5 px-5 py-2.5 rounded-b-lg">
              <span className="text-on-surface-variant">
                Active Cases: <strong className="text-primary">{dept.activeCasesCount}</strong>
              </span>
              <span className="text-emerald-700 font-semibold flex items-center gap-1">
                <CheckCircle2 className="w-3.5 h-3.5" /> {dept.resolvedCount} Closed
              </span>
            </div>
          </Card>
        ))}
      </div>

      {/* Modal Dialog for Add / Edit */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-primary/40 backdrop-blur-sm">
          <div className="bg-surface-lowest w-full max-w-md rounded-lg shadow-floating border border-outline-variant/40 p-6 flex flex-col gap-4">
            <h3 className="text-base font-bold font-display text-primary">
              {editingDept ? 'Edit Department SLA & Nodal Officer' : 'Register New Line Agency'}
            </h3>

            <form onSubmit={handleSave} className="flex flex-col gap-3 text-xs">
              <div>
                <label className="block font-semibold text-primary mb-1">Department Name</label>
                <input
                  type="text"
                  required
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="e.g. Irrigation and Flood Control"
                  className="w-full px-3 py-2 rounded border border-outline-variant/60 bg-surface-lowest"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-semibold text-primary mb-1">Code</label>
                  <input
                    type="text"
                    required
                    value={code}
                    onChange={(e) => setCode(e.target.value)}
                    placeholder="IFCD"
                    className="w-full px-3 py-2 rounded border border-outline-variant/60 bg-surface-lowest"
                  />
                </div>
                <div>
                  <label className="block font-semibold text-primary mb-1">Target SLA (Hours)</label>
                  <input
                    type="number"
                    min="1"
                    required
                    value={slaHours}
                    onChange={(e) => setSlaHours(Number(e.target.value))}
                    className="w-full px-3 py-2 rounded border border-outline-variant/60 bg-surface-lowest"
                  />
                </div>
              </div>

              <div>
                <label className="block font-semibold text-primary mb-1">Nodal Officer Name</label>
                <input
                  type="text"
                  required
                  value={nodalOfficer}
                  onChange={(e) => setNodalOfficer(e.target.value)}
                  placeholder="Er. Alok Sharma"
                  className="w-full px-3 py-2 rounded border border-outline-variant/60 bg-surface-lowest"
                />
              </div>

              <div>
                <label className="block font-semibold text-primary mb-1">Contact Email</label>
                <input
                  type="email"
                  required
                  value={contactEmail}
                  onChange={(e) => setContactEmail(e.target.value)}
                  placeholder="alok.sharma@delhi.gov.in"
                  className="w-full px-3 py-2 rounded border border-outline-variant/60 bg-surface-lowest"
                />
              </div>

              <div>
                <label className="block font-semibold text-primary mb-1">Scope & Description</label>
                <textarea
                  rows={2}
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Jurisdictional civic mandate..."
                  className="w-full px-3 py-2 rounded border border-outline-variant/60 bg-surface-lowest"
                />
              </div>

              <div className="flex items-center justify-end gap-2 pt-3 border-t border-outline-variant/20">
                <Button size="sm" variant="outline" type="button" onClick={() => setIsModalOpen(false)}>
                  Cancel
                </Button>
                <Button size="sm" variant="primary" type="submit">
                  Save Department
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Delete Confirmation */}
      <ConfirmationDialog
        isOpen={!!deleteCandidate}
        title="Remove Department Agency"
        description={`Are you sure you want to remove ${deleteCandidate?.name} (${deleteCandidate?.code})? Existing complaint associations will need reassignment.`}
        confirmLabel="Remove Department"
        isDestructive
        onConfirm={() => {
          if (deleteCandidate) {
            deleteDepartment(deleteCandidate.id);
            setDeleteCandidate(null);
          }
        }}
        onCancel={() => setDeleteCandidate(null)}
      />
    </div>
  );
};
