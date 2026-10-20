import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { useAppData } from '../../context/useAppData';
import { useRolePreview } from '../../context/useRolePreview';
import { PlusCircle, Upload, MapPin, CheckCircle2, ArrowRight } from 'lucide-react';

export const CitizenSubmitComplaintPage: React.FC = () => {
  const navigate = useNavigate();
  const { addComplaint, departments } = useAppData();
  const { currentUser } = useRolePreview();

  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [category, setCategory] = useState('Road Infrastructure');
  const [departmentId, setDepartmentId] = useState(departments[0]?.id || 'dept_pwd');
  const [locationAddress, setLocationAddress] = useState('');
  const [wardZone, setWardZone] = useState('Ward 24 - South Delhi');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submittedRef, setSubmittedRef] = useState<string | null>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!title || !description || !locationAddress) {
      alert('Please complete all required fields.');
      return;
    }

    setIsSubmitting(true);
    setTimeout(() => {
      const selectedDept = departments.find((d) => d.id === departmentId) || departments[0];

      const newComplaint = addComplaint({
        title,
        description,
        category,
        departmentId: selectedDept.id,
        departmentName: selectedDept.name,
        wardZone,
        locationAddress,
        status: 'submitted',
        citizenName: currentUser.name,
        citizenContactMasked: '+91 98******12',
        resolutionDueAt: new Date(Date.now() + 48 * 3600 * 1000).toISOString(),
      });

      setIsSubmitting(false);
      setSubmittedRef(newComplaint.trackingNumber);
    }, 400);
  };

  return (
    <div className="flex flex-col gap-6 max-w-3xl mx-auto">
      {/* Header Banner */}
      <div className="bg-surface-container p-6 rounded-lg border border-outline-variant/30 shadow-card flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <PlusCircle className="w-6 h-6 text-primary" />
            <h1 className="text-2xl font-bold font-display text-primary">Lodge Municipal Grievance</h1>
          </div>
          <p className="text-xs text-on-surface-variant max-w-xl mt-1">
            Report potholes, drainage overflows, hazardous electrical lines, or municipal sanitation delays directly to authorized line agencies.
          </p>
        </div>

        <span className="px-2.5 py-1 rounded bg-secondary text-white text-xs font-bold uppercase tracking-wider">
          Citizen Portal
        </span>
      </div>

      {submittedRef ? (
        <Card className="p-8 text-center flex flex-col items-center gap-4">
          <div className="w-14 h-14 rounded-full bg-emerald-100 text-emerald-700 flex items-center justify-center">
            <CheckCircle2 className="w-8 h-8" />
          </div>

          <h2 className="text-lg font-bold font-display text-primary">
            Grievance Registered Successfully
          </h2>
          <p className="text-xs text-on-surface-variant max-w-md leading-relaxed">
            Your complaint has been logged and assigned simulated reference docket{' '}
            <strong className="font-mono text-primary font-bold">{submittedRef}</strong>. AI automated
            triage has evaluated the record and dispatched notice to the zonal grievance desk.
          </p>

          <div className="flex items-center gap-3 mt-3">
            <Button
              size="sm"
              variant="outline"
              onClick={() => {
                setSubmittedRef(null);
                setTitle('');
                setDescription('');
                setLocationAddress('');
              }}
            >
              Submit Another Grievance
            </Button>
            <Button
              size="sm"
              variant="primary"
              icon={<ArrowRight className="w-3.5 h-3.5" />}
              onClick={() => navigate('/app/citizen/my-complaints')}
            >
              Track in My Complaints
            </Button>
          </div>
        </Card>
      ) : (
        <Card title="Grievance Particulars & Location Details">
          <form onSubmit={handleSubmit} className="flex flex-col gap-4 text-xs">
            <div>
              <label className="block font-semibold text-primary mb-1">
                Grievance Title / Short Summary <span className="text-error">*</span>
              </label>
              <input
                type="text"
                required
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="e.g. Deep pothole causing skids near Metro Pillar 142"
                className="w-full px-3 py-2 rounded border border-outline-variant/60 bg-surface-lowest"
              />
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block font-semibold text-primary mb-1">Civic Category</label>
                <select
                  value={category}
                  onChange={(e) => setCategory(e.target.value)}
                  className="w-full px-3 py-2 rounded border border-outline-variant/60 bg-surface-lowest"
                >
                  <option value="Road Infrastructure">Road Infrastructure</option>
                  <option value="Water & Sewage">Water & Sewage</option>
                  <option value="Electrical Hazard">Electrical Hazard</option>
                  <option value="Sanitation & Solid Waste">Sanitation & Solid Waste</option>
                  <option value="Street Lighting">Street Lighting</option>
                </select>
              </div>

              <div>
                <label className="block font-semibold text-primary mb-1">Line Agency</label>
                <select
                  value={departmentId}
                  onChange={(e) => setDepartmentId(e.target.value)}
                  className="w-full px-3 py-2 rounded border border-outline-variant/60 bg-surface-lowest"
                >
                  {departments.map((d) => (
                    <option key={d.id} value={d.id}>
                      {d.name} ({d.code})
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div>
              <label className="block font-semibold text-primary mb-1">
                Detailed Incident Description <span className="text-error">*</span>
              </label>
              <textarea
                rows={4}
                required
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Describe dimensions, duration of issue, proximity to landmarks, and danger to pedestrians..."
                className="w-full px-3 py-2 rounded border border-outline-variant/60 bg-surface-lowest"
              />
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block font-semibold text-primary mb-1">
                  Location / Street Landmark <span className="text-error">*</span>
                </label>
                <div className="relative">
                  <MapPin className="w-3.5 h-3.5 text-outline absolute left-3 top-1/2 -translate-y-1/2" />
                  <input
                    type="text"
                    required
                    value={locationAddress}
                    onChange={(e) => setLocationAddress(e.target.value)}
                    placeholder="Opposite Metro Pillar 142, Outer Ring Road"
                    className="w-full pl-9 pr-3 py-2 rounded border border-outline-variant/60 bg-surface-lowest"
                  />
                </div>
              </div>

              <div>
                <label className="block font-semibold text-primary mb-1">Municipal Ward</label>
                <input
                  type="text"
                  value={wardZone}
                  onChange={(e) => setWardZone(e.target.value)}
                  placeholder="Ward 24 - South Delhi"
                  className="w-full px-3 py-2 rounded border border-outline-variant/60 bg-surface-lowest"
                />
              </div>
            </div>

            {/* Photo Upload Sandbox */}
            <div className="p-4 rounded-lg border-2 border-dashed border-outline-variant/60 bg-surface-container-low/40 flex flex-col items-center justify-center text-center">
              <Upload className="w-8 h-8 text-outline mb-1" />
              <span className="font-semibold text-primary">Upload Photographic Evidence</span>
              <span className="text-[11px] text-on-surface-variant mt-0.5">
                PNG, JPG or WebP (Simulated computer vision triage analyzes uploaded damage)
              </span>
              <input type="file" className="text-[11px] text-on-surface-variant mt-2" />
            </div>

            <div className="flex items-center justify-end gap-2 pt-3 border-t border-outline-variant/20">
              <Button size="sm" variant="outline" type="button" onClick={() => navigate(-1)}>
                Cancel
              </Button>
              <Button size="sm" variant="primary" type="submit" disabled={isSubmitting}>
                {isSubmitting ? 'Registering Docket...' : 'Submit Grievance to Municipal Desk'}
              </Button>
            </div>
          </form>
        </Card>
      )}
    </div>
  );
};
