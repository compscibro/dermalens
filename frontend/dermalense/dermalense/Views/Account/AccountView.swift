//
//  AccountView.swift
//  dermalense
//
//  Created by Mohammed Abdur Rahman on 2/14/26.
//

import SwiftUI

struct AccountView: View {
    @Environment(AppState.self) private var appState
    @State private var showEditProfile = false

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(spacing: DLSpacing.lg) {
                    profileHeader
                    profileInfoCard
                    historySection
                }
                .padding(DLSpacing.md)
            }
            .navigationTitle("Account")
            .navigationBarTitleDisplayMode(.large)
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Button {
                        showEditProfile = true
                    } label: {
                        Text("Edit")
                            .font(DLFont.body)
                            .fontWeight(.semibold)
                    }
                    .tint(DLColor.primaryFallback)
                }
            }
            .sheet(isPresented: $showEditProfile) {
                EditProfileView()
            }
        }
    }

    // MARK: - Profile Header

    private var profileHeader: some View {
        VStack(spacing: DLSpacing.md) {
            ZStack {
                Circle()
                    .fill(
                        LinearGradient(
                            colors: [DLColor.primaryFallback, DLColor.secondaryFallback],
                            startPoint: .topLeading,
                            endPoint: .bottomTrailing
                        )
                    )
                    .frame(width: 100, height: 100)

                Image(systemName: appState.user.avatarSystemName)
                    .font(.system(size: 44))
                    .foregroundStyle(.white)
            }

            VStack(spacing: 4) {
                Text(appState.user.name)
                    .font(DLFont.title)

                Text("@\(appState.user.username)")
                    .font(DLFont.body)
                    .foregroundStyle(.secondary)
            }

            // Stats row
            HStack(spacing: DLSpacing.xl) {
                statItem(value: "\(appState.scanHistory.count)", label: "Scans")
                statDivider
                statItem(value: latestScore, label: "Latest Score")
                statDivider
                statItem(value: streak, label: "Streak")
            }
            .padding(.vertical, DLSpacing.md)
            .padding(.horizontal, DLSpacing.lg)
            .background(Color(.systemGray6))
            .clipShape(RoundedRectangle(cornerRadius: DLRadius.lg))
        }
    }

    private func statItem(value: String, label: String) -> some View {
        VStack(spacing: 4) {
            Text(value)
                .font(.system(size: 20, weight: .bold, design: .rounded))
                .foregroundStyle(DLColor.primaryFallback)
            Text(label)
                .font(DLFont.small)
                .foregroundStyle(.secondary)
        }
    }

    private var statDivider: some View {
        Rectangle()
            .fill(Color(.systemGray4))
            .frame(width: 1, height: 30)
    }

    private var latestScore: String {
        if let latest = appState.scanHistory.first {
            return String(format: "%.0f", latest.overallScore)
        }
        return "--"
    }

    private var streak: String {
        return "\(appState.scanHistory.count)w"
    }

    // MARK: - Profile Info Card

    private var profileInfoCard: some View {
        VStack(spacing: 0) {
            infoRow(icon: "person.fill", label: "Name", value: appState.user.name)
            Divider().padding(.leading, 48)
            infoRow(icon: "envelope.fill", label: "Email", value: appState.user.email)
            Divider().padding(.leading, 48)
            infoRow(icon: "at", label: "Username", value: "@\(appState.user.username)")
        }
        .background(Color(.systemGray6))
        .clipShape(RoundedRectangle(cornerRadius: DLRadius.lg))
    }

    private func infoRow(icon: String, label: String, value: String) -> some View {
        HStack(spacing: DLSpacing.md) {
            Image(systemName: icon)
                .font(.system(size: 14))
                .foregroundStyle(DLColor.primaryFallback)
                .frame(width: 24)

            VStack(alignment: .leading, spacing: 2) {
                Text(label)
                    .font(DLFont.small)
                    .foregroundStyle(.secondary)
                    .textCase(.uppercase)
                Text(value)
                    .font(DLFont.body)
            }

            Spacer()
        }
        .padding(DLSpacing.md)
    }

    // MARK: - History Section

    private var historySection: some View {
        VStack(alignment: .leading, spacing: DLSpacing.md) {
            HStack {
                Text("Scan History")
                    .font(DLFont.headline)
                Spacer()
                NavigationLink {
                    FullHistoryView()
                } label: {
                    Text("See All")
                        .font(DLFont.caption)
                        .foregroundStyle(DLColor.primaryFallback)
                }
            }

            if appState.scanHistory.isEmpty {
                emptyHistoryView
            } else {
                ForEach(appState.scanHistory) { record in
                    NavigationLink {
                        HistoryDetailView(record: record)
                    } label: {
                        historyRow(record)
                    }
                    .buttonStyle(.plain)
                }
            }
        }
    }

    private func historyRow(_ record: ScanRecord) -> some View {
        HStack(spacing: DLSpacing.md) {
            // Thumbnail
            RoundedRectangle(cornerRadius: DLRadius.sm)
                .fill(scoreColor(for: record.overallScore).opacity(0.15))
                .frame(width: 50, height: 50)
                .overlay(
                    Image(systemName: record.thumbnailSystemName)
                        .font(.system(size: 22))
                        .foregroundStyle(scoreColor(for: record.overallScore))
                )

            VStack(alignment: .leading, spacing: 4) {
                Text(record.date, style: .date)
                    .font(DLFont.body)
                    .fontWeight(.medium)
                    .foregroundStyle(.primary)

                HStack(spacing: 4) {
                    ForEach(record.concerns.prefix(3), id: \.self) { concern in
                        Text(concern)
                            .font(.system(size: 10, weight: .medium))
                            .padding(.horizontal, 6)
                            .padding(.vertical, 2)
                            .background(
                                Capsule()
                                    .fill(Color(.systemGray5))
                            )
                            .foregroundStyle(.secondary)
                    }
                }
            }

            Spacer()

            VStack(alignment: .trailing, spacing: 2) {
                Text(String(format: "%.0f", record.overallScore))
                    .font(.system(size: 22, weight: .bold, design: .rounded))
                    .foregroundStyle(scoreColor(for: record.overallScore))
                Text("Score")
                    .font(DLFont.small)
                    .foregroundStyle(.secondary)
            }

            Image(systemName: "chevron.right")
                .font(.system(size: 12))
                .foregroundStyle(.tertiary)
        }
        .padding(DLSpacing.md)
        .background(Color(.systemGray6))
        .clipShape(RoundedRectangle(cornerRadius: DLRadius.md))
    }

    private var emptyHistoryView: some View {
        VStack(spacing: DLSpacing.sm) {
            Image(systemName: "clock.arrow.circlepath")
                .font(.system(size: 36))
                .foregroundStyle(.tertiary)
            Text("No scans yet")
                .font(DLFont.body)
                .foregroundStyle(.secondary)
            Text("Complete your first scan to see history here.")
                .font(DLFont.caption)
                .foregroundStyle(.tertiary)
        }
        .frame(maxWidth: .infinity)
        .padding(DLSpacing.xl)
        .background(Color(.systemGray6))
        .clipShape(RoundedRectangle(cornerRadius: DLRadius.lg))
    }

    // MARK: - Helpers

    private func scoreColor(for score: Double) -> Color {
        if score >= 80 { return .green }
        else if score >= 65 { return .mint }
        else if score >= 50 { return .orange }
        else { return .red }
    }
}

#Preview {
    AccountView()
        .environment(AppState())
}
