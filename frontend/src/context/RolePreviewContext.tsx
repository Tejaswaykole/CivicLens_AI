import React, { useState, type ReactNode } from 'react';
import type { UserRole } from '../types';
import { MOCK_USERS } from '../mock/data';
import { RolePreviewContext } from './useRolePreview';

export const RolePreviewProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [currentRole, setCurrentRole] = useState<UserRole>('system_admin');
  const isDevMode = import.meta.env.DEV || import.meta.env.VITE_ENABLE_DEV_ROLE_SWITCHER === 'true';

  const currentUser = MOCK_USERS[currentRole] || MOCK_USERS.system_admin;

  const setRole = (role: UserRole) => {
    setCurrentRole(role);
  };

  return (
    <RolePreviewContext.Provider value={{ currentRole, currentUser, setRole, isDevMode }}>
      {children}
    </RolePreviewContext.Provider>
  );
};
