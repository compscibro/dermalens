//
//  HistoryDetailView.swift
//  dermalense
//
//  Created by Mohammed Abdur Rahman on 2/14/26.
//

import SwiftUI

struct HistoryDetailView: View {
    let record: ScanRecord

    var body: some View {
        ScrollView {
            VStack(spacing: DLSpacing.lg) {
                // Score header
                scoreHeader

                // Photos section
                photosSection

                // Concerns
                concernsSection

                // Form data placeholder
                formDataSection
            }
            .padding(DLSpacing.md)
        }
        .navigationTitle("Scan Details")
        .navigationBarTitleDisplayMode(.inline)
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

    // MARK: - Photos

    private var photosSection: some View {
        VStack(alignment: .leading, spacing: DLSpacing.sm) {
            Text("Photos")
                .font(DLFont.headline)

            HStack(spacing: DLSpacing.sm) {
                photoPlaceholder("Front")
                photoPlaceholder("Left")
                photoPlaceholder("Right")
            }
        }
    }

    private func photoPlaceholder(_ label: String) -> some View {
        VStack(spacing: DLSpacing.xs) {
            RoundedRectangle(cornerRadius: DLRadius.md)
                .fill(Color(.systemGray6))
                .frame(height: 120)
                .overlay(
                    VStack(spacing: 4) {
                        Image(systemName: "photo")
                            .font(.system(size: 24))
                            .foregroundStyle(.tertiary)
                        Text(label)
                            .font(DLFont.small)
                            .foregroundStyle(.tertiary)
                    }
                )
        }
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
            Text("Form Responses")
                .font(DLFont.headline)

            VStack(spacing: 0) {
                formRow(label: "Skin Type", value: "Combination")
                Divider()
                formRow(label: "Sensitivity", value: "Moderate")
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
    }
}
