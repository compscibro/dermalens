//
//  SkinAnalysisView.swift
//  dermalense
//
//  Created by Mohammed Abdur Rahman on 2/14/26.
//

import SwiftUI

struct SkinAnalysisView: View {
    var scan: SkinScan?
    var onNext: () -> Void

    @State private var animateScores = false

    var body: some View {
        Group {
            if let scan {
                scanContent(scan)
            } else {
                ContentUnavailableView(
                    "No Scan Yet",
                    systemImage: "waveform.path.ecg",
                    description: Text("Upload your photos to see your skin analysis results.")
                )
            }
        }
    }

    private func scanContent(_ scan: SkinScan) -> some View {
        ScrollView {
            VStack(spacing: DLSpacing.lg) {
                overallScoreCard(scan)
                metricsGrid(scan)
                summaryCard(scan)
                aiDisclaimer
                nextButton
            }
            .padding(DLSpacing.md)
        }
        .onAppear {
            withAnimation(.easeOut(duration: 1.0).delay(0.3)) {
                animateScores = true
            }
        }
    }

    // MARK: - Overall Score

    private func overallScoreCard(_ scan: SkinScan) -> some View {
        VStack(spacing: DLSpacing.md) {
            Text("Your Skin Score")
                .font(DLFont.headline)
                .foregroundStyle(.secondary)

            ZStack {
                Circle()
                    .stroke(Color(.systemGray5), lineWidth: 12)

                Circle()
                    .trim(from: 0, to: animateScores ? scan.overallScore / 100.0 : 0)
                    .stroke(
                        scoreGradient(for: scan.overallScore),
                        style: StrokeStyle(lineWidth: 12, lineCap: .round)
                    )
                    .rotationEffect(.degrees(-90))

                VStack(spacing: 2) {
                    Text(animateScores ? String(format: "%.1f", scan.overallScore) : "0.0")
                        .font(.system(size: 42, weight: .bold, design: .rounded))
                        .foregroundStyle(DLColor.primaryFallback)
                        .contentTransition(.numericText())

                    Text("out of 100")
                        .font(DLFont.caption)
                        .foregroundStyle(.secondary)
                }
            }
            .frame(width: 160, height: 160)

            Text(scoreLabel(for: scan.overallScore))
                .font(DLFont.headline)
                .foregroundStyle(scoreColor(for: scan.overallScore))
                .padding(.horizontal, 16)
                .padding(.vertical, 6)
                .background(
                    Capsule()
                        .fill(scoreColor(for: scan.overallScore).opacity(0.12))
                )
        }
        .frame(maxWidth: .infinity)
        .padding(DLSpacing.lg)
        .background(Color(.systemGray6))
        .clipShape(RoundedRectangle(cornerRadius: DLRadius.xl))
    }

    // MARK: - Metrics Grid

    private func metricsGrid(_ scan: SkinScan) -> some View {
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
        VStack(alignment: .leading, spacing: DLSpacing.sm) {
            HStack {
                Image(systemName: metric.icon)
                    .font(.system(size: 14))
                    .foregroundStyle(metricColor(metric.color))

                Text(metric.name)
                    .font(DLFont.caption)
                    .fontWeight(.semibold)

                Spacer()
            }

            HStack(alignment: .firstTextBaseline, spacing: 2) {
                Text(animateScores ? String(format: "%.1f", metric.score) : "0.0")
                    .font(.system(size: 22, weight: .bold, design: .rounded))
                    .foregroundStyle(.primary)
                    .contentTransition(.numericText())

                Text("%")
                    .font(DLFont.caption)
                    .foregroundStyle(.secondary)
            }

            GeometryReader { geo in
                ZStack(alignment: .leading) {
                    RoundedRectangle(cornerRadius: 3)
                        .fill(Color(.systemGray5))
                        .frame(height: 6)

                    RoundedRectangle(cornerRadius: 3)
                        .fill(metricColor(metric.color))
                        .frame(width: animateScores ? geo.size.width * metric.score / 100.0 : 0, height: 6)
                }
            }
            .frame(height: 6)

            Text(metric.colorDescription)
                .font(DLFont.small)
                .foregroundStyle(metricColor(metric.color))
        }
        .padding(DLSpacing.md)
        .background(Color(.systemGray6))
        .clipShape(RoundedRectangle(cornerRadius: DLRadius.md))
    }

    // MARK: - Summary

    private func summaryCard(_ scan: SkinScan) -> some View {
        VStack(alignment: .leading, spacing: DLSpacing.sm) {
            HStack {
                Image(systemName: "doc.text.fill")
                    .foregroundStyle(DLColor.primaryFallback)
                Text("Skin Summary")
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

    // MARK: - Disclaimer

    private var aiDisclaimer: some View {
        HStack(spacing: DLSpacing.xs) {
            Image(systemName: "info.circle")
                .font(.system(size: 11))
            Text("DermaLens isn't human. It can make mistakes, so double check important info. For medical advice, consult with medical professionals.")
                .font(.system(size: 11))
        }
        .foregroundStyle(.tertiary)
        .frame(maxWidth: .infinity)
        .padding(.vertical, DLSpacing.xs)
    }

    // MARK: - Next

    private var nextButton: some View {
        Button {
            onNext()
        } label: {
            HStack(spacing: DLSpacing.sm) {
                Image(systemName: "clock.fill")
                Text("View Routine Plan")
                    .fontWeight(.semibold)
            }
            .frame(maxWidth: .infinity)
            .padding(.vertical, 16)
            .background(
                RoundedRectangle(cornerRadius: DLRadius.md)
                    .fill(DLColor.primaryFallback)
            )
            .foregroundStyle(.white)
        }
        .padding(.bottom, DLSpacing.xl)
    }

    // MARK: - Helpers

    private func scoreGradient(for score: Double) -> LinearGradient {
        if score >= 75 {
            return LinearGradient(colors: [.green, .mint], startPoint: .leading, endPoint: .trailing)
        } else if score >= 50 {
            return LinearGradient(colors: [.yellow, .orange], startPoint: .leading, endPoint: .trailing)
        } else {
            return LinearGradient(colors: [.orange, .red], startPoint: .leading, endPoint: .trailing)
        }
    }

    private func scoreLabel(for score: Double) -> String {
        if score >= 80 { return "Excellent" }
        else if score >= 65 { return "Good" }
        else if score >= 50 { return "Fair" }
        else { return "Needs Work" }
    }

    private func scoreColor(for score: Double) -> Color {
        if score >= 80 { return .green }
        else if score >= 65 { return .mint }
        else if score >= 50 { return .orange }
        else { return .red }
    }

    private func metricColor(_ colorString: String) -> Color {
        switch colorString.lowercased() {
        case "green": return .green
        case "yellow": return .yellow
        case "orange": return .orange
        case "red": return .red
        default: return .gray
        }
    }
}

#Preview {
    SkinAnalysisView(scan: .sample, onNext: {})
}
