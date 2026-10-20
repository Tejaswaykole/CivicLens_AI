import React, { useState, type ReactNode } from 'react';
import type {
  Complaint,
  Department,
  User,
  AuditLogItem,
  NotificationItem,
  ComplaintPriority,
  ComplaintStatus,
} from '../types';
import {
  INITIAL_COMPLAINTS,
  INITIAL_DEPARTMENTS,
  INITIAL_USERS,
  INITIAL_AUDIT_LOGS,
  INITIAL_NOTIFICATIONS,
} from '../mock/data';
import { AppDataContext } from './useAppData';

export const AppDataProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [complaints, setComplaints] = useState<Complaint[]>(INITIAL_COMPLAINTS);
  const [departments, setDepartments] = useState<Department[]>(INITIAL_DEPARTMENTS);
  const [users, setUsers] = useState<User[]>(INITIAL_USERS);
  const [auditLogs, setAuditLogs] = useState<AuditLogItem[]>(INITIAL_AUDIT_LOGS);
  const [notifications, setNotifications] = useState<NotificationItem[]>(INITIAL_NOTIFICATIONS);

  // 1. Add Complaint (from Citizen submission)
  const addComplaint = (
    data: Omit<Complaint, 'id' | 'trackingNumber' | 'createdAt' | 'updatedAt' | 'statusHistory' | 'aiAssessment' | 'effectivePriority'>
  ): Complaint => {
    const randomSuffix = Math.floor(1000 + Math.random() * 9000);
    const trackingNumber = `DEL-2024-${randomSuffix}`;
    const id = `cmp_${Date.now()}`;
    const now = new Date().toISOString();

    const isCritical = data.description.toLowerCase().includes('accident') || data.description.toLowerCase().includes('spark') || data.description.toLowerCase().includes('wire');
    const isHigh = data.description.toLowerCase().includes('water') || data.description.toLowerCase().includes('sewage') || data.description.toLowerCase().includes('deep');
    const aiPriority: ComplaintPriority = isCritical ? 'critical' : isHigh ? 'high' : 'medium';
    const confidence = isCritical ? 0.92 : isHigh ? 0.78 : 0.86;

    const newComplaint: Complaint = {
      ...data,
      id,
      trackingNumber,
      status: 'submitted',
      effectivePriority: aiPriority,
      createdAt: now,
      updatedAt: now,
      resolutionDueAt: new Date(Date.now() + 48 * 3600 * 1000).toISOString(),
      aiAssessment: {
        suggestedPriority: aiPriority,
        confidenceScore: confidence,
        urgencyReasoning: `Simulated heuristic NLP triage evaluated text features indicating ${aiPriority} urgency.`,
        detectedCategories: [data.category, 'Public Asset Report'],
        flaggedSafetyHazard: isCritical,
        requiresHITLReview: confidence < 0.75 || isCritical,
        modelEvaluatedAt: now,
        influentialFeatures: [
          { feature: 'citizen reported severity', weight: 0.35 },
          { feature: 'zonal incident density', weight: 0.28 },
        ],
      },
      statusHistory: [
        {
          id: `hist_${Date.now()}`,
          status: 'submitted',
          title: 'Grievance Registered',
          note: 'Submitted via CivicLens Citizen Web Portal.',
          timestamp: now,
          actor: data.citizenName,
        },
      ],
    };

    setComplaints((prev) => [newComplaint, ...prev]);

    const newAudit: AuditLogItem = {
      id: `aud_${Date.now()}`,
      eventType: 'SYSTEM_ALERT',
      description: `New grievance ${trackingNumber} logged`,
      actorName: data.citizenName,
      actorRole: 'citizen',
      targetId: id,
      details: `Citizen submitted '${data.title}' under ${data.departmentName}.`,
      isSimulated: true,
      timestamp: now,
    };
    setAuditLogs((prev) => [newAudit, ...prev]);

    const newNotif: NotificationItem = {
      id: `notif_${Date.now()}`,
      role: 'grievance_officer',
      title: `New Grievance: ${trackingNumber}`,
      message: `${data.title} (${data.wardZone}) logged and awaiting triage.`,
      type: 'info',
      createdAt: now,
      read: false,
      link: '/app/officer/inbox',
    };
    setNotifications((prev) => [newNotif, ...prev]);

    return newComplaint;
  };

  // 2. Concur with AI Priority
  const concurComplaint = (
    complaintId: string,
    officerId: string,
    officerName: string,
    notes = 'Concurred with AI priority assessment.'
  ) => {
    const now = new Date().toISOString();
    setComplaints((prev) =>
      prev.map((c) => {
        if (c.id === complaintId) {
          const priority = c.aiAssessment.suggestedPriority;
          return {
            ...c,
            status: 'triaged',
            effectivePriority: priority,
            updatedAt: now,
            humanConfirmation: {
              confirmedPriority: priority,
              confirmedByOfficerId: officerId,
              confirmedByOfficerName: officerName,
              officerNotes: notes,
              confirmedAt: now,
              status: 'concurred',
            },
            statusHistory: [
              ...c.statusHistory,
              {
                id: `hist_${Date.now()}`,
                status: 'triaged',
                title: 'Officer Concurrence Recorded',
                note: notes,
                timestamp: now,
                actor: officerName,
              },
            ],
          };
        }
        return c;
      })
    );

    const c = complaints.find((item) => item.id === complaintId);
    if (c) {
      setAuditLogs((prev) => [
        {
          id: `aud_${Date.now()}`,
          eventType: 'CONCURRENCE',
          description: `Concurred with ${c.aiAssessment.suggestedPriority} priority on ${c.trackingNumber}`,
          actorName: officerName,
          actorRole: 'grievance_officer',
          targetId: complaintId,
          details: notes,
          isSimulated: true,
          timestamp: now,
        },
        ...prev,
      ]);
    }
  };

  // 3. Override Priority
  const overrideComplaintPriority = (
    complaintId: string,
    newPriority: ComplaintPriority,
    officerId: string,
    officerName: string,
    reason: string
  ) => {
    const now = new Date().toISOString();
    setComplaints((prev) =>
      prev.map((c) => {
        if (c.id === complaintId) {
          return {
            ...c,
            status: 'triaged',
            effectivePriority: newPriority,
            updatedAt: now,
            humanConfirmation: {
              confirmedPriority: newPriority,
              confirmedByOfficerId: officerId,
              confirmedByOfficerName: officerName,
              officerNotes: reason,
              confirmedAt: now,
              status: 'overridden',
            },
            statusHistory: [
              ...c.statusHistory,
              {
                id: `hist_${Date.now()}`,
                status: 'triaged',
                title: `Priority Adjusted to ${newPriority.toUpperCase()} by Officer`,
                note: `Review Reason: ${reason}`,
                timestamp: now,
                actor: officerName,
              },
            ],
          };
        }
        return c;
      })
    );

    const c = complaints.find((item) => item.id === complaintId);
    if (c) {
      setAuditLogs((prev) => [
        {
          id: `aud_${Date.now()}`,
          eventType: 'HITL_OVERRIDE',
          description: `Overrode priority from ${c.aiAssessment.suggestedPriority} to ${newPriority} on ${c.trackingNumber}`,
          actorName: officerName,
          actorRole: 'grievance_officer',
          targetId: complaintId,
          details: reason,
          isSimulated: true,
          timestamp: now,
        },
        ...prev,
      ]);
    }
  };

  // 4. Update Status
  const updateComplaintStatus = (
    complaintId: string,
    newStatus: ComplaintStatus,
    actorName: string,
    note: string
  ) => {
    const now = new Date().toISOString();
    setComplaints((prev) =>
      prev.map((c) => {
        if (c.id === complaintId) {
          return {
            ...c,
            status: newStatus,
            updatedAt: now,
            resolutionNotes: newStatus === 'resolved' ? note : c.resolutionNotes,
            statusHistory: [
              ...c.statusHistory,
              {
                id: `hist_${Date.now()}`,
                status: newStatus,
                title: `Status updated to ${newStatus.replace('_', ' ').toUpperCase()}`,
                note,
                timestamp: now,
                actor: actorName,
              },
            ],
          };
        }
        return c;
      })
    );

    const c = complaints.find((item) => item.id === complaintId);
    if (c) {
      setAuditLogs((prev) => [
        {
          id: `aud_${Date.now()}`,
          eventType: 'STATUS_CHANGE',
          description: `Updated status of ${c.trackingNumber} to ${newStatus}`,
          actorName,
          actorRole: 'department_officer',
          targetId: complaintId,
          details: note,
          isSimulated: true,
          timestamp: now,
        },
        ...prev,
      ]);
    }
  };

  // 5. Submit Citizen Feedback
  const submitResolutionFeedback = (complaintId: string, rating: number, comments: string) => {
    const now = new Date().toISOString();
    setComplaints((prev) =>
      prev.map((c) => {
        if (c.id === complaintId) {
          return {
            ...c,
            resolutionFeedback: {
              rating,
              comments,
              submittedAt: now,
            },
          };
        }
        return c;
      })
    );
  };

  // Department actions
  const addDepartment = (dept: Omit<Department, 'id' | 'activeCasesCount' | 'resolvedCount'>) => {
    const newDept: Department = {
      ...dept,
      id: `dept_${Date.now()}`,
      activeCasesCount: 0,
      resolvedCount: 0,
    };
    setDepartments((prev) => [...prev, newDept]);
  };

  const updateDepartment = (deptId: string, updates: Partial<Department>) => {
    setDepartments((prev) =>
      prev.map((d) => (d.id === deptId ? { ...d, ...updates } : d))
    );
  };

  const deleteDepartment = (deptId: string) => {
    setDepartments((prev) => prev.filter((d) => d.id !== deptId));
  };

  // User actions
  const addUser = (userData: Omit<User, 'id' | 'createdAt'>) => {
    const newUser: User = {
      ...userData,
      id: `usr_${Date.now()}`,
      createdAt: new Date().toISOString(),
    };
    setUsers((prev) => [...prev, newUser]);
  };

  const toggleUserStatus = (userId: string) => {
    setUsers((prev) =>
      prev.map((u) => (u.id === userId ? { ...u, isActive: !u.isActive } : u))
    );
  };

  const deleteUser = (userId: string) => {
    setUsers((prev) => prev.filter((u) => u.id !== userId));
  };

  // Notifications
  const markNotificationRead = (notifId: string) => {
    setNotifications((prev) =>
      prev.map((n) => (n.id === notifId ? { ...n, read: true } : n))
    );
  };

  const markAllNotificationsRead = () => {
    setNotifications((prev) => prev.map((n) => ({ ...n, read: true })));
  };

  return (
    <AppDataContext.Provider
      value={{
        complaints,
        departments,
        users,
        auditLogs,
        notifications,
        addComplaint,
        concurComplaint,
        overrideComplaintPriority,
        updateComplaintStatus,
        submitResolutionFeedback,
        addDepartment,
        updateDepartment,
        deleteDepartment,
        addUser,
        toggleUserStatus,
        deleteUser,
        markNotificationRead,
        markAllNotificationsRead,
      }}
    >
      {children}
    </AppDataContext.Provider>
  );
};
