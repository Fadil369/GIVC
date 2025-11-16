import Vapor

func routes(_ app: Application) throws {
    // MARK: - System Routes

    app.get { req async in
        return [
            "service": "ClaimLinc API",
            "version": "1.0.0",
            "status": "running",
            "timestamp": Date().ISO8601Format(),
            "endpoints": [
                "normalize": "/api/v1/normalize",
                "validate": "/api/v1/validate",
                "batch_process": "/api/v1/batch",
                "test_data": "/api/v1/test-data",
                "health": "/health",
                "docs": "/docs"
            ]
        ]
    }

    app.get("health") { req async throws -> HealthResponse in
        let healthController = HealthController()
        return try await healthController.check(req)
    }

    app.get("api", "v1", "system", "stats") { req async throws -> SystemStatsResponse in
        let systemController = SystemController()
        return try await systemController.getStats(req)
    }

    // MARK: - API v1 Routes

    let api = app.grouped("api", "v1")

    // Claim processing routes
    try api.register(collection: ClaimController())

    // Validation routes
    try api.register(collection: ValidationController())

    // Batch processing routes
    try api.register(collection: BatchController())

    // Test data generation routes
    try api.register(collection: TestDataController())

    // Portal automation routes
    try api.register(collection: AutomationController())

    // Export routes
    try api.register(collection: ExportController())

    // Workflow routes
    try api.register(collection: WorkflowController())

    app.logger.info("Routes registered successfully")
}

// MARK: - Response Models

struct HealthResponse: Content {
    let status: String
    let timestamp: String
    let services: [String: String]
}

struct SystemStatsResponse: Content {
    let uptime: String
    let memoryUsage: String
    let processingCapacity: String
    let supportedPayers: [String]
    let apiVersion: String
    let endpointsAvailable: [String]
    let timestamp: String
}
