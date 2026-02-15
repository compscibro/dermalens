//
//  DermaLensApp.swift
//  dermalense
//
//  Created by Mohammed Abdur Rahman on 2/14/26.
//

import SwiftUI

@main
struct DermaLensApp: App {
    @State private var appState = AppState()

    var body: some Scene {
        WindowGroup {
            Group {
                if appState.isOnboarded {
                    MainTabView()
                        .environment(appState)
                } else {
                    OnboardingView()
                        .environment(appState)
                }
            }
            .task {
                // Demo mode: always start fresh at signup
                appState.savedIsOnboarded = false
                appState.isOnboarded = false
            }
        }
    }
}
