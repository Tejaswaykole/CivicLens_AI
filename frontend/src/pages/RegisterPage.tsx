import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useNavigate, Link } from 'react-router-dom';
import { Button } from '../components/ui/Button';
import { User, Mail, Lock, Phone, ArrowRight } from 'lucide-react';
import { useRolePreview } from '../context/useRolePreview';

const registerSchema = z
  .object({
    fullName: z.string().min(2, 'Full name must be at least 2 characters'),
    email: z.string().email('Please enter a valid email address'),
    phone: z.string().min(10, 'Phone number must be at least 10 digits'),
    password: z.string().min(6, 'Password must be at least 6 characters'),
    confirmPassword: z.string(),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: "Passwords don't match",
    path: ['confirmPassword'],
  });

type RegisterFormData = z.infer<typeof registerSchema>;

export const RegisterPage: React.FC = () => {
  const navigate = useNavigate();
  const { setRole } = useRolePreview();

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
  });

  const onSubmit = () => {
    setRole('citizen');
    navigate('/app/dashboard');
  };

  return (
    <div className="min-h-screen bg-surface-container-high/40 flex items-center justify-center p-4">
      <div className="w-full max-w-md bg-surface-lowest rounded-xl shadow-card border border-outline-variant/40 p-8 flex flex-col gap-6">
        <div className="flex flex-col items-center text-center">
          <div className="w-12 h-12 rounded-lg bg-midnight-indigo text-white font-bold font-display text-xl flex items-center justify-center shadow-sm mb-3">
            CL
          </div>
          <h1 className="text-xl font-bold font-display text-primary">Citizen Registration</h1>
          <p className="text-xs text-on-surface-variant mt-1">
            Register to lodge civic complaints, track repair status, and receive SMS alerts
          </p>
        </div>

        <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-3">
          <div>
            <label className="block text-xs font-semibold text-primary mb-1">Full Name</label>
            <div className="relative">
              <User className="w-3.5 h-3.5 text-outline absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                {...register('fullName')}
                placeholder="Pooja Sharma"
                className="w-full pl-9 pr-3 py-2 text-xs rounded border border-outline-variant/60 bg-surface-lowest text-on-surface focus:outline-none focus:border-primary"
              />
            </div>
            {errors.fullName && (
              <span className="text-[11px] text-error mt-0.5 block">{errors.fullName.message}</span>
            )}
          </div>

          <div>
            <label className="block text-xs font-semibold text-primary mb-1">Email Address</label>
            <div className="relative">
              <Mail className="w-3.5 h-3.5 text-outline absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="email"
                {...register('email')}
                placeholder="citizen@example.com"
                className="w-full pl-9 pr-3 py-2 text-xs rounded border border-outline-variant/60 bg-surface-lowest text-on-surface focus:outline-none focus:border-primary"
              />
            </div>
            {errors.email && (
              <span className="text-[11px] text-error mt-0.5 block">{errors.email.message}</span>
            )}
          </div>

          <div>
            <label className="block text-xs font-semibold text-primary mb-1">Mobile Number</label>
            <div className="relative">
              <Phone className="w-3.5 h-3.5 text-outline absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="tel"
                {...register('phone')}
                placeholder="+91 98765 43210"
                className="w-full pl-9 pr-3 py-2 text-xs rounded border border-outline-variant/60 bg-surface-lowest text-on-surface focus:outline-none focus:border-primary"
              />
            </div>
            {errors.phone && (
              <span className="text-[11px] text-error mt-0.5 block">{errors.phone.message}</span>
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

          <div>
            <label className="block text-xs font-semibold text-primary mb-1">Confirm Password</label>
            <div className="relative">
              <Lock className="w-3.5 h-3.5 text-outline absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="password"
                {...register('confirmPassword')}
                className="w-full pl-9 pr-3 py-2 text-xs rounded border border-outline-variant/60 bg-surface-lowest text-on-surface focus:outline-none focus:border-primary"
              />
            </div>
            {errors.confirmPassword && (
              <span className="text-[11px] text-error mt-0.5 block">
                {errors.confirmPassword.message}
              </span>
            )}
          </div>

          <Button
            type="submit"
            className="w-full mt-2"
            disabled={isSubmitting}
            icon={<ArrowRight className="w-4 h-4" />}
          >
            Create Citizen Account
          </Button>
        </form>

        <div className="text-center text-xs text-on-surface-variant border-t border-outline-variant/20 pt-4">
          <span>Already registered? </span>
          <Link to="/login" className="text-secondary font-semibold hover:underline">
            Sign In
          </Link>
        </div>
      </div>
    </div>
  );
};
