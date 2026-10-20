import React, { useState } from 'react';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { MOCK_NOTIFICATIONS } from '../mock/data';
import type { NotificationItem } from '../types';
import { AlertTriangle, Info, CheckCircle2, CheckCheck } from 'lucide-react';

export const NotificationsPage: React.FC = () => {
  const [notifications, setNotifications] = useState<NotificationItem[]>(MOCK_NOTIFICATIONS);

  const markAllRead = () => {
    setNotifications((prev) => prev.map((n) => ({ ...n, read: true })));
  };

  const getIcon = (type: NotificationItem['type']) => {
    switch (type) {
      case 'alert':
      case 'urgent':
        return <AlertTriangle className="w-4 h-4 text-error" />;
      case 'success':
        return <CheckCircle2 className="w-4 h-4 text-emerald-600" />;
      case 'info':
      default:
        return <Info className="w-4 h-4 text-primary" />;
    }
  };

  return (
    <div className="flex flex-col gap-6 max-w-4xl mx-auto">
      <div className="bg-surface-container p-6 rounded-lg border border-outline-variant/30 shadow-card flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold font-display text-primary">System Notifications</h1>
          <p className="text-xs text-on-surface-variant max-w-xl mt-1">
            Real-time alerts, HITL triage mandates, and municipal escalations.
          </p>
        </div>
        <Button size="sm" variant="outline" icon={<CheckCheck className="w-3.5 h-3.5" />} onClick={markAllRead}>
          Mark All Read
        </Button>
      </div>

      <Card>
        <div className="divide-y divide-outline-variant/20">
          {notifications.map((n) => (
            <div
              key={n.id}
              className={`py-3.5 px-4 flex items-start gap-3 rounded transition-colors ${
                !n.read ? 'bg-secondary/5 font-medium' : ''
              }`}
            >
              <div className="p-2 rounded-full bg-surface-container shrink-0 mt-0.5">
                {getIcon(n.type)}
              </div>
              <div className="flex flex-col flex-1">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-primary">{n.title}</span>
                  <span className="text-[10px] text-on-surface-variant">Just now</span>
                </div>
                <p className="text-xs text-on-surface-variant mt-0.5">{n.message}</p>
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
};
