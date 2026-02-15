//
//  EditProfileView.swift
//  dermalense
//
//  Created by Mohammed Abdur Rahman on 2/14/26.
//

import SwiftUI

struct EditProfileView: View {
    @Environment(AppState.self) private var appState
    @Environment(\.dismiss) private var dismiss

    @State private var name: String = ""
    @State private var username: String = ""
    @State private var isSaving = false
    @State private var errorMessage: String?

    var body: some View {
        NavigationStack {
            Form {
                Section {
                    HStack {
                        Spacer()
                        ZStack {
                            Circle()
                                .fill(
                                    LinearGradient(
                                        colors: [DLColor.primaryFallback, DLColor.secondaryFallback],
                                        startPoint: .topLeading,
                                        endPoint: .bottomTrailing
                                    )
                                )
                                .frame(width: 80, height: 80)

                            Image(systemName: "person.crop.circle.fill")
                                .font(.system(size: 36))
                                .foregroundStyle(.white)
                        }
                        .overlay(alignment: .bottomTrailing) {
                            Image(systemName: "camera.circle.fill")
                                .font(.system(size: 24))
                                .foregroundStyle(DLColor.primaryFallback)
                                .background(Circle().fill(.white).frame(width: 20, height: 20))
                        }
                        Spacer()
                    }
                    .listRowBackground(Color.clear)
                }

                Section("Personal Information") {
                    HStack {
                        Image(systemName: "person.fill")
                            .foregroundStyle(DLColor.primaryFallback)
                            .frame(width: 24)
                        TextField("Name", text: $name)
                    }

                    HStack {
                        Image(systemName: "envelope.fill")
                            .foregroundStyle(DLColor.primaryFallback)
                            .frame(width: 24)
                        Text(appState.user.email.isEmpty ? appState.userEmail : appState.user.email)
                            .foregroundStyle(.secondary)
                    }

                    HStack {
                        Image(systemName: "at")
                            .foregroundStyle(DLColor.primaryFallback)
                            .frame(width: 24)
                        TextField("Username", text: $username)
                            .autocapitalization(.none)
                    }
                }

                if let errorMessage {
                    Section {
                        Text(errorMessage)
                            .font(DLFont.caption)
                            .foregroundStyle(.red)
                    }
                }

                Section {
                    Button {
                        Task { await saveProfile() }
                    } label: {
                        HStack {
                            Spacer()
                            if isSaving {
                                ProgressView()
                                    .tint(DLColor.primaryFallback)
                            } else {
                                Text("Save Changes")
                                    .fontWeight(.semibold)
                                    .foregroundStyle(DLColor.primaryFallback)
                            }
                            Spacer()
                        }
                    }
                    .disabled(isSaving || name.trimmingCharacters(in: .whitespaces).isEmpty)
                }
            }
            .navigationTitle("Edit Profile")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .topBarLeading) {
                    Button("Cancel") { dismiss() }
                        .tint(.secondary)
                }
            }
            .onAppear {
                name = appState.user.name
                username = appState.user.username
            }
        }
    }

    private func saveProfile() async {
        isSaving = true
        errorMessage = nil

        do {
            let updated = try await APIService.shared.updateProfile(
                email: appState.userEmail,
                name: name.trimmingCharacters(in: .whitespaces),
                username: username.trimmingCharacters(in: .whitespaces),
                avatarSystemName: nil
            )
            appState.user = updated
            isSaving = false
            dismiss()
        } catch {
            isSaving = false
            errorMessage = "Failed to save: \(error.localizedDescription)"
        }
    }
}

#Preview {
    EditProfileView()
        .environment(AppState())
}
