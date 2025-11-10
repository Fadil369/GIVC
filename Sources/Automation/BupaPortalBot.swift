import Foundation
import AsyncHTTPClient
import SwiftSoup
import Logging

/// Automation bot for Bupa Arabia provider portal
public actor BupaPortalBot {
    private let baseURL = "https://provider.bupa.com.sa"
    private let downloadDir: URL
    private let httpClient: HTTPClient
    private let logger: Logger

    private var cookies: [String: String] = [:]
    private var sessionToken: String?

    public init(
        downloadDir: URL? = nil,
        httpClient: HTTPClient? = nil,
        logger: Logger = Logger(label: "com.brainsait.claimlinc.bupa-bot")
    ) {
        self.downloadDir = downloadDir ?? FileManager.default.temporaryDirectory.appendingPathComponent("bupa-downloads")
        self.httpClient = httpClient ?? HTTPClient(eventLoopGroupProvider: .createNew)
        self.logger = logger

        // Create download directory
        try? FileManager.default.createDirectory(at: self.downloadDir, withIntermediateDirectories: true)
    }

    deinit {
        try? httpClient.syncShutdown()
    }

    // MARK: - Public API

    /// Login to Bupa provider portal
    public func login(username: String, password: String) async throws -> Bool {
        logger.info("Logging in to Bupa portal...")

        let loginURL = "\(baseURL)/Provider/Default.aspx"

        // First, get the login page to extract any required tokens
        var request = HTTPClientRequest(url: loginURL)
        request.method = .GET

        let response = try await httpClient.execute(request, timeout: .seconds(30))
        let body = try await response.body.collect(upTo: 1024 * 1024) // 1MB limit

        guard let htmlString = String(buffer: body) else {
            logger.error("Failed to decode login page")
            return false
        }

        // Parse HTML to get form tokens (ViewState, etc.)
        let document = try SwiftSoup.parse(htmlString)
        let viewState = try? document.select("input[name='__VIEWSTATE']").first()?.attr("value")
        let viewStateGenerator = try? document.select("input[name='__VIEWSTATEGENERATOR']").first()?.attr("value")
        let eventValidation = try? document.select("input[name='__EVENTVALIDATION']").first()?.attr("value")

        // Prepare login request
        var loginRequest = HTTPClientRequest(url: loginURL)
        loginRequest.method = .POST
        loginRequest.headers.add(name: "Content-Type", value: "application/x-www-form-urlencoded")

        // Build form data
        var formData: [String: String] = [
            "txtUserName": username,
            "txtPassword": password,
            "btnLogin": "Login"
        ]

        if let viewState = viewState {
            formData["__VIEWSTATE"] = viewState
        }
        if let viewStateGenerator = viewStateGenerator {
            formData["__VIEWSTATEGENERATOR"] = viewStateGenerator
        }
        if let eventValidation = eventValidation {
            formData["__EVENTVALIDATION"] = eventValidation
        }

        let bodyString = formData.map { "\($0.key)=\($0.value.addingPercentEncoding(withAllowedCharacters: .urlQueryAllowed) ?? $0.value)" }.joined(separator: "&")
        loginRequest.body = .bytes(ByteBuffer(string: bodyString))

        // Execute login
        let loginResponse = try await httpClient.execute(loginRequest, timeout: .seconds(30))

        // Store cookies
        if let setCookieHeaders = loginResponse.headers["Set-Cookie"].first {
            parseCookies(setCookieHeaders)
        }

        // Check if login was successful (look for welcome message or redirect)
        let loginBody = try await loginResponse.body.collect(upTo: 1024 * 1024)
        if let loginHtml = String(buffer: loginBody) {
            let loginDoc = try SwiftSoup.parse(loginHtml)

            // Check for success indicators
            if try loginDoc.select("#MainContent_lblWelcome").first() != nil {
                logger.info("✅ Bupa login successful")
                return true
            }

            // Check for error message
            if let errorElement = try loginDoc.select("#lblErrorMessage").first() {
                let errorText = try errorElement.text()
                logger.error("❌ Bupa login failed: \(errorText)")
                return false
            }
        }

        logger.error("❌ Bupa login failed: Unknown error")
        return false
    }

    /// Navigate to claims submission section
    public func navigateToClaimsSection() async throws -> Bool {
        logger.info("Navigating to claims section...")

        let claimsLinks = ["Claims", "Submit Claims", "Claims Submission", "New Claim"]

        for linkText in claimsLinks {
            do {
                // Try to find and follow the link
                let url = "\(baseURL)/Provider/Claims.aspx" // Typical claims URL

                var request = HTTPClientRequest(url: url)
                request.method = .GET
                request.headers = buildHeaders()

                let response = try await httpClient.execute(request, timeout: .seconds(30))

                if response.status == .ok {
                    logger.info("✅ Navigated to claims section")
                    return true
                }
            } catch {
                logger.debug("Failed to navigate using link: \(linkText)")
                continue
            }
        }

        logger.error("❌ Could not find claims section")
        return false
    }

    /// Upload claim file to Bupa portal
    public func uploadClaimFile(filePath: URL) async throws -> String? {
        logger.info("Uploading claim file: \(filePath.lastPathComponent)")

        let uploadURL = "\(baseURL)/Provider/ClaimsUpload.aspx"

        // Read file data
        let fileData = try Data(contentsOf: filePath)

        // Create multipart form data request
        let boundary = "----WebKitFormBoundary\(UUID().uuidString)"

        var request = HTTPClientRequest(url: uploadURL)
        request.method = .POST
        request.headers.add(name: "Content-Type", value: "multipart/form-data; boundary=\(boundary)")

        // Build multipart body
        var body = Data()

        // Add file field
        body.append("--\(boundary)\r\n".data(using: .utf8)!)
        body.append("Content-Disposition: form-data; name=\"FileUpload1\"; filename=\"\(filePath.lastPathComponent)\"\r\n".data(using: .utf8)!)
        body.append("Content-Type: application/octet-stream\r\n\r\n".data(using: .utf8)!)
        body.append(fileData)
        body.append("\r\n".data(using: .utf8)!)

        // Add submit button
        body.append("--\(boundary)\r\n".data(using: .utf8)!)
        body.append("Content-Disposition: form-data; name=\"btnUpload\"\r\n\r\n".data(using: .utf8)!)
        body.append("Upload\r\n".data(using: .utf8)!)

        // Close boundary
        body.append("--\(boundary)--\r\n".data(using: .utf8)!)

        request.body = .bytes(ByteBuffer(data: body))

        // Execute upload
        let response = try await httpClient.execute(request, timeout: .seconds(60))
        let responseBody = try await response.body.collect(upTo: 1024 * 1024)

        if let htmlString = String(buffer: responseBody) {
            let document = try SwiftSoup.parse(htmlString)

            // Look for submission ID or confirmation
            let confirmationSelectors = ["#lblConfirmation", "#lblSuccessMessage", "#lblSubmissionID"]

            for selector in confirmationSelectors {
                if let element = try? document.select(selector).first() {
                    let text = try element.text()
                    if text.contains("success") || text.contains("submitted") {
                        logger.info("✅ File uploaded successfully")

                        // Extract submission ID if present
                        let regex = try? NSRegularExpression(pattern: "[A-Z]{2,3}-\\d+")
                        if let match = regex?.firstMatch(in: text, range: NSRange(text.startIndex..., in: text)) {
                            if let range = Range(match.range, in: text) {
                                let submissionId = String(text[range])
                                logger.info("Submission ID: \(submissionId)")
                                return submissionId
                            }
                        }

                        return "UPLOADED"
                    }
                }
            }
        }

        logger.warning("Upload completed but no confirmation found")
        return nil
    }

    /// Check claim status
    public func checkClaimStatus(submissionId: String) async throws -> ClaimStatus? {
        logger.info("Checking status for submission: \(submissionId)")

        let statusURL = "\(baseURL)/Provider/ClaimsStatus.aspx"

        var request = HTTPClientRequest(url: statusURL)
        request.method = .GET
        request.headers = buildHeaders()

        let response = try await httpClient.execute(request, timeout: .seconds(30))
        let body = try await response.body.collect(upTo: 1024 * 1024)

        if let htmlString = String(buffer: body) {
            let document = try SwiftSoup.parse(htmlString)

            // Search for the submission ID in tables
            if let table = try? document.select("table").first() {
                let rows = try table.select("tr")

                for row in rows {
                    let cells = try row.select("td")
                    if cells.count > 0 {
                        let cellTexts = try cells.map { try $0.text() }

                        if cellTexts.first(where: { $0.contains(submissionId) }) != nil {
                            return ClaimStatus(
                                submissionId: submissionId,
                                status: cellTexts.count > 1 ? cellTexts[1] : "Unknown",
                                amount: cellTexts.count > 2 ? cellTexts[2] : nil,
                                processingDate: Date()
                            )
                        }
                    }
                }
            }
        }

        return nil
    }

    /// Download rejection report
    public func downloadRejectionReport() async throws -> URL? {
        logger.info("Downloading rejection report...")

        let reportsURL = "\(baseURL)/Provider/Reports.aspx"

        var request = HTTPClientRequest(url: reportsURL)
        request.method = .GET
        request.headers = buildHeaders()

        let response = try await httpClient.execute(request, timeout: .seconds(30))
        let body = try await response.body.collect(upTo: 1024 * 1024 * 10) // 10MB limit for reports

        let filename = "bupa_rejection_\(Date().ISO8601Format()).xlsx"
        let filepath = downloadDir.appendingPathComponent(filename)

        try Data(buffer: body).write(to: filepath)

        logger.info("✅ Downloaded rejection report: \(filepath.lastPathComponent)")
        return filepath
    }

    /// Logout from portal
    public func logout() async throws {
        logger.info("Logging out...")

        let logoutURL = "\(baseURL)/Provider/Logout.aspx"

        var request = HTTPClientRequest(url: logoutURL)
        request.method = .GET
        request.headers = buildHeaders()

        _ = try await httpClient.execute(request, timeout: .seconds(30))

        logger.info("✅ Logged out successfully")
    }

    // MARK: - Helper Methods

    private func buildHeaders() -> HTTPHeaders {
        var headers = HTTPHeaders()
        headers.add(name: "User-Agent", value: "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36")
        headers.add(name: "Accept", value: "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8")

        // Add cookies
        if !cookies.isEmpty {
            let cookieString = cookies.map { "\($0.key)=\($0.value)" }.joined(separator: "; ")
            headers.add(name: "Cookie", value: cookieString)
        }

        return headers
    }

    private func parseCookies(_ setCookieHeader: String) {
        let components = setCookieHeader.components(separatedBy: ";")
        if let firstComponent = components.first {
            let keyValue = firstComponent.components(separatedBy: "=")
            if keyValue.count == 2 {
                cookies[keyValue[0].trimmingCharacters(in: .whitespaces)] = keyValue[1].trimmingCharacters(in: .whitespaces)
            }
        }
    }
}

// MARK: - Supporting Models

public struct ClaimStatus: Codable, Sendable {
    public let submissionId: String
    public let status: String
    public let amount: String?
    public let processingDate: Date?

    enum CodingKeys: String, CodingKey {
        case submissionId = "submission_id"
        case status
        case amount
        case processingDate = "processing_date"
    }
}
