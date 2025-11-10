import Vapor

struct ClaimController: RouteCollection {
    func boot(routes: RoutesBuilder) throws {
        let claims = routes.grouped("normalize")
        claims.post(use: normalize)
    }

    func normalize(_ req: Request) async throws -> NormalizationResponse {
        let startTime = Date()
        let request = try req.content.decode(ClaimRequest.self)

        req.logger.info("Normalizing claim from format: \(request.sourceFormat)")

        // Get normalizer service
        let normalizer = ClaimNormalizer()

        // Normalize the claim
        let result = await normalizer.normalize(request.claimData, sourceFormat: request.sourceFormat)

        switch result {
        case .success(let normalizedClaim):
            var validationResult: ValidationResult? = nil

            // Validate if requested
            if request.validationRequired {
                let validator = ClaimValidator()
                validationResult = await validator.validate(normalizedClaim)
            }

            let processingTime = Date().timeIntervalSince(startTime)

            return NormalizationResponse(
                claimId: normalizedClaim.claimId,
                normalizedData: normalizedClaim,
                validationResult: validationResult,
                processingTime: processingTime,
                sourceFormat: request.sourceFormat,
                metadata: ProcessingMetadata(
                    processedAt: Date(),
                    apiVersion: "1.0.0"
                )
            )

        case .failure(let error):
            req.logger.error("Normalization failed: \(error)")
            throw Abort(.badRequest, reason: "Normalization failed: \(error.description)")
        }
    }
}

// MARK: - Request/Response Models

struct ClaimRequest: Content {
    let claimData: [String: AnyEncodableValue]
    let sourceFormat: String
    let validationRequired: Bool

    enum CodingKeys: String, CodingKey {
        case claimData = "claim_data"
        case sourceFormat = "source_format"
        case validationRequired = "validation_required"
    }
}

struct NormalizationResponse: Content {
    let claimId: String
    let normalizedData: StandardClaim
    let validationResult: ValidationResult?
    let processingTime: TimeInterval
    let sourceFormat: String
    let metadata: ProcessingMetadata

    enum CodingKeys: String, CodingKey {
        case claimId = "claim_id"
        case normalizedData = "normalized_data"
        case validationResult = "validation_result"
        case processingTime = "processing_time"
        case sourceFormat = "source_format"
        case metadata
    }
}

// MARK: - AnyEncodableValue for dynamic JSON

struct AnyEncodableValue: Codable {
    let value: Any

    init(_ value: Any) {
        self.value = value
    }

    init(from decoder: Decoder) throws {
        let container = try decoder.singleValueContainer()

        if let intValue = try? container.decode(Int.self) {
            value = intValue
        } else if let doubleValue = try? container.decode(Double.self) {
            value = doubleValue
        } else if let stringValue = try? container.decode(String.self) {
            value = stringValue
        } else if let boolValue = try? container.decode(Bool.self) {
            value = boolValue
        } else if let arrayValue = try? container.decode([AnyEncodableValue].self) {
            value = arrayValue.map { $0.value }
        } else if let dictValue = try? container.decode([String: AnyEncodableValue].self) {
            value = dictValue.mapValues { $0.value }
        } else {
            throw DecodingError.dataCorruptedError(
                in: container,
                debugDescription: "Cannot decode AnyEncodableValue"
            )
        }
    }

    func encode(to encoder: Encoder) throws {
        var container = encoder.singleValueContainer()

        if let intValue = value as? Int {
            try container.encode(intValue)
        } else if let doubleValue = value as? Double {
            try container.encode(doubleValue)
        } else if let stringValue = value as? String {
            try container.encode(stringValue)
        } else if let boolValue = value as? Bool {
            try container.encode(boolValue)
        } else if let arrayValue = value as? [Any] {
            try container.encode(arrayValue.map { AnyEncodableValue($0) })
        } else if let dictValue = value as? [String: Any] {
            try container.encode(dictValue.mapValues { AnyEncodableValue($0) })
        } else {
            throw EncodingError.invalidValue(
                value,
                EncodingError.Context(
                    codingPath: encoder.codingPath,
                    debugDescription: "Cannot encode AnyEncodableValue"
                )
            )
        }
    }
}

extension AnyEncodableValue: Equatable {
    static func == (lhs: AnyEncodableValue, rhs: AnyEncodableValue) -> Bool {
        // Simple equality check - extend as needed
        return String(describing: lhs.value) == String(describing: rhs.value)
    }
}

extension AnyEncodableValue: Hashable {
    func hash(into hasher: inout Hasher) {
        hasher.combine(String(describing: value))
    }
}
