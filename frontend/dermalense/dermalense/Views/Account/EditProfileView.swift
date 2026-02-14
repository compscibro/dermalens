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
    @State private var email: String = ""
    @State private var username: String = ""

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
                        TextField("Email", text: $email)
                            .keyboardType(.emailAddress)
                            .textContentType(.emailAddress)
                            .autocapitalization(.none)
                    }

                    HStack {
                        Image(systemName: "at")
                            .foregroundStyle(DLColor.primaryFallback)
                            .frame(width: 24)
                        TextField("Username", text: $username)
                            .autocapitalization(.none)
                    }
                }

                Section {
                    Button("Save Changes") {
                        appState.user.name = name
                        appState.user.email = email
                        appState.user.username = username
                        dismiss()
                    }
                    .frame(maxWidth: .infinity)
                    .fontWeight(.semibold)
                    .foregroundStyle(DLColor.primaryFallback)
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
                email = appState.user.email
                username = appState.user.username
            }
        }
    }
}

#Preview {
    EditProfileView()
        .environment(AppState())
}
