import { createContext, useContext } from 'react';
import type {
  Complaint,
  Department,
  User,
  AuditLogItem,
  NotificationItem,
  ComplaintPriority,
  ComplaintStatus,
} from '../types';

export interface AppDataContextType {
  complaints: Complaint[];
  departments: Department[];
  users: User[];
  auditLogs: AuditLogItem[];
  notifications: NotificationItem[];
  
  // Complaint Actions
  addComplaint: (newComplaint: Omit<Complaint, 'id' | 'trackingNumber' | 'createdAt' | 'updatedAt' | 'statusHistory' | 'aiAssessment' | 'effectivePriority'>) => Complaint;
  concurComplaint: (complaintId: string, officerId: string, officerName: string, notes?: string) => void;
  overrideComplaintPriority: (complaintId: string, newPriority: ComplaintPriority, officerId: string, officerName: string, reason: string) => void;
  updateComplaintStatus: (complaintId: string, newStatus: ComplaintStatus, actorName: string, note: string) => void;
  submitResolutionFeedback: (complaintId: string, rating: number, comments: string) => void;
  
  // Department Actions
  addDepartment: (dept: Omit<Department, 'id' | 'activeCasesCount' | 'resolvedCount'>) => void;
  updateDepartment: (deptId: string, updates: Partial<Department>) => void;
  deleteDepartment: (deptId: string) => void;

  // User Actions
  addUser: (user: Omit<User, 'id' | 'createdAt'>) => void;
  toggleUserStatus: (userId: string) => void;
  deleteUser: (userId: string) => void;

  // Notification Actions
  markNotificationRead: (notifId: string) => void;
  markAllNotificationsRead: () => void;
}

export const AppDataContext = createContext<AppDataContextType | undefined>(undefined);

export const useAppData = () => {
  const context = useContext(AppDataContext);
  if (!context) {
    throw new Error('useAppData must be used within an AppDataProvider');
  }
  return context;
};
