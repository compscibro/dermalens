//
//  Models.swift
//  dermalense
//
//  Created by Mohammed Abdur Rahman on 2/14/26.
//

import Foundation
import Observation

// MARK: - App State

@Observable
class AppState {
    var isOnboarded: Bool = false
    var user: UserProfile = .placeholder
    var scanHistory: [ScanRecord] = []
    var currentScan: SkinScan?
    var chatMessages: [ChatMessage] = []
    var routinePlan: RoutinePlan?

    // Current concerns form (shared between dashboard steps)
    var currentConcernsForm: SkinConcernsForm?

    // Chat session tracking
    var chatSessionId: String?

    // Loading states
    var isUploadingScan: Bool = false
    var isLoadingProfile: Bool = false
    var isLoadingHistory: Bool = false
    var isSendingMessage: Bool = false
    var isLoadingRoutine: Bool = false

    // Error states
    var scanError: String?
    var profileError: String?
    var chatError: String?

    // Upload progress feedback
    var uploadProgress: String?

    // Retake state
    var retakeRequired: Bool = false
    var retakeMessage: String?
    var retakeReasons: [String] = []

    // Persistence via UserDefaults
    var userEmail: String {
        get { UserDefaults.standard.string(forKey: "dermalens_userEmail") ?? "" }
        set { UserDefaults.standard.set(newValue, forKey: "dermalens_userEmail") }
    }

    var savedIsOnboarded: Bool {
        get { UserDefaults.standard.bool(forKey: "dermalens_isOnboarded") }
        set { UserDefaults.standard.set(newValue, forKey: "dermalens_isOnboarded") }
    }
}

// MARK: - User

struct UserProfile: Identifiable {
    let id: UUID
    var name: String
    var email: String
    var username: String
    var avatarSystemName: String

    static let placeholder = UserProfile(
        id: UUID(),
        name: "",
        email: "",
        username: "",
        avatarSystemName: "person.crop.circle.fill"
    )
}

// MARK: - Skin Scan

struct SkinScan: Identifiable {
    let id: UUID
    let date: Date
    var frontImageName: String?
    var leftImageName: String?
    var rightImageName: String?
    var scores: [SkinMetric]
    var overallScore: Double
    var summary: String

    static let sample = SkinScan(
        id: UUID(),
        date: Date(),
        frontImageName: nil,
        leftImageName: nil,
        rightImageName: nil,
        scores: SkinMetric.sampleMetrics,
        overallScore: 72.5,
        summary: "Your skin is in good overall condition. Some mild acne detected on the forehead area. Hydration levels are slightly below optimal. Oil production is balanced."
    )
}

struct SkinMetric: Identifiable {
    let id: UUID
    let name: String
    let score: Double // 0.0 - 100.0
    let icon: String
    let color: String

    /// Convert color string to SwiftUI-friendly description.
    var colorDescription: String {
        switch color.lowercased() {
        case "green": return "Good"
        case "yellow": return "Fair"
        case "orange": return "Needs Attention"
        case "red": return "Poor"
        default: return "Unknown"
        }
    }

    static let sampleMetrics: [SkinMetric] = [
        SkinMetric(id: UUID(), name: "Acne", score: 25.3, icon: "circle.fill", color: "yellow"),
        SkinMetric(id: UUID(), name: "Redness", score: 15.0, icon: "flame.fill", color: "green"),
        SkinMetric(id: UUID(), name: "Oiliness", score: 42.8, icon: "drop.fill", color: "orange"),
        SkinMetric(id: UUID(), name: "Dryness", score: 18.5, icon: "sun.max.fill", color: "green"),
        SkinMetric(id: UUID(), name: "Wrinkles", score: 8.2, icon: "lines.measurement.horizontal", color: "green"),
        SkinMetric(id: UUID(), name: "Dark Spots", score: 31.0, icon: "circle.dashed", color: "yellow"),
        SkinMetric(id: UUID(), name: "Pores", score: 55.1, icon: "circle.grid.3x3.fill", color: "orange"),
        SkinMetric(id: UUID(), name: "Texture", score: 68.4, icon: "square.grid.3x3.topleft.filled", color: "red"),
    ]
}

// MARK: - Skin Concerns Form

struct SkinConcernsForm {
    var primaryConcerns: Set<String> = []
    var biggestInsecurity: String = ""
    var skinType: String = "Normal"
    var sensitivityLevel: String = "Moderate"
    var additionalNotes: String = ""

    static let skinTypes = ["Dry", "Oily", "Combination", "Normal", "Sensitive"]
    static let sensitivityLevels = ["Low", "Moderate", "High"]

    static let availableConcerns = [
        "Acne & Breakouts",
        "Redness & Irritation",
        "Oily Skin",
        "Dry Patches",
        "Dark Spots & Hyperpigmentation",
        "Fine Lines & Wrinkles",
        "Large Pores",
        "Uneven Texture",
        "Dark Circles",
        "Sun Damage",
    ]
}

// MARK: - Routine Plan

struct RoutinePlan: Identifiable {
    let id: UUID
    let date: Date
    var morningSteps: [RoutineStep]
    var eveningSteps: [RoutineStep]
    var weeklySteps: [RoutineStep]

    static let sample = RoutinePlan(
        id: UUID(),
        date: Date(),
        morningSteps: [
            RoutineStep(id: UUID(), order: 1, name: "Gentle Cleanser", description: "Use a mild, pH-balanced cleanser. Massage gently for 60 seconds.", productSuggestion: "CeraVe Hydrating Cleanser", icon: "drop.fill"),
            RoutineStep(id: UUID(), order: 2, name: "Vitamin C Serum", description: "Apply 3-4 drops of vitamin C serum to brighten and protect.", productSuggestion: "Timeless 20% Vitamin C + E", icon: "sun.min.fill"),
            RoutineStep(id: UUID(), order: 3, name: "Moisturizer", description: "Apply a lightweight, non-comedogenic moisturizer.", productSuggestion: "Neutrogena Hydro Boost", icon: "humidity.fill"),
            RoutineStep(id: UUID(), order: 4, name: "Sunscreen SPF 50", description: "Finish with broad-spectrum SPF 50. Reapply every 2 hours.", productSuggestion: "EltaMD UV Clear SPF 46", icon: "sun.max.trianglebadge.exclamationmark.fill"),
        ],
        eveningSteps: [
            RoutineStep(id: UUID(), order: 1, name: "Oil Cleanser", description: "Double cleanse starting with an oil-based cleanser to remove sunscreen.", productSuggestion: "DHC Deep Cleansing Oil", icon: "drop.fill"),
            RoutineStep(id: UUID(), order: 2, name: "Water Cleanser", description: "Follow with a gentle water-based cleanser.", productSuggestion: "La Roche-Posay Toleriane", icon: "drop.fill"),
            RoutineStep(id: UUID(), order: 3, name: "Niacinamide Serum", description: "Apply niacinamide to reduce pore appearance and control oil.", productSuggestion: "The Ordinary Niacinamide 10%", icon: "testtube.2"),
            RoutineStep(id: UUID(), order: 4, name: "Retinol Treatment", description: "Apply a pea-sized amount of retinol. Start 2x/week, build up.", productSuggestion: "Differin Adapalene Gel 0.1%", icon: "moon.fill"),
            RoutineStep(id: UUID(), order: 5, name: "Night Moisturizer", description: "Seal in actives with a rich night cream.", productSuggestion: "CeraVe PM Moisturizing Lotion", icon: "humidity.fill"),
        ],
        weeklySteps: [
            RoutineStep(id: UUID(), order: 1, name: "Chemical Exfoliant", description: "Use a BHA exfoliant 2x/week to unclog pores.", productSuggestion: "Paula's Choice 2% BHA", icon: "sparkles"),
            RoutineStep(id: UUID(), order: 2, name: "Hydrating Mask", description: "Apply a hydrating sheet mask 1x/week for deep moisture.", productSuggestion: "Dr. Jart+ Ceramidin Mask", icon: "face.dashed"),
        ]
    )
}

struct RoutineStep: Identifiable {
    let id: UUID
    let order: Int
    let name: String
    let description: String
    let productSuggestion: String
    let icon: String
}

// MARK: - Chat

struct ChatMessage: Identifiable {
    let id: UUID
    let content: String
    let isUser: Bool
    let timestamp: Date

    static let sampleConversation: [ChatMessage] = [
        ChatMessage(id: UUID(), content: "Hi! I've been following the routine for a week now. How should I assess if it's working?", isUser: true, timestamp: Date().addingTimeInterval(-3600)),
        ChatMessage(id: UUID(), content: "Great question! After one week, look for these signs:\n\n1. Reduced redness or irritation\n2. Skin feels more hydrated\n3. Fewer new breakouts\n\nIt's normal for skin to go through a 'purging' phase with retinol. If irritation is severe, reduce retinol to once a week. Would you like to upload new photos so I can compare?", isUser: false, timestamp: Date().addingTimeInterval(-3500)),
        ChatMessage(id: UUID(), content: "I think the oiliness has gotten a bit better but I'm still breaking out on my chin.", isUser: true, timestamp: Date().addingTimeInterval(-1800)),
        ChatMessage(id: UUID(), content: "Chin breakouts can be hormonal, which topical products alone may not fully address. Let's try adjusting your routine:\n\n- Add a spot treatment with benzoyl peroxide 2.5% for the chin area\n- Continue with the current routine otherwise\n\nIf breakouts persist after 2 more weeks, I'd recommend uploading new photos for a fresh scan.", isUser: false, timestamp: Date().addingTimeInterval(-1700)),
    ]
}

// MARK: - Scan History Record

struct ScanRecord: Identifiable {
    let id: UUID
    let date: Date
    let overallScore: Double
    let thumbnailSystemName: String
    let concerns: [String]

    static let sampleHistory: [ScanRecord] = [
        ScanRecord(id: UUID(), date: Date(), overallScore: 72.5, thumbnailSystemName: "face.smiling", concerns: ["Oiliness", "Pores", "Acne"]),
        ScanRecord(id: UUID(), date: Calendar.current.date(byAdding: .day, value: -7, to: Date())!, overallScore: 68.0, thumbnailSystemName: "face.smiling", concerns: ["Oiliness", "Dark Spots", "Texture"]),
        ScanRecord(id: UUID(), date: Calendar.current.date(byAdding: .day, value: -14, to: Date())!, overallScore: 63.2, thumbnailSystemName: "face.smiling", concerns: ["Acne", "Oiliness", "Redness"]),
        ScanRecord(id: UUID(), date: Calendar.current.date(byAdding: .day, value: -21, to: Date())!, overallScore: 59.8, thumbnailSystemName: "face.smiling", concerns: ["Acne", "Dryness", "Redness"]),
    ]
}
