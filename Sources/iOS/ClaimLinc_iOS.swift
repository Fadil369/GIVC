import SwiftUI

@main
struct ClaimLinc_iOS: App {
    @StateObject private var appState = AppState()

    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(appState)
        }
    }
}

// MARK: - Content View

struct ContentView: View {
    @EnvironmentObject var appState: AppState
    @State private var selectedTab: Tab = .dashboard

    enum Tab {
        case dashboard
        case claims
        case analytics
        case more
    }

    var body: some View {
        TabView(selection: $selectedTab) {
            DashboardView()
                .tabItem {
                    Label("Dashboard", systemImage: "chart.bar.fill")
                }
                .tag(Tab.dashboard)

            ClaimsView()
                .tabItem {
                    Label("Claims", systemImage: "doc.text.fill")
                }
                .tag(Tab.claims)

            AnalyticsView()
                .tabItem {
                    Label("Analytics", systemImage: "chart.line.uptrend.xyaxis")
                }
                .tag(Tab.analytics)

            MoreView()
                .tabItem {
                    Label("More", systemImage: "ellipsis")
                }
                .tag(Tab.more)
        }
    }
}

// MARK: - Dashboard View

struct DashboardView: View {
    @State private var kpiData = KPIData.sample

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(spacing: 20) {
                    // Welcome Header
                    VStack(alignment: .leading, spacing: 8) {
                        Text("Welcome back,")
                            .font(.title3)
                            .foregroundColor(.secondary)

                        Text("Dr. Fadil")
                            .font(.largeTitle)
                            .fontWeight(.bold)
                    }
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .padding(.horizontal)

                    // KPI Cards
                    LazyVGrid(columns: [
                        GridItem(.flexible()),
                        GridItem(.flexible())
                    ], spacing: 16) {
                        KPICardCompact(
                            title: "Total Claims",
                            value: kpiData.totalClaims.formatted(),
                            icon: "doc.text.fill",
                            color: .blue,
                            trend: "+12%"
                        )

                        KPICardCompact(
                            title: "Rejections",
                            value: kpiData.totalRejections.formatted(),
                            icon: "exclamationmark.triangle.fill",
                            color: .red,
                            trend: "-8%"
                        )

                        KPICardCompact(
                            title: "Approved",
                            value: kpiData.approvedClaims.formatted(),
                            icon: "checkmark.circle.fill",
                            color: .green,
                            trend: "+5%"
                        )

                        KPICardCompact(
                            title: "Amount",
                            value: "\(kpiData.totalAmount / 1000)K",
                            icon: "dollarsign.circle.fill",
                            color: .purple,
                            trend: "+18%"
                        )
                    }
                    .padding(.horizontal)

                    // Recent Activity
                    VStack(alignment: .leading, spacing: 12) {
                        Text("Recent Activity")
                            .font(.headline)
                            .padding(.horizontal)

                        VStack(spacing: 0) {
                            ForEach(Activity.samples) { activity in
                                ActivityRow(activity: activity)
                                    .padding(.horizontal)
                                    .padding(.vertical, 12)

                                if activity.id != Activity.samples.last?.id {
                                    Divider()
                                        .padding(.leading, 60)
                                }
                            }
                        }
                        .background(
                            RoundedRectangle(cornerRadius: 12)
                                .fill(Color(.systemBackground))
                                .shadow(color: .black.opacity(0.05), radius: 8)
                        )
                        .padding(.horizontal)
                    }

                    // Quick Actions
                    VStack(alignment: .leading, spacing: 12) {
                        Text("Quick Actions")
                            .font(.headline)
                            .padding(.horizontal)

                        LazyVGrid(columns: [
                            GridItem(.flexible()),
                            GridItem(.flexible())
                        ], spacing: 12) {
                            QuickActionButton(icon: "doc.badge.plus", title: "New Claim", color: .blue)
                            QuickActionButton(icon: "arrow.up.doc.fill", title: "Upload", color: .green)
                            QuickActionButton(icon: "chart.bar.doc.horizontal", title: "Reports", color: .orange)
                            QuickActionButton(icon: "gearshape.2.fill", title: "Automation", color: .purple)
                        }
                        .padding(.horizontal)
                    }
                }
                .padding(.vertical)
            }
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(action: { kpiData = KPIData.sample }) {
                        Image(systemName: "arrow.clockwise")
                    }
                }
            }
        }
    }
}

// MARK: - Compact KPI Card for iOS

struct KPICardCompact: View {
    let title: String
    let value: String
    let icon: String
    let color: Color
    let trend: String?

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                Image(systemName: icon)
                    .font(.title3)
                    .foregroundColor(color)

                Spacer()

                if let trend = trend {
                    Text(trend)
                        .font(.caption)
                        .fontWeight(.semibold)
                        .foregroundColor(trend.hasPrefix("+") ? .green : .red)
                }
            }

            Text(value)
                .font(.system(size: 28, weight: .bold, design: .rounded))

            Text(title)
                .font(.caption)
                .foregroundColor(.secondary)
        }
        .padding()
        .frame(height: 120)
        .background(
            RoundedRectangle(cornerRadius: 12)
                .fill(Color(.systemBackground))
                .shadow(color: .black.opacity(0.05), radius: 8)
        )
    }
}

// MARK: - Activity Row

struct ActivityRow: View {
    let activity: Activity

    var body: some View {
        HStack(spacing: 12) {
            Image(systemName: activity.icon)
                .font(.body)
                .foregroundColor(.white)
                .frame(width: 36, height: 36)
                .background(Circle().fill(activity.color))

            VStack(alignment: .leading, spacing: 4) {
                Text(activity.title)
                    .font(.subheadline)
                    .lineLimit(2)

                Text(activity.time)
                    .font(.caption)
                    .foregroundColor(.secondary)
            }

            Spacer()
        }
    }
}

// MARK: - Quick Action Button

struct QuickActionButton: View {
    let icon: String
    let title: String
    let color: Color

    var body: some View {
        Button(action: {}) {
            VStack(spacing: 8) {
                Image(systemName: icon)
                    .font(.title2)
                    .foregroundColor(.white)
                    .frame(width: 50, height: 50)
                    .background(
                        Circle()
                            .fill(
                                LinearGradient(
                                    colors: [color, color.opacity(0.7)],
                                    startPoint: .topLeading,
                                    endPoint: .bottomTrailing
                                )
                            )
                    )

                Text(title)
                    .font(.caption)
                    .foregroundColor(.primary)
            }
            .frame(maxWidth: .infinity)
            .padding(.vertical, 12)
            .background(
                RoundedRectangle(cornerRadius: 12)
                    .fill(Color(.systemBackground))
                    .shadow(color: .black.opacity(0.05), radius: 8)
            )
        }
        .buttonStyle(.plain)
    }
}

// MARK: - Other Views

struct ClaimsView: View {
    var body: some View {
        NavigationStack {
            List {
                ForEach(0..<20) { index in
                    ClaimRow(
                        claimId: "CL-2025-\(1000 + index)",
                        patient: "Patient \(index + 1)",
                        amount: "SAR \((index + 1) * 1000)",
                        status: index % 3 == 0 ? "Approved" : (index % 3 == 1 ? "Pending" : "Rejected")
                    )
                }
            }
            .navigationTitle("Claims")
        }
    }
}

struct ClaimRow: View {
    let claimId: String
    let patient: String
    let amount: String
    let status: String

    var statusColor: Color {
        switch status {
        case "Approved": return .green
        case "Rejected": return .red
        default: return .orange
        }
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                Text(claimId)
                    .font(.headline)

                Spacer()

                Text(status)
                    .font(.caption)
                    .fontWeight(.semibold)
                    .foregroundColor(.white)
                    .padding(.horizontal, 8)
                    .padding(.vertical, 4)
                    .background(Capsule().fill(statusColor))
            }

            HStack {
                Text(patient)
                    .font(.subheadline)
                    .foregroundColor(.secondary)

                Spacer()

                Text(amount)
                    .font(.subheadline)
                    .fontWeight(.semibold)
            }
        }
        .padding(.vertical, 4)
    }
}

struct AnalyticsView: View {
    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(spacing: 20) {
                    Text("Analytics Dashboard")
                        .font(.title2)
                        .fontWeight(.bold)

                    Text("Charts and insights coming soon...")
                        .foregroundColor(.secondary)
                }
                .padding()
            }
            .navigationTitle("Analytics")
        }
    }
}

struct MoreView: View {
    var body: some View {
        NavigationStack {
            List {
                Section("Portal Automation") {
                    NavigationLink("Bupa Arabia") {
                        Text("Bupa Automation")
                    }
                    NavigationLink("GlobeMed") {
                        Text("GlobeMed Automation")
                    }
                    NavigationLink("Waseel") {
                        Text("Waseel Automation")
                    }
                }

                Section("Reports") {
                    NavigationLink("Monthly Reports") {
                        Text("Monthly Reports")
                    }
                    NavigationLink("Rejection Analysis") {
                        Text("Rejection Analysis")
                    }
                }

                Section("Settings") {
                    NavigationLink("Preferences") {
                        Text("Preferences")
                    }
                    NavigationLink("About") {
                        Text("About ClaimLinc")
                    }
                }
            }
            .navigationTitle("More")
        }
    }
}

// MARK: - App State

class AppState: ObservableObject {
    @Published var isProcessing = false
    @Published var selectedClaim: String?
}

// MARK: - Sample Data

struct KPIData {
    var totalClaims: Int
    var totalRejections: Int
    var approvedClaims: Int
    var totalAmount: Int

    static let sample = KPIData(
        totalClaims: 1247,
        totalRejections: 89,
        approvedClaims: 1048,
        totalAmount: 3_254_780
    )
}

struct Activity: Identifiable {
    let id = UUID()
    let icon: String
    let color: Color
    let title: String
    let time: String

    static let samples = [
        Activity(icon: "doc.fill", color: .blue, title: "New claim from Riyadh", time: "5 min ago"),
        Activity(icon: "exclamationmark.circle.fill", color: .red, title: "15 claims rejected", time: "15 min ago"),
        Activity(icon: "checkmark.circle.fill", color: .green, title: "23 claims approved", time: "1 hour ago"),
        Activity(icon: "person.badge.plus.fill", color: .purple, title: "New team member added", time: "2 hours ago")
    ]
}

#Preview {
    ContentView()
        .environmentObject(AppState())
}
