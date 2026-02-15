//
//  DashboardView.swift
//  dermalense
//
//  Created by Mohammed Abdur Rahman on 2/14/26.
//

import SwiftUI

struct DashboardView: View {
    @Environment(AppState.self) private var appState
    @State private var currentStep: DashboardStep = .concerns
    @State private var concernsForm: SkinConcernsForm?
    @State private var flowId = UUID()

    enum DashboardStep: Int, CaseIterable {
        case concerns = 0
        case upload = 1
        case analysis = 2
        case routine = 3
        case chat = 4

        var title: String {
            switch self {
            case .upload: return "Upload"
            case .concerns: return "Concerns"
            case .analysis: return "Analysis"
            case .routine: return "Routine"
            case .chat: return "Chat"
            }
        }

        var icon: String {
            switch self {
            case .upload: return "camera.fill"
            case .concerns: return "list.clipboard.fill"
            case .analysis: return "waveform.path.ecg"
            case .routine: return "clock.fill"
            case .chat: return "message.fill"
            }
        }
    }

    var body: some View {
        NavigationStack {
            VStack(spacing: 0) {
                stepIndicator
                    .padding(.horizontal, DLSpacing.md)
                    .padding(.top, DLSpacing.sm)

                TabView(selection: $currentStep) {
                    ConcernsFormView(onSubmit: { form in
                        concernsForm = form
                        appState.currentConcernsForm = form
                        advanceStep()
                    })
                    .tag(DashboardStep.concerns)

                    PhotoUploadView(
                        concernsForm: concernsForm,
                        onSubmit: { scan in
                            appState.currentScan = scan
                            advanceStep()
                            // Fetch routine for this scan
                            Task {
                                do {
                                    let routine = try await APIService.shared.getRoutine(
                                        email: appState.userEmail,
                                        scanId: scan.id.uuidString.lowercased()
                                    )
                                    appState.routinePlan = routine
                                } catch {
                                    // Routine fetch failed
                                }
                            }
                            // Refresh scan history
                            Task {
                                if let history = try? await APIService.shared.getScanHistory(
                                    email: appState.userEmail
                                ) {
                                    appState.scanHistory = history
                                }
                            }
                        }
                    )
                    .tag(DashboardStep.upload)

                    SkinAnalysisView(
                        scan: appState.currentScan,
                        onNext: { advanceStep() }
                    )
                    .tag(DashboardStep.analysis)

                    RoutinePlanView(
                        plan: appState.routinePlan,
                        onNext: { advanceStep() }
                    )
                    .tag(DashboardStep.routine)

                    ChatView()
                        .tag(DashboardStep.chat)
                }
                .id(flowId)
                .tabViewStyle(.page(indexDisplayMode: .never))
                .animation(.easeInOut(duration: 0.3), value: currentStep)
            }
            .navigationTitle("DermaLens")
            .navigationBarTitleDisplayMode(.large)
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Button {
                        resetFlow()
                    } label: {
                        Image(systemName: "arrow.counterclockwise")
                            .font(.system(size: 14, weight: .semibold))
                    }
                    .tint(DLColor.primaryFallback)
                }
            }
        }
    }

    // MARK: - Step Indicator

    private var stepIndicator: some View {
        HStack(spacing: DLSpacing.xs) {
            ForEach(DashboardStep.allCases, id: \.rawValue) { step in
                stepPill(for: step)
            }
        }
    }

    private func stepPill(for step: DashboardStep) -> some View {
        let canNav = canNavigateTo(step)
        return Button {
            if canNav {
                withAnimation { currentStep = step }
            }
        } label: {
            HStack(spacing: 4) {
                Image(systemName: step.icon)
                    .font(.system(size: 10))
                if currentStep == step {
                    Text(step.title)
                        .font(.system(size: 11, weight: .semibold, design: .rounded))
                }
            }
            .padding(.horizontal, currentStep == step ? 12 : 8)
            .padding(.vertical, 8)
            .background(
                Capsule()
                    .fill(currentStep == step ? DLColor.primaryFallback : canNav ? Color(.systemGray6) : Color(.systemGray6).opacity(0.5))
            )
            .foregroundStyle(currentStep == step ? .white : canNav ? Color.secondary : Color.secondary.opacity(0.4))
        }
        .buttonStyle(.plain)
        .animation(.spring(response: 0.35, dampingFraction: 0.8), value: currentStep)
    }

    private func canNavigateTo(_ step: DashboardStep) -> Bool {
        switch step {
        case .concerns: return true
        case .upload: return concernsForm != nil
        case .analysis: return appState.currentScan != nil
        case .routine: return appState.routinePlan != nil
        case .chat: return appState.currentScan != nil
        }
    }

    private func advanceStep() {
        let allCases = DashboardStep.allCases
        if let idx = allCases.firstIndex(of: currentStep), idx + 1 < allCases.count {
            withAnimation { currentStep = allCases[idx + 1] }
        }
    }

    private func resetFlow() {
        withAnimation {
            currentStep = .concerns
            concernsForm = nil
            appState.currentScan = nil
            appState.currentConcernsForm = nil
            appState.routinePlan = nil
            appState.chatMessages = []
            appState.chatSessionId = nil
            appState.scanError = nil
            appState.retakeRequired = false
            // Change flowId to force SwiftUI to destroy and recreate all child views,
            // resetting their internal @State (form fields, selected photos, etc.)
            flowId = UUID()
        }
    }
}

#Preview {
    DashboardView()
        .environment(AppState())
}
