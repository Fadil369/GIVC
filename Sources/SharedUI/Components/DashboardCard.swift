import SwiftUI

/// Reusable dashboard card component
public struct DashboardCard<Content: View>: View {
    let title: String
    let subtitle: String?
    let icon: String?
    let gradient: [Color]
    let content: () -> Content

    public init(
        title: String,
        subtitle: String? = nil,
        icon: String? = nil,
        gradient: [Color] = [.blue, .purple],
        @ViewBuilder content: @escaping () -> Content
    ) {
        self.title = title
        self.subtitle = subtitle
        self.icon = icon
        self.gradient = gradient
        self.content = content
    }

    public var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                if let icon = icon {
                    Image(systemName: icon)
                        .font(.title2)
                        .foregroundStyle(
                            LinearGradient(
                                colors: gradient,
                                startPoint: .topLeading,
                                endPoint: .bottomTrailing
                            )
                        )
                }

                VStack(alignment: .leading, spacing: 4) {
                    Text(title)
                        .font(.headline)
                        .foregroundColor(.primary)

                    if let subtitle = subtitle {
                        Text(subtitle)
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                }

                Spacer()
            }

            content()
        }
        .padding()
        .background(
            RoundedRectangle(cornerRadius: 12)
                .fill(Color(NSColor.controlBackgroundColor))
                .shadow(color: .black.opacity(0.05), radius: 8, x: 0, y: 2)
        )
    }
}

/// KPI Card for displaying key metrics
public struct KPICard: View {
    let title: String
    let value: String
    let icon: String
    let gradient: [Color]
    let trend: Trend?

    public enum Trend {
        case up(String)
        case down(String)
        case neutral

        var icon: String {
            switch self {
            case .up: return "arrow.up.right"
            case .down: return "arrow.down.right"
            case .neutral: return "minus"
            }
        }

        var color: Color {
            switch self {
            case .up: return .green
            case .down: return .red
            case .neutral: return .gray
            }
        }

        var text: String? {
            switch self {
            case .up(let value), .down(let value): return value
            case .neutral: return nil
            }
        }
    }

    public init(
        title: String,
        value: String,
        icon: String,
        gradient: [Color] = [.blue, .purple],
        trend: Trend? = nil
    ) {
        self.title = title
        self.value = value
        self.icon = icon
        self.gradient = gradient
        self.trend = trend
    }

    public var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                Image(systemName: icon)
                    .font(.title3)
                    .foregroundStyle(
                        LinearGradient(
                            colors: gradient,
                            startPoint: .topLeading,
                            endPoint: .bottomTrailing
                        )
                    )

                Spacer()

                if let trend = trend {
                    HStack(spacing: 4) {
                        Image(systemName: trend.icon)
                            .font(.caption)

                        if let text = trend.text {
                            Text(text)
                                .font(.caption2)
                                .fontWeight(.semibold)
                        }
                    }
                    .foregroundColor(trend.color)
                }
            }

            Text(value)
                .font(.system(size: 32, weight: .bold, design: .rounded))
                .foregroundColor(.primary)

            Text(title)
                .font(.subheadline)
                .foregroundColor(.secondary)
        }
        .padding()
        .frame(minWidth: 200, minHeight: 120)
        .background(
            RoundedRectangle(cornerRadius: 12)
                .fill(Color(NSColor.controlBackgroundColor))
                .shadow(color: .black.opacity(0.05), radius: 8, x: 0, y: 2)
        )
    }
}

/// Activity item view
public struct ActivityItem: View {
    let icon: String
    let iconColor: Color
    let title: String
    let subtitle: String

    public init(icon: String, iconColor: Color, title: String, subtitle: String) {
        self.icon = icon
        self.iconColor = iconColor
        self.title = title
        self.subtitle = subtitle
    }

    public var body: some View {
        HStack(spacing: 12) {
            Image(systemName: icon)
                .font(.title3)
                .foregroundColor(.white)
                .frame(width: 40, height: 40)
                .background(
                    Circle()
                        .fill(iconColor)
                )

            VStack(alignment: .leading, spacing: 4) {
                Text(title)
                    .font(.subheadline)
                    .foregroundColor(.primary)

                Text(subtitle)
                    .font(.caption)
                    .foregroundColor(.secondary)
            }

            Spacer()
        }
        .padding(.vertical, 8)
    }
}

#if DEBUG
struct DashboardCard_Previews: PreviewProvider {
    static var previews: some View {
        VStack(spacing: 20) {
            KPICard(
                title: "Total Claims",
                value: "1,247",
                icon: "doc.text.fill",
                gradient: [.blue, .purple],
                trend: .up("+12%")
            )

            KPICard(
                title: "Rejections",
                value: "89",
                icon: "exclamationmark.triangle.fill",
                gradient: [.orange, .red],
                trend: .down("-8%")
            )

            DashboardCard(
                title: "Recent Activity",
                subtitle: "Last 24 hours",
                icon: "clock.fill",
                gradient: [.green, .blue]
            ) {
                VStack(spacing: 8) {
                    ActivityItem(
                        icon: "doc.fill",
                        iconColor: .blue,
                        title: "New claim submitted",
                        subtitle: "5 minutes ago"
                    )

                    ActivityItem(
                        icon: "exclamationmark.circle.fill",
                        iconColor: .red,
                        title: "Rejection alert",
                        subtitle: "15 minutes ago"
                    )
                }
            }
        }
        .padding()
        .frame(width: 400)
    }
}
#endif
