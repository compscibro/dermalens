//
//  ChatView.swift
//  dermalense
//
//  Created by Mohammed Abdur Rahman on 2/14/26.
//

import SwiftUI

struct ChatView: View {
    @State private var messages: [ChatMessage] = ChatMessage.sampleConversation
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

            Button {
                // Upload new photos action
            } label: {
                Image(systemName: "camera.fill")
                    .font(.system(size: 14))
                    .padding(8)
                    .background(Circle().fill(Color(.systemGray6)))
            }
            .tint(.primary)
        }
        .padding(.horizontal, DLSpacing.md)
        .padding(.vertical, DLSpacing.sm)
    }

    // MARK: - Messages

    private var messagesScrollView: some View {
        ScrollViewReader { proxy in
            ScrollView {
                LazyVStack(spacing: DLSpacing.sm) {
                    quickActionsBar
                        .padding(.top, DLSpacing.sm)

                    ForEach(messages) { message in
                        messageBubble(message)
                            .id(message.id)
                    }

                    if isAITyping {
                        typingIndicator
                    }
                }
                .padding(.horizontal, DLSpacing.md)
                .padding(.bottom, DLSpacing.sm)
            }
            .onChange(of: messages.count) { _, _ in
                if let last = messages.last {
                    withAnimation {
                        proxy.scrollTo(last.id, anchor: .bottom)
                    }
                }
            }
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
                quickActionChip("Upload new photos", icon: "camera")
                quickActionChip("Change a product", icon: "arrow.triangle.2.circlepath")
                quickActionChip("Explain a step", icon: "questionmark.circle")
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
                        inputText.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty
                        ? Color(.systemGray4)
                        : DLColor.primaryFallback
                    )
            }
            .disabled(inputText.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty)
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

    private func sendMessage(_ text: String) {
        let trimmed = text.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmed.isEmpty else { return }

        let userMessage = ChatMessage(id: UUID(), content: trimmed, isUser: true, timestamp: Date())
        messages.append(userMessage)
        inputText = ""
        isInputFocused = false

        // Simulate AI response
        isAITyping = true
        DispatchQueue.main.asyncAfter(deadline: .now() + 2.0) {
            isAITyping = false
            let aiResponse = ChatMessage(
                id: UUID(),
                content: "Thanks for sharing! Based on your progress, I'd recommend continuing your current routine for another week. Consistency is key. If you'd like, upload new photos and I can do a fresh comparison scan to track changes.",
                isUser: false,
                timestamp: Date()
            )
            messages.append(aiResponse)
        }
    }
}

#Preview {
    ChatView()
}
