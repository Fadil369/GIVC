import Vapor
import Fluent
import FluentPostgresDriver
import Redis
import Queues
import QueuesRedisDriver
import JWT

@main
enum Entrypoint {
    static func main() async throws {
        var env = try Environment.detect()
        try LoggingSystem.bootstrap(from: &env)

        let app = Application(env)
        defer { app.shutdown() }

        do {
            try await configure(app)
            try app.run()
        } catch {
            app.logger.report(error: error)
            throw error
        }
    }
}

/// Configure the Vapor application
func configure(_ app: Application) async throws {
    // MARK: - Server Configuration

    app.http.server.configuration.hostname = "0.0.0.0"
    app.http.server.configuration.port = 8000

    // MARK: - Database Configuration

    // PostgreSQL
    var tlsConfig: TLSConfiguration = .makeClientConfiguration()
    tlsConfig.certificateVerification = .none

    app.databases.use(.postgres(
        hostname: Environment.get("DB_HOST") ?? "localhost",
        port: Environment.get("DB_PORT").flatMap(Int.init) ?? 5432,
        username: Environment.get("DB_USER") ?? "postgres",
        password: Environment.get("DB_PASSWORD") ?? "",
        database: Environment.get("DB_NAME") ?? "claimlinc",
        tls: .prefer(try! NIOSSLContext(configuration: tlsConfig))
    ), as: .psql)

    // MARK: - Redis Configuration

    app.redis.configuration = try RedisConfiguration(
        hostname: Environment.get("REDIS_HOST") ?? "localhost",
        port: Environment.get("REDIS_PORT").flatMap(Int.init) ?? 6379,
        password: Environment.get("REDIS_PASSWORD")
    )

    // MARK: - Queues Configuration

    app.queues.use(.redis(url: Environment.get("REDIS_URL") ?? "redis://localhost:6379"))

    // Register queue jobs
    app.queues.add(ClaimProcessingJob())
    app.queues.add(PortalSubmissionJob())

    // Start queue workers
    if app.environment != .testing {
        try app.queues.startInProcessJobs()
    }

    // MARK: - Middleware

    // Security headers
    app.middleware.use(SecurityHeadersMiddleware())

    // CORS
    let corsConfiguration = CORSMiddleware.Configuration(
        allowedOrigin: .all,
        allowedMethods: [.GET, .POST, .PUT, .DELETE, .OPTIONS, .PATCH],
        allowedHeaders: [.accept, .authorization, .contentType, .origin, .xRequestedWith]
    )
    app.middleware.use(CORSMiddleware(configuration: corsConfiguration))

    // Error handling
    app.middleware.use(ErrorMiddleware.default(environment: app.environment))

    // File middleware for serving static files
    app.middleware.use(FileMiddleware(publicDirectory: app.directory.publicDirectory))

    // MARK: - Migrations

    app.migrations.add(CreateClaim())
    app.migrations.add(CreateValidation())
    app.migrations.add(CreateSubmission())

    if app.environment == .development {
        try await app.autoMigrate()
    }

    // MARK: - Routes

    try routes(app)

    app.logger.info("ClaimLinc API Server configured successfully")
}
