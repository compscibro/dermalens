//
//  ChatView.swift
//  dermalense
//
//  Created by Mohammed Abdur Rahman on 2/14/26.
//

import SwiftUI

struct ChatView: View {
    @Environment(AppState.self) private var appState
    @State private var inputText = ""
    @State private var isAITyping = false
    @FocusState private var isInputFocused: Bool

    var body: some View {
        VStack(spacing: 0) {
            chatHeader
            Divider()
            messagesScrollView
            Divider()
            inputBar
            aiDisclaimer
        }
        .task {
            await loadChatHistoryIfNeeded()
        }
    }

    // MARK: - Header

    private var chatHeader: some View {
        HStack(spacing: DLSpacing.sm) {
            Circle()
                .fill(
                    LinearGradient(
                        colors: [DLColor.primaryFallback, DLColor.secondaryFallback],
                        startPoint: .topLeading,
                        endPoint: .bottomTrailing
                    )
                )
                .frame(width: 36, height: 36)
                .overlay(
                    Image(systemName: "brain.head.profile")
                        .font(.system(size: 16))
                        .foregroundStyle(.white)
                )

            VStack(alignment: .leading, spacing: 2) {
                Text("DermaLens AI")
                    .font(DLFont.headline)
                Text(isAITyping ? "Typing..." : "Online")
                    .font(DLFont.caption)
                    .foregroundStyle(isAITyping ? DLColor.accentFallback : .green)
            }

            Spacer()
        }
        .padding(.horizontal, DLSpacing.md)
        .padding(.vertical, DLSpacing.sm)
    }

    // MARK: - Messages

    private var messagesScrollView: some View {
        ScrollViewReader { proxy in
            ScrollView {
                LazyVStack(spacing: DLSpacing.sm) {
                    if appState.chatMessages.isEmpty && !isAITyping {
                        welcomeMessage
                            .padding(.top, DLSpacing.lg)
                    }

                    quickActionsBar
                        .padding(.top, DLSpacing.sm)

                    ForEach(appState.chatMessages) { message in
                        messageBubble(message)
                            .id(message.id)
                    }

                    if let error = appState.chatError {
                        errorMessage(error)
                    }

                    if isAITyping {
                        typingIndicator
                    }
                }
                .padding(.horizontal, DLSpacing.md)
                .padding(.bottom, DLSpacing.sm)
            }
            .onChange(of: appState.chatMessages.count) { _, _ in
                if let last = appState.chatMessages.last {
                    withAnimation {
                        proxy.scrollTo(last.id, anchor: .bottom)
                    }
                }
            }
        }
    }

    private var welcomeMessage: some View {
        VStack(spacing: DLSpacing.md) {
            Image(systemName: "sparkles")
                .font(.system(size: 32))
                .foregroundStyle(DLColor.primaryFallback)

            Text("Ask me anything about your skin analysis, routine, or skincare in general!")
                .font(DLFont.body)
                .foregroundStyle(.secondary)
                .multilineTextAlignment(.center)
                .padding(.horizontal, DLSpacing.xl)
        }
    }

    private func messageBubble(_ message: ChatMessage) -> some View {
        HStack(alignment: .bottom, spacing: DLSpacing.sm) {
            if message.isUser { Spacer(minLength: 48) }

            if !message.isUser {
                Circle()
                    .fill(DLColor.primaryFallback.opacity(0.15))
                    .frame(width: 28, height: 28)
                    .overlay(
                        Image(systemName: "brain.head.profile")
                            .font(.system(size: 12))
                            .foregroundStyle(DLColor.primaryFallback)
                    )
            }

            VStack(alignment: message.isUser ? .trailing : .leading, spacing: 4) {
                Text(message.content)
                    .font(DLFont.body)
                    .foregroundStyle(message.isUser ? .white : .primary)
                    .padding(.horizontal, 14)
                    .padding(.vertical, 10)
                    .background(
                        RoundedRectangle(cornerRadius: 18, style: .continuous)
                            .fill(message.isUser ? DLColor.primaryFallback : Color(.systemGray6))
                    )

                Text(message.timestamp, style: .time)
                    .font(.system(size: 10))
                    .foregroundStyle(.tertiary)
            }

            if !message.isUser { Spacer(minLength: 48) }
        }
    }

    private func errorMessage(_ error: String) -> some View {
        HStack(spacing: DLSpacing.xs) {
            Image(systemName: "exclamationmark.triangle.fill")
                .font(.system(size: 12))
                .foregroundStyle(.orange)
            Text(error)
                .font(DLFont.caption)
                .foregroundStyle(.secondary)
        }
        .padding(DLSpacing.sm)
        .background(Color.orange.opacity(0.1))
        .clipShape(RoundedRectangle(cornerRadius: DLRadius.sm))
    }

    private var typingIndicator: some View {
        HStack(alignment: .bottom, spacing: DLSpacing.sm) {
            Circle()
                .fill(DLColor.primaryFallback.opacity(0.15))
                .frame(width: 28, height: 28)
                .overlay(
                    Image(systemName: "brain.head.profile")
                        .font(.system(size: 12))
                        .foregroundStyle(DLColor.primaryFallback)
                )

            HStack(spacing: 4) {
                ForEach(0..<3) { i in
                    Circle()
                        .fill(Color(.systemGray3))
                        .frame(width: 7, height: 7)
                        .scaleEffect(isAITyping ? 1.0 : 0.5)
                        .animation(
                            .easeInOut(duration: 0.6)
                            .repeatForever()
                            .delay(Double(i) * 0.2),
                            value: isAITyping
                        )
                }
            }
            .padding(.horizontal, 16)
            .padding(.vertical, 12)
            .background(
                RoundedRectangle(cornerRadius: 18, style: .continuous)
                    .fill(Color(.systemGray6))
            )

            Spacer()
        }
    }

    // MARK: - Quick Actions

    private var quickActionsBar: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack(spacing: DLSpacing.sm) {
                quickActionChip("Is my routine working?", icon: "checkmark.circle")
                quickActionChip("Explain a step", icon: "questionmark.circle")
                quickActionChip("Change a product", icon: "arrow.triangle.2.circlepath")
                quickActionChip("Skincare tips", icon: "lightbulb")
            }
        }
    }

    private func quickActionChip(_ text: String, icon: String) -> some View {
        Button {
            sendMessage(text)
        } label: {
            HStack(spacing: 4) {
                Image(systemName: icon)
                    .font(.system(size: 11))
                Text(text)
                    .font(DLFont.caption)
            }
            .padding(.horizontal, 12)
            .padding(.vertical, 8)
            .background(
                Capsule()
                    .strokeBorder(DLColor.primaryFallback.opacity(0.3), lineWidth: 1)
            )
            .foregroundStyle(DLColor.primaryFallback)
        }
        .buttonStyle(.plain)
    }

    // MARK: - Input Bar

    private var inputBar: some View {
        HStack(spacing: DLSpacing.sm) {
            TextField("Ask about your routine...", text: $inputText, axis: .vertical)
                .font(DLFont.body)
                .lineLimit(1...4)
                .focused($isInputFocused)
                .padding(.horizontal, 14)
                .padding(.vertical, 10)
                .background(
                    RoundedRectangle(cornerRadius: 20)
                        .fill(Color(.systemGray6))
                )

            Button {
                sendMessage(inputText)
            } label: {
                Image(systemName: "arrow.up.circle.fill")
                    .font(.system(size: 32))
                    .foregroundStyle(
                        inputText.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty || isAITyping
                        ? Color(.systemGray4)
                        : DLColor.primaryFallback
                    )
            }
            .disabled(inputText.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty || isAITyping)
        }
        .padding(.horizontal, DLSpacing.md)
        .padding(.vertical, DLSpacing.sm)
    }

    // MARK: - Disclaimer

    private var aiDisclaimer: some View {
        HStack(spacing: DLSpacing.xs) {
            Image(systemName: "info.circle")
                .font(.system(size: 10))
            Text("DermaLens isn't human. It can make mistakes, so double check important info. For medical advice, consult with medical professionals.")
                .font(.system(size: 10))
        }
        .foregroundStyle(.tertiary)
        .frame(maxWidth: .infinity)
        .padding(.horizontal, DLSpacing.md)
        .padding(.bottom, DLSpacing.xs)
    }

    // MARK: - Actions

    private func loadChatHistoryIfNeeded() async {
        guard let sessionId = appState.chatSessionId,
              appState.chatMessages.isEmpty else { return }

        do {
            let history = try await APIService.shared.getChatHistory(
                email: appState.userEmail,
                sessionId: sessionId
            )
            appState.chatMessages = history
        } catch {
            // Silently fail — user can still start a new conversation
        }
    }

    private func sendMessage(_ text: String) {
        let trimmed = text.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmed.isEmpty else { return }

        // Add user message immediately
        let userMessage = ChatMessage(id: UUID(), content: trimmed, isUser: true, timestamp: Date())
        appState.chatMessages.append(userMessage)
        inputText = ""
        isInputFocused = false
        appState.chatError = nil

        // Generate session ID if first message
        if appState.chatSessionId == nil {
            appState.chatSessionId = UUID().uuidString.lowercased()
        }

        // Send to API
        isAITyping = true
        Task {
            do {
                let aiResponse = try await APIService.shared.sendChatMessage(
                    email: appState.userEmail,
                    content: trimmed,
                    sessionId: appState.chatSessionId
                )
                isAITyping = false
                appState.chatMessages.append(aiResponse)
            } catch {
                isAITyping = false
                appState.chatError = "Failed to get a response. Please try again."
            }
        }
    }
}

#Preview {
    ChatView()
        .environment(AppState())
}
