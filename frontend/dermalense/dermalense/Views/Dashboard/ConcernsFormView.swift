//
//  ConcernsFormView.swift
//  dermalense
//
//  Created by Mohammed Abdur Rahman on 2/14/26.
//

import SwiftUI

struct ConcernsFormView: View {
    var onSubmit: (SkinConcernsForm) -> Void

    @State private var form = SkinConcernsForm()

    private var isFormValid: Bool {
        !form.primaryConcerns.isEmpty && !form.biggestInsecurity.isEmpty
    }

    var body: some View {
        ScrollView {
            VStack(spacing: DLSpacing.lg) {
                headerSection
                primaryConcernsSection
                insecuritySection
                skinTypeSection
                sensitivitySection
                notesSection
                submitButton
            }
            .padding(DLSpacing.md)
        }
    }

    // MARK: - Header

    private var headerSection: some View {
        VStack(spacing: DLSpacing.sm) {
            Image(systemName: "list.clipboard.fill")
                .font(.system(size: 40))
                .foregroundStyle(DLColor.secondaryFallback)

            Text("Tell Us About Your Skin")
                .font(DLFont.title)
                .foregroundStyle(DLColor.primaryFallback)

            Text("Help our AI understand your priorities so we can create the most effective plan for you.")
                .font(DLFont.body)
                .foregroundStyle(.secondary)
                .multilineTextAlignment(.center)
                .padding(.horizontal, DLSpacing.md)
        }
    }

    // MARK: - Primary Concerns

    private var primaryConcernsSection: some View {
        VStack(alignment: .leading, spacing: DLSpacing.sm) {
            sectionLabel("Primary Concerns", subtitle: "Select all that apply")

            FlowLayout(spacing: DLSpacing.sm) {
                ForEach(SkinConcernsForm.availableConcerns, id: \.self) { concern in
                    concernChip(concern)
                }
            }
        }
        .padding(DLSpacing.md)
        .background(Color(.systemGray6))
        .clipShape(RoundedRectangle(cornerRadius: DLRadius.lg))
    }

    private func concernChip(_ concern: String) -> some View {
        let isSelected = form.primaryConcerns.contains(concern)
        return Button {
            withAnimation(.spring(response: 0.25)) {
                if isSelected {
                    form.primaryConcerns.remove(concern)
                } else {
                    form.primaryConcerns.insert(concern)
                }
            }
        } label: {
            Text(concern)
                .font(DLFont.caption)
                .fontWeight(isSelected ? .semibold : .regular)
                .padding(.horizontal, 14)
                .padding(.vertical, 8)
                .background(
                    Capsule()
                        .fill(isSelected ? DLColor.primaryFallback : Color(.systemBackground))
                )
                .foregroundStyle(isSelected ? .white : .primary)
                .overlay(
                    Capsule()
                        .strokeBorder(isSelected ? Color.clear : Color(.systemGray4), lineWidth: 1)
                )
        }
        .buttonStyle(.plain)
    }

    // MARK: - Biggest Insecurity

    private var insecuritySection: some View {
        VStack(alignment: .leading, spacing: DLSpacing.sm) {
            sectionLabel("Biggest Insecurity", subtitle: "What bothers you the most?")

            TextField("e.g., Acne scars on my cheeks", text: $form.biggestInsecurity)
                .font(DLFont.body)
                .padding(DLSpacing.md)
                .background(Color(.systemBackground))
                .clipShape(RoundedRectangle(cornerRadius: DLRadius.md))
        }
        .padding(DLSpacing.md)
        .background(Color(.systemGray6))
        .clipShape(RoundedRectangle(cornerRadius: DLRadius.lg))
    }

    // MARK: - Skin Type

    private var skinTypeSection: some View {
        VStack(alignment: .leading, spacing: DLSpacing.sm) {
            sectionLabel("Skin Type", subtitle: nil)

            HStack(spacing: DLSpacing.sm) {
                ForEach(SkinConcernsForm.skinTypes, id: \.self) { type in
                    skinTypeButton(type)
                }
            }
        }
        .padding(DLSpacing.md)
        .background(Color(.systemGray6))
        .clipShape(RoundedRectangle(cornerRadius: DLRadius.lg))
    }

    private func skinTypeButton(_ type: String) -> some View {
        let isSelected = form.skinType == type
        return Button {
            withAnimation(.spring(response: 0.25)) { form.skinType = type }
        } label: {
            Text(type)
                .font(.system(size: 12, weight: isSelected ? .semibold : .regular, design: .rounded))
                .frame(maxWidth: .infinity)
                .padding(.vertical, 10)
                .background(
                    RoundedRectangle(cornerRadius: DLRadius.sm)
                        .fill(isSelected ? DLColor.primaryFallback : Color(.systemBackground))
                )
                .foregroundStyle(isSelected ? .white : .primary)
        }
        .buttonStyle(.plain)
    }

    // MARK: - Sensitivity

    private var sensitivitySection: some View {
        VStack(alignment: .leading, spacing: DLSpacing.sm) {
            sectionLabel("Sensitivity Level", subtitle: nil)

            Picker("Sensitivity", selection: $form.sensitivityLevel) {
                ForEach(SkinConcernsForm.sensitivityLevels, id: \.self) { level in
                    Text(level).tag(level)
                }
            }
            .pickerStyle(.segmented)
        }
        .padding(DLSpacing.md)
        .background(Color(.systemGray6))
        .clipShape(RoundedRectangle(cornerRadius: DLRadius.lg))
    }

    // MARK: - Additional Notes

    private var notesSection: some View {
        VStack(alignment: .leading, spacing: DLSpacing.sm) {
            sectionLabel("Additional Notes", subtitle: "Optional")

            TextField("Anything else we should know...", text: $form.additionalNotes, axis: .vertical)
                .font(DLFont.body)
                .lineLimit(3...6)
                .padding(DLSpacing.md)
                .background(Color(.systemBackground))
                .clipShape(RoundedRectangle(cornerRadius: DLRadius.md))
        }
        .padding(DLSpacing.md)
        .background(Color(.systemGray6))
        .clipShape(RoundedRectangle(cornerRadius: DLRadius.lg))
    }

    // MARK: - Submit

    private var submitButton: some View {
        Button {
            onSubmit(form)
        } label: {
            HStack(spacing: DLSpacing.sm) {
                Image(systemName: "camera.fill")
                Text("Continue to Photos")
                    .fontWeight(.semibold)
            }
            .frame(maxWidth: .infinity)
            .padding(.vertical, 16)
            .background(
                RoundedRectangle(cornerRadius: DLRadius.md)
                    .fill(isFormValid ? DLColor.secondaryFallback : Color(.systemGray4))
            )
            .foregroundStyle(.white)
        }
        .disabled(!isFormValid)
        .padding(.bottom, DLSpacing.xl)
    }

    // MARK: - Helpers

    private func sectionLabel(_ title: String, subtitle: String?) -> some View {
        VStack(alignment: .leading, spacing: 2) {
            Text(title)
                .font(DLFont.headline)
            if let subtitle {
                Text(subtitle)
                    .font(DLFont.caption)
                    .foregroundStyle(.secondary)
            }
        }
    }
}

// MARK: - Flow Layout

struct FlowLayout: Layout {
    var spacing: CGFloat = 8

    func sizeThatFits(proposal: ProposedViewSize, subviews: Subviews, cache: inout ()) -> CGSize {
        let result = layout(in: proposal.width ?? 0, subviews: subviews)
        return result.size
    }

    func placeSubviews(in bounds: CGRect, proposal: ProposedViewSize, subviews: Subviews, cache: inout ()) {
        let result = layout(in: bounds.width, subviews: subviews)
        for (index, position) in result.positions.enumerated() {
            subviews[index].place(at: CGPoint(x: bounds.minX + position.x, y: bounds.minY + position.y), proposal: .unspecified)
        }
    }

    private func layout(in width: CGFloat, subviews: Subviews) -> (size: CGSize, positions: [CGPoint]) {
        var positions: [CGPoint] = []
        var currentX: CGFloat = 0
        var currentY: CGFloat = 0
        var lineHeight: CGFloat = 0

        for subview in subviews {
            let size = subview.sizeThatFits(.unspecified)
            if currentX + size.width > width, currentX > 0 {
                currentX = 0
                currentY += lineHeight + spacing
                lineHeight = 0
            }
            positions.append(CGPoint(x: currentX, y: currentY))
            lineHeight = max(lineHeight, size.height)
            currentX += size.width + spacing
        }

        return (CGSize(width: width, height: currentY + lineHeight), positions)
    }
}

#Preview {
    ConcernsFormView(onSubmit: { _ in })
}
