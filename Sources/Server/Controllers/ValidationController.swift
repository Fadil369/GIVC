import Vapor

struct ValidationController: RouteCollection {
    func boot(routes: RoutesBuilder) throws {
        let validation = routes.grouped("validate")
        validation.post(use: validate)
    }

    func validate(_ req: Request) async throws -> ValidationResult {
        let claim = try req.content.decode(StandardClaim.self)

        req.logger.info("Validating claim: \(claim.claimId)")

        let validator = ClaimValidator()
        let result = await validator.validate(claim)

        return result
    }
}
