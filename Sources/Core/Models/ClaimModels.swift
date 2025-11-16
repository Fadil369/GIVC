import Foundation
import ModelsR4 // FHIR R4 Models

// MARK: - Core Claim Models

/// Standard claim data structure for ClaimLinc system
public struct StandardClaim: Codable, Identifiable, Sendable {
    public let id: UUID
    public var claimId: String
    public var provider: Provider
    public var patient: Patient
    public var claimDetails: ClaimDetails
    public var payer: Payer
    public var submission: SubmissionInfo
    public var metadata: ClaimMetadata?

    public init(
        id: UUID = UUID(),
        claimId: String,
        provider: Provider,
        patient: Patient,
        claimDetails: ClaimDetails,
        payer: Payer,
        submission: SubmissionInfo,
        metadata: ClaimMetadata? = nil
    ) {
        self.id = id
        self.claimId = claimId
        self.provider = provider
        self.patient = patient
        self.claimDetails = claimDetails
        self.payer = payer
        self.submission = submission
        self.metadata = metadata
    }

    enum CodingKeys: String, CodingKey {
        case id
        case claimId = "claim_id"
        case provider
        case patient
        case claimDetails = "claim_details"
        case payer
        case submission
        case metadata
    }
}

// MARK: - Provider Information

public struct Provider: Codable, Sendable {
    public var name: String
    public var code: String
    public var branch: String
    public var licenseNumber: String?
    public var contactInfo: ContactInfo?

    public init(
        name: String,
        code: String,
        branch: String,
        licenseNumber: String? = nil,
        contactInfo: ContactInfo? = nil
    ) {
        self.name = name
        self.code = code
        self.branch = branch
        self.licenseNumber = licenseNumber
        self.contactInfo = contactInfo
    }

    enum CodingKeys: String, CodingKey {
        case name, code, branch
        case licenseNumber = "license_number"
        case contactInfo = "contact_info"
    }
}

// MARK: - Patient Information

public struct Patient: Codable, Sendable {
    public var memberId: String
    public var name: String
    public var nationalId: String?
    public var dateOfBirth: Date?
    public var gender: Gender?
    public var contactInfo: ContactInfo?

    public init(
        memberId: String,
        name: String,
        nationalId: String? = nil,
        dateOfBirth: Date? = nil,
        gender: Gender? = nil,
        contactInfo: ContactInfo? = nil
    ) {
        self.memberId = memberId
        self.name = name
        self.nationalId = nationalId
        self.dateOfBirth = dateOfBirth
        self.gender = gender
        self.contactInfo = contactInfo
    }

    public enum Gender: String, Codable, Sendable {
        case male = "male"
        case female = "female"
        case other = "other"
        case unknown = "unknown"
    }

    enum CodingKeys: String, CodingKey {
        case memberId = "member_id"
        case name
        case nationalId = "national_id"
        case dateOfBirth = "date_of_birth"
        case gender
        case contactInfo = "contact_info"
    }
}

// MARK: - Claim Details

public struct ClaimDetails: Codable, Sendable {
    public var serviceDate: Date
    public var totalAmount: Decimal
    public var diagnosisCodes: [String]
    public var procedureCodes: [ProcedureCode]
    public var services: [Service]?
    public var encounterType: EncounterType?

    public init(
        serviceDate: Date,
        totalAmount: Decimal,
        diagnosisCodes: [String],
        procedureCodes: [ProcedureCode],
        services: [Service]? = nil,
        encounterType: EncounterType? = nil
    ) {
        self.serviceDate = serviceDate
        self.totalAmount = totalAmount
        self.diagnosisCodes = diagnosisCodes
        self.procedureCodes = procedureCodes
        self.services = services
        self.encounterType = encounterType
    }

    public enum EncounterType: String, Codable, Sendable {
        case inpatient = "inpatient"
        case outpatient = "outpatient"
        case emergency = "emergency"
        case daycase = "daycase"
    }

    enum CodingKeys: String, CodingKey {
        case serviceDate = "service_date"
        case totalAmount = "total_amount"
        case diagnosisCodes = "diagnosis_codes"
        case procedureCodes = "procedure_codes"
        case services
        case encounterType = "encounter_type"
    }
}

public struct ProcedureCode: Codable, Sendable {
    public var code: String
    public var description: String?
    public var quantity: Int
    public var unitPrice: Decimal?

    public init(code: String, description: String? = nil, quantity: Int = 1, unitPrice: Decimal? = nil) {
        self.code = code
        self.description = description
        self.quantity = quantity
        self.unitPrice = unitPrice
    }

    enum CodingKeys: String, CodingKey {
        case code, description, quantity
        case unitPrice = "unit_price"
    }
}

public struct Service: Codable, Sendable {
    public var code: String
    public var description: String
    public var quantity: Int
    public var unitPrice: Decimal
    public var netPrice: Decimal
    public var tax: Decimal?

    public init(
        code: String,
        description: String,
        quantity: Int,
        unitPrice: Decimal,
        netPrice: Decimal,
        tax: Decimal? = nil
    ) {
        self.code = code
        self.description = description
        self.quantity = quantity
        self.unitPrice = unitPrice
        self.netPrice = netPrice
        self.tax = tax
    }

    enum CodingKeys: String, CodingKey {
        case code, description, quantity
        case unitPrice = "unit_price"
        case netPrice = "net_price"
        case tax
    }
}

// MARK: - Payer Information

public struct Payer: Codable, Sendable {
    public var name: String
    public var payerId: String?
    public var insuranceType: InsuranceType
    public var policyNumber: String?

    public init(
        name: String,
        payerId: String? = nil,
        insuranceType: InsuranceType,
        policyNumber: String? = nil
    ) {
        self.name = name
        self.payerId = payerId
        self.insuranceType = insuranceType
        self.policyNumber = policyNumber
    }

    public enum InsuranceType: String, Codable, Sendable {
        case private = "private"
        case government = "government"
        case military = "military"
        case corporate = "corporate"
    }

    enum CodingKeys: String, CodingKey {
        case name
        case payerId = "payer_id"
        case insuranceType = "insurance_type"
        case policyNumber = "policy_number"
    }
}

// MARK: - Submission Information

public struct SubmissionInfo: Codable, Sendable {
    public var method: SubmissionMethod
    public var timestamp: Date
    public var batchId: String?
    public var status: SubmissionStatus
    public var submittedBy: String?
    public var responseTimestamp: Date?

    public init(
        method: SubmissionMethod,
        timestamp: Date = Date(),
        batchId: String? = nil,
        status: SubmissionStatus = .pending,
        submittedBy: String? = nil,
        responseTimestamp: Date? = nil
    ) {
        self.method = method
        self.timestamp = timestamp
        self.batchId = batchId
        self.status = status
        self.submittedBy = submittedBy
        self.responseTimestamp = responseTimestamp
    }

    public enum SubmissionMethod: String, Codable, Sendable {
        case nphies = "NPHIES"
        case portal = "PORTAL"
        case email = "EMAIL"
        case api = "API"
    }

    public enum SubmissionStatus: String, Codable, Sendable {
        case pending = "pending"
        case submitted = "submitted"
        case processing = "processing"
        case approved = "approved"
        case rejected = "rejected"
        case partiallyApproved = "partially_approved"
        case error = "error"
    }

    enum CodingKeys: String, CodingKey {
        case method, timestamp, status
        case batchId = "batch_id"
        case submittedBy = "submitted_by"
        case responseTimestamp = "response_timestamp"
    }
}

// MARK: - Contact Information

public struct ContactInfo: Codable, Sendable {
    public var phone: String?
    public var email: String?
    public var address: String?
    public var city: String?
    public var postalCode: String?

    public init(
        phone: String? = nil,
        email: String? = nil,
        address: String? = nil,
        city: String? = nil,
        postalCode: String? = nil
    ) {
        self.phone = phone
        self.email = email
        self.address = address
        self.city = city
        self.postalCode = postalCode
    }

    enum CodingKeys: String, CodingKey {
        case phone, email, address, city
        case postalCode = "postal_code"
    }
}

// MARK: - Metadata

public struct ClaimMetadata: Codable, Sendable {
    public var sourceFormat: String?
    public var processedAt: Date?
    public var validationScore: Double?
    public var complianceStatus: String?
    public var nphiesReferenceNumber: String?
    public var tags: [String]?

    public init(
        sourceFormat: String? = nil,
        processedAt: Date? = nil,
        validationScore: Double? = nil,
        complianceStatus: String? = nil,
        nphiesReferenceNumber: String? = nil,
        tags: [String]? = nil
    ) {
        self.sourceFormat = sourceFormat
        self.processedAt = processedAt
        self.validationScore = validationScore
        self.complianceStatus = complianceStatus
        self.nphiesReferenceNumber = nphiesReferenceNumber
        self.tags = tags
    }

    enum CodingKeys: String, CodingKey {
        case sourceFormat = "source_format"
        case processedAt = "processed_at"
        case validationScore = "validation_score"
        case complianceStatus = "compliance_status"
        case nphiesReferenceNumber = "nphies_reference_number"
        case tags
    }
}

// MARK: - Branch Mapping

public enum Branch: String, Codable, CaseIterable, Sendable {
    case mainRiyadh = "MainRiyadh"
    case unaizah = "Unaizah"
    case abha = "Abha"
    case madinah = "Madinah"
    case khamis = "Khamis"
    case jazan = "Jazan"

    /// Normalize branch name from various formats
    public static func normalize(_ branchName: String) -> Branch? {
        let normalized = branchName.lowercased().trimmingCharacters(in: .whitespacesAndNewlines)

        switch normalized {
        case "riyadh", "main riyadh", "mainriyadh":
            return .mainRiyadh
        case "unaizah", "unayzah":
            return .unaizah
        case "abha":
            return .abha
        case "madinah", "medina":
            return .madinah
        case "khamis", "khamis mushait", "khamis mushayt":
            return .khamis
        case "jazan", "jizan":
            return .jazan
        default:
            return nil
        }
    }
}

// MARK: - Payer Types

public enum PayerType: String, Codable, CaseIterable, Sendable {
    case bupa = "bupa"
    case tawuniya = "tawuniya"
    case globemed = "globemed"
    case waseel = "waseel"
    case najm = "najm"
    case medgulf = "medgulf"
    case saico = "saico"

    public var displayName: String {
        switch self {
        case .bupa:
            return "Bupa Arabia"
        case .tawuniya:
            return "Tawuniya"
        case .globemed:
            return "GlobeMed"
        case .waseel:
            return "Waseel"
        case .najm:
            return "Najm"
        case .medgulf:
            return "MedGulf"
        case .saico:
            return "SAICO"
        }
    }
}
