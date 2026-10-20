import React, { useState } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { useRolePreview } from '../../context/useRolePreview';
import { useAppData } from '../../context/useAppData';
import {
  LayoutDashboard,
  Users,
  Building2,
  FileText,
  BrainCircuit,
  SlidersHorizontal,
  BarChart3,
  History,
  ShieldCheck,
  Bell,
  Search,
  Menu,
  X,
  LogOut,
  CheckCircle,
  Sliders,
  Sparkles,
  Truck,
  PlusCircle,
} from 'lucide-react';

interface AppShellProps {
  children: React.ReactNode;
}

export const AppShell: React.FC<AppShellProps> = ({ children }) => {
  const { currentUser, currentRole } = useRolePreview();
  const { notifications } = useAppData();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [notifDropdownOpen, setNotifDropdownOpen] = useState(false);
  const navigate = useNavigate();

  const unreadNotifs = notifications.filter((n) => !n.read).length;

  // Role-specific navigation items mapped cleanly to Phase 2 implemented routes
  const getNavLinks = () => {
    switch (currentRole) {
      case 'system_admin':
        return [
          {
            group: 'Overview',
            items: [
              { name: 'System Overview', path: '/app/dashboard', icon: LayoutDashboard },
            ],
          },
          {
            group: 'Management',
            items: [
              { name: 'Users & Roles', path: '/app/admin/users', icon: Users },
              { name: 'Departments', path: '/app/admin/departments', icon: Building2 },
            ],
          },
          {
            group: 'Intelligence',
            items: [
              { name: 'Complaints Ledger', path: '/app/officer/inbox', icon: FileText },
              { name: 'AI Explainability', path: '/app/ai-explainability', icon: BrainCircuit },
              { name: 'Model Information', path: '/app/admin/models', icon: SlidersHorizontal },
              { name: 'System Analytics', path: '/app/admin/analytics', icon: BarChart3 },
            ],
          },
          {
            group: 'Governance',
            items: [
              { name: 'Audit History', path: '/app/admin/audit', icon: History },
              { name: 'Responsible AI', path: '/app/admin/responsible-ai', icon: ShieldCheck },
            ],
          },
        ];

      case 'grievance_officer':
        return [
          {
            group: 'Triage Operations',
            items: [
              { name: 'Officer Console', path: '/app/dashboard', icon: LayoutDashboard },
              { name: 'Complaint Inbox', path: '/app/officer/inbox', icon: FileText },
              { name: 'HITL Review Queue', path: '/app/officer/hitl', icon: CheckCircle },
            ],
          },
          {
            group: 'Intelligence Sandbox',
            items: [
              { name: 'Complaint Analyzer', path: '/app/officer/analyzer', icon: Sparkles },
              { name: 'What-If Simulator', path: '/app/officer/simulator', icon: Sliders },
            ],
          },
        ];

      case 'department_officer':
        return [
          {
            group: 'Field Operations',
            items: [
              { name: 'Department Dashboard', path: '/app/dashboard', icon: LayoutDashboard },
              { name: 'Assigned Work Orders', path: '/app/department/work-orders', icon: FileText },
              { name: 'Field Crews', path: '/app/department/crews', icon: Truck },
            ],
          },
        ];

      case 'citizen':
      default:
        return [
          {
            group: 'Citizen Services',
            items: [
              { name: 'Grievance Dashboard', path: '/app/dashboard', icon: LayoutDashboard },
              { name: 'Submit Grievance', path: '/app/citizen/submit', icon: PlusCircle },
              { name: 'My Complaints', path: '/app/citizen/my-complaints', icon: FileText },
              { name: 'Citizen Charter', path: '/app/citizen/charter', icon: ShieldCheck },
            ],
          },
        ];
    }
  };

  const navGroups = getNavLinks();

  return (
    <div className="min-h-screen bg-surface-container-high/30 flex">
      {/* Desktop Sidebar (Midnight Indigo #282B4A brand container) */}
      <aside className="hidden lg:flex w-72 bg-midnight-indigo text-white flex-col justify-between fixed top-0 bottom-0 left-0 z-40 border-r border-white/10 select-none">
        <div className="flex flex-col flex-1 overflow-y-auto">
          {/* Logo / Header */}
          <div className="p-5 border-b border-white/10">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded bg-white text-midnight-indigo font-bold flex items-center justify-center font-display text-sm tracking-tight shadow-sm">
                CL
              </div>
              <div className="flex flex-col">
                <span className="font-bold font-display text-base tracking-tight text-white leading-none">
                  CivicLens AI
                </span>
                <span className="text-[10px] text-white/60 tracking-wider uppercase font-semibold mt-1">
                  Municipal Redressal Platform
                </span>
              </div>
            </div>
          </div>

          {/* Navigation Groups */}
          <nav className="flex flex-col py-3 px-3 gap-1">
            {navGroups.map((group, idx) => (
              <div key={idx} className="mb-2">
                <div className="px-3 pt-3 pb-1">
                  <span className="text-[10px] font-bold uppercase tracking-widest text-white/40">
                    {group.group}
                  </span>
                </div>
                {group.items.map((item) => (
                  <NavLink
                    key={item.path}
                    to={item.path}
                    end={item.path === '/app/dashboard'}
                    className={({ isActive }) =>
                      `flex items-center justify-between px-3 py-2 rounded text-xs transition-colors ${
                        isActive
                          ? 'bg-secondary/40 text-white border-l-4 border-surface font-semibold shadow-sm'
                          : 'text-white/70 hover:bg-white/5 hover:text-white'
                      }`
                    }
                  >
                    <div className="flex items-center gap-2.5">
                      <item.icon className="w-4 h-4" />
                      <span>{item.name}</span>
                    </div>
                  </NavLink>
                ))}
              </div>
            ))}
          </nav>
        </div>

        {/* User Card at bottom of sidebar */}
        <div className="p-4 border-t border-white/10 bg-black/20">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-9 h-9 rounded-full bg-secondary flex items-center justify-center shrink-0 border border-white/20 text-white font-bold text-xs">
              {currentUser.avatarInitials}
            </div>
            <div className="flex flex-col min-w-0">
              <span className="text-xs text-white font-semibold truncate leading-tight">
                {currentUser.name}
              </span>
              <span className="text-[10px] text-white/60 truncate leading-tight mt-0.5 font-medium">
                {currentUser.designation || currentUser.role.replace('_', ' ').toUpperCase()}
              </span>
            </div>
          </div>
          <div className="flex items-center justify-between pt-2 border-t border-white/10 text-[11px] text-white/60">
            <NavLink to="/app/profile" className="hover:text-white transition-colors">
              Profile
            </NavLink>
            <NavLink to="/app/notifications" className="hover:text-white transition-colors">
              Alerts
            </NavLink>
            <button
              onClick={() => navigate('/login')}
              className="hover:text-white transition-colors flex items-center gap-1"
            >
              Sign out
            </button>
          </div>
        </div>
      </aside>

      {/* Main Container */}
      <div className="lg:pl-72 flex flex-col flex-1 min-h-screen">
        {/* Top Header */}
        <header className="h-16 bg-surface-bright/95 backdrop-blur-md border-b border-outline-variant/30 sticky top-0 z-30 px-4 sm:px-6 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="lg:hidden p-1.5 rounded text-on-surface hover:bg-surface-container"
              aria-label="Toggle Navigation Menu"
            >
              {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>

            <div className="flex items-center gap-1.5 text-xs text-on-surface-variant">
              <span className="hover:text-on-surface cursor-pointer">CivicLens</span>
              <span className="text-outline-variant">/</span>
              <span className="text-on-surface font-semibold capitalize">
                {currentRole.replace('_', ' ')}
              </span>
            </div>

            <div className="hidden md:flex items-center ml-2">
              <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded bg-surface-container border border-outline-variant/40 text-[10px] font-semibold text-on-surface-variant">
                <span className="w-1.5 h-1.5 rounded-full bg-secondary" />
                NCT Operational Pilot
              </span>
            </div>
          </div>

          {/* Center search bar */}
          <div className="hidden md:flex flex-1 max-w-sm mx-4">
            <div className="relative w-full">
              <Search className="w-3.5 h-3.5 text-outline absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none" />
              <input
                type="text"
                placeholder="Search token, ward, officer (⌘K)..."
                className="w-full h-8 pl-8 pr-3 rounded text-xs bg-surface-container-low border border-outline-variant/40 placeholder:text-outline focus:outline-none focus:border-primary"
              />
            </div>
          </div>

          {/* Right Header items */}
          <div className="flex items-center gap-3 shrink-0">
            {/* Notification bell dropdown */}
            <div className="relative">
              <button
                onClick={() => setNotifDropdownOpen(!notifDropdownOpen)}
                className="relative p-2 text-on-surface-variant hover:text-on-surface rounded hover:bg-surface-container transition-colors"
                aria-label="Notifications"
              >
                <Bell className="w-4 h-4" />
                {unreadNotifs > 0 && (
                  <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-error ring-2 ring-white" />
                )}
              </button>

              {notifDropdownOpen && (
                <div className="absolute right-0 mt-2 w-80 bg-surface-lowest rounded-lg shadow-floating border border-outline-variant/40 p-3 z-50 animate-fade-in">
                  <div className="flex items-center justify-between pb-2 border-b border-outline-variant/20 mb-2">
                    <span className="text-xs font-bold text-primary font-display">Notifications</span>
                    <NavLink
                      to="/app/notifications"
                      onClick={() => setNotifDropdownOpen(false)}
                      className="text-[11px] text-secondary font-medium hover:underline"
                    >
                      View all
                    </NavLink>
                  </div>
                  <div className="flex flex-col gap-2 max-h-60 overflow-y-auto">
                    {notifications.map((n) => (
                      <div
                        key={n.id}
                        className="p-2 rounded bg-surface-container-low/50 hover:bg-surface-container border border-outline-variant/20 text-xs"
                      >
                        <p className="font-semibold text-primary text-[11px]">{n.title}</p>
                        <p className="text-[11px] text-on-surface-variant mt-0.5">{n.message}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* User Avatar */}
            <div className="flex items-center gap-2 pl-2 border-l border-outline-variant/30">
              <div className="w-7 h-7 rounded-full bg-secondary text-white flex items-center justify-center font-bold text-[11px]">
                {currentUser.avatarInitials}
              </div>
              <div className="hidden sm:flex flex-col text-left">
                <span className="text-xs font-semibold text-on-surface leading-tight">
                  {currentUser.name}
                </span>
                <span className="text-[10px] text-secondary font-medium capitalize">
                  {currentRole.replace('_', ' ')}
                </span>
              </div>
            </div>
          </div>
        </header>

        {/* Mobile Navigation Drawer */}
        {mobileMenuOpen && (
          <div className="lg:hidden bg-midnight-indigo text-white p-4 border-b border-white/10 z-40">
            <nav className="flex flex-col gap-1">
              {navGroups.map((g, idx) => (
                <div key={idx} className="mb-2">
                  <div className="text-[10px] uppercase font-bold text-white/40 mb-1">{g.group}</div>
                  {g.items.map((i) => (
                    <NavLink
                      key={i.path}
                      to={i.path}
                      onClick={() => setMobileMenuOpen(false)}
                      className="flex items-center gap-2 px-3 py-2 rounded text-xs text-white/80 hover:bg-white/10"
                    >
                      <i.icon className="w-4 h-4" />
                      <span>{i.name}</span>
                    </NavLink>
                  ))}
                </div>
              ))}
              <button
                onClick={() => {
                  setMobileMenuOpen(false);
                  navigate('/login');
                }}
                className="flex items-center gap-2 px-3 py-2 rounded text-xs text-red-300 hover:bg-red-500/20 mt-2"
              >
                <LogOut className="w-4 h-4" />
                <span>Sign Out</span>
              </button>
            </nav>
          </div>
        )}

        {/* Main Content Area */}
        <main className="flex-1 p-4 sm:p-6 lg:p-8 max-w-7xl w-full mx-auto">{children}</main>
      </div>
    </div>
  );
};
