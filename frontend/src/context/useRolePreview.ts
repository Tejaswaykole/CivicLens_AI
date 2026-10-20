import { createContext, useContext } from 'react';
import type { User, UserRole } from '../types';

export interface RolePreviewContextType {
  currentRole: UserRole;
  currentUser: User;
  setRole: (role: UserRole) => void;
  isDevMode: boolean;
}

export const RolePreviewContext = createContext<RolePreviewContextType | undefined>(undefined);

export const useRolePreview = () => {
  const context = useContext(RolePreviewContext);
  if (!context) {
    throw new Error('useRolePreview must be used within a RolePreviewProvider');
  }
  return context;
};
