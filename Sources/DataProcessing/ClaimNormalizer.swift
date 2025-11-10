import Foundation
import Logging

/// Service for normalizing claims from various payer formats to standard format
public actor ClaimNormalizer {
    private let logger: Logger

    public init(logger: Logger = Logger(label: "com.brainsait.claimlinc.normalizer")) {
        self.logger = logger
    }

    // MARK: - Public API

    /// Normalize a single claim from source format to standard format
    public func normalize(
        _ claimData: [String: Any],
        sourceFormat: String
    ) async -> Result<StandardClaim, NormalizationError> {
        logger.info("Normalizing claim from format: \(sourceFormat)")

        let format = sourceFormat.lowercased()

        switch format {
        case "bupa":
            return await normalizeBupaClaim(claimData)
        case "globemed":
            return await normalizeGlobeMedClaim(claimData)
        case "waseel", "tawuniya":
            return await normalizeWaseelClaim(claimData)
        case "generic":
            return await normalizeGenericClaim(claimData)
        default:
            logger.warning("Unknown source format: \(sourceFormat), attempting generic normalization")
            return await normalizeGenericClaim(claimData)
        }
    }

    /// Normalize multiple claims in batch
    public func normalizeBatch(
        _ claimsData: [[String: Any]],
        sourceFormat: String
    ) async -> [Result<StandardClaim, NormalizationError>] {
        logger.info("Batch normalizing \(claimsData.count) claims from format: \(sourceFormat)")

        return await withTaskGroup(of: (Int, Result<StandardClaim, NormalizationError>).self) { group in
            for (index, claimData) in claimsData.enumerated() {
                group.addTask {
                    let result = await self.normalize(claimData, sourceFormat: sourceFormat)
                    return (index, result)
                }
            }

            var results: [(Int, Result<StandardClaim, NormalizationError>)] = []
            for await result in group {
                results.append(result)
            }

            // Sort by original index to maintain order
            return results.sorted { $0.0 < $1.0 }.map { $0.1 }
        }
    }

    // MARK: - Format-Specific Normalization

    private func normalizeBupaClaim(_ data: [String: Any]) async -> Result<StandardClaim, NormalizationError> {
        do {
            // Extract Bupa-specific fields
            let claimId = getString(from: data, key: "ClaimNumber") ?? getString(from: data, key: "claim_number") ?? "UNKNOWN"

            // Provider information
            let providerName = getString(from: data, key: "ProviderName") ?? ""
            let providerCode = getString(from: data, key: "ProviderCode") ?? ""
            let branchName = getString(from: data, key: "Branch") ?? getString(from: data, key: "BranchName") ?? ""
            let normalizedBranch = Branch.normalize(branchName)?.rawValue ?? branchName

            let provider = Provider(
                name: providerName,
                code: providerCode,
                branch: normalizedBranch,
                licenseNumber: getString(from: data, key: "LicenseNumber")
            )

            // Patient information
            let memberId = getString(from: data, key: "MemberID") ?? getString(from: data, key: "PatientID") ?? ""
            let patientName = getString(from: data, key: "PatientName") ?? ""
            let nationalId = getString(from: data, key: "NationalID")
            let dateOfBirth = getDate(from: data, key: "DOB")
            let genderString = getString(from: data, key: "Gender")
            let gender = Patient.Gender(rawValue: genderString?.lowercased() ?? "unknown")

            let patient = Patient(
                memberId: memberId,
                name: patientName,
                nationalId: nationalId,
                dateOfBirth: dateOfBirth,
                gender: gender
            )

            // Claim details
            let serviceDate = getDate(from: data, key: "ServiceDate") ?? Date()
            let totalAmount = getDecimal(from: data, key: "TotalAmount") ?? 0
            let diagnosisCodes = getStringArray(from: data, key: "DiagnosisCodes") ?? []

            // Procedure codes
            var procedureCodes: [ProcedureCode] = []
            if let procedures = data["Procedures"] as? [[String: Any]] {
                procedureCodes = procedures.compactMap { proc in
                    guard let code = proc["Code"] as? String else { return nil }
                    return ProcedureCode(
                        code: code,
                        description: proc["Description"] as? String,
                        quantity: proc["Quantity"] as? Int ?? 1,
                        unitPrice: getDecimal(from: proc, key: "UnitPrice")
                    )
                }
            }

            let claimDetails = ClaimDetails(
                serviceDate: serviceDate,
                totalAmount: totalAmount,
                diagnosisCodes: diagnosisCodes,
                procedureCodes: procedureCodes
            )

            // Payer information
            let payer = Payer(
                name: "Bupa Arabia",
                payerId: "BUPA",
                insuranceType: .private,
                policyNumber: getString(from: data, key: "PolicyNumber")
            )

            // Submission information
            let submission = SubmissionInfo(
                method: .portal,
                timestamp: Date(),
                status: .pending
            )

            // Metadata
            let metadata = ClaimMetadata(
                sourceFormat: "bupa",
                processedAt: Date()
            )

            let standardClaim = StandardClaim(
                claimId: claimId,
                provider: provider,
                patient: patient,
                claimDetails: claimDetails,
                payer: payer,
                submission: submission,
                metadata: metadata
            )

            logger.info("Successfully normalized Bupa claim: \(claimId)")
            return .success(standardClaim)

        } catch {
            logger.error("Failed to normalize Bupa claim: \(error)")
            return .failure(.invalidData("Failed to normalize Bupa claim: \(error.localizedDescription)"))
        }
    }

    private func normalizeGlobeMedClaim(_ data: [String: Any]) async -> Result<StandardClaim, NormalizationError> {
        // Similar to Bupa but with GlobeMed-specific field mappings
        do {
            let claimId = getString(from: data, key: "claim_id") ?? getString(from: data, key: "ClaimID") ?? "UNKNOWN"

            let provider = Provider(
                name: getString(from: data, key: "provider_name") ?? "",
                code: getString(from: data, key: "provider_code") ?? "",
                branch: Branch.normalize(getString(from: data, key: "branch") ?? "")?.rawValue ?? ""
            )

            let patient = Patient(
                memberId: getString(from: data, key: "member_id") ?? "",
                name: getString(from: data, key: "patient_name") ?? ""
            )

            let claimDetails = ClaimDetails(
                serviceDate: getDate(from: data, key: "service_date") ?? Date(),
                totalAmount: getDecimal(from: data, key: "total_amount") ?? 0,
                diagnosisCodes: getStringArray(from: data, key: "diagnosis_codes") ?? [],
                procedureCodes: []
            )

            let payer = Payer(
                name: "GlobeMed",
                payerId: "GLOBEMED",
                insuranceType: .private
            )

            let submission = SubmissionInfo(
                method: .portal,
                timestamp: Date(),
                status: .pending
            )

            let metadata = ClaimMetadata(sourceFormat: "globemed", processedAt: Date())

            let standardClaim = StandardClaim(
                claimId: claimId,
                provider: provider,
                patient: patient,
                claimDetails: claimDetails,
                payer: payer,
                submission: submission,
                metadata: metadata
            )

            logger.info("Successfully normalized GlobeMed claim: \(claimId)")
            return .success(standardClaim)

        } catch {
            logger.error("Failed to normalize GlobeMed claim: \(error)")
            return .failure(.invalidData("Failed to normalize GlobeMed claim: \(error.localizedDescription)"))
        }
    }

    private func normalizeWaseelClaim(_ data: [String: Any]) async -> Result<StandardClaim, NormalizationError> {
        // Waseel uses FHIR format
        // This would include FHIR Bundle parsing
        do {
            // Check if this is a FHIR Bundle
            if let resourceType = data["resourceType"] as? String, resourceType == "Bundle" {
                return await normalizeFHIRBundle(data)
            }

            // Fall back to generic normalization
            return await normalizeGenericClaim(data)

        } catch {
            logger.error("Failed to normalize Waseel claim: \(error)")
            return .failure(.invalidData("Failed to normalize Waseel claim: \(error.localizedDescription)"))
        }
    }

    private func normalizeFHIRBundle(_ data: [String: Any]) async -> Result<StandardClaim, NormalizationError> {
        // Parse FHIR Bundle structure
        // This would use the FHIRModels library
        logger.warning("FHIR Bundle parsing not fully implemented yet")
        return await normalizeGenericClaim(data)
    }

    private func normalizeGenericClaim(_ data: [String: Any]) async -> Result<StandardClaim, NormalizationError> {
        // Generic normalization with common field names
        do {
            let claimId = getString(from: data, key: "claim_id")
                ?? getString(from: data, key: "claimId")
                ?? getString(from: data, key: "id")
                ?? "UNKNOWN"

            let provider = Provider(
                name: getString(from: data, key: "provider_name") ?? getString(from: data, key: "providerName") ?? "",
                code: getString(from: data, key: "provider_code") ?? getString(from: data, key: "providerCode") ?? "",
                branch: getString(from: data, key: "branch") ?? ""
            )

            let patient = Patient(
                memberId: getString(from: data, key: "member_id") ?? getString(from: data, key: "memberId") ?? "",
                name: getString(from: data, key: "patient_name") ?? getString(from: data, key: "patientName") ?? ""
            )

            let claimDetails = ClaimDetails(
                serviceDate: getDate(from: data, key: "service_date") ?? getDate(from: data, key: "serviceDate") ?? Date(),
                totalAmount: getDecimal(from: data, key: "total_amount") ?? getDecimal(from: data, key: "totalAmount") ?? 0,
                diagnosisCodes: getStringArray(from: data, key: "diagnosis_codes") ?? getStringArray(from: data, key: "diagnosisCodes") ?? [],
                procedureCodes: []
            )

            let payer = Payer(
                name: getString(from: data, key: "payer_name") ?? getString(from: data, key: "payerName") ?? "Unknown",
                insuranceType: .private
            )

            let submission = SubmissionInfo(
                method: .api,
                timestamp: Date(),
                status: .pending
            )

            let metadata = ClaimMetadata(sourceFormat: "generic", processedAt: Date())

            let standardClaim = StandardClaim(
                claimId: claimId,
                provider: provider,
                patient: patient,
                claimDetails: claimDetails,
                payer: payer,
                submission: submission,
                metadata: metadata
            )

            logger.info("Successfully normalized generic claim: \(claimId)")
            return .success(standardClaim)

        } catch {
            logger.error("Failed to normalize generic claim: \(error)")
            return .failure(.invalidData("Failed to normalize generic claim: \(error.localizedDescription)"))
        }
    }

    // MARK: - Helper Methods

    private func getString(from dict: [String: Any], key: String) -> String? {
        return dict[key] as? String
    }

    private func getStringArray(from dict: [String: Any], key: String) -> [String]? {
        return dict[key] as? [String]
    }

    private func getDecimal(from dict: [String: Any], key: String) -> Decimal? {
        if let value = dict[key] as? Double {
            return Decimal(value)
        } else if let value = dict[key] as? Int {
            return Decimal(value)
        } else if let value = dict[key] as? String, let double = Double(value) {
            return Decimal(double)
        }
        return nil
    }

    private func getDate(from dict: [String: Any], key: String) -> Date? {
        if let value = dict[key] as? String {
            let formatter = ISO8601DateFormatter()
            if let date = formatter.date(from: value) {
                return date
            }

            // Try alternative date formats
            let dateFormatter = DateFormatter()
            dateFormatter.dateFormat = "yyyy-MM-dd"
            if let date = dateFormatter.date(from: value) {
                return date
            }
        }
        return dict[key] as? Date
    }
}

// MARK: - Normalization Error

public enum NormalizationError: Error, CustomStringConvertible {
    case invalidData(String)
    case unsupportedFormat(String)
    case missingRequiredField(String)
    case parsingError(String)

    public var description: String {
        switch self {
        case .invalidData(let message):
            return "Invalid data: \(message)"
        case .unsupportedFormat(let format):
            return "Unsupported format: \(format)"
        case .missingRequiredField(let field):
            return "Missing required field: \(field)"
        case .parsingError(let message):
            return "Parsing error: \(message)"
        }
    }
}
