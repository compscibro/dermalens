//
//  DashboardView.swift
//  dermalense
//
//  Created by Mohammed Abdur Rahman on 2/14/26.
//

import SwiftUI

struct DashboardView: View {
    @Environment(AppState.self) private var appState
    @State private var currentStep: DashboardStep = .upload

    enum DashboardStep: Int, CaseIterable {
        case upload = 0
        case concerns = 1
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
                    PhotoUploadView(onNext: { advanceStep() })
                        .tag(DashboardStep.upload)

                    ConcernsFormView(onNext: { advanceStep() })
                        .tag(DashboardStep.concerns)

                    SkinAnalysisView(onNext: { advanceStep() })
                        .tag(DashboardStep.analysis)

                    RoutinePlanView(onNext: { advanceStep() })
                        .tag(DashboardStep.routine)

                    ChatView()
                        .tag(DashboardStep.chat)
                }
                .tabViewStyle(.page(indexDisplayMode: .never))
                .animation(.easeInOut(duration: 0.3), value: currentStep)
            }
            .navigationTitle("DermaLens")
            .navigationBarTitleDisplayMode(.large)
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Button {
                        currentStep = .upload
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
        Button {
            withAnimation { currentStep = step }
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
                    .fill(currentStep == step ? DLColor.primaryFallback : Color(.systemGray6))
            )
            .foregroundStyle(currentStep == step ? .white : .secondary)
        }
        .buttonStyle(.plain)
        .animation(.spring(response: 0.35, dampingFraction: 0.8), value: currentStep)
    }

    private func advanceStep() {
        let allCases = DashboardStep.allCases
        if let idx = allCases.firstIndex(of: currentStep), idx + 1 < allCases.count {
            withAnimation { currentStep = allCases[idx + 1] }
        }
    }
}

#Preview {
    DashboardView()
        .environment(AppState())
}
