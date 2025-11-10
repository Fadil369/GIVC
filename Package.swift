// swift-tools-version: 5.9
// The swift-tools-version declares the minimum version of Swift required to build this package.

import PackageDescription

let package = Package(
    name: "ClaimLinc-GIVC",
    platforms: [
        .macOS(.v14),
        .iOS(.v17)
    ],
    products: [
        // Vapor Backend API Server
        .executable(
            name: "ClaimLinc-Server",
            targets: ["ClaimLinc-Server"]
        ),
        // macOS Application
        .executable(
            name: "ClaimLinc-macOS",
            targets: ["ClaimLinc-macOS"]
        ),
        // iOS Application (framework for Xcode project)
        .library(
            name: "ClaimLinc-iOS-Core",
            targets: ["ClaimLinc-iOS-Core"]
        ),
        // Shared Core Library
        .library(
            name: "ClaimLinc-Core",
            targets: ["ClaimLinc-Core"]
        ),
        // Portal Automation Library
        .library(
            name: "ClaimLinc-Automation",
            targets: ["ClaimLinc-Automation"]
        ),
        // Data Processing Library
        .library(
            name: "ClaimLinc-DataProcessing",
            targets: ["ClaimLinc-DataProcessing"]
        )
    ],
    dependencies: [
        // Vapor - Swift web framework
        .package(url: "https://github.com/vapor/vapor.git", from: "4.89.0"),

        // Fluent - ORM for database
        .package(url: "https://github.com/vapor/fluent.git", from: "4.8.0"),
        .package(url: "https://github.com/vapor/fluent-postgres-driver.git", from: "2.7.0"),

        // Redis client
        .package(url: "https://github.com/vapor/redis.git", from: "4.10.0"),

        // WebDriver for browser automation
        .package(url: "https://github.com/tid-kijyun/WebDriverAgent.git", branch: "master"),

        // AsyncHTTPClient for network requests
        .package(url: "https://github.com/swift-server/async-http-client.git", from: "1.19.0"),

        // SwiftSoup for HTML parsing
        .package(url: "https://github.com/scinfu/SwiftSoup.git", from: "2.6.0"),

        // Queues for async task processing
        .package(url: "https://github.com/vapor/queues.git", from: "1.13.0"),
        .package(url: "https://github.com/vapor/queues-redis-driver.git", from: "1.1.0"),

        // JWT for authentication
        .package(url: "https://github.com/vapor/jwt.git", from: "4.2.0"),

        // FHIR Models for healthcare data
        .package(url: "https://github.com/apple/FHIRModels.git", from: "0.5.0"),

        // Logging
        .package(url: "https://github.com/apple/swift-log.git", from: "1.5.3"),

        // Crypto for security
        .package(url: "https://github.com/apple/swift-crypto.git", from: "3.0.0")
    ],
    targets: [
        // ==================== SHARED CORE ====================
        .target(
            name: "ClaimLinc-Core",
            dependencies: [
                .product(name: "Logging", package: "swift-log"),
                .product(name: "Crypto", package: "swift-crypto"),
                .product(name: "ModelsR4", package: "FHIRModels")
            ],
            path: "Sources/Core"
        ),

        // ==================== BACKEND API SERVER ====================
        .executableTarget(
            name: "ClaimLinc-Server",
            dependencies: [
                "ClaimLinc-Core",
                "ClaimLinc-DataProcessing",
                "ClaimLinc-Automation",
                .product(name: "Vapor", package: "vapor"),
                .product(name: "Fluent", package: "fluent"),
                .product(name: "FluentPostgresDriver", package: "fluent-postgres-driver"),
                .product(name: "Redis", package: "redis"),
                .product(name: "Queues", package: "queues"),
                .product(name: "QueuesRedisDriver", package: "queues-redis-driver"),
                .product(name: "JWT", package: "jwt")
            ],
            path: "Sources/Server"
        ),

        // ==================== DATA PROCESSING ====================
        .target(
            name: "ClaimLinc-DataProcessing",
            dependencies: [
                "ClaimLinc-Core",
                .product(name: "Logging", package: "swift-log")
            ],
            path: "Sources/DataProcessing"
        ),

        // ==================== PORTAL AUTOMATION ====================
        .target(
            name: "ClaimLinc-Automation",
            dependencies: [
                "ClaimLinc-Core",
                .product(name: "AsyncHTTPClient", package: "async-http-client"),
                .product(name: "SwiftSoup", package: "SwiftSoup"),
                .product(name: "Logging", package: "swift-log")
            ],
            path: "Sources/Automation"
        ),

        // ==================== macOS APPLICATION ====================
        .executableTarget(
            name: "ClaimLinc-macOS",
            dependencies: [
                "ClaimLinc-Core",
                "ClaimLinc-Shared-UI",
                .product(name: "AsyncHTTPClient", package: "async-http-client")
            ],
            path: "Sources/macOS"
        ),

        // ==================== iOS CORE ====================
        .target(
            name: "ClaimLinc-iOS-Core",
            dependencies: [
                "ClaimLinc-Core",
                "ClaimLinc-Shared-UI",
                .product(name: "AsyncHTTPClient", package: "async-http-client")
            ],
            path: "Sources/iOS"
        ),

        // ==================== SHARED UI COMPONENTS ====================
        .target(
            name: "ClaimLinc-Shared-UI",
            dependencies: [
                "ClaimLinc-Core"
            ],
            path: "Sources/SharedUI"
        ),

        // ==================== TESTS ====================
        .testTarget(
            name: "ClaimLinc-Tests",
            dependencies: [
                "ClaimLinc-Core",
                "ClaimLinc-Server",
                "ClaimLinc-DataProcessing",
                "ClaimLinc-Automation",
                .product(name: "XCTVapor", package: "vapor")
            ],
            path: "Tests"
        )
    ]
)
