import SwiftUI

@main
struct ClaimLinc_macOS: App {
    @StateObject private var appState = AppState()

    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(appState)
                .frame(minWidth: 1200, minHeight: 800)
        }
        .commands {
            CommandGroup(replacing: .newItem) {
                Button("New Claim") {
                    appState.showNewClaimSheet = true
                }
                .keyboardShortcut("n", modifiers: .command)
            }

            CommandGroup(after: .sidebar) {
                Button("Toggle Sidebar") {
                    NSApp.keyWindow?.contentViewController?.view.window?.toggleSidebar(nil)
                }
                .keyboardShortcut("s", modifiers: [.command, .option])
            }
        }

        #if os(macOS)
        Settings {
            SettingsView()
        }
        #endif
    }
}

// MARK: - Content View

struct ContentView: View {
    @EnvironmentObject var appState: AppState
    @State private var selectedView: SidebarItem = .dashboard

    var body: some View {
        NavigationSplitView {
            Sidebar(selection: $selectedView)
        } detail: {
            DetailView(selectedView: selectedView)
        }
    }
}

// MARK: - Sidebar

enum SidebarItem: String, CaseIterable, Identifiable {
    case dashboard = "Dashboard"
    case claims = "Claims"
    case analytics = "Analytics"
    case automation = "Automation"
    case reports = "Reports"
    case settings = "Settings"

    var id: String { rawValue }

    var icon: String {
        switch self {
        case .dashboard: return "chart.bar.fill"
        case .claims: return "doc.text.fill"
        case .analytics: return "chart.line.uptrend.xyaxis"
        case .automation: return "gearshape.2.fill"
        case .reports: return "doc.richtext.fill"
        case .settings: return "gear"
        }
    }
}

struct Sidebar: View {
    @Binding var selection: SidebarItem

    var body: some View {
        List(SidebarItem.allCases, selection: $selection) { item in
            NavigationLink(value: item) {
                Label(item.rawValue, systemImage: item.icon)
            }
        }
        .navigationTitle("ClaimLinc")
        .frame(minWidth: 200)
    }
}

// MARK: - Detail View

struct DetailView: View {
    let selectedView: SidebarItem

    var body: some View {
        Group {
            switch selectedView {
            case .dashboard:
                DashboardView()
            case .claims:
                ClaimsView()
            case .analytics:
                AnalyticsView()
            case .automation:
                AutomationView()
            case .reports:
                ReportsView()
            case .settings:
                SettingsView()
            }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
    }
}

// MARK: - Dashboard View

struct DashboardView: View {
    @EnvironmentObject var appState: AppState
    @State private var kpiData = KPIData.sample

    var body: some View {
        ScrollView {
            VStack(spacing: 20) {
                // Header
                HStack {
                    VStack(alignment: .leading, spacing: 4) {
                        Text("Dashboard")
                            .font(.largeTitle)
                            .fontWeight(.bold)

                        Text("Welcome back, Dr. Fadil")
                            .font(.subheadline)
                            .foregroundColor(.secondary)
                    }

                    Spacer()

                    Button(action: { kpiData = KPIData.sample }) {
                        Label("Refresh", systemImage: "arrow.clockwise")
                    }
                    .buttonStyle(.bordered)
                }
                .padding(.horizontal)

                // KPI Cards
                LazyVGrid(columns: [
                    GridItem(.flexible()),
                    GridItem(.flexible()),
                    GridItem(.flexible()),
                    GridItem(.flexible())
                ], spacing: 20) {
                    KPICard(
                        title: "Total Claims",
                        value: kpiData.totalClaims.formatted(),
                        icon: "doc.text.fill",
                        gradient: [.blue, .purple],
                        trend: .up("+12%")
                    )

                    KPICard(
                        title: "Rejections",
                        value: kpiData.totalRejections.formatted(),
                        icon: "exclamationmark.triangle.fill",
                        gradient: [.orange, .red],
                        trend: .down("-8%")
                    )

                    KPICard(
                        title: "Approved",
                        value: kpiData.approvedClaims.formatted(),
                        icon: "checkmark.circle.fill",
                        gradient: [.green, .teal],
                        trend: .up("+5%")
                    )

                    KPICard(
                        title: "Total Amount",
                        value: "SAR \(kpiData.totalAmount.formatted())",
                        icon: "dollarsign.circle.fill",
                        gradient: [.purple, .pink],
                        trend: .up("+18%")
                    )
                }
                .padding(.horizontal)

                // Recent Activity
                DashboardCard(
                    title: "Recent Activity",
                    subtitle: "Last 24 hours",
                    icon: "clock.fill",
                    gradient: [.blue, .purple]
                ) {
                    VStack(spacing: 12) {
                        ForEach(Activity.samples) { activity in
                            ActivityItem(
                                icon: activity.icon,
                                iconColor: activity.color,
                                title: activity.title,
                                subtitle: activity.time
                            )
                        }
                    }
                }
                .padding(.horizontal)
            }
            .padding(.vertical)
        }
    }
}

// MARK: - Other Views (Placeholders)

struct ClaimsView: View {
    var body: some View {
        VStack {
            Text("Claims Management")
                .font(.largeTitle)
                .fontWeight(.bold)
            Text("Manage and track all claims")
                .foregroundColor(.secondary)
        }
    }
}

struct AnalyticsView: View {
    var body: some View {
        VStack {
            Text("Analytics")
                .font(.largeTitle)
                .fontWeight(.bold)
            Text("View insights and trends")
                .foregroundColor(.secondary)
        }
    }
}

struct AutomationView: View {
    var body: some View {
        VStack {
            Text("Portal Automation")
                .font(.largeTitle)
                .fontWeight(.bold)
            Text("Manage automated submissions")
                .foregroundColor(.secondary)
        }
    }
}

struct ReportsView: View {
    var body: some View {
        VStack {
            Text("Reports")
                .font(.largeTitle)
                .fontWeight(.bold)
            Text("Generate and view reports")
                .foregroundColor(.secondary)
        }
    }
}

struct SettingsView: View {
    var body: some View {
        VStack {
            Text("Settings")
                .font(.largeTitle)
                .fontWeight(.bold)
            Text("Configure application settings")
                .foregroundColor(.secondary)
        }
    }
}

// MARK: - App State

class AppState: ObservableObject {
    @Published var showNewClaimSheet = false
    @Published var isProcessing = false
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
        Activity(icon: "doc.fill", color: .blue, title: "New claim submission from Riyadh branch", time: "5 min ago"),
        Activity(icon: "exclamationmark.circle.fill", color: .red, title: "Rejection alert: 15 claims from Bupa", time: "15 min ago"),
        Activity(icon: "checkmark.circle.fill", color: .green, title: "Resubmission successful: 23 claims approved", time: "1 hour ago"),
        Activity(icon: "person.badge.plus.fill", color: .purple, title: "New team member: Sarah Ahmed (Unaizah)", time: "2 hours ago")
    ]
}
