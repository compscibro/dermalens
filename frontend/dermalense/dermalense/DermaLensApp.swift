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
            if appState.isOnboarded {
                MainTabView()
                    .environment(appState)
            } else {
                OnboardingView()
                    .environment(appState)
            }
        }
    }
}
