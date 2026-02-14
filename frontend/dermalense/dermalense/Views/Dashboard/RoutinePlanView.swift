//
//  RoutinePlanView.swift
//  dermalense
//
//  Created by Mohammed Abdur Rahman on 2/14/26.
//

import SwiftUI

struct RoutinePlanView: View {
    var onNext: () -> Void

    @State private var plan: RoutinePlan = .sample
    @State private var selectedSection: RoutineSection = .morning

    enum RoutineSection: String, CaseIterable, Identifiable {
        case morning = "Morning"
        case evening = "Evening"
        case weekly = "Weekly"

        var id: String { rawValue }

        var icon: String {
            switch self {
            case .morning: return "sun.horizon.fill"
            case .evening: return "moon.stars.fill"
            case .weekly: return "calendar"
            }
        }

        var color: Color {
            switch self {
            case .morning: return .orange
            case .evening: return .indigo
            case .weekly: return .teal
            }
        }
    }

    var body: some View {
        ScrollView {
            VStack(spacing: DLSpacing.lg) {
                headerSection
                sectionPicker
                routineSteps
                chatButton
            }
            .padding(DLSpacing.md)
        }
    }

    // MARK: - Header

    private var headerSection: some View {
        VStack(spacing: DLSpacing.sm) {
            Image(systemName: "sparkles")
                .font(.system(size: 40))
                .foregroundStyle(DLColor.accentFallback)

            Text("Your Routine Plan")
                .font(DLFont.title)
                .foregroundStyle(DLColor.primaryFallback)

            Text("Personalized skincare routine based on your scan results and concerns.")
                .font(DLFont.body)
                .foregroundStyle(.secondary)
                .multilineTextAlignment(.center)
                .padding(.horizontal, DLSpacing.md)
        }
    }

    // MARK: - Section Picker

    private var sectionPicker: some View {
        HStack(spacing: DLSpacing.sm) {
            ForEach(RoutineSection.allCases) { section in
                sectionTab(section)
            }
        }
    }

    private func sectionTab(_ section: RoutineSection) -> some View {
        let isSelected = selectedSection == section
        return Button {
            withAnimation(.spring(response: 0.3)) { selectedSection = section }
        } label: {
            VStack(spacing: 6) {
                Image(systemName: section.icon)
                    .font(.system(size: 20))
                Text(section.rawValue)
                    .font(DLFont.caption)
                    .fontWeight(.semibold)
            }
            .frame(maxWidth: .infinity)
            .padding(.vertical, 14)
            .background(
                RoundedRectangle(cornerRadius: DLRadius.md)
                    .fill(isSelected ? section.color.opacity(0.15) : Color(.systemGray6))
            )
            .overlay(
                RoundedRectangle(cornerRadius: DLRadius.md)
                    .strokeBorder(isSelected ? section.color : Color.clear, lineWidth: 2)
            )
            .foregroundStyle(isSelected ? section.color : .secondary)
        }
        .buttonStyle(.plain)
    }

    // MARK: - Steps

    private var routineSteps: some View {
        let steps: [RoutineStep] = {
            switch selectedSection {
            case .morning: return plan.morningSteps
            case .evening: return plan.eveningSteps
            case .weekly: return plan.weeklySteps
            }
        }()

        return VStack(spacing: 0) {
            ForEach(Array(steps.enumerated()), id: \.element.id) { index, step in
                stepRow(step, isLast: index == steps.count - 1)
            }
        }
    }

    private func stepRow(_ step: RoutineStep, isLast: Bool) -> some View {
        HStack(alignment: .top, spacing: DLSpacing.md) {
            // Timeline dot + line
            VStack(spacing: 0) {
                Circle()
                    .fill(selectedSection.color)
                    .frame(width: 12, height: 12)
                    .padding(.top, 4)

                if !isLast {
                    Rectangle()
                        .fill(selectedSection.color.opacity(0.3))
                        .frame(width: 2)
                }
            }
            .frame(width: 12)

            // Content
            VStack(alignment: .leading, spacing: DLSpacing.sm) {
                HStack {
                    Image(systemName: step.icon)
                        .font(.system(size: 14))
                        .foregroundStyle(selectedSection.color)

                    Text("Step \(step.order)")
                        .font(DLFont.small)
                        .foregroundStyle(.secondary)
                        .textCase(.uppercase)
                }

                Text(step.name)
                    .font(DLFont.headline)

                Text(step.description)
                    .font(DLFont.body)
                    .foregroundStyle(.secondary)
                    .lineSpacing(2)

                HStack(spacing: 4) {
                    Image(systemName: "tag.fill")
                        .font(.system(size: 10))
                    Text(step.productSuggestion)
                        .font(DLFont.caption)
                }
                .foregroundStyle(DLColor.primaryFallback)
                .padding(.horizontal, 10)
                .padding(.vertical, 6)
                .background(
                    Capsule()
                        .fill(DLColor.primaryFallback.opacity(0.1))
                )
            }
            .padding(.bottom, DLSpacing.lg)
        }
    }

    // MARK: - Chat CTA

    private var chatButton: some View {
        Button {
            onNext()
        } label: {
            HStack(spacing: DLSpacing.sm) {
                Image(systemName: "message.fill")
                VStack(alignment: .leading, spacing: 2) {
                    Text("Have Questions?")
                        .fontWeight(.semibold)
                    Text("Chat with AI about your routine")
                        .font(DLFont.caption)
                        .opacity(0.8)
                }
                Spacer()
                Image(systemName: "chevron.right")
            }
            .frame(maxWidth: .infinity, alignment: .leading)
            .padding(DLSpacing.md)
            .background(
                RoundedRectangle(cornerRadius: DLRadius.lg)
                    .fill(
                        LinearGradient(
                            colors: [DLColor.primaryFallback, DLColor.secondaryFallback],
                            startPoint: .leading,
                            endPoint: .trailing
                        )
                    )
            )
            .foregroundStyle(.white)
        }
        .padding(.bottom, DLSpacing.xl)
    }
}

#Preview {
    RoutinePlanView(onNext: {})
}
