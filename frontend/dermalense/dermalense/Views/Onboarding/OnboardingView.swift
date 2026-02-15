//
//  OnboardingView.swift
//  dermalense
//
//  Created by Mohammed Abdur Rahman on 2/14/26.
//

import SwiftUI

struct OnboardingView: View {
    @Environment(AppState.self) private var appState

    @State private var username = ""
    @FocusState private var isUsernameFocused: Bool

    private var isFormValid: Bool {
        !username.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty
    }

    var body: some View {
        ScrollView {
            VStack(spacing: DLSpacing.xl) {
                Spacer(minLength: DLSpacing.xxl)

                // MARK: - Branding
                brandingHeader

                // MARK: - Form
                formField

                // MARK: - Get Started
                getStartedButton

                Spacer(minLength: DLSpacing.lg)
            }
            .padding(.horizontal, DLSpacing.lg)
        }
        .background(Color(.systemBackground))
    }

    // MARK: - Branding Header

    private var brandingHeader: some View {
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
                    .frame(width: 90, height: 90)

                Image(systemName: "faceid")
                    .font(.system(size: 40))
                    .foregroundStyle(.white)
            }

            Text("DermaLens")
                .font(.system(size: 32, weight: .bold, design: .rounded))
                .foregroundStyle(DLColor.primaryFallback)

            Text("Your AI-powered skincare companion.\nCreate an account to get started.")
                .font(DLFont.body)
                .foregroundStyle(.secondary)
                .multilineTextAlignment(.center)
        }
    }

    // MARK: - Form Field

    private var formField: some View {
        VStack(spacing: DLSpacing.md) {
            VStack(alignment: .leading, spacing: DLSpacing.xs) {
                Text("Username")
                    .font(DLFont.caption)
                    .fontWeight(.semibold)
                    .foregroundStyle(.secondary)
                    .textCase(.uppercase)

                HStack(spacing: DLSpacing.sm) {
                    Image(systemName: "at")
                        .font(.system(size: 14))
                        .foregroundStyle(DLColor.primaryFallback)
                        .frame(width: 20)

                    TextField("Choose a username", text: $username)
                        .font(DLFont.body)
                        .textContentType(.username)
                        .autocapitalization(.none)
                        .focused($isUsernameFocused)
                        .submitLabel(.done)
                        .onSubmit {
                            isUsernameFocused = false
                            if isFormValid { createAccount() }
                        }
                }
                .padding(DLSpacing.md)
                .background(Color(.systemGray6))
                .clipShape(RoundedRectangle(cornerRadius: DLRadius.md))
            }
        }
    }

    // MARK: - Get Started Button

    private var getStartedButton: some View {
        Button {
            createAccount()
        } label: {
            HStack(spacing: DLSpacing.sm) {
                Text("Get Started")
                    .fontWeight(.semibold)
                Image(systemName: "arrow.right")
            }
            .frame(maxWidth: .infinity)
            .padding(.vertical, 16)
            .background(
                RoundedRectangle(cornerRadius: DLRadius.md)
                    .fill(isFormValid ? DLColor.primaryFallback : Color(.systemGray4))
            )
            .foregroundStyle(.white)
        }
        .disabled(!isFormValid)
        .animation(.easeInOut(duration: 0.2), value: isFormValid)
    }

    // MARK: - Actions

    private func createAccount() {
        let trimmedUsername = username.trimmingCharacters(in: .whitespacesAndNewlines)

        appState.user = UserProfile(
            id: UUID(),
            name: "",
            email: "",
            username: trimmedUsername,
            avatarSystemName: "person.crop.circle.fill"
        )

        withAnimation(.easeInOut(duration: 0.4)) {
            appState.isOnboarded = true
        }
    }
}

#Preview {
    OnboardingView()
        .environment(AppState())
}
