import Foundation

/// Errors that can occur during API communication.
enum APIError: LocalizedError {
    case invalidURL
    case networkError(Error)
    case httpError(statusCode: Int, data: Data?)
    case decodingError(Error)
    case retakeRequired(message: String, reasons: [String])
    case unknown

    var errorDescription: String? {
        switch self {
        case .invalidURL:
            return "Invalid server URL."
        case .networkError(let error):
            return "Network error: \(error.localizedDescription)"
        case .httpError(let code, _):
            return "Server error (\(code)). Please try again."
        case .decodingError(let error):
            return "Could not read server response: \(error.localizedDescription)"
        case .retakeRequired(let message, _):
            return message
        case .unknown:
            return "An unexpected error occurred."
        }
    }

    var isRetakeRequired: Bool {
        if case .retakeRequired = self { return true }
        return false
    }
}
