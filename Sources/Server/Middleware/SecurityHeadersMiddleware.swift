import Vapor

/// Middleware to add security headers to all responses
public struct SecurityHeadersMiddleware: AsyncMiddleware {
    public init() {}

    public func respond(to request: Request, chainingTo next: AsyncResponder) async throws -> Response {
        let response = try await next.respond(to: request)

        // Prevent MIME type sniffing
        response.headers.add(name: "X-Content-Type-Options", value: "nosniff")

        // Prevent clickjacking
        response.headers.add(name: "X-Frame-Options", value: "DENY")

        // Enable XSS protection
        response.headers.add(name: "X-XSS-Protection", value: "1; mode=block")

        // Force HTTPS in production
        response.headers.add(name: "Strict-Transport-Security", value: "max-age=31536000; includeSubDomains; preload")

        // Content Security Policy
        response.headers.add(name: "Content-Security-Policy", value: [
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline'",
            "style-src 'self' 'unsafe-inline'",
            "img-src 'self' data: https:",
            "font-src 'self'",
            "connect-src 'self'",
            "frame-ancestors 'none'"
        ].joined(separator: "; "))

        // Referrer Policy
        response.headers.add(name: "Referrer-Policy", value: "strict-origin-when-cross-origin")

        // Permissions Policy
        response.headers.add(name: "Permissions-Policy", value: [
            "geolocation=()",
            "microphone=()",
            "camera=()",
            "payment=()",
            "usb=()"
        ].joined(separator: ", "))

        return response
    }
}
