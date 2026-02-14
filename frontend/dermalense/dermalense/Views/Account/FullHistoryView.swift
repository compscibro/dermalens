//
//  FullHistoryView.swift
//  dermalense
//
//  Created by Mohammed Abdur Rahman on 2/14/26.
//

import SwiftUI

struct FullHistoryView: View {
    @Environment(AppState.self) private var appState

    var body: some View {
        ScrollView {
            VStack(spacing: DLSpacing.md) {
                // Score trend chart placeholder
                scoreTrendCard

                // All records
                ForEach(appState.scanHistory) { record in
                    NavigationLink {
                        HistoryDetailView(record: record)
                    } label: {
                        historyCard(record)
                    }
                    .buttonStyle(.plain)
                }
            }
            .padding(DLSpacing.md)
        }
        .navigationTitle("Scan History")
        .navigationBarTitleDisplayMode(.large)
    }

    // MARK: - Score Trend

    private var scoreTrendCard: some View {
        VStack(alignment: .leading, spacing: DLSpacing.sm) {
            Text("Score Trend")
                .font(DLFont.headline)

            // Simple bar chart
            HStack(alignment: .bottom, spacing: DLSpacing.sm) {
                ForEach(appState.scanHistory.reversed()) { record in
                    VStack(spacing: 4) {
                        Text(String(format: "%.0f", record.overallScore))
                            .font(.system(size: 10, weight: .semibold, design: .rounded))
                            .foregroundStyle(.secondary)

                        RoundedRectangle(cornerRadius: 4)
                            .fill(
                                LinearGradient(
                                    colors: [scoreColor(for: record.overallScore).opacity(0.6), scoreColor(for: record.overallScore)],
                                    startPoint: .bottom,
                                    endPoint: .top
                                )
                            )
                            .frame(height: max(20, CGFloat(record.overallScore) * 1.2))

                        Text(record.date, format: .dateTime.month(.abbreviated).day())
                            .font(.system(size: 9))
                            .foregroundStyle(.tertiary)
                    }
                    .frame(maxWidth: .infinity)
                }
            }
            .frame(height: 140)
            .padding(.top, DLSpacing.sm)
        }
        .padding(DLSpacing.md)
        .background(Color(.systemGray6))
        .clipShape(RoundedRectangle(cornerRadius: DLRadius.lg))
    }

    // MARK: - History Card

    private func historyCard(_ record: ScanRecord) -> some View {
        HStack(spacing: DLSpacing.md) {
            RoundedRectangle(cornerRadius: DLRadius.sm)
                .fill(scoreColor(for: record.overallScore).opacity(0.15))
                .frame(width: 56, height: 56)
                .overlay(
                    VStack(spacing: 2) {
                        Text(String(format: "%.0f", record.overallScore))
                            .font(.system(size: 18, weight: .bold, design: .rounded))
                            .foregroundStyle(scoreColor(for: record.overallScore))
                        Text("Score")
                            .font(.system(size: 9))
                            .foregroundStyle(.secondary)
                    }
                )

            VStack(alignment: .leading, spacing: 6) {
                Text(record.date, style: .date)
                    .font(DLFont.body)
                    .fontWeight(.medium)

                HStack(spacing: 4) {
                    ForEach(record.concerns, id: \.self) { concern in
                        Text(concern)
                            .font(.system(size: 10, weight: .medium))
                            .padding(.horizontal, 6)
                            .padding(.vertical, 2)
                            .background(Capsule().fill(Color(.systemGray5)))
                            .foregroundStyle(.secondary)
                    }
                }
            }

            Spacer()

            Image(systemName: "chevron.right")
                .font(.system(size: 12))
                .foregroundStyle(.tertiary)
        }
        .padding(DLSpacing.md)
        .background(Color(.systemGray6))
        .clipShape(RoundedRectangle(cornerRadius: DLRadius.md))
    }

    private func scoreColor(for score: Double) -> Color {
        if score >= 80 { return .green }
        else if score >= 65 { return .mint }
        else if score >= 50 { return .orange }
        else { return .red }
    }
}

#Preview {
    NavigationStack {
        FullHistoryView()
            .environment(AppState())
    }
}
