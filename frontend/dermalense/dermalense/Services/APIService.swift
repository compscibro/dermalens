import Foundation
import UIKit

// MARK: - API Response DTOs

/// These structs map exactly to the backend JSON schemas.
/// Each has a `toDomain()` method that converts to the existing Swift domain model.

struct APIUserProfile: Codable {
    let id: String
    let name: String
    let email: String
    let username: String
    let avatarSystemName: String
}

struct APISkinMetric: Codable {
    let id: String
    let name: String
    let score: Double
    let icon: String
    let color: String
}

struct APISkinScan: Codable {
    let id: String
    let date: String
    let frontImageName: String?
    let leftImageName: String?
    let rightImageName: String?
    let scores: [APISkinMetric]
    let overallScore: Double
    let summary: String
}

struct APIScanRecord: Codable {
    let id: String
    let date: String
    let overallScore: Double
    let thumbnailSystemName: String
    let concerns: [String]
}

struct APIRoutineStep: Codable {
    let id: String
    let order: Int
    let name: String
    let description: String
    let productSuggestion: String
    let icon: String
}

struct APIRoutinePlan: Codable {
    let id: String
    let date: String
    let morningSteps: [APIRoutineStep]
    let eveningSteps: [APIRoutineStep]
    let weeklySteps: [APIRoutineStep]
}

struct APIChatMessage: Codable {
    let id: String
    let content: String
    let isUser: Bool
    let timestamp: String
}

// Request bodies
struct APIChatRequest: Codable {
    let content: String
    let sessionId: String?
}

struct APIProfileUpdate: Codable {
    let name: String?
    let username: String?
    let avatarSystemName: String?
}

// Retake error detail from 422 response
struct APIRetakeDetail: Codable {
    let message: String?
    let retake_required: Bool?
    let metrics: APIRetakeMetrics?
}

struct APIRetakeMetrics: Codable {
    let retake_reasons: [String]?
}

// MARK: - DTO → Domain Conversions

extension APIUserProfile {
    func toDomain() -> UserProfile {
        UserProfile(
            id: UUID(uuidString: id) ?? UUID(),
            name: name,
            email: email,
            username: username,
            avatarSystemName: avatarSystemName
        )
    }
}

extension APISkinMetric {
    func toDomain() -> SkinMetric {
        SkinMetric(
            id: UUID(uuidString: id) ?? UUID(),
            name: name,
            score: score,
            icon: icon,
            color: color
        )
    }
}

extension APISkinScan {
    func toDomain() -> SkinScan {
        let isoFormatter = ISO8601DateFormatter()
        isoFormatter.formatOptions = [.withInternetDateTime, .withFractionalSeconds]
        let parsedDate = isoFormatter.date(from: date)
            ?? ISO8601DateFormatter().date(from: date)
            ?? Date()

        return SkinScan(
            id: UUID(uuidString: id) ?? UUID(),
            date: parsedDate,
            frontImageName: frontImageName,
            leftImageName: leftImageName,
            rightImageName: rightImageName,
            scores: scores.map { $0.toDomain() },
            overallScore: overallScore,
            summary: summary
        )
    }
}

extension APIScanRecord {
    func toDomain() -> ScanRecord {
        let isoFormatter = ISO8601DateFormatter()
        isoFormatter.formatOptions = [.withInternetDateTime, .withFractionalSeconds]
        let parsedDate = isoFormatter.date(from: date)
            ?? ISO8601DateFormatter().date(from: date)
            ?? Date()

        return ScanRecord(
            id: UUID(uuidString: id) ?? UUID(),
            date: parsedDate,
            overallScore: overallScore,
            thumbnailSystemName: thumbnailSystemName,
            concerns: concerns
        )
    }
}

extension APIRoutineStep {
    func toDomain() -> RoutineStep {
        RoutineStep(
            id: UUID(uuidString: id) ?? UUID(),
            order: order,
            name: name,
            description: description,
            productSuggestion: productSuggestion,
            icon: icon
        )
    }
}

extension APIRoutinePlan {
    func toDomain() -> RoutinePlan {
        let isoFormatter = ISO8601DateFormatter()
        isoFormatter.formatOptions = [.withInternetDateTime, .withFractionalSeconds]
        let parsedDate = isoFormatter.date(from: date)
            ?? ISO8601DateFormatter().date(from: date)
            ?? Date()

        return RoutinePlan(
            id: UUID(uuidString: id) ?? UUID(),
            date: parsedDate,
            morningSteps: morningSteps.map { $0.toDomain() },
            eveningSteps: eveningSteps.map { $0.toDomain() },
            weeklySteps: weeklySteps.map { $0.toDomain() }
        )
    }
}

extension APIChatMessage {
    func toDomain() -> ChatMessage {
        let isoFormatter = ISO8601DateFormatter()
        isoFormatter.formatOptions = [.withInternetDateTime, .withFractionalSeconds]
        let parsedDate = isoFormatter.date(from: timestamp)
            ?? ISO8601DateFormatter().date(from: timestamp)
            ?? Date()

        return ChatMessage(
            id: UUID(uuidString: id) ?? UUID(),
            content: content,
            isUser: isUser,
            timestamp: parsedDate
        )
    }
}

// MARK: - API Service

/// Centralized networking layer for all DermaLens API calls.
class APIService {
    static let shared = APIService()

    private let baseURL: String
    private let session: URLSession
    private let decoder: JSONDecoder

    private init() {
        // EC2 production server
        self.baseURL = "http://18.212.229.221:8000/api/v1"
        let config = URLSessionConfiguration.default
        config.timeoutIntervalForRequest = 120 // AI analysis can take a while
        config.timeoutIntervalForResource = 180
        self.session = URLSession(configuration: config)
        self.decoder = JSONDecoder()
    }

    // MARK: - User Profile

    /// Fetch user profile. Auto-creates on backend if it doesn't exist.
    func getProfile(email: String) async throws -> UserProfile {
        let url = try buildURL(path: "/users/profile", queryItems: [
            URLQueryItem(name: "email", value: email),
        ])
        let (data, response) = try await perform(.get, url: url)
        try validateResponse(response, data: data)
        let dto = try decoder.decode(APIUserProfile.self, from: data)
        return dto.toDomain()
    }

    /// Update user profile fields.
    func updateProfile(
        email: String,
        name: String?,
        username: String?,
        avatarSystemName: String?
    ) async throws -> UserProfile {
        let url = try buildURL(path: "/users/profile", queryItems: [
            URLQueryItem(name: "email", value: email),
        ])
        let body = APIProfileUpdate(
            name: name,
            username: username,
            avatarSystemName: avatarSystemName
        )
        let bodyData = try JSONEncoder().encode(body)
        let (data, response) = try await perform(.put, url: url, body: bodyData, contentType: "application/json")
        try validateResponse(response, data: data)
        let dto = try decoder.decode(APIUserProfile.self, from: data)
        return dto.toDomain()
    }

    // MARK: - Scans

    /// Upload 3 face photos + concerns, run AI analysis, generate routine.
    func uploadScan(
        email: String,
        frontImageData: Data,
        leftImageData: Data,
        rightImageData: Data,
        concerns: SkinConcernsForm
    ) async throws -> SkinScan {
        let url = try buildURL(path: "/scans/upload", queryItems: [
            URLQueryItem(name: "email", value: email),
        ])

        let boundary = "Boundary-\(UUID().uuidString)"

        // Compress images before upload
        let front = compressImage(frontImageData) ?? frontImageData
        let left = compressImage(leftImageData) ?? leftImageData
        let right = compressImage(rightImageData) ?? rightImageData

        // Build concerns JSON string
        let concernsJSON = encodeConcernsJSON(concerns)

        let body = createMultipartBody(
            boundary: boundary,
            files: [
                (fieldName: "front", fileName: "front.jpg", data: front, mimeType: "image/jpeg"),
                (fieldName: "left", fileName: "left.jpg", data: left, mimeType: "image/jpeg"),
                (fieldName: "right", fileName: "right.jpg", data: right, mimeType: "image/jpeg"),
            ],
            fields: [
                (name: "concerns", value: concernsJSON),
            ]
        )

        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("multipart/form-data; boundary=\(boundary)", forHTTPHeaderField: "Content-Type")
        request.httpBody = body
        request.timeoutInterval = 120

        let (data, response) = try await session.data(for: request)

        // Check for 422 retake error
        if let httpResponse = response as? HTTPURLResponse, httpResponse.statusCode == 422 {
            let retakeInfo = try? decoder.decode([String: APIRetakeDetail].self, from: data)
            let detail = retakeInfo?["detail"]
            throw APIError.retakeRequired(
                message: detail?.message ?? "Image quality insufficient. Please retake your photos.",
                reasons: detail?.metrics?.retake_reasons ?? []
            )
        }

        try validateResponse(response, data: data)
        let dto = try decoder.decode(APISkinScan.self, from: data)
        return dto.toDomain()
    }

    /// Get a specific scan by ID.
    func getScan(email: String, scanId: String) async throws -> SkinScan {
        let url = try buildURL(path: "/scans/\(scanId)", queryItems: [
            URLQueryItem(name: "email", value: email),
        ])
        let (data, response) = try await perform(.get, url: url)
        try validateResponse(response, data: data)
        let dto = try decoder.decode(APISkinScan.self, from: data)
        return dto.toDomain()
    }

    /// Get scan history for a user.
    func getScanHistory(email: String) async throws -> [ScanRecord] {
        let url = try buildURL(path: "/scans/history/list", queryItems: [
            URLQueryItem(name: "email", value: email),
        ])
        let (data, response) = try await perform(.get, url: url)
        try validateResponse(response, data: data)
        let dtos = try decoder.decode([APIScanRecord].self, from: data)
        return dtos.map { $0.toDomain() }
    }

    // MARK: - Routines

    /// Get the routine plan for a specific scan.
    func getRoutine(email: String, scanId: String) async throws -> RoutinePlan {
        let url = try buildURL(path: "/routines/\(scanId)", queryItems: [
            URLQueryItem(name: "email", value: email),
        ])
        let (data, response) = try await perform(.get, url: url)
        try validateResponse(response, data: data)
        let dto = try decoder.decode(APIRoutinePlan.self, from: data)
        return dto.toDomain()
    }

    /// Get the most recent routine plan.
    func getLatestRoutine(email: String) async throws -> RoutinePlan {
        let url = try buildURL(path: "/routines/latest/plan", queryItems: [
            URLQueryItem(name: "email", value: email),
        ])
        let (data, response) = try await perform(.get, url: url)
        try validateResponse(response, data: data)
        let dto = try decoder.decode(APIRoutinePlan.self, from: data)
        return dto.toDomain()
    }

    // MARK: - Chat

    /// Send a chat message and receive the AI response.
    func sendChatMessage(
        email: String,
        content: String,
        sessionId: String?
    ) async throws -> ChatMessage {
        let url = try buildURL(path: "/chat/message", queryItems: [
            URLQueryItem(name: "email", value: email),
        ])
        let body = APIChatRequest(content: content, sessionId: sessionId)
        let bodyData = try JSONEncoder().encode(body)
        let (data, response) = try await perform(.post, url: url, body: bodyData, contentType: "application/json")
        try validateResponse(response, data: data)
        let dto = try decoder.decode(APIChatMessage.self, from: data)
        return dto.toDomain()
    }

    /// Get chat history.
    func getChatHistory(email: String, sessionId: String?) async throws -> [ChatMessage] {
        var queryItems = [URLQueryItem(name: "email", value: email)]
        if let sessionId {
            queryItems.append(URLQueryItem(name: "sessionId", value: sessionId))
        }
        let url = try buildURL(path: "/chat/history", queryItems: queryItems)
        let (data, response) = try await perform(.get, url: url)
        try validateResponse(response, data: data)
        let dtos = try decoder.decode([APIChatMessage].self, from: data)
        return dtos.map { $0.toDomain() }
    }

    // MARK: - Helpers

    private enum HTTPMethod: String {
        case get = "GET"
        case post = "POST"
        case put = "PUT"
    }

    private func buildURL(path: String, queryItems: [URLQueryItem]) throws -> URL {
        guard var components = URLComponents(string: baseURL + path) else {
            throw APIError.invalidURL
        }
        components.queryItems = queryItems
        guard let url = components.url else {
            throw APIError.invalidURL
        }
        return url
    }

    private func perform(
        _ method: HTTPMethod,
        url: URL,
        body: Data? = nil,
        contentType: String? = nil
    ) async throws -> (Data, URLResponse) {
        var request = URLRequest(url: url)
        request.httpMethod = method.rawValue
        if let contentType {
            request.setValue(contentType, forHTTPHeaderField: "Content-Type")
        }
        request.httpBody = body

        do {
            return try await session.data(for: request)
        } catch {
            throw APIError.networkError(error)
        }
    }

    private func validateResponse(_ response: URLResponse, data: Data) throws {
        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.unknown
        }
        guard (200...299).contains(httpResponse.statusCode) else {
            throw APIError.httpError(statusCode: httpResponse.statusCode, data: data)
        }
    }

    // MARK: - Multipart Form

    private func createMultipartBody(
        boundary: String,
        files: [(fieldName: String, fileName: String, data: Data, mimeType: String)],
        fields: [(name: String, value: String)]
    ) -> Data {
        var body = Data()

        for field in fields {
            body.append("--\(boundary)\r\n")
            body.append("Content-Disposition: form-data; name=\"\(field.name)\"\r\n\r\n")
            body.append("\(field.value)\r\n")
        }

        for file in files {
            body.append("--\(boundary)\r\n")
            body.append("Content-Disposition: form-data; name=\"\(file.fieldName)\"; filename=\"\(file.fileName)\"\r\n")
            body.append("Content-Type: \(file.mimeType)\r\n\r\n")
            body.append(file.data)
            body.append("\r\n")
        }

        body.append("--\(boundary)--\r\n")
        return body
    }

    // MARK: - Concerns JSON

    private func encodeConcernsJSON(_ form: SkinConcernsForm) -> String {
        let dict: [String: Any] = [
            "primaryConcerns": Array(form.primaryConcerns),
            "biggestInsecurity": form.biggestInsecurity,
            "skinType": form.skinType,
            "sensitivityLevel": form.sensitivityLevel,
            "additionalNotes": form.additionalNotes,
        ]
        guard let data = try? JSONSerialization.data(withJSONObject: dict),
              let json = String(data: data, encoding: .utf8)
        else {
            return "{}"
        }
        return json
    }

    // MARK: - Image Compression

    /// Compress image to JPEG, resizing to max dimension for fast upload.
    func compressImage(
        _ data: Data,
        maxDimension: CGFloat = 1024,
        quality: CGFloat = 0.7
    ) -> Data? {
        guard let image = UIImage(data: data) else { return nil }
        let maxSide = max(image.size.width, image.size.height)
        let scale = min(maxDimension / maxSide, 1.0)
        if scale >= 1.0 {
            // Already small enough, just compress quality
            return image.jpegData(compressionQuality: quality)
        }
        let newSize = CGSize(
            width: image.size.width * scale,
            height: image.size.height * scale
        )
        let renderer = UIGraphicsImageRenderer(size: newSize)
        let resized = renderer.image { _ in
            image.draw(in: CGRect(origin: .zero, size: newSize))
        }
        return resized.jpegData(compressionQuality: quality)
    }
}

// MARK: - Data Extension for Multipart

private extension Data {
    mutating func append(_ string: String) {
        if let data = string.data(using: .utf8) {
            append(data)
        }
    }
}
