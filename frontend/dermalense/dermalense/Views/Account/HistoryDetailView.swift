//
//  HistoryDetailView.swift
//  dermalense
//
//  Created by Mohammed Abdur Rahman on 2/14/26.
//

import SwiftUI

struct HistoryDetailView: View {
    @Environment(AppState.self) private var appState
    let record: ScanRecord

    @State private var fullScan: SkinScan?
    @State private var isLoading = false

    var body: some View {
        ScrollView {
            VStack(spacing: DLSpacing.lg) {
                // Score header
                scoreHeader

                // Metrics grid (if loaded)
                if let fullScan {
                    metricsSection(fullScan)
                    summarySection(fullScan)
                } else if isLoading {
                    HStack {
                        Spacer()
                        VStack(spacing: DLSpacing.sm) {
                            ProgressView()
                            Text("Loading details...")
                                .font(DLFont.caption)
                                .foregroundStyle(.secondary)
                        }
                        Spacer()
                    }
                    .padding(DLSpacing.xl)
                }

                // Concerns
                concernsSection

                // Form data
                formDataSection
            }
            .padding(DLSpacing.md)
        }
        .navigationTitle("Scan Details")
        .navigationBarTitleDisplayMode(.inline)
        .task {
            await loadFullScan()
        }
    }

    // MARK: - Data Loading

    private func loadFullScan() async {
        guard !appState.userEmail.isEmpty else { return }
        isLoading = true
        do {
            let scan = try await APIService.shared.getScan(
                email: appState.userEmail,
                scanId: record.id.uuidString.lowercased()
            )
            fullScan = scan
            isLoading = false
        } catch {
            isLoading = false
            // Silently fail — we still show the record data
        }
    }

    // MARK: - Score Header

    private var scoreHeader: some View {
        VStack(spacing: DLSpacing.md) {
            ZStack {
                Circle()
                    .stroke(Color(.systemGray5), lineWidth: 10)

                Circle()
                    .trim(from: 0, to: record.overallScore / 100.0)
                    .stroke(
                        scoreGradient,
                        style: StrokeStyle(lineWidth: 10, lineCap: .round)
                    )
                    .rotationEffect(.degrees(-90))

                VStack(spacing: 2) {
                    Text(String(format: "%.1f", record.overallScore))
                        .font(.system(size: 36, weight: .bold, design: .rounded))
                        .foregroundStyle(scoreColor)
                    Text("Overall Score")
                        .font(DLFont.caption)
                        .foregroundStyle(.secondary)
                }
            }
            .frame(width: 140, height: 140)

            Text(record.date, style: .date)
                .font(DLFont.body)
                .foregroundStyle(.secondary)
        }
        .frame(maxWidth: .infinity)
        .padding(DLSpacing.lg)
        .background(Color(.systemGray6))
        .clipShape(RoundedRectangle(cornerRadius: DLRadius.xl))
    }

    // MARK: - Metrics

    private func metricsSection(_ scan: SkinScan) -> some View {
        VStack(alignment: .leading, spacing: DLSpacing.sm) {
            Text("Detailed Breakdown")
                .font(DLFont.headline)

            LazyVGrid(columns: [GridItem(.flexible()), GridItem(.flexible())], spacing: DLSpacing.sm) {
                ForEach(scan.scores) { metric in
                    metricCard(metric)
                }
            }
        }
    }

    private func metricCard(_ metric: SkinMetric) -> some View {
        VStack(alignment: .leading, spacing: DLSpacing.xs) {
            HStack {
                Image(systemName: metric.icon)
                    .font(.system(size: 12))
                    .foregroundStyle(metricColor(metric.color))
                Text(metric.name)
                    .font(DLFont.caption)
                    .fontWeight(.semibold)
                Spacer()
            }

            HStack(alignment: .firstTextBaseline, spacing: 2) {
                Text(String(format: "%.1f", metric.score))
                    .font(.system(size: 18, weight: .bold, design: .rounded))
                Text("%")
                    .font(DLFont.small)
                    .foregroundStyle(.secondary)
            }

            GeometryReader { geo in
                ZStack(alignment: .leading) {
                    RoundedRectangle(cornerRadius: 3)
                        .fill(Color(.systemGray5))
                        .frame(height: 5)
                    RoundedRectangle(cornerRadius: 3)
                        .fill(metricColor(metric.color))
                        .frame(width: geo.size.width * metric.score / 100.0, height: 5)
                }
            }
            .frame(height: 5)

            Text(metric.colorDescription)
                .font(DLFont.small)
                .foregroundStyle(metricColor(metric.color))
        }
        .padding(DLSpacing.sm)
        .background(Color(.systemGray6))
        .clipShape(RoundedRectangle(cornerRadius: DLRadius.md))
    }

    // MARK: - Summary

    private func summarySection(_ scan: SkinScan) -> some View {
        VStack(alignment: .leading, spacing: DLSpacing.sm) {
            HStack {
                Image(systemName: "doc.text.fill")
                    .foregroundStyle(DLColor.primaryFallback)
                Text("AI Summary")
                    .font(DLFont.headline)
            }

            Text(scan.summary)
                .font(DLFont.body)
                .foregroundStyle(.secondary)
                .lineSpacing(4)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(DLSpacing.md)
        .background(Color(.systemGray6))
        .clipShape(RoundedRectangle(cornerRadius: DLRadius.lg))
    }

    // MARK: - Concerns

    private var concernsSection: some View {
        VStack(alignment: .leading, spacing: DLSpacing.sm) {
            Text("Top Concerns")
                .font(DLFont.headline)

            FlowLayout(spacing: DLSpacing.sm) {
                ForEach(record.concerns, id: \.self) { concern in
                    Text(concern)
                        .font(DLFont.caption)
                        .fontWeight(.medium)
                        .padding(.horizontal, 12)
                        .padding(.vertical, 6)
                        .background(
                            Capsule()
                                .fill(DLColor.primaryFallback.opacity(0.1))
                        )
                        .foregroundStyle(DLColor.primaryFallback)
                }
            }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(DLSpacing.md)
        .background(Color(.systemGray6))
        .clipShape(RoundedRectangle(cornerRadius: DLRadius.lg))
    }

    // MARK: - Form Data

    private var formDataSection: some View {
        VStack(alignment: .leading, spacing: DLSpacing.sm) {
            Text("Scan Info")
                .font(DLFont.headline)

            VStack(spacing: 0) {
                formRow(label: "Date", value: record.date.formatted(date: .long, time: .shortened))
                Divider()
                formRow(label: "Overall Score", value: String(format: "%.1f", record.overallScore))
                Divider()
                formRow(label: "Primary Concern", value: record.concerns.first ?? "N/A")
            }
            .background(Color(.systemBackground))
            .clipShape(RoundedRectangle(cornerRadius: DLRadius.md))
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(DLSpacing.md)
        .background(Color(.systemGray6))
        .clipShape(RoundedRectangle(cornerRadius: DLRadius.lg))
    }

    private func formRow(label: String, value: String) -> some View {
        HStack {
            Text(label)
                .font(DLFont.caption)
                .foregroundStyle(.secondary)
            Spacer()
            Text(value)
                .font(DLFont.body)
                .fontWeight(.medium)
        }
        .padding(DLSpacing.md)
    }

    // MARK: - Helpers

    private func metricColor(_ colorString: String) -> Color {
        switch colorString.lowercased() {
        case "green": return .green
        case "yellow": return .yellow
        case "orange": return .orange
        case "red": return .red
        default: return .gray
        }
    }

    private var scoreColor: Color {
        if record.overallScore >= 80 { return .green }
        else if record.overallScore >= 65 { return .mint }
        else if record.overallScore >= 50 { return .orange }
        else { return .red }
    }

    private var scoreGradient: LinearGradient {
        if record.overallScore >= 75 {
            return LinearGradient(colors: [.green, .mint], startPoint: .leading, endPoint: .trailing)
        } else if record.overallScore >= 50 {
            return LinearGradient(colors: [.yellow, .orange], startPoint: .leading, endPoint: .trailing)
        } else {
            return LinearGradient(colors: [.orange, .red], startPoint: .leading, endPoint: .trailing)
        }
    }
}

#Preview {
    NavigationStack {
        HistoryDetailView(record: ScanRecord.sampleHistory[0])
            .environment(AppState())
    }
}
