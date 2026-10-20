import React, { useState } from 'react';
import { Card } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { ConfirmationDialog } from '../../components/ui/ConfirmationDialog';
import { useAppData } from '../../context/useAppData';
import type { User, UserRole } from '../../types';
import { Users, Search, Plus, Trash2, Power, Mail, MapPin } from 'lucide-react';

export const UserManagementPage: React.FC = () => {
  const { users, addUser, toggleUserStatus, deleteUser } = useAppData();
  const [search, setSearch] = useState('');
  const [roleFilter, setRoleFilter] = useState<string>('ALL');
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [deleteCandidate, setDeleteCandidate] = useState<User | null>(null);

  // New user form state
  const [newName, setNewName] = useState('');
  const [newEmail, setNewEmail] = useState('');
  const [newRole, setNewRole] = useState<UserRole>('grievance_officer');
  const [newDesignation, setNewDesignation] = useState('');
  const [newWard, setNewWard] = useState('Zone 1 - Central');

  const filtered = users.filter((u) => {
    const matchesSearch =
      u.name.toLowerCase().includes(search.toLowerCase()) ||
      u.email.toLowerCase().includes(search.toLowerCase()) ||
      (u.designation && u.designation.toLowerCase().includes(search.toLowerCase()));
    const matchesRole = roleFilter === 'ALL' || u.role === roleFilter;
    return matchesSearch && matchesRole;
  });

  const handleCreateUser = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newName || !newEmail) return;

    const initials = newName
      .split(' ')
      .map((n) => n[0])
      .slice(0, 2)
      .join('')
      .toUpperCase();

    addUser({
      name: newName,
      email: newEmail,
      role: newRole,
      designation: newDesignation || `${newRole.replace('_', ' ').toUpperCase()}`,
      wardOrZone: newWard,
      avatarInitials: initials || 'CL',
      isActive: true,
    });

    setIsAddModalOpen(false);
    setNewName('');
    setNewEmail('');
    setNewDesignation('');
  };

  return (
    <div className="flex flex-col gap-6">
      {/* Page Header */}
      <div className="bg-surface-container p-6 rounded-lg border border-outline-variant/30 shadow-card flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <Users className="w-6 h-6 text-primary" />
            <h1 className="text-2xl font-bold font-display text-primary">User & Role Management</h1>
          </div>
          <p className="text-xs text-on-surface-variant max-w-xl mt-1">
            Oversee administrative personnel, zonal grievance officers, field department engineers,
            and citizen portal permissions.
          </p>
        </div>

        <Button
          size="sm"
          icon={<Plus className="w-4 h-4" />}
          onClick={() => setIsAddModalOpen(true)}
        >
          Add Officer / User
        </Button>
      </div>

      {/* Filter and User Roster Card */}
      <Card
        title="Active Municipal Personnel & User Accounts"
        subtitle={`Showing ${filtered.length} of ${users.length} registered accounts`}
        action={
          <div className="flex items-center gap-2 flex-wrap">
            <div className="relative">
              <Search className="w-3.5 h-3.5 text-outline absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                placeholder="Search by name, email, designation..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="pl-8 pr-3 py-1.5 text-xs rounded border border-outline-variant/60 bg-surface-lowest text-on-surface focus:outline-none focus:border-primary w-64"
              />
            </div>
            <select
              value={roleFilter}
              onChange={(e) => setRoleFilter(e.target.value)}
              className="py-1.5 px-3 text-xs rounded border border-outline-variant/60 bg-surface-lowest text-on-surface focus:outline-none focus:border-primary"
            >
              <option value="ALL">All Roles</option>
              <option value="system_admin">System Administrator</option>
              <option value="grievance_officer">Grievance Officer</option>
              <option value="department_officer">Department Officer</option>
              <option value="citizen">Citizen</option>
            </select>
          </div>
        }
      >
        <div className="overflow-x-auto -mx-5">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="bg-surface-container text-on-surface-variant uppercase tracking-wider text-[10px] font-bold border-y border-outline-variant/30">
                <th className="py-3 px-4">User</th>
                <th className="py-3 px-3">Role & Designation</th>
                <th className="py-3 px-3">Zonal Jurisdiction</th>
                <th className="py-3 px-3">Status</th>
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-outline-variant/20">
              {filtered.map((u) => (
                <tr key={u.id} className="hover:bg-surface-low/50 transition-colors">
                  <td className="py-3 px-4">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-full bg-secondary text-white font-bold text-xs flex items-center justify-center shrink-0">
                        {u.avatarInitials}
                      </div>
                      <div className="flex flex-col">
                        <span className="font-semibold text-primary">{u.name}</span>
                        <span className="text-[11px] text-on-surface-variant flex items-center gap-1">
                          <Mail className="w-3 h-3 text-outline" /> {u.email}
                        </span>
                      </div>
                    </div>
                  </td>
                  <td className="py-3 px-3">
                    <span className="font-semibold text-primary block capitalize">
                      {u.role.replace('_', ' ')}
                    </span>
                    <span className="text-[11px] text-on-surface-variant block mt-0.5">
                      {u.designation}
                    </span>
                  </td>
                  <td className="py-3 px-3">
                    <span className="text-on-surface flex items-center gap-1">
                      <MapPin className="w-3 h-3 text-secondary" /> {u.wardOrZone || 'NCT HQ'}
                    </span>
                  </td>
                  <td className="py-3 px-3">
                    <span
                      className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-bold ${
                        u.isActive
                          ? 'bg-emerald-100 text-emerald-800'
                          : 'bg-gray-200 text-gray-700'
                      }`}
                    >
                      <span
                        className={`w-1.5 h-1.5 rounded-full ${
                          u.isActive ? 'bg-emerald-600' : 'bg-gray-500'
                        }`}
                      />
                      {u.isActive ? 'Active' : 'Disabled'}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-right">
                    <div className="flex items-center justify-end gap-1.5">
                      <Button
                        size="sm"
                        variant="outline"
                        title={u.isActive ? 'Deactivate user' : 'Activate user'}
                        onClick={() => toggleUserStatus(u.id)}
                      >
                        <Power className="w-3.5 h-3.5" />
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        className="text-error hover:bg-error-container/30"
                        title="Delete user record"
                        onClick={() => setDeleteCandidate(u)}
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </Button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      {/* Add User Modal */}
      {isAddModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-primary/40 backdrop-blur-sm">
          <div className="bg-surface-lowest w-full max-w-md rounded-lg shadow-floating border border-outline-variant/40 p-6 flex flex-col gap-4">
            <h3 className="text-base font-bold font-display text-primary">
              Register New Municipal Personnel
            </h3>
            <form onSubmit={handleCreateUser} className="flex flex-col gap-3 text-xs">
              <div>
                <label className="block font-semibold text-primary mb-1">Full Name</label>
                <input
                  type="text"
                  required
                  value={newName}
                  onChange={(e) => setNewName(e.target.value)}
                  placeholder="e.g. Ramesh Chandra"
                  className="w-full px-3 py-2 rounded border border-outline-variant/60 bg-surface-lowest"
                />
              </div>

              <div>
                <label className="block font-semibold text-primary mb-1">Official Email</label>
                <input
                  type="email"
                  required
                  value={newEmail}
                  onChange={(e) => setNewEmail(e.target.value)}
                  placeholder="ramesh.chandra@civiclens.gov.in"
                  className="w-full px-3 py-2 rounded border border-outline-variant/60 bg-surface-lowest"
                />
              </div>

              <div>
                <label className="block font-semibold text-primary mb-1">Assigned Role</label>
                <select
                  value={newRole}
                  onChange={(e) => setNewRole(e.target.value as UserRole)}
                  className="w-full px-3 py-2 rounded border border-outline-variant/60 bg-surface-lowest"
                >
                  <option value="system_admin">System Administrator</option>
                  <option value="grievance_officer">Grievance Officer (Triage / HITL)</option>
                  <option value="department_officer">Department Officer (Field)</option>
                  <option value="citizen">Citizen Account</option>
                </select>
              </div>

              <div>
                <label className="block font-semibold text-primary mb-1">Designation Title</label>
                <input
                  type="text"
                  value={newDesignation}
                  onChange={(e) => setNewDesignation(e.target.value)}
                  placeholder="Assistant Engineer (Sanitation)"
                  className="w-full px-3 py-2 rounded border border-outline-variant/60 bg-surface-lowest"
                />
              </div>

              <div>
                <label className="block font-semibold text-primary mb-1">Jurisdiction Ward / Zone</label>
                <input
                  type="text"
                  value={newWard}
                  onChange={(e) => setNewWard(e.target.value)}
                  placeholder="Zone 4 - Ward 18"
                  className="w-full px-3 py-2 rounded border border-outline-variant/60 bg-surface-lowest"
                />
              </div>

              <div className="flex items-center justify-end gap-2 pt-3 border-t border-outline-variant/20">
                <Button size="sm" variant="outline" type="button" onClick={() => setIsAddModalOpen(false)}>
                  Cancel
                </Button>
                <Button size="sm" variant="primary" type="submit">
                  Save Officer Account
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Confirm Delete Dialog */}
      <ConfirmationDialog
        isOpen={!!deleteCandidate}
        title="Revoke and Delete User Account"
        description={`Are you sure you want to permanently delete the account for ${deleteCandidate?.name} (${deleteCandidate?.email})? This action updates the local session ledger.`}
        confirmLabel="Confirm Deletion"
        isDestructive
        onConfirm={() => {
          if (deleteCandidate) {
            deleteUser(deleteCandidate.id);
            setDeleteCandidate(null);
          }
        }}
        onCancel={() => setDeleteCandidate(null)}
      />
    </div>
  );
};
