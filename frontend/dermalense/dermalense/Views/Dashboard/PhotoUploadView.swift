//
//  PhotoUploadView.swift
//  dermalense
//
//  Created by Mohammed Abdur Rahman on 2/14/26.
//

import SwiftUI
import PhotosUI

struct PhotoUploadView: View {
    var onNext: () -> Void

    @State private var frontImage: PhotosPickerItem?
    @State private var leftImage: PhotosPickerItem?
    @State private var rightImage: PhotosPickerItem?
    @State private var frontImageData: Data?
    @State private var leftImageData: Data?
    @State private var rightImageData: Data?
    @State private var isSubmitting = false

    private var allPhotosSelected: Bool {
        frontImageData != nil && leftImageData != nil && rightImageData != nil
    }

    var body: some View {
        ScrollView {
            VStack(spacing: DLSpacing.lg) {
                headerSection
                photoGrid
                submitButton
            }
            .padding(DLSpacing.md)
        }
    }

    // MARK: - Header

    private var headerSection: some View {
        VStack(spacing: DLSpacing.sm) {
            Image(systemName: "faceid")
                .font(.system(size: 48))
                .foregroundStyle(DLColor.primaryFallback)
                .padding(.bottom, DLSpacing.xs)

            Text("Upload Your Photos")
                .font(DLFont.title)
                .foregroundStyle(DLColor.primaryFallback)

            Text("Take 3 photos of your face for a comprehensive skin analysis. Make sure you're in good lighting.")
                .font(DLFont.body)
                .foregroundStyle(.secondary)
                .multilineTextAlignment(.center)
                .padding(.horizontal, DLSpacing.lg)
        }
    }

    // MARK: - Photo Grid

    private var photoGrid: some View {
        VStack(spacing: DLSpacing.md) {
            // Front photo - large
            photoCard(
                title: "Front",
                subtitle: "Face the camera directly",
                systemImage: "person.fill",
                imageData: frontImageData,
                pickerSelection: $frontImage
            )
            .frame(height: 200)
            .onChange(of: frontImage) { _, newValue in
                loadImage(from: newValue) { frontImageData = $0 }
            }

            // Side photos - side by side
            HStack(spacing: DLSpacing.md) {
                photoCard(
                    title: "Left Side",
                    subtitle: "Turn left 90\u{00B0}",
                    systemImage: "arrow.turn.up.left",
                    imageData: leftImageData,
                    pickerSelection: $leftImage
                )
                .frame(height: 160)
                .onChange(of: leftImage) { _, newValue in
                    loadImage(from: newValue) { leftImageData = $0 }
                }

                photoCard(
                    title: "Right Side",
                    subtitle: "Turn right 90\u{00B0}",
                    systemImage: "arrow.turn.up.right",
                    imageData: rightImageData,
                    pickerSelection: $rightImage
                )
                .frame(height: 160)
                .onChange(of: rightImage) { _, newValue in
                    loadImage(from: newValue) { rightImageData = $0 }
                }
            }
        }
    }

    // MARK: - Photo Card

    private func photoCard(
        title: String,
        subtitle: String,
        systemImage: String,
        imageData: Data?,
        pickerSelection: Binding<PhotosPickerItem?>
    ) -> some View {
        PhotosPicker(selection: pickerSelection, matching: .images) {
            ZStack {
                if let imageData, let uiImage = UIImage(data: imageData) {
                    Image(uiImage: uiImage)
                        .resizable()
                        .scaledToFill()
                        .clipped()
                        .overlay(
                            LinearGradient(
                                colors: [.black.opacity(0.4), .clear],
                                startPoint: .bottom,
                                endPoint: .center
                            )
                        )
                        .overlay(alignment: .bottomLeading) {
                            HStack {
                                Image(systemName: "checkmark.circle.fill")
                                    .foregroundStyle(.green)
                                Text(title)
                                    .font(DLFont.caption)
                                    .fontWeight(.semibold)
                            }
                            .foregroundStyle(.white)
                            .padding(DLSpacing.sm)
                        }
                } else {
                    VStack(spacing: DLSpacing.sm) {
                        Image(systemName: systemImage)
                            .font(.system(size: 28))
                            .foregroundStyle(DLColor.primaryFallback.opacity(0.6))

                        Text(title)
                            .font(DLFont.headline)
                            .foregroundStyle(.primary)

                        Text(subtitle)
                            .font(DLFont.caption)
                            .foregroundStyle(.secondary)
                    }
                    .frame(maxWidth: .infinity, maxHeight: .infinity)
                    .background(Color(.systemGray6))
                }
            }
            .clipShape(RoundedRectangle(cornerRadius: DLRadius.lg))
            .overlay(
                RoundedRectangle(cornerRadius: DLRadius.lg)
                    .strokeBorder(
                        imageData != nil ? Color.green.opacity(0.5) : DLColor.primaryFallback.opacity(0.2),
                        style: imageData != nil ? StrokeStyle(lineWidth: 2) : StrokeStyle(lineWidth: 2, dash: [8, 4])
                    )
            )
        }
        .buttonStyle(.plain)
    }

    // MARK: - Submit

    private var submitButton: some View {
        Button {
            isSubmitting = true
            // Simulate upload delay, then advance
            DispatchQueue.main.asyncAfter(deadline: .now() + 1.5) {
                isSubmitting = false
                onNext()
            }
        } label: {
            HStack(spacing: DLSpacing.sm) {
                if isSubmitting {
                    ProgressView()
                        .tint(.white)
                } else {
                    Image(systemName: "arrow.up.circle.fill")
                }
                Text(isSubmitting ? "Uploading..." : "Submit Photos")
                    .fontWeight(.semibold)
            }
            .frame(maxWidth: .infinity)
            .padding(.vertical, 16)
            .background(
                RoundedRectangle(cornerRadius: DLRadius.md)
                    .fill(allPhotosSelected ? DLColor.primaryFallback : Color(.systemGray4))
            )
            .foregroundStyle(.white)
        }
        .disabled(!allPhotosSelected || isSubmitting)
        .animation(.easeInOut, value: allPhotosSelected)
    }

    // MARK: - Helpers

    private func loadImage(from item: PhotosPickerItem?, completion: @escaping (Data?) -> Void) {
        guard let item else { return }
        item.loadTransferable(type: Data.self) { result in
            DispatchQueue.main.async {
                switch result {
                case .success(let data):
                    completion(data)
                case .failure:
                    completion(nil)
                }
            }
        }
    }
}

#Preview {
    PhotoUploadView(onNext: {})
}
