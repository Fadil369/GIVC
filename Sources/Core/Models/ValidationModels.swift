import Foundation

// MARK: - Validation Models

/// Result of claim validation
public struct ValidationResult: Codable, Sendable {
    public var claimId: String
    public var validationStatus: ValidationStatus
    public var validationScore: Double
    public var complianceStatus: ComplianceStatus
    public var errors: [ValidationError]
    public var warnings: [ValidationWarning]
    public var recommendations: [String]
    public var dataQualityMetrics: DataQualityMetrics

    public init(
        claimId: String,
        validationStatus: ValidationStatus,
        validationScore: Double,
        complianceStatus: ComplianceStatus,
        errors: [ValidationError] = [],
        warnings: [ValidationWarning] = [],
        recommendations: [String] = [],
        dataQualityMetrics: DataQualityMetrics
    ) {
        self.claimId = claimId
        self.validationStatus = validationStatus
        self.validationScore = validationScore
        self.complianceStatus = complianceStatus
        self.errors = errors
        self.warnings = warnings
        self.recommendations = recommendations
        self.dataQualityMetrics = dataQualityMetrics
    }

    public enum ValidationStatus: String, Codable, Sendable {
        case passed = "passed"
        case failed = "failed"
        case warning = "warning"
        case requiresReview = "requires_review"
    }

    public enum ComplianceStatus: String, Codable, Sendable {
        case compliant = "compliant"
        case nonCompliant = "non_compliant"
        case partiallyCompliant = "partially_compliant"
        case requiresReview = "requires_review"
    }

    enum CodingKeys: String, CodingKey {
        case claimId = "claim_id"
        case validationStatus = "validation_status"
        case validationScore = "validation_score"
        case complianceStatus = "compliance_status"
        case errors, warnings, recommendations
        case dataQualityMetrics = "data_quality_metrics"
    }
}

// MARK: - Validation Error

public struct ValidationError: Codable, Sendable, Identifiable {
    public let id: UUID
    public var code: String
    public var field: String?
    public var message: String
    public var severity: Severity
    public var category: ErrorCategory

    public init(
        id: UUID = UUID(),
        code: String,
        field: String? = nil,
        message: String,
        severity: Severity,
        category: ErrorCategory
    ) {
        self.id = id
        self.code = code
        self.field = field
        self.message = message
        self.severity = severity
        self.category = category
    }

    public enum Severity: String, Codable, Sendable {
        case critical = "critical"
        case high = "high"
        case medium = "medium"
        case low = "low"
    }

    public enum ErrorCategory: String, Codable, Sendable {
        case missingData = "missing_data"
        case invalidFormat = "invalid_format"
        case compliance = "compliance"
        case businessRule = "business_rule"
        case dataQuality = "data_quality"
    }
}

// MARK: - Validation Warning

public struct ValidationWarning: Codable, Sendable, Identifiable {
    public let id: UUID
    public var code: String
    public var field: String?
    public var message: String
    public var recommendation: String?

    public init(
        id: UUID = UUID(),
        code: String,
        field: String? = nil,
        message: String,
        recommendation: String? = nil
    ) {
        self.id = id
        self.code = code
        self.field = field
        self.message = message
        self.recommendation = recommendation
    }
}

// MARK: - Data Quality Metrics

public struct DataQualityMetrics: Codable, Sendable {
    public var completeness: Double
    public var accuracy: Double
    public var consistency: Double
    public var validity: Double
    public var timeliness: Double

    public init(
        completeness: Double = 0.0,
        accuracy: Double = 0.0,
        consistency: Double = 0.0,
        validity: Double = 0.0,
        timeliness: Double = 0.0
    ) {
        self.completeness = completeness
        self.accuracy = accuracy
        self.consistency = consistency
        self.validity = validity
        self.timeliness = timeliness
    }

    /// Calculate overall quality score (0-100)
    public var overallScore: Double {
        return (completeness + accuracy + consistency + validity + timeliness) / 5.0
    }
}

// MARK: - Normalization Result

public struct NormalizationResult: Codable, Sendable {
    public var claimId: String
    public var normalizedData: StandardClaim
    public var validationResult: ValidationResult?
    public var processingTime: TimeInterval
    public var sourceFormat: String
    public var metadata: ProcessingMetadata

    public init(
        claimId: String,
        normalizedData: StandardClaim,
        validationResult: ValidationResult? = nil,
        processingTime: TimeInterval,
        sourceFormat: String,
        metadata: ProcessingMetadata
    ) {
        self.claimId = claimId
        self.normalizedData = normalizedData
        self.validationResult = validationResult
        self.processingTime = processingTime
        self.sourceFormat = sourceFormat
        self.metadata = metadata
    }

    enum CodingKeys: String, CodingKey {
        case claimId = "claim_id"
        case normalizedData = "normalized_data"
        case validationResult = "validation_result"
        case processingTime = "processing_time"
        case sourceFormat = "source_format"
        case metadata
    }
}

public struct ProcessingMetadata: Codable, Sendable {
    public var processedAt: Date
    public var apiVersion: String
    public var processorId: String?

    public init(
        processedAt: Date = Date(),
        apiVersion: String = "1.0.0",
        processorId: String? = nil
    ) {
        self.processedAt = processedAt
        self.apiVersion = apiVersion
        self.processorId = processorId
    }

    enum CodingKeys: String, CodingKey {
        case processedAt = "processed_at"
        case apiVersion = "api_version"
        case processorId = "processor_id"
    }
}

// MARK: - Batch Processing Result

public struct BatchProcessingResult: Codable, Sendable {
    public var totalClaims: Int
    public var successfullyProcessed: Int
    public var failed: Int
    public var processingTime: TimeInterval
    public var results: [StandardClaim]
    public var summaryReport: SummaryReport

    public init(
        totalClaims: Int,
        successfullyProcessed: Int,
        failed: Int,
        processingTime: TimeInterval,
        results: [StandardClaim],
        summaryReport: SummaryReport
    ) {
        self.totalClaims = totalClaims
        self.successfullyProcessed = successfullyProcessed
        self.failed = failed
        self.processingTime = processingTime
        self.results = results
        self.summaryReport = summaryReport
    }

    public var successRate: Double {
        guard totalClaims > 0 else { return 0.0 }
        return (Double(successfullyProcessed) / Double(totalClaims)) * 100.0
    }

    enum CodingKeys: String, CodingKey {
        case totalClaims = "total_claims"
        case successfullyProcessed = "successfully_processed"
        case failed
        case processingTime = "processing_time"
        case results
        case summaryReport = "summary_report"
    }
}

public struct SummaryReport: Codable, Sendable {
    public var totalClaims: Int
    public var successfullyProcessed: Int
    public var failed: Int
    public var successRate: Double
    public var averageProcessingTime: Double

    public init(
        totalClaims: Int,
        successfullyProcessed: Int,
        failed: Int,
        successRate: Double,
        averageProcessingTime: Double
    ) {
        self.totalClaims = totalClaims
        self.successfullyProcessed = successfullyProcessed
        self.failed = failed
        self.successRate = successRate
        self.averageProcessingTime = averageProcessingTime
    }

    enum CodingKeys: String, CodingKey {
        case totalClaims = "total_claims"
        case successfullyProcessed = "successfully_processed"
        case failed
        case successRate = "success_rate"
        case averageProcessingTime = "average_processing_time"
    }
}
