import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useNavigate, Link } from 'react-router-dom';
import { Button } from '../components/ui/Button';
import { Lock, Mail, ArrowRight } from 'lucide-react';
import { useRolePreview } from '../context/useRolePreview';
import type { UserRole } from '../types';

const loginSchema = z.object({
  email: z.string().email('Please enter a valid government or citizen email address'),
  password: z.string().min(6, 'Password must be at least 6 characters long'),
  role: z.enum(['system_admin', 'grievance_officer', 'department_officer', 'citizen']),
});

type LoginFormData = z.infer<typeof loginSchema>;

export const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const { setRole } = useRolePreview();

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      email: 'ananya.sen@civiclens.gov.in',
      password: 'password123',
      role: 'system_admin',
    },
  });

  const onSubmit = (data: LoginFormData) => {
    setRole(data.role as UserRole);
    navigate('/app/dashboard');
  };

  return (
    <div className="min-h-screen bg-surface-container-high/40 flex items-center justify-center p-4">
      <div className="w-full max-w-md bg-surface-lowest rounded-xl shadow-card border border-outline-variant/40 p-8 flex flex-col gap-6">
        {/* Brand Header */}
        <div className="flex flex-col items-center text-center">
          <div className="w-12 h-12 rounded-lg bg-midnight-indigo text-white font-bold font-display text-xl flex items-center justify-center shadow-sm mb-3">
            CL
          </div>
          <h1 className="text-xl font-bold font-display text-primary">CivicLens AI</h1>
          <p className="text-xs text-on-surface-variant mt-1">
            Official Municipal Grievance & Triage Portal
          </p>
        </div>

        {/* Advisory */}
        <div className="p-3 rounded bg-surface-container border border-outline-variant/30 text-[11px] text-on-surface-variant leading-relaxed">
          <strong>Notice:</strong> This is a Phase 1 front-end demonstration environment. Select a
          role below to preview role-specific triage workstations.
        </div>

        {/* Login Form */}
        <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-4">
          <div>
            <label className="block text-xs font-semibold text-primary mb-1">
              Select Role Preview
            </label>
            <select
              {...register('role')}
              className="w-full px-3 py-2 text-xs rounded border border-outline-variant/60 bg-surface-lowest text-on-surface focus:outline-none focus:border-primary"
            >
              <option value="system_admin">System Administrator (IAS / HQ)</option>
              <option value="grievance_officer">Grievance Officer (Triage / HITL)</option>
              <option value="department_officer">Department Officer (PWD / Field)</option>
              <option value="citizen">Citizen (Public Portal)</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold text-primary mb-1">Email Address</label>
            <div className="relative">
              <Mail className="w-3.5 h-3.5 text-outline absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="email"
                {...register('email')}
                className="w-full pl-9 pr-3 py-2 text-xs rounded border border-outline-variant/60 bg-surface-lowest text-on-surface focus:outline-none focus:border-primary"
              />
            </div>
            {errors.email && (
              <span className="text-[11px] text-error mt-0.5 block">{errors.email.message}</span>
            )}
          </div>

          <div>
            <label className="block text-xs font-semibold text-primary mb-1">Password</label>
            <div className="relative">
              <Lock className="w-3.5 h-3.5 text-outline absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="password"
                {...register('password')}
                className="w-full pl-9 pr-3 py-2 text-xs rounded border border-outline-variant/60 bg-surface-lowest text-on-surface focus:outline-none focus:border-primary"
              />
            </div>
            {errors.password && (
              <span className="text-[11px] text-error mt-0.5 block">{errors.password.message}</span>
            )}
          </div>

          <Button
            type="submit"
            className="w-full mt-2"
            disabled={isSubmitting}
            icon={<ArrowRight className="w-4 h-4" />}
          >
            Access Dashboard
          </Button>
        </form>

        <div className="text-center text-xs text-on-surface-variant border-t border-outline-variant/20 pt-4">
          <span>Don't have an account? </span>
          <Link to="/register" className="text-secondary font-semibold hover:underline">
            Register as Citizen
          </Link>
        </div>
      </div>
    </div>
  );
};
