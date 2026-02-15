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
    @State private var email = ""
    @State private var isCreating = false
    @State private var errorMessage: String?
    @FocusState private var focusedField: Field?

    private enum Field { case username, email }

    private var isFormValid: Bool {
        !username.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty
            && email.contains("@") && email.contains(".")
    }

    var body: some View {
        ScrollView {
            VStack(spacing: DLSpacing.xl) {
                Spacer(minLength: DLSpacing.xxl)

                // MARK: - Branding
                brandingHeader

                // MARK: - Form
                formFields

                // MARK: - Error
                if let errorMessage {
                    Text(errorMessage)
                        .font(DLFont.caption)
                        .foregroundStyle(.red)
                        .multilineTextAlignment(.center)
                        .transition(.opacity)
                }

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

    // MARK: - Form Fields

    private var formFields: some View {
        VStack(spacing: DLSpacing.md) {
            // Username
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
                        .focused($focusedField, equals: .username)
                        .submitLabel(.next)
                        .onSubmit { focusedField = .email }
                }
                .padding(DLSpacing.md)
                .background(Color(.systemGray6))
                .clipShape(RoundedRectangle(cornerRadius: DLRadius.md))
            }

            // Email
            VStack(alignment: .leading, spacing: DLSpacing.xs) {
                Text("Email")
                    .font(DLFont.caption)
                    .fontWeight(.semibold)
                    .foregroundStyle(.secondary)
                    .textCase(.uppercase)

                HStack(spacing: DLSpacing.sm) {
                    Image(systemName: "envelope")
                        .font(.system(size: 14))
                        .foregroundStyle(DLColor.primaryFallback)
                        .frame(width: 20)

                    TextField("your@email.com", text: $email)
                        .font(DLFont.body)
                        .textContentType(.emailAddress)
                        .keyboardType(.emailAddress)
                        .autocapitalization(.none)
                        .focused($focusedField, equals: .email)
                        .submitLabel(.done)
                        .onSubmit {
                            focusedField = nil
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
                if isCreating {
                    ProgressView()
                        .tint(.white)
                } else {
                    Text("Get Started")
                        .fontWeight(.semibold)
                    Image(systemName: "arrow.right")
                }
            }
            .frame(maxWidth: .infinity)
            .padding(.vertical, 16)
            .background(
                RoundedRectangle(cornerRadius: DLRadius.md)
                    .fill(isFormValid && !isCreating ? DLColor.primaryFallback : Color(.systemGray4))
            )
            .foregroundStyle(.white)
        }
        .disabled(!isFormValid || isCreating)
        .animation(.easeInOut(duration: 0.2), value: isFormValid)
    }

    // MARK: - Actions

    private func createAccount() {
        let trimmedUsername = username.trimmingCharacters(in: .whitespacesAndNewlines)
        let trimmedEmail = email.trimmingCharacters(in: .whitespacesAndNewlines).lowercased()

        isCreating = true
        errorMessage = nil

        Task {
            do {
                // Auto-creates profile on backend if it doesn't exist
                var profile = try await APIService.shared.getProfile(email: trimmedEmail)

                // Update with user-provided username if different
                if profile.username != trimmedUsername {
                    profile = try await APIService.shared.updateProfile(
                        email: trimmedEmail,
                        name: nil,
                        username: trimmedUsername,
                        avatarSystemName: nil
                    )
                }

                appState.user = profile
                appState.userEmail = trimmedEmail
                appState.savedIsOnboarded = true

                withAnimation(.easeInOut(duration: 0.4)) {
                    appState.isOnboarded = true
                }
            } catch {
                withAnimation {
                    errorMessage = error.localizedDescription
                }
            }
            isCreating = false
        }
    }
}

#Preview {
    OnboardingView()
        .environment(AppState())
}
