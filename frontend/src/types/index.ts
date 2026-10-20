// CivicLens AI - Core TypeScript Domain Models
// Strictly separates AI-suggested values from Human-confirmed decisions

export type UserRole =
  | 'system_admin'
  | 'grievance_officer'
  | 'department_officer'
  | 'citizen';

export interface User {
  id: string;
  name: string;
  email: string;
  role: UserRole;
  designation?: string;
  departmentId?: string;
  departmentName?: string;
  wardOrZone?: string;
  avatarInitials: string;
  isActive: boolean;
  createdAt: string;
}

export type ComplaintPriority = 'critical' | 'high' | 'medium' | 'low';

export type ComplaintStatus =
  | 'submitted'
  | 'in_review'
  | 'triaged'
  | 'assigned'
  | 'in_progress'
  | 'resolved'
  | 'rejected';

export interface AIPriorityAssessment {
  suggestedPriority: ComplaintPriority;
  confidenceScore: number; // e.g. 0.88 for 88%
  urgencyReasoning: string;
  detectedCategories: string[];
  flaggedSafetyHazard: boolean;
  requiresHITLReview: boolean; // Mandated if < 75% or sensitive category
  modelEvaluatedAt: string;
  influentialFeatures?: { feature: string; weight: number }[];
}

export interface HumanConfirmation {
  confirmedPriority: ComplaintPriority;
  confirmedByOfficerId: string;
  confirmedByOfficerName: string;
  officerNotes?: string;
  confirmedAt: string;
  status: 'pending' | 'concurred' | 'overridden';
}

export interface ReviewEvent {
  id: string;
  complaintId: string;
  trackingNumber: string;
  officerId: string;
  officerName: string;
  action: 'concurred' | 'overridden' | 'escalated' | 'status_updated';
  previousPriority?: ComplaintPriority;
  newPriority?: ComplaintPriority;
  previousStatus?: ComplaintStatus;
  newStatus?: ComplaintStatus;
  reviewReason: string;
  timestamp: string;
}

export interface Department {
  id: string;
  name: string;
  code: string;
  description: string;
  nodalOfficer: string;
  contactEmail: string;
  slaTargetHours: number;
  activeCasesCount: number;
  resolvedCount: number;
}

export interface StatusHistoryItem {
  id: string;
  status: ComplaintStatus;
  title: string;
  note: string;
  timestamp: string;
  actor: string;
}

export interface Complaint {
  id: string;
  trackingNumber: string;
  title: string;
  description: string;
  category: string;
  departmentId: string;
  departmentName: string;
  wardZone: string;
  locationAddress: string;
  status: ComplaintStatus;
  
  // AI vs Human Priority Distinction
  aiAssessment: AIPriorityAssessment;
  humanConfirmation?: HumanConfirmation;
  effectivePriority: ComplaintPriority; // Human priority if confirmed, else temporary fallback

  citizenName: string;
  citizenContactMasked: string;
  assignedOfficerName?: string;
  assignedCrewUnit?: string;
  resolutionNotes?: string;
  createdAt: string;
  updatedAt: string;
  resolutionDueAt: string;
  imageUrl?: string;
  statusHistory: StatusHistoryItem[];
  resolutionFeedback?: {
    rating: number; // 1-5
    comments: string;
    submittedAt: string;
  };
}

export interface NotificationItem {
  id: string;
  userId?: string;
  role?: UserRole;
  title: string;
  message: string;
  type: 'urgent' | 'info' | 'success' | 'alert';
  createdAt: string;
  read: boolean;
  link?: string;
}

export interface AuditLogItem {
  id: string;
  eventType: 'HITL_OVERRIDE' | 'CONCURRENCE' | 'STATUS_CHANGE' | 'DEPARTMENT_UPDATE' | 'USER_CREATE' | 'SYSTEM_ALERT';
  description: string;
  actorName: string;
  actorRole: UserRole;
  targetId: string;
  details: string;
  isSimulated: boolean;
  timestamp: string;
}
