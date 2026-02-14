//
//  MainTabView.swift
//  dermalense
//
//  Created by Mohammed Abdur Rahman on 2/14/26.
//

import SwiftUI

struct MainTabView: View {
    @State private var selectedTab: Tab = .dashboard

    enum Tab {
        case dashboard, account
    }

    var body: some View {
        TabView(selection: $selectedTab) {
            DashboardView()
                .tabItem {
                    Label("Dashboard", systemImage: "rectangle.grid.1x2.fill")
                }
                .tag(Tab.dashboard)

            AccountView()
                .tabItem {
                    Label("Account", systemImage: "person.fill")
                }
                .tag(Tab.account)
        }
        .tint(DLColor.primaryFallback)
    }
}

#Preview {
    MainTabView()
        .environment(AppState())
}
