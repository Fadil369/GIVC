// Type definitions for GIVC Healthcare Platform (converted to JavaScript)
// This file contains JSDoc comments for IDE support and documentation

/**
 * @typedef {Object} User
 * @property {string} id
 * @property {string} email
 * @property {string} name
 * @property {UserRole} role
 * @property {Permission[]} permissions
 * @property {Date} [lastLogin]
 * @property {string} [avatar]
 * @property {string} [organization]
 * @property {string} [specialty]
 */

/**
 * @typedef {'admin'|'physician'|'nurse'|'technician'|'billing_specialist'|'compliance_officer'|'patient'} UserRole
 */

/**
 * @typedef {'read_medical_data'|'write_medical_data'|'delete_medical_data'|'access_ai_agents'|'manage_users'|'view_compliance'|'manage_billing'|'export_data'} Permission
 */

/**
 * @typedef {Object} MedicalFile
 * @property {string} id
 * @property {string} name
 * @property {MedicalFileType} type
 * @property {number} size
 * @property {Date} uploadedAt
 * @property {string} uploadedBy
 * @property {FileCategory} category
 * @property {ProcessingStatus} status
 * @property {string} [url]
 * @property {MedicalFileMetadata} [metadata]
 * @property {AnalysisResult[]} [analysisResults]
 * @property {ComplianceStatus} complianceStatus
 */

/**
 * @typedef {'dicom'|'lab_result'|'clinical_note'|'prescription'|'insurance_document'|'patient_record'|'imaging_report'|'pathology_report'} MedicalFileType
 */

/**
 * @typedef {'radiology'|'laboratory'|'clinical'|'administrative'|'billing'|'insurance'} FileCategory
 */

/**
 * @typedef {'uploading'|'queued'|'processing'|'completed'|'failed'|'requires_review'} ProcessingStatus
 */

/**
 * @typedef {Object} MedicalFileMetadata
 * @property {string} [patientId]
 * @property {Date} [studyDate]
 * @property {string} [modality]
 * @property {string} [bodyPart]
 * @property {string} [physician]
 * @property {string} [institution]
 * @property {string} [studyDescription]
 * @property {string} [seriesDescription]
 * @property {number} [imageCount]
 * @property {number[]} [pixelSpacing]
 * @property {number} [sliceThickness]
 */

/**
 * @typedef {Object} AnalysisResult
 * @property {string} id
 * @property {string} fileId
 * @property {AIAgentType} agentType
 * @property {number} confidence
 * @property {Finding[]} findings
 * @property {Recommendation[]} recommendations
 * @property {Date} processedAt
 * @property {number} processingTime
 * @property {string} version
 */

/**
 * @typedef {'dicom_analysis'|'lab_parser'|'clinical_decision'|'compliance_monitor'} AIAgentType
 */

/**
 * @typedef {Object} Finding
 * @property {FindingType} type
 * @property {string} description
 * @property {Severity} severity
 * @property {AnatomicalLocation} [location]
 * @property {Measurement[]} [measurements]
 * @property {number} confidence
 * @property {string} [icd10Code]
 * @property {string} [snomedCode]
 */

/**
 * @typedef {'abnormality'|'normal'|'critical'|'incidental'|'artifact'|'measurement'} FindingType
 */

/**
 * @typedef {'critical'|'high'|'medium'|'low'|'normal'} Severity
 */

/**
 * @typedef {Object} AnatomicalLocation
 * @property {string} region
 * @property {'left'|'right'|'bilateral'} [laterality]
 * @property {Object} [coordinates]
 * @property {number} coordinates.x
 * @property {number} coordinates.y
 * @property {number} [coordinates.z]
 */

/**
 * @typedef {Object} Measurement
 * @property {string} type
 * @property {number} value
 * @property {string} unit
 * @property {Object} [normalRange]
 * @property {number} normalRange.min
 * @property {number} normalRange.max
 */

/**
 * @typedef {Object} Recommendation
 * @property {RecommendationType} type
 * @property {string} description
 * @property {Priority} priority
 * @property {string} [timeframe]
 * @property {string} [followUp]
 * @property {string[]} [references]
 */

/**
 * @typedef {'immediate_action'|'follow_up'|'additional_testing'|'specialist_referral'|'medication_adjustment'|'lifestyle_modification'} RecommendationType
 */

/**
 * @typedef {'emergency'|'urgent'|'routine'|'when_convenient'} Priority
 */

/**
 * @typedef {Object} TriageAssessment
 * @property {string} id
 * @property {string} patientId
 * @property {Symptom[]} symptoms
 * @property {UrgencyLevel} urgencyLevel
 * @property {TriageRecommendation[]} recommendations
 * @property {number} [estimatedWaitTime]
 * @property {string} [specialtyRequired]
 * @property {Date} createdAt
 * @property {Date} [completedAt]
 */

/**
 * @typedef {Object} Symptom
 * @property {string} name
 * @property {number} severity - Scale 1-10
 * @property {string} duration
 * @property {'sudden'|'gradual'|'chronic'} onset
 * @property {string} [location]
 * @property {string} [character]
 * @property {string[]} [aggravatingFactors]
 * @property {string[]} [relievingFactors]
 */

/**
 * @typedef {'emergency'|'urgent'|'semi_urgent'|'standard'|'non_urgent'} UrgencyLevel
 */

/**
 * @typedef {Object} TriageRecommendation
 * @property {'immediate_care'|'scheduled_appointment'|'self_care'|'emergency_services'} type
 * @property {string} description
 * @property {string} timeframe
 * @property {string} [department]
 * @property {string} [provider]
 */

/**
 * @typedef {'compliant'|'non_compliant'|'under_review'|'requires_action'} ComplianceStatus
 */

/**
 * @typedef {Object} ComplianceEvent
 * @property {string} id
 * @property {ComplianceEventType} type
 * @property {ComplianceSeverity} severity
 * @property {string} description
 * @property {string} userId
 * @property {string} [resourceId]
 * @property {Date} timestamp
 * @property {boolean} resolved
 * @property {string} [resolution]
 * @property {Date} [resolvedAt]
 * @property {string} [resolvedBy]
 */

/**
 * @typedef {'unauthorized_access'|'data_export'|'failed_authentication'|'policy_violation'|'data_breach'|'audit_log_access'|'encryption_failure'|'retention_violation'} ComplianceEventType
 */

/**
 * @typedef {'critical'|'high'|'medium'|'low'|'informational'} ComplianceSeverity
 */

/**
 * @typedef {Object} BillingRecord
 * @property {string} id
 * @property {string} patientId
 * @property {Date} serviceDate
 * @property {string} provider
 * @property {string[]} icd10Codes
 * @property {string[]} cptCodes
 * @property {number} chargeAmount
 * @property {number} paidAmount
 * @property {InsuranceClaim} [insuranceClaim]
 * @property {BillingStatus} status
 * @property {Date} createdAt
 * @property {Date} updatedAt
 */

/**
 * @typedef {'draft'|'submitted'|'in_process'|'paid'|'denied'|'appealed'|'written_off'} BillingStatus
 */

/**
 * @typedef {Object} InsuranceClaim
 * @property {string} id
 * @property {string} payerId
 * @property {Date} submittedDate
 * @property {number} claimAmount
 * @property {number} [approvedAmount]
 * @property {string} [denialReason]
 * @property {ClaimStatus} status
 */

/**
 * @typedef {'pending'|'approved'|'denied'|'under_review'|'appealed'} ClaimStatus
 */

/**
 * @typedef {Object} ApiResponse
 * @template T
 * @property {boolean} success
 * @property {T} [data]
 * @property {Object} [error]
 * @property {string} error.code
 * @property {string} error.message
 * @property {*} [error.details]
 * @property {Date} timestamp
 * @property {string} requestId
 */

/**
 * @typedef {Object} PaginatedResponse
 * @template T
 * @extends ApiResponse<T[]>
 * @property {Object} pagination
 * @property {number} pagination.page
 * @property {number} pagination.limit
 * @property {number} pagination.total
 * @property {boolean} pagination.hasNext
 * @property {boolean} pagination.hasPrevious
 */

/**
 * @typedef {Object} DashboardMetrics
 * @property {number} totalFiles
 * @property {number} filesProcessedToday
 * @property {number} aiProcessingQueue
 * @property {number} complianceScore
 * @property {number} activeUsers
 * @property {number} systemUptime
 * @property {number} averageProcessingTime
 * @property {number} criticalAlerts
 */

/**
 * @typedef {Object} ChartData
 * @property {string[]} labels
 * @property {Object[]} datasets
 * @property {string} datasets[].label
 * @property {number[]} datasets[].data
 * @property {string} [datasets[].backgroundColor]
 * @property {string} [datasets[].borderColor]
 * @property {number} [datasets[].borderWidth]
 */

/**
 * @typedef {Object} AppError
 * @property {string} code
 * @property {string} message
 * @property {'low'|'medium'|'high'|'critical'} severity
 * @property {Date} timestamp
 * @property {string} [userId]
 * @property {Object} [context]
 */

/**
 * @typedef {Object} Notification
 * @property {string} id
 * @property {NotificationType} type
 * @property {string} title
 * @property {string} message
 * @property {NotificationSeverity} severity
 * @property {boolean} read
 * @property {Date} createdAt
 * @property {string} [actionUrl]
 * @property {string} [actionText]
 * @property {Date} [expiresAt]
 */

/**
 * @typedef {'system'|'security'|'compliance'|'processing'|'billing'|'user_action'} NotificationType
 */

/**
 * @typedef {'info'|'warning'|'error'|'success'} NotificationSeverity
 */

// Export constants for validation and defaults
export const USER_ROLES = ['admin', 'physician', 'nurse', 'technician', 'billing_specialist', 'compliance_officer', 'patient'];
export const PERMISSIONS = ['read_medical_data', 'write_medical_data', 'delete_medical_data', 'access_ai_agents', 'manage_users', 'view_compliance', 'manage_billing', 'export_data'];
export const MEDICAL_FILE_TYPES = ['dicom', 'lab_result', 'clinical_note', 'prescription', 'insurance_document', 'patient_record', 'imaging_report', 'pathology_report'];
export const FILE_CATEGORIES = ['radiology', 'laboratory', 'clinical', 'administrative', 'billing', 'insurance'];
export const PROCESSING_STATUSES = ['uploading', 'queued', 'processing', 'completed', 'failed', 'requires_review'];
export const URGENCY_LEVELS = ['emergency', 'urgent', 'semi_urgent', 'standard', 'non_urgent'];
export const COMPLIANCE_STATUSES = ['compliant', 'non_compliant', 'under_review', 'requires_action'];
