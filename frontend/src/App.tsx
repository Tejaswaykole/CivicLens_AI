import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { RolePreviewProvider } from './context/RolePreviewContext';
import { AppDataProvider } from './context/AppDataContext';
import { AppShell } from './components/layout/AppShell';
import { DevRoleSwitcher } from './components/common/DevRoleSwitcher';

// Pages
import { DashboardPage } from './pages/DashboardPage';
import { LoginPage } from './pages/LoginPage';
import { RegisterPage } from './pages/RegisterPage';
import { ProfilePage } from './pages/ProfilePage';
import { NotificationsPage } from './pages/NotificationsPage';
import { AIExplainabilityPage } from './pages/AIExplainabilityPage';
import { NotFoundPage } from './pages/NotFoundPage';

// System Administrator Pages
import { UserManagementPage } from './pages/admin/UserManagementPage';
import { DepartmentManagementPage } from './pages/admin/DepartmentManagementPage';
import { AuditHistoryPage } from './pages/admin/AuditHistoryPage';
import { ResponsibleAIPage } from './pages/admin/ResponsibleAIPage';
import { ModelInformationPage } from './pages/admin/ModelInformationPage';
import { SystemAnalyticsPage } from './pages/admin/SystemAnalyticsPage';

// Grievance Officer Pages
import { OfficerComplaintInboxPage } from './pages/officer/OfficerComplaintInboxPage';
import { OfficerComplaintDetailsPage } from './pages/officer/OfficerComplaintDetailsPage';
import { OfficerAnalyzerPage } from './pages/officer/OfficerAnalyzerPage';
import { OfficerWhatIfSimulatorPage } from './pages/officer/OfficerWhatIfSimulatorPage';
import { OfficerHITLReviewPage } from './pages/officer/OfficerHITLReviewPage';

// Department Officer Pages
import { DepartmentWorkOrdersPage } from './pages/department/DepartmentWorkOrdersPage';
import { DepartmentCrewsPage } from './pages/department/DepartmentCrewsPage';

// Citizen Pages
import { CitizenMyComplaintsPage } from './pages/citizen/CitizenMyComplaintsPage';
import { CitizenSubmitComplaintPage } from './pages/citizen/CitizenSubmitComplaintPage';
import { CitizenCharterPage } from './pages/citizen/CitizenCharterPage';

export const App: React.FC = () => {
  return (
    <AppDataProvider>
      <RolePreviewProvider>
        <BrowserRouter>
          <Routes>
            {/* Public Authentication routes */}
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />

            {/* Root redirect to dashboard */}
            <Route path="/" element={<Navigate to="/app/dashboard" replace />} />

            {/* Protected Application Shell routes */}
            <Route
              path="/app/*"
              element={
                <AppShell>
                  <Routes>
                    {/* Common / Core Routes */}
                    <Route path="dashboard" element={<DashboardPage />} />
                    <Route path="profile" element={<ProfilePage />} />
                    <Route path="notifications" element={<NotificationsPage />} />
                    <Route path="ai-explainability" element={<AIExplainabilityPage />} />

                    {/* System Administrator Routes */}
                    <Route path="admin/users" element={<UserManagementPage />} />
                    <Route path="admin/departments" element={<DepartmentManagementPage />} />
                    <Route path="admin/audit" element={<AuditHistoryPage />} />
                    <Route path="admin/responsible-ai" element={<ResponsibleAIPage />} />
                    <Route path="admin/models" element={<ModelInformationPage />} />
                    <Route path="admin/analytics" element={<SystemAnalyticsPage />} />

                    {/* Grievance Officer Routes */}
                    <Route path="officer/inbox" element={<OfficerComplaintInboxPage />} />
                    <Route path="officer/complaints/:id" element={<OfficerComplaintDetailsPage />} />
                    <Route path="officer/analyzer" element={<OfficerAnalyzerPage />} />
                    <Route path="officer/simulator" element={<OfficerWhatIfSimulatorPage />} />
                    <Route path="officer/hitl" element={<OfficerHITLReviewPage />} />

                    {/* Department Officer Routes */}
                    <Route path="department/work-orders" element={<DepartmentWorkOrdersPage />} />
                    <Route path="department/crews" element={<DepartmentCrewsPage />} />

                    {/* Citizen Routes */}
                    <Route path="citizen/submit" element={<CitizenSubmitComplaintPage />} />
                    <Route path="citizen/my-complaints" element={<CitizenMyComplaintsPage />} />
                    <Route path="citizen/charter" element={<CitizenCharterPage />} />

                    {/* Fallback inside App */}
                    <Route path="*" element={<Navigate to="/app/dashboard" replace />} />
                  </Routes>
                </AppShell>
              }
            />

            {/* 404 Route */}
            <Route path="*" element={<NotFoundPage />} />
          </Routes>

          {/* Global Dev-Only Role Switcher */}
          <DevRoleSwitcher />
        </BrowserRouter>
      </RolePreviewProvider>
    </AppDataProvider>
  );
};

export default App;
