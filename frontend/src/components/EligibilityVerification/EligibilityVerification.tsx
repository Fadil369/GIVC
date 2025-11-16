/**
 * GIVC Healthcare Platform - Eligibility Verification Component
 * Dr. Al Fadil (BRAINSAIT LTD) - RCM Accredited
 *
 * Multi-step wizard for checking patient insurance eligibility
 * Integrates with NPHIES and payer systems via FastAPI backend
 */

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '@/hooks/useAuth';
import { OasisApi } from '@/services/oasisApi';
import type { EligibilityCheckRequest, EligibilityResponse } from '@/services/oasisApi';

// Initialize API client
const api = new OasisApi();

interface FormData {
  memberId: string;
  payerId: string;
  serviceDate: string;
  patientName: string;
  patientGender: string;
  patientDob: string;
}

const steps = [
  { id: 0, nameAr: 'العضو والدافع', nameEn: 'Member & Payer' },
  { id: 1, nameAr: 'تفاصيل الخدمة', nameEn: 'Service Details' },
  { id: 2, nameAr: 'بيانات المريض', nameEn: 'Patient (Optional)' },
  { id: 3, nameAr: 'المراجعة والإرسال', nameEn: 'Review & Submit' }
];

const EligibilityVerification = () => {
  const { user } = useAuth();
  const [currentStep, setCurrentStep] = useState(0);
  const [formData, setFormData] = useState<FormData>({
    memberId: '',
    payerId: '',
    serviceDate: new Date().toISOString().split('T')[0],
    patientName: '',
    patientGender: '',
    patientDob: ''
  });
  const [result, setResult] = useState<EligibilityResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const nextStep = () => setCurrentStep((prev) => Math.min(prev + 1, steps.length - 1));
  const prevStep = () => setCurrentStep((prev) => Math.max(prev - 1, 0));

  const submitEligibility = async () => {
    setLoading(true);
    setError(null);
    try {
      const request: EligibilityCheckRequest = {
        member_id: formData.memberId,
        payer_id: formData.payerId,
        service_date: formData.serviceDate
      };

      const data = await api.checkEligibility(request);
      setResult(data);
      nextStep();
    } catch (err) {
      setError((err as Error).message || 'فشل التحقق من الأهلية / Eligibility check failed');
    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => {
    setCurrentStep(0);
    setFormData({
      memberId: '',
      payerId: '',
      serviceDate: new Date().toISOString().split('T')[0],
      patientName: '',
      patientGender: '',
      patientDob: ''
    });
    setResult(null);
    setError(null);
  };

  // Render the horizontal stepper header
  const renderStepper = () => (
    <div className="flex justify-between mb-8 px-4">
      {steps.map((step, index) => {
        const isActive = index === currentStep;
        const isCompleted = index < currentStep;
        return (
          <div key={step.id} className="flex-1 text-center relative">
            {/* Connection Line */}
            {index < steps.length - 1 && (
              <div className={`absolute top-4 left-1/2 w-full h-0.5 ${
                isCompleted ? 'bg-green-500' : 'bg-gray-200'
              }`} style={{ zIndex: 0 }} />
            )}

            {/* Step Circle */}
            <div className="relative z-10 flex flex-col items-center">
              <motion.div
                initial={false}
                animate={{
                  scale: isActive ? 1.1 : 1,
                  backgroundColor: isCompleted ? '#10b981' : isActive ? '#3b82f6' : '#e5e7eb'
                }}
                className={`w-10 h-10 rounded-full flex items-center justify-center mb-2 shadow-md ${
                  isCompleted || isActive ? 'text-white' : 'text-gray-600'
                }`}
              >
                {isCompleted ? '✓' : index + 1}
              </motion.div>
              <div className="text-center">
                <span className={`block text-sm font-semibold ${
                  isActive ? 'text-blue-700' : 'text-gray-600'
                }`}>
                  {step.nameAr}
                </span>
                <span className={`block text-xs ${
                  isActive ? 'text-blue-600' : 'text-gray-500'
                }`}>
                  {step.nameEn}
                </span>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );

  const renderStepContent = () => {
    switch (currentStep) {
      case 0:
        return (
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            className="space-y-6"
          >
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                رقم العضو / Member ID *
              </label>
              <input
                type="text"
                name="memberId"
                required
                value={formData.memberId}
                onChange={handleChange}
                placeholder="e.g., MEM123456789"
                className="block w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                معرف شركة التأمين / Payer ID *
              </label>
              <select
                name="payerId"
                required
                value={formData.payerId}
                onChange={handleChange}
                className="block w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
              >
                <option value="">اختر شركة التأمين / Select Payer...</option>
                <option value="bupa">Bupa Arabia / بوبا العربية</option>
                <option value="globemed">GlobeMed / جلوبميد</option>
                <option value="tawuniya">Tawuniya / التعاونية</option>
                <option value="medgulf">MedGulf / الخليج للتأمين</option>
                <option value="alrajhi">Al Rajhi Takaful / الراجحي تكافل</option>
                <option value="saico">SAICO / سايكو</option>
              </select>
            </div>
          </motion.div>
        );
      case 1:
        return (
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            className="space-y-6"
          >
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                تاريخ الخدمة / Service Date *
              </label>
              <input
                type="date"
                name="serviceDate"
                required
                value={formData.serviceDate}
                onChange={handleChange}
                className="block w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
              />
              <p className="mt-2 text-xs text-gray-500">
                حدد تاريخ الخدمة المتوقع للتحقق من الأهلية
                <br />
                Provide the date of service the patient will receive
              </p>
            </div>
          </motion.div>
        );
      case 2:
        return (
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            className="space-y-6"
          >
            <p className="text-sm text-gray-600 mb-4">
              المعلومات التالية اختيارية ولكنها قد تساعد في التحقق الدقيق
              <br />
              The following information is optional but may help with accurate verification
            </p>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                اسم المريض / Patient Name
              </label>
              <input
                type="text"
                name="patientName"
                value={formData.patientName}
                onChange={handleChange}
                placeholder="e.g., Ahmed Mohammed Ali"
                className="block w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                الجنس / Patient Gender
              </label>
              <select
                name="patientGender"
                value={formData.patientGender}
                onChange={handleChange}
                className="block w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
              >
                <option value="">اختر... / Select…</option>
                <option value="male">ذكر / Male</option>
                <option value="female">أنثى / Female</option>
                <option value="other">آخر / Other</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                تاريخ الميلاد / Patient DOB
              </label>
              <input
                type="date"
                name="patientDob"
                value={formData.patientDob}
                onChange={handleChange}
                className="block w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
              />
            </div>
          </motion.div>
        );
      case 3:
        return (
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            className="space-y-6"
          >
            {!result ? (
              <>
                <h3 className="text-xl font-semibold text-gray-800 mb-4">
                  مراجعة المعلومات / Review Information
                </h3>
                <div className="bg-gray-50 rounded-lg p-6 space-y-3 border border-gray-200">
                  <div className="flex justify-between py-2 border-b border-gray-200">
                    <span className="font-medium text-gray-700">رقم العضو / Member ID:</span>
                    <span className="text-gray-900">{formData.memberId}</span>
                  </div>
                  <div className="flex justify-between py-2 border-b border-gray-200">
                    <span className="font-medium text-gray-700">شركة التأمين / Payer ID:</span>
                    <span className="text-gray-900">{formData.payerId}</span>
                  </div>
                  <div className="flex justify-between py-2 border-b border-gray-200">
                    <span className="font-medium text-gray-700">تاريخ الخدمة / Service Date:</span>
                    <span className="text-gray-900">{formData.serviceDate}</span>
                  </div>
                  {formData.patientName && (
                    <div className="flex justify-between py-2 border-b border-gray-200">
                      <span className="font-medium text-gray-700">اسم المريض / Patient Name:</span>
                      <span className="text-gray-900">{formData.patientName}</span>
                    </div>
                  )}
                  {formData.patientGender && (
                    <div className="flex justify-between py-2 border-b border-gray-200">
                      <span className="font-medium text-gray-700">الجنس / Gender:</span>
                      <span className="text-gray-900">{formData.patientGender}</span>
                    </div>
                  )}
                  {formData.patientDob && (
                    <div className="flex justify-between py-2">
                      <span className="font-medium text-gray-700">تاريخ الميلاد / DOB:</span>
                      <span className="text-gray-900">{formData.patientDob}</span>
                    </div>
                  )}
                </div>
                <div className="pt-4">
                  <button
                    disabled={loading}
                    onClick={submitEligibility}
                    className="w-full px-6 py-4 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-semibold shadow-md disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
                  >
                    {loading ? (
                      <>
                        <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                        جاري التحقق... / Submitting…
                      </>
                    ) : (
                      'إرسال طلب التحقق / Submit Eligibility Check'
                    )}
                  </button>
                </div>
              </>
            ) : (
              <div className="space-y-6">
                <h2 className="text-2xl font-bold text-gray-900 mb-4">
                  نتيجة التحقق / Verification Result
                </h2>
                <div className={`p-6 border-2 rounded-lg ${
                  result.eligible
                    ? 'bg-green-50 border-green-300'
                    : 'bg-red-50 border-red-300'
                }`}>
                  <div className="flex items-center mb-4">
                    <div className={`w-12 h-12 rounded-full flex items-center justify-center mr-4 ${
                      result.eligible ? 'bg-green-500' : 'bg-red-500'
                    }`}>
                      <span className="text-white text-2xl">
                        {result.eligible ? '✓' : '✗'}
                      </span>
                    </div>
                    <div>
                      <h3 className={`text-xl font-bold ${
                        result.eligible ? 'text-green-800' : 'text-red-800'
                      }`}>
                        {result.eligible ? 'مؤهل / Eligible' : 'غير مؤهل / Ineligible'}
                      </h3>
                      <p className="text-sm text-gray-600">
                        العضو: {result.member_id}
                      </p>
                    </div>
                  </div>
                  <div className="space-y-3 border-t pt-4">
                    <div className="flex justify-between">
                      <span className="font-semibold text-gray-700">حالة التغطية / Coverage Status:</span>
                      <span className="text-gray-900">{result.coverage_status || 'N/A'}</span>
                    </div>
                    {result.message && (
                      <div className="bg-white p-4 rounded-md border border-gray-200">
                        <p className="font-semibold text-gray-700 mb-1">رسالة / Message:</p>
                        <p className="text-gray-900">{result.message}</p>
                      </div>
                    )}
                    {result.benefits && (
                      <div className="bg-white p-4 rounded-md border border-gray-200">
                        <p className="font-semibold text-gray-700 mb-2">المزايا / Benefits:</p>
                        <pre className="text-xs text-gray-700 overflow-x-auto">
                          {JSON.stringify(result.benefits, null, 2)}
                        </pre>
                      </div>
                    )}
                  </div>
                </div>
                <button
                  onClick={resetForm}
                  className="w-full px-6 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors font-semibold"
                >
                  تحقق جديد / New Check
                </button>
              </div>
            )}
          </motion.div>
        );
      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-4xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white shadow-xl rounded-2xl border border-gray-200 overflow-hidden"
        >
          {/* Header */}
          <div className="bg-gradient-to-r from-blue-600 to-blue-700 px-8 py-6">
            <h1 className="text-3xl font-bold text-white mb-2">
              التحقق من الأهلية
            </h1>
            <p className="text-blue-100">
              Eligibility Verification • NPHIES & Payer Integration
            </p>
          </div>

          {/* Content */}
          <div className="p-8">
            {renderStepper()}

            <AnimatePresence mode="wait">
              <div key={currentStep}>
                {renderStepContent()}
              </div>
            </AnimatePresence>

            {/* Navigation Buttons */}
            {!result && currentStep < 3 && (
              <div className="flex justify-between mt-8 pt-6 border-t border-gray-200">
                <button
                  onClick={prevStep}
                  disabled={currentStep === 0}
                  className="px-6 py-3 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 disabled:opacity-50 disabled:cursor-not-allowed font-semibold transition-colors"
                >
                  السابق / Previous
                </button>
                <button
                  onClick={nextStep}
                  disabled={
                    (currentStep === 0 && (!formData.memberId || !formData.payerId)) ||
                    (currentStep === 1 && !formData.serviceDate)
                  }
                  className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed font-semibold transition-colors"
                >
                  التالي / Next
                </button>
              </div>
            )}

            {/* Error Display */}
            {error && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className="mt-6 p-4 bg-red-50 border border-red-200 rounded-lg"
              >
                <p className="text-red-700 text-sm font-medium flex items-center">
                  <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                  </svg>
                  {error}
                </p>
              </motion.div>
            )}
          </div>

          {/* Footer */}
          <div className="bg-gray-50 px-8 py-4 border-t border-gray-200">
            <p className="text-xs text-gray-600 text-center">
              جميع البيانات محمية وفقًا لمعايير HIPAA و PDPL
              <br />
              All data is protected in accordance with HIPAA & PDPL standards
            </p>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default EligibilityVerification;
