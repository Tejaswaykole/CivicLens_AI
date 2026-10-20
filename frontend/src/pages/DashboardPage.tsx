import React from 'react';
import { useRolePreview } from '../context/useRolePreview';
import { SystemAdminDashboard } from '../components/dashboard/SystemAdminDashboard';
import { OfficerConsoleDashboard } from '../components/dashboard/OfficerConsoleDashboard';
import { DepartmentOfficerDashboard } from '../components/dashboard/DepartmentOfficerDashboard';
import { CitizenDashboard } from '../components/dashboard/CitizenDashboard';

export const DashboardPage: React.FC = () => {
  const { currentRole } = useRolePreview();

  switch (currentRole) {
    case 'system_admin':
      return <SystemAdminDashboard />;
    case 'grievance_officer':
      return <OfficerConsoleDashboard />;
    case 'department_officer':
      return <DepartmentOfficerDashboard />;
    case 'citizen':
    default:
      return <CitizenDashboard />;
  }
};
