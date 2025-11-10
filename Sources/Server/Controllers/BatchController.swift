import Vapor

struct BatchController: RouteCollection {
    func boot(routes: RoutesBuilder) throws {
        let batch = routes.grouped("batch")
        batch.post(use: processBatch)
    }

    func processBatch(_ req: Request) async throws -> BatchProcessingResponse {
        let startTime = Date()
        let request = try req.content.decode(BatchClaimRequest.self)

        req.logger.info("Processing batch of \(request.claimsData.count) claims")

        let normalizer = ClaimNormalizer()

        // Convert to dictionary format
        let claimsData = request.claimsData.map { claim in
            claim.mapValues { $0.value }
        }

        // Normalize all claims
        let normalizedResults = await normalizer.normalizeBatch(claimsData, sourceFormat: request.sourceFormat)

        var successfulClaims: [StandardClaim] = []
        var failedCount = 0

        // Process results
        for result in normalizedResults {
            switch result {
            case .success(let claim):
                successfulClaims.append(claim)
            case .failure(let error):
                req.logger.error("Batch normalization error: \(error)")
                failedCount += 1
            }
        }

        // Validate if requested
        if request.validationRequired {
            let validator = ClaimValidator()
            _ = await validator.validateBatch(successfulClaims)
        }

        let processingTime = Date().timeIntervalSince(startTime)
        let totalClaims = request.claimsData.count

        let summaryReport = SummaryReport(
            totalClaims: totalClaims,
            successfullyProcessed: successfulClaims.count,
            failed: failedCount,
            successRate: Double(successfulClaims.count) / Double(totalClaims) * 100.0,
            averageProcessingTime: processingTime / Double(totalClaims)
        )

        return BatchProcessingResponse(
            totalClaims: totalClaims,
            successfullyProcessed: successfulClaims.count,
            failed: failedCount,
            processingTime: processingTime,
            results: successfulClaims,
            summaryReport: summaryReport
        )
    }
}

// MARK: - Request/Response Models

struct BatchClaimRequest: Content {
    let claimsData: [[String: AnyEncodableValue]]
    let sourceFormat: String
    let validationRequired: Bool

    enum CodingKeys: String, CodingKey {
        case claimsData = "claims_data"
        case sourceFormat = "source_format"
        case validationRequired = "validation_required"
    }
}

struct BatchProcessingResponse: Content {
    let totalClaims: Int
    let successfullyProcessed: Int
    let failed: Int
    let processingTime: TimeInterval
    let results: [StandardClaim]
    let summaryReport: SummaryReport

    enum CodingKeys: String, CodingKey {
        case totalClaims = "total_claims"
        case successfullyProcessed = "successfully_processed"
        case failed
        case processingTime = "processing_time"
        case results
        case summaryReport = "summary_report"
    }
}
