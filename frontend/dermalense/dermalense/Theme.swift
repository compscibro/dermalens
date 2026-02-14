//
//  Theme.swift
//  dermalense
//
//  Created by Mohammed Abdur Rahman on 2/14/26.
//

import SwiftUI

enum DLColor {
    static let primary = Color("Primary")
    static let secondary = Color("Secondary")
    static let accent = Color("Accent")
    static let cardBackground = Color("CardBackground")
    static let textPrimary = Color("TextPrimary")
    static let textSecondary = Color("TextSecondary")

    // Fallback colors if asset catalog colors aren't set up
    static let primaryFallback = Color(red: 0.29, green: 0.56, blue: 0.89)   // Calm blue
    static let secondaryFallback = Color(red: 0.22, green: 0.78, blue: 0.65) // Teal green
    static let accentFallback = Color(red: 0.95, green: 0.6, blue: 0.25)     // Warm amber
    static let surfaceFallback = Color(red: 0.96, green: 0.97, blue: 0.98)   // Light gray
}

enum DLFont {
    static let largeTitle = Font.system(size: 28, weight: .bold, design: .rounded)
    static let title = Font.system(size: 22, weight: .semibold, design: .rounded)
    static let headline = Font.system(size: 17, weight: .semibold, design: .rounded)
    static let body = Font.system(size: 15, weight: .regular, design: .default)
    static let caption = Font.system(size: 13, weight: .regular, design: .default)
    static let small = Font.system(size: 11, weight: .medium, design: .default)
}

enum DLSpacing {
    static let xs: CGFloat = 4
    static let sm: CGFloat = 8
    static let md: CGFloat = 16
    static let lg: CGFloat = 24
    static let xl: CGFloat = 32
    static let xxl: CGFloat = 48
}

enum DLRadius {
    static let sm: CGFloat = 8
    static let md: CGFloat = 12
    static let lg: CGFloat = 16
    static let xl: CGFloat = 24
    static let full: CGFloat = 999
}
