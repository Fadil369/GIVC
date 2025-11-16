# ClaimLinc-GIVC Swift Makefile

.PHONY: help build run test clean server macos ios docker docs

# Default target
help:
	@echo "ClaimLinc-GIVC Swift Build System"
	@echo ""
	@echo "Available targets:"
	@echo "  build         - Build all targets"
	@echo "  server        - Run backend API server"
	@echo "  macos         - Run macOS application"
	@echo "  ios           - Build iOS application"
	@echo "  test          - Run all tests"
	@echo "  test-cov      - Run tests with coverage"
	@echo "  clean         - Clean build artifacts"
	@echo "  docker        - Build and run Docker containers"
	@echo "  docs          - Generate documentation"
	@echo "  lint          - Run SwiftLint"
	@echo "  format        - Format code with swift-format"
	@echo ""

# Build all targets
build:
	@echo "Building all targets..."
	swift build

# Build release
build-release:
	@echo "Building release..."
	swift build -c release

# Run backend server
server:
	@echo "Starting ClaimLinc API Server..."
	swift run ClaimLinc-Server

# Run macOS app
macos:
	@echo "Starting macOS application..."
	swift run ClaimLinc-macOS

# Build iOS app (requires Xcode)
ios:
	@echo "Building iOS application..."
	xcodebuild -scheme ClaimLinc-iOS -destination 'platform=iOS Simulator,name=iPhone 15 Pro' build

# Run all tests
test:
	@echo "Running tests..."
	swift test

# Run tests with coverage
test-cov:
	@echo "Running tests with coverage..."
	swift test --enable-code-coverage
	@echo "Coverage report generated at .build/debug/codecov"

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	swift package clean
	rm -rf .build
	rm -rf *.xcodeproj

# Generate Xcode project
xcode:
	@echo "Generating Xcode project..."
	swift package generate-xcodeproj
	open ClaimLinc-GIVC.xcodeproj

# Run SwiftLint
lint:
	@echo "Running SwiftLint..."
	@if command -v swiftlint > /dev/null; then \
		swiftlint; \
	else \
		echo "SwiftLint not installed. Install with: brew install swiftlint"; \
	fi

# Format code
format:
	@echo "Formatting code..."
	@if command -v swift-format > /dev/null; then \
		find Sources -name "*.swift" -exec swift-format -i {} \;; \
	else \
		echo "swift-format not installed. Install with: brew install swift-format"; \
	fi

# Docker operations
docker:
	@echo "Building Docker containers..."
	docker-compose up -d

docker-build:
	@echo "Building Docker images..."
	docker-compose build

docker-stop:
	@echo "Stopping Docker containers..."
	docker-compose down

# Database operations
db-setup:
	@echo "Setting up database..."
	createdb claimlinc || true
	@echo "Database created"

db-migrate:
	@echo "Running migrations..."
	swift run ClaimLinc-Server migrate --yes

db-reset:
	@echo "Resetting database..."
	dropdb claimlinc || true
	createdb claimlinc
	swift run ClaimLinc-Server migrate --yes

# Redis operations
redis-start:
	@echo "Starting Redis..."
	redis-server

redis-cli:
	@echo "Starting Redis CLI..."
	redis-cli

# Development helpers
dev-setup:
	@echo "Setting up development environment..."
	@echo "1. Installing dependencies..."
	swift package resolve
	@echo "2. Setting up database..."
	make db-setup
	@echo "3. Creating .env file..."
	@if [ ! -f .env ]; then cp .env.example .env; fi
	@echo "✅ Development environment ready!"
	@echo "Edit .env with your credentials, then run 'make server'"

dev-run:
	@echo "Starting development environment..."
	@make -j2 redis-start server

# Documentation
docs:
	@echo "Generating documentation..."
	swift package generate-documentation
	@echo "Documentation available at .build/plugins/Swift-DocC/outputs"

# Install tools
install-tools:
	@echo "Installing development tools..."
	brew install swiftlint swift-format
	@echo "Tools installed!"

# Archive for distribution
archive-macos:
	@echo "Archiving macOS app..."
	xcodebuild -scheme ClaimLinc-macOS -configuration Release archive -archivePath ./build/ClaimLinc-macOS.xcarchive

archive-ios:
	@echo "Archiving iOS app..."
	xcodebuild -scheme ClaimLinc-iOS -configuration Release -sdk iphoneos archive -archivePath ./build/ClaimLinc-iOS.xcarchive

# Version info
version:
	@echo "ClaimLinc-GIVC Swift Version Information"
	@echo "========================================="
	@echo "Swift Version:"
	@swift --version
	@echo ""
	@echo "Xcode Version:"
	@xcodebuild -version
	@echo ""
	@echo "Package Dependencies:"
	@swift package show-dependencies

# Health check
health:
	@echo "System Health Check"
	@echo "==================="
	@echo -n "PostgreSQL: "
	@pg_isready || echo "❌ Not running"
	@echo -n "Redis: "
	@redis-cli ping > /dev/null 2>&1 && echo "✅ Running" || echo "❌ Not running"
	@echo -n "Swift: "
	@swift --version | head -1
	@echo -n "Vapor CLI: "
	@vapor --version 2>/dev/null || echo "Not installed (optional)"
