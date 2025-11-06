import { useMemo, useState } from 'react';
import apiClient from '@/lib/api';
import type { LocaleMessages } from '@/types/dashboard';

type RiskLevel = 'low' | 'medium' | 'high';

interface ClaimSubmissionWorkspaceProps {
  messages: LocaleMessages;
  locale: 'en' | 'ar';
}

interface ClaimFormState {
  patientId: string;
  patientName: string;
  dob: string;
  claimNumber: string;
  serviceDate: string;
  payer: string;
  totalAmount: string;
  icdCode: string;
  cptCode: string;
}

const defaultState: ClaimFormState = {
  patientId: '',
  patientName: '',
  dob: '',
  claimNumber: '',
  serviceDate: '',
  payer: '',
  totalAmount: '',
  icdCode: '',
  cptCode: '',
};

export function ClaimSubmissionWorkspace({ messages, locale }: ClaimSubmissionWorkspaceProps) {
  const [formState, setFormState] = useState<ClaimFormState>(defaultState);
  const [submitting, setSubmitting] = useState(false);
  const [feedback, setFeedback] = useState<{ status: 'idle' | 'success' | 'error'; message?: string }>({ status: 'idle' });

  const riskLevel: RiskLevel = useMemo(() => {
    const amount = Number(formState.totalAmount) || 0;
    if (!formState.icdCode || !formState.cptCode) {
      return 'medium';
    }
    if (amount > 5000) {
      return 'high';
    }
    if (amount > 1500) {
      return 'medium';
    }
    return 'low';
  }, [formState.cptCode, formState.icdCode, formState.totalAmount]);

  const riskCopy: Record<RiskLevel, { label: string; colorClass: string; widthClass: string }> = {
    low: { label: messages.riskLow, colorClass: 'bg-emerald-500', widthClass: 'w-[20%]' },
    medium: { label: messages.riskMedium, colorClass: 'bg-amber-500', widthClass: 'w-[60%]' },
    high: { label: messages.riskHigh, colorClass: 'bg-rose-500', widthClass: 'w-[90%]' },
  };

  const handleChange = (field: keyof ClaimFormState) => (event: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setFormState((prev) => ({ ...prev, [field]: event.target.value }));
  };

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setSubmitting(true);
    setFeedback({ status: 'idle' });

    try {
      const claimPayload = {
        claim_data: {
          claimNumber: formState.claimNumber,
          icdCode: formState.icdCode,
          cptCode: formState.cptCode,
          totalAmount: Number(formState.totalAmount || 0),
        },
        patient_info: {
          patientId: formState.patientId,
          patientName: formState.patientName,
          dob: formState.dob,
        },
        provider_info: {
          payer: formState.payer,
          serviceDate: formState.serviceDate,
        },
      };

      await apiClient.submitClaimToNPHIES(claimPayload);

      await apiClient.submitToOASIS({
        patient_id: formState.patientId,
        claim_number: formState.claimNumber,
        service_date: formState.serviceDate,
        payer: formState.payer,
        diagnosis_codes: [formState.icdCode],
        procedure_codes: [formState.cptCode],
        total_amount: Number(formState.totalAmount || 0),
      });

      setFeedback({ status: 'success', message: messages.submitToPayer });
      setFormState(defaultState);
    } catch (error) {
      setFeedback({ status: 'error', message: (error as Error).message });
    } finally {
      setSubmitting(false);
    }
  };

  const direction = locale === 'ar' ? 'rtl' : 'ltr';

  return (
    <section dir={direction} className="space-y-6 rounded-2xl bg-white p-8 shadow-lg ring-1 ring-slate-100 dark:bg-slate-900 dark:ring-slate-800">
      <header className="space-y-2">
        <h2 className="text-2xl font-bold text-slate-900 dark:text-white">{messages.claimWorkspace}</h2>
        <p className="text-sm text-slate-500 dark:text-slate-400">{messages.submitClaim}</p>
      </header>

      <form onSubmit={handleSubmit} className="space-y-8">
        <div>
          <h3 className="text-lg font-semibold text-slate-800 dark:text-slate-200">{messages.patientInformation}</h3>
          <div className="mt-4 grid gap-4 md:grid-cols-3">
            <InputField id="patient-id" label="Patient ID" value={formState.patientId} onChange={handleChange('patientId')} required />
            <InputField id="patient-name" label="Patient Name" value={formState.patientName} onChange={handleChange('patientName')} required />
            <InputField id="dob" label="Date of Birth" type="date" value={formState.dob} onChange={handleChange('dob')} required />
          </div>
        </div>

        <div>
          <h3 className="text-lg font-semibold text-slate-800 dark:text-slate-200">{messages.claimDetails}</h3>
          <div className="mt-4 grid gap-4 md:grid-cols-4">
            <InputField id="claim-number" label="Claim Number" value={formState.claimNumber} onChange={handleChange('claimNumber')} required />
            <InputField id="service-date" label="Service Date" type="date" value={formState.serviceDate} onChange={handleChange('serviceDate')} required />
            <div className="flex flex-col gap-2">
              <label className="text-sm font-medium text-slate-600 dark:text-slate-300" htmlFor="payer">Payer</label>
              <select
                id="payer"
                className="h-12 rounded-lg border border-slate-200 bg-slate-50 px-4 text-slate-800 transition focus:border-sky-500 focus:outline-none focus:ring-2 focus:ring-sky-200 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-200 dark:focus:border-sky-400 dark:focus:ring-sky-500/40"
                value={formState.payer}
                onChange={handleChange('payer')}
                required
              >
                <option value="">Select a Payer</option>
                <option value="PAYER_A">Payer A</option>
                <option value="PAYER_B">Payer B</option>
                <option value="PAYER_C">Payer C</option>
              </select>
            </div>
            <InputField id="total-amount" label="Total Claim Amount" type="number" value={formState.totalAmount} onChange={handleChange('totalAmount')} required min="0" step="0.01" />
          </div>
        </div>

        <div>
          <h3 className="text-lg font-semibold text-slate-800 dark:text-slate-200">{messages.diagnosisProcedures}</h3>
          <div className="mt-4 grid gap-4 md:grid-cols-2">
            <InputField id="icd-code" label="ICD Code" placeholder="e.g., J45.0" value={formState.icdCode} onChange={handleChange('icdCode')} required />
            <InputField id="cpt-code" label="CPT Code" placeholder="e.g., 99213" value={formState.cptCode} onChange={handleChange('cptCode')} required />
          </div>
        </div>

        <div>
          <h3 className="text-lg font-semibold text-slate-800 dark:text-slate-200">{messages.denialRiskAssessment}</h3>
          <div className="mt-4 rounded-xl bg-sky-50 p-6 dark:bg-sky-900/40">
            <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
              <div>
                <p className="text-sm font-medium text-slate-500 dark:text-slate-400">Denial Risk Score</p>
                <p className={`text-2xl font-bold uppercase ${riskLevel === 'high' ? 'text-rose-600' : riskLevel === 'medium' ? 'text-amber-500' : 'text-emerald-500'}`}>
                  {riskCopy[riskLevel].label}
                </p>
              </div>
              <div className="w-full md:max-w-xs">
                <div className="h-3 rounded-full bg-slate-200 dark:bg-slate-700">
                  <div className={`${riskCopy[riskLevel].colorClass} ${riskCopy[riskLevel].widthClass} h-3 rounded-full transition-all`} />
                </div>
                <p className="mt-2 text-xs text-slate-500 dark:text-slate-400">
                  {riskLevel === 'low' && 'Low risk due to compliant coding and modest claim amount.'}
                  {riskLevel === 'medium' && 'Moderate risk. Review documentation before submission.'}
                  {riskLevel === 'high' && 'High risk. Attach supporting documents and escalate if needed.'}
                </p>
              </div>
            </div>
          </div>
        </div>

        {feedback.status !== 'idle' && (
          <div
            role="alert"
            className={`rounded-lg border p-4 text-sm ${feedback.status === 'success' ? 'border-emerald-200 bg-emerald-50 text-emerald-700 dark:border-emerald-800/70 dark:bg-emerald-900/30 dark:text-emerald-200' : 'border-rose-200 bg-rose-50 text-rose-700 dark:border-rose-800/70 dark:bg-rose-900/30 dark:text-rose-200'}`}
          >
            {feedback.message}
          </div>
        )}

        <button
          type="submit"
          disabled={submitting}
          className="flex h-12 w-full items-center justify-center rounded-lg bg-sky-600 text-white font-semibold transition hover:bg-sky-700 disabled:cursor-not-allowed disabled:bg-sky-400"
        >
          {submitting ? 'Submitting...' : messages.submitToPayer}
        </button>
      </form>
    </section>
  );
}

interface InputFieldProps {
  id: string;
  label: string;
  value: string;
  onChange: (event: React.ChangeEvent<HTMLInputElement>) => void;
  type?: string;
  required?: boolean;
  placeholder?: string;
  min?: string;
  step?: string;
}

function InputField({ id, label, value, onChange, type = 'text', required, placeholder, min, step }: InputFieldProps) {
  return (
    <label className="flex flex-col gap-2 text-sm font-medium text-slate-600 dark:text-slate-300" htmlFor={id}>
      {label}
      <input
        id={id}
        name={id}
        value={value}
        onChange={onChange}
        type={type}
        required={required}
        placeholder={placeholder}
        min={min}
        step={step}
        className="h-12 rounded-lg border border-slate-200 bg-white px-4 text-slate-800 transition focus:border-sky-500 focus:outline-none focus:ring-2 focus:ring-sky-200 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-200 dark:focus:border-sky-400 dark:focus:ring-sky-500/40"
      />
    </label>
  );
}
