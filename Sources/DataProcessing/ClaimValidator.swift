import Foundation
import Logging

/// Service for validating claims for quality and compliance
public actor ClaimValidator {
    private let logger: Logger

    public init(logger: Logger = Logger(label: "com.brainsait.claimlinc.validator")) {
        self.logger = logger
    }

    // MARK: - Public API

    /// Validate a single claim
    public func validate(_ claim: StandardClaim) async -> ValidationResult {
        logger.info("Validating claim: \(claim.claimId)")

        var errors: [ValidationError] = []
        var warnings: [ValidationWarning] = []
        var recommendations: [String] = []

        // Run all validation checks
        errors.append(contentsOf: await validateRequiredFields(claim))
        errors.append(contentsOf: await validateDataFormats(claim))
        errors.append(contentsOf: await validateBusinessRules(claim))
        errors.append(contentsOf: await validateCompliance(claim))

        warnings.append(contentsOf: await checkDataQuality(claim))

        // Calculate quality metrics
        let metrics = await calculateQualityMetrics(claim, errors: errors, warnings: warnings)

        // Generate recommendations
        recommendations = await generateRecommendations(claim, errors: errors, warnings: warnings)

        // Determine overall status
        let validationStatus = determineValidationStatus(errors: errors, warnings: warnings)
        let complianceStatus = determineComplianceStatus(errors: errors)

        // Calculate validation score (0-100)
        let validationScore = calculateValidationScore(errors: errors, warnings: warnings, metrics: metrics)

        let result = ValidationResult(
            claimId: claim.claimId,
            validationStatus: validationStatus,
            validationScore: validationScore,
            complianceStatus: complianceStatus,
            errors: errors,
            warnings: warnings,
            recommendations: recommendations,
            dataQualityMetrics: metrics
        )

        logger.info("Validation completed for claim: \(claim.claimId) - Status: \(validationStatus.rawValue), Score: \(validationScore)")
        return result
    }

    /// Validate multiple claims in batch
    public func validateBatch(_ claims: [StandardClaim]) async -> [ValidationResult] {
        logger.info("Batch validating \(claims.count) claims")

        return await withTaskGroup(of: (String, ValidationResult).self) { group in
            for claim in claims {
                group.addTask {
                    let result = await self.validate(claim)
                    return (claim.claimId, result)
                }
            }

            var results: [ValidationResult] = []
            for await (_, result) in group {
                results.append(result)
            }
            return results
        }
    }

    // MARK: - Validation Checks

    private func validateRequiredFields(_ claim: StandardClaim) async -> [ValidationError] {
        var errors: [ValidationError] = []

        // Claim ID
        if claim.claimId.isEmpty || claim.claimId == "UNKNOWN" {
            errors.append(ValidationError(
                code: "REQ-001",
                field: "claimId",
                message: "Claim ID is required",
                severity: .critical,
                category: .missingData
            ))
        }

        // Provider
        if claim.provider.name.isEmpty {
            errors.append(ValidationError(
                code: "REQ-002",
                field: "provider.name",
                message: "Provider name is required",
                severity: .critical,
                category: .missingData
            ))
        }

        if claim.provider.code.isEmpty {
            errors.append(ValidationError(
                code: "REQ-003",
                field: "provider.code",
                message: "Provider code is required",
                severity: .high,
                category: .missingData
            ))
        }

        // Patient
        if claim.patient.memberId.isEmpty {
            errors.append(ValidationError(
                code: "REQ-004",
                field: "patient.memberId",
                message: "Patient member ID is required",
                severity: .critical,
                category: .missingData
            ))
        }

        if claim.patient.name.isEmpty {
            errors.append(ValidationError(
                code: "REQ-005",
                field: "patient.name",
                message: "Patient name is required",
                severity: .high,
                category: .missingData
            ))
        }

        // Claim Details
        if claim.claimDetails.totalAmount <= 0 {
            errors.append(ValidationError(
                code: "REQ-006",
                field: "claimDetails.totalAmount",
                message: "Total amount must be greater than zero",
                severity: .critical,
                category: .invalidFormat
            ))
        }

        if claim.claimDetails.diagnosisCodes.isEmpty {
            errors.append(ValidationError(
                code: "REQ-007",
                field: "claimDetails.diagnosisCodes",
                message: "At least one diagnosis code is required",
                severity: .high,
                category: .missingData
            ))
        }

        if claim.claimDetails.procedureCodes.isEmpty {
            errors.append(ValidationError(
                code: "REQ-008",
                field: "claimDetails.procedureCodes",
                message: "At least one procedure code is required",
                severity: .high,
                category: .missingData
            ))
        }

        return errors
    }

    private func validateDataFormats(_ claim: StandardClaim) async -> [ValidationError] {
        var errors: [ValidationError] = []

        // Validate National ID format (10 digits for Saudi Arabia)
        if let nationalId = claim.patient.nationalId {
            if !nationalId.matches(pattern: "^[0-9]{10}$") {
                errors.append(ValidationError(
                    code: "FMT-001",
                    field: "patient.nationalId",
                    message: "National ID must be 10 digits",
                    severity: .medium,
                    category: .invalidFormat
                ))
            }
        }

        // Validate diagnosis codes (ICD-10 format)
        for (index, code) in claim.claimDetails.diagnosisCodes.enumerated() {
            if !code.matches(pattern: "^[A-Z][0-9]{2}(\\.[0-9]{1,2})?$") {
                errors.append(ValidationError(
                    code: "FMT-002",
                    field: "claimDetails.diagnosisCodes[\(index)]",
                    message: "Invalid ICD-10 diagnosis code format: \(code)",
                    severity: .medium,
                    category: .invalidFormat
                ))
            }
        }

        // Validate service date is not in the future
        if claim.claimDetails.serviceDate > Date() {
            errors.append(ValidationError(
                code: "FMT-003",
                field: "claimDetails.serviceDate",
                message: "Service date cannot be in the future",
                severity: .high,
                category: .invalidFormat
            ))
        }

        // Validate service date is not too old (e.g., > 1 year)
        let oneYearAgo = Calendar.current.date(byAdding: .year, value: -1, to: Date()) ?? Date()
        if claim.claimDetails.serviceDate < oneYearAgo {
            errors.append(ValidationError(
                code: "FMT-004",
                field: "claimDetails.serviceDate",
                message: "Service date is more than 1 year old",
                severity: .medium,
                category: .compliance
            ))
        }

        return errors
    }

    private func validateBusinessRules(_ claim: StandardClaim) async -> [ValidationError] {
        var errors: [ValidationError] = []

        // Validate total amount matches sum of procedures
        let proceduresTotal = claim.claimDetails.procedureCodes.reduce(Decimal(0)) { total, procedure in
            let quantity = Decimal(procedure.quantity)
            let unitPrice = procedure.unitPrice ?? 0
            return total + (quantity * unitPrice)
        }

        if proceduresTotal > 0 && abs(proceduresTotal.doubleValue - claim.claimDetails.totalAmount.doubleValue) > 0.01 {
            errors.append(ValidationError(
                code: "BUS-001",
                field: "claimDetails.totalAmount",
                message: "Total amount (\(claim.claimDetails.totalAmount)) does not match sum of procedures (\(proceduresTotal))",
                severity: .medium,
                category: .businessRule
            ))
        }

        // Validate reasonable claim amounts (e.g., not > 1,000,000 SAR)
        if claim.claimDetails.totalAmount > 1_000_000 {
            errors.append(ValidationError(
                code: "BUS-002",
                field: "claimDetails.totalAmount",
                message: "Claim amount exceeds maximum limit (1,000,000 SAR)",
                severity: .high,
                category: .businessRule
            ))
        }

        return errors
    }

    private func validateCompliance(_ claim: StandardClaim) async -> [ValidationError] {
        var errors: [ValidationError] = []

        // Saudi Health Insurance regulations require claims to be submitted within 30 days
        let thirtyDaysAgo = Calendar.current.date(byAdding: .day, value: -30, to: Date()) ?? Date()
        if claim.claimDetails.serviceDate < thirtyDaysAgo && claim.submission.timestamp > Date() {
            errors.append(ValidationError(
                code: "CMP-001",
                field: "submission.timestamp",
                message: "Claim submitted more than 30 days after service date (Saudi regulation)",
                severity: .high,
                category: .compliance
            ))
        }

        // HIPAA/PDPL compliance - ensure no sensitive data is logged
        // (This is handled at the application level, not in validation)

        return errors
    }

    private func checkDataQuality(_ claim: StandardClaim) async -> [ValidationWarning] {
        var warnings: [ValidationWarning] = []

        // Check for missing optional but recommended fields
        if claim.patient.dateOfBirth == nil {
            warnings.append(ValidationWarning(
                code: "QUA-001",
                field: "patient.dateOfBirth",
                message: "Patient date of birth is missing",
                recommendation: "Including date of birth improves claim processing accuracy"
            ))
        }

        if claim.patient.gender == nil || claim.patient.gender == .unknown {
            warnings.append(ValidationWarning(
                code: "QUA-002",
                field: "patient.gender",
                message: "Patient gender is missing or unknown",
                recommendation: "Including gender is recommended for accurate processing"
            ))
        }

        if claim.provider.licenseNumber == nil {
            warnings.append(ValidationWarning(
                code: "QUA-003",
                field: "provider.licenseNumber",
                message: "Provider license number is missing",
                recommendation: "Including license number helps verify provider credentials"
            ))
        }

        // Check for procedure descriptions
        let missingDescriptions = claim.claimDetails.procedureCodes.filter { $0.description == nil }
        if !missingDescriptions.isEmpty {
            warnings.append(ValidationWarning(
                code: "QUA-004",
                field: "claimDetails.procedureCodes",
                message: "\(missingDescriptions.count) procedure(s) missing descriptions",
                recommendation: "Adding procedure descriptions improves claim clarity"
            ))
        }

        return warnings
    }

    // MARK: - Metrics Calculation

    private func calculateQualityMetrics(
        _ claim: StandardClaim,
        errors: [ValidationError],
        warnings: [ValidationWarning]
    ) async -> DataQualityMetrics {
        // Completeness: percentage of non-null optional fields
        var completenessScore = 100.0
        if claim.patient.dateOfBirth == nil { completenessScore -= 10 }
        if claim.patient.gender == nil { completenessScore -= 10 }
        if claim.patient.nationalId == nil { completenessScore -= 10 }
        if claim.provider.licenseNumber == nil { completenessScore -= 10 }
        if claim.payer.policyNumber == nil { completenessScore -= 10 }

        // Accuracy: based on format validation errors
        let formatErrors = errors.filter { $0.category == .invalidFormat }
        let accuracyScore = max(0, 100.0 - Double(formatErrors.count) * 20.0)

        // Consistency: based on business rule violations
        let businessRuleErrors = errors.filter { $0.category == .businessRule }
        let consistencyScore = max(0, 100.0 - Double(businessRuleErrors.count) * 25.0)

        // Validity: based on required field validation
        let missingDataErrors = errors.filter { $0.category == .missingData }
        let validityScore = max(0, 100.0 - Double(missingDataErrors.count) * 20.0)

        // Timeliness: based on submission timing
        let complianceErrors = errors.filter { $0.category == .compliance }
        let timelinessScore = max(0, 100.0 - Double(complianceErrors.count) * 30.0)

        return DataQualityMetrics(
            completeness: completenessScore,
            accuracy: accuracyScore,
            consistency: consistencyScore,
            validity: validityScore,
            timeliness: timelinessScore
        )
    }

    private func calculateValidationScore(
        errors: [ValidationError],
        warnings: [ValidationWarning],
        metrics: DataQualityMetrics
    ) -> Double {
        // Start with quality score
        var score = metrics.overallScore

        // Deduct points for errors based on severity
        for error in errors {
            switch error.severity {
            case .critical:
                score -= 20.0
            case .high:
                score -= 10.0
            case .medium:
                score -= 5.0
            case .low:
                score -= 2.0
            }
        }

        // Deduct small points for warnings
        score -= Double(warnings.count) * 1.0

        return max(0, min(100, score))
    }

    private func determineValidationStatus(
        errors: [ValidationError],
        warnings: [ValidationWarning]
    ) -> ValidationResult.ValidationStatus {
        let criticalErrors = errors.filter { $0.severity == .critical }
        let highErrors = errors.filter { $0.severity == .high }

        if !criticalErrors.isEmpty {
            return .failed
        } else if !highErrors.isEmpty {
            return .requiresReview
        } else if !errors.isEmpty || !warnings.isEmpty {
            return .warning
        } else {
            return .passed
        }
    }

    private func determineComplianceStatus(
        errors: [ValidationError]
    ) -> ValidationResult.ComplianceStatus {
        let complianceErrors = errors.filter { $0.category == .compliance }
        let criticalComplianceErrors = complianceErrors.filter { $0.severity == .critical || $0.severity == .high }

        if !criticalComplianceErrors.isEmpty {
            return .nonCompliant
        } else if !complianceErrors.isEmpty {
            return .partiallyCompliant
        } else {
            return .compliant
        }
    }

    private func generateRecommendations(
        _ claim: StandardClaim,
        errors: [ValidationError],
        warnings: [ValidationWarning]
    ) async -> [String] {
        var recommendations: [String] = []

        // Add recommendations based on errors
        if errors.contains(where: { $0.category == .missingData }) {
            recommendations.append("Complete all required fields to ensure claim acceptance")
        }

        if errors.contains(where: { $0.category == .invalidFormat }) {
            recommendations.append("Verify data formats match Saudi health insurance standards (ICD-10, etc.)")
        }

        if errors.contains(where: { $0.category == .compliance }) {
            recommendations.append("Submit claims within 30 days of service date per Saudi regulations")
        }

        if errors.contains(where: { $0.category == .businessRule }) {
            recommendations.append("Verify claim amounts and ensure procedure totals match")
        }

        // Add recommendations from warnings
        for warning in warnings {
            if let rec = warning.recommendation {
                recommendations.append(rec)
            }
        }

        return recommendations
    }
}

// MARK: - String Extension for Regex

private extension String {
    func matches(pattern: String) -> Bool {
        guard let regex = try? NSRegularExpression(pattern: pattern, options: []) else {
            return false
        }
        let range = NSRange(location: 0, length: self.utf16.count)
        return regex.firstMatch(in: self, options: [], range: range) != nil
    }
}

// MARK: - Decimal Extension

private extension Decimal {
    var doubleValue: Double {
        return NSDecimalNumber(decimal: self).doubleValue
    }
}
