# ==============================================================================
# Project Title : SmartScan - Document Enhancement and Segmentation System
# Course        : Image and Video Processing (IVP) Mini Project (3rd Year B.Tech CS)
# Group Members :
#   1. Parth Chaturvedi (E235) - Stage 1: Preprocessing & Contrast Enhancement
#   2. Divyansh Karel   (E236) - Stage 2 & 3: Edge Detection & Thresholding
#   3. Himanshu Garg    (E250) - Stage 4: Morphological Cleaning & PSNR Evaluation
# ==============================================================================

import os
import math
import cv2
import numpy as np
import matplotlib.pyplot as plt

# Get the folder where this script is saved so paths always work
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_IMAGE_PATH = os.path.join(BASE_DIR, "sample_document.jpg")
RESULTS_DIR = os.path.join(BASE_DIR, "results")

os.makedirs(RESULTS_DIR, exist_ok=True)


# ------------------------------------------------------------------------------
# Helper: Create a sample noisy & shadowed document if image is not found
# ------------------------------------------------------------------------------
def create_sample_if_missing(path):
    if os.path.exists(path):
        return

    # 1. Start with a plain white page (800 x 600 pixels)
    img = np.ones((800, 600), dtype=np.uint8) * 255

    # 2. Write text on the page
    lines = [
        "PROJECT PHASE-I",
        "SmartScan System",
        "IVP Mini Project",
        "Group Members:",
        "Parth Chaturvedi (E235)",
        "Divyansh Karel (E236)",
        "Himanshu Garg (E250)",
        "",
        "This is a sample document",
        "with three common problems:",
        "- Heavy dark shadows",
        "- Salt and pepper noise dots",
        "- Broken text letters"
    ]
    y = 50
    for line in lines:
        cv2.putText(img, line, (50, y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
        y += 40

    # 3. Add a dark shadow across the page
    rows, cols = img.shape
    for i in range(rows):
        for j in range(cols):
            shadow_factor = 1.0 - 0.6 * ((i / rows) + (j / cols)) / 2
            img[i, j] = int(img[i, j] * shadow_factor)

    # 4. Add random black and white noise dots (Salt & Pepper noise)
    noise = np.random.randint(0, 255, img.shape)
    img[noise < 5] = 0      # Black dots (pepper)
    img[noise > 250] = 255  # White dots (salt)

    cv2.imwrite(path, img)
    print("Created sample noisy document at:", path)


# ==============================================================================
# STAGE 1: PREPROCESSING & ENHANCEMENT (Parth Chaturvedi - E235)
# ==============================================================================
def preprocess_image(gray_img):
    # Step 1A: Median Filter (5x5) to remove salt-and-pepper noise dots
    denoised = cv2.medianBlur(gray_img, 5)

    # Step 1B: Illumination Normalization to remove the dark background shadow
    # We blur the image heavily to estimate the background shadow, then divide by it
    background = cv2.GaussianBlur(denoised, (75, 75), 0)
    normalized = cv2.divide(denoised, background, scale=255)

    # Step 1C: CLAHE (Contrast Limited Adaptive Histogram Equalization)
    # Makes the text darker and sharper locally in small 8x8 tiles
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(normalized)

    return enhanced


# ==============================================================================
# STAGE 2: EDGE DETECTION (Divyansh Karel - E236)
# ==============================================================================
def detect_edges(enhanced_img):
    # Canny Edge Detector finds sharp boundaries of the letters
    edges = cv2.Canny(enhanced_img, 50, 150)
    return edges


# ==============================================================================
# STAGE 3: IMAGE SEGMENTATION / THRESHOLDING (Divyansh Karel - E236)
# ==============================================================================
def segment_document(enhanced_img):
    # Method A: Global Otsu Thresholding (uses ONE single cutoff value for whole page)
    # We include this to show how normal global thresholding struggles with shadows
    _, otsu_binary = cv2.threshold(
        enhanced_img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )

    # Method B: Local Adaptive Thresholding (calculates threshold for small 21x21 regions)
    # This cleanly separates black text from the white background everywhere
    adaptive_binary = cv2.adaptiveThreshold(
        enhanced_img,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        blockSize=21,
        C=10
    )

    return otsu_binary, adaptive_binary


# ==============================================================================
# STAGE 4: MORPHOLOGICAL POST-PROCESSING & PSNR (Himanshu Garg - E250)
# ==============================================================================
def clean_with_morphology(binary_img):
    # Note: In OpenCV morphology, operations work on WHITE foreground pixels.
    # Since our text is BLACK (0) on a WHITE (255) page, we invert the image first.
    inverted = cv2.bitwise_not(binary_img)

    # 3x3 rectangular structuring element (kernel)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))

    # Step 4A: Morphological Opening (Erosion -> Dilation)
    # Removes tiny leftover noise dots in the background
    opened = cv2.morphologyEx(inverted, cv2.MORPH_OPEN, kernel)

    # Step 4B: Morphological Closing (Dilation -> Erosion)
    # Fills tiny gaps and joins broken strokes inside the letters
    closed = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, kernel)

    # Invert back so text is black and page is white again
    final_clean = cv2.bitwise_not(closed)
    return final_clean


def calculate_psnr(original_img, final_img):
    # Mean Squared Error (MSE) = average of squared differences between pixels
    mse = np.mean((original_img.astype(float) - final_img.astype(float)) ** 2)
    if mse == 0:
        return 100.0

    # PSNR formula = 20 * log10(255 / sqrt(MSE))
    psnr = 20 * math.log10(255.0 / math.sqrt(mse))
    return psnr


# ==============================================================================
# MAIN PROGRAM FLOW
# ==============================================================================
def main():
    print("Starting SmartScan Document Enhancement Pipeline...\n")

    # 1. Ensure sample image exists and load it
    create_sample_if_missing(INPUT_IMAGE_PATH)
    original_bgr = cv2.imread(INPUT_IMAGE_PATH)

    if original_bgr is None:
        print("Error: Could not read sample_document.jpg!")
        return

    # Convert color image to Grayscale
    gray = cv2.cvtColor(original_bgr, cv2.COLOR_BGR2GRAY)
    cv2.imwrite(os.path.join(RESULTS_DIR, "1_original_gray.jpg"), gray)
    print("[Step 1] Loaded image and converted to Grayscale.")

    # 2. Run Stage 1: Preprocessing & Enhancement
    enhanced = preprocess_image(gray)
    cv2.imwrite(os.path.join(RESULTS_DIR, "2_enhanced.jpg"), enhanced)
    print("[Step 2] Applied Median Filter, Shadow Removal, and CLAHE.")

    # 3. Run Stage 2: Edge Detection
    edges = detect_edges(enhanced)
    cv2.imwrite(os.path.join(RESULTS_DIR, "3_edges.jpg"), edges)
    print("[Step 3] Extracted text boundaries using Canny Edge Detector.")

    # 4. Run Stage 3: Segmentation (Otsu vs Adaptive)
    otsu_bin, adaptive_bin = segment_document(enhanced)
    cv2.imwrite(os.path.join(RESULTS_DIR, "4_otsu_bin.jpg"), otsu_bin)
    cv2.imwrite(os.path.join(RESULTS_DIR, "5_adaptive_bin.jpg"), adaptive_bin)
    print("[Step 4] Segmented text using Global Otsu and Local Adaptive Thresholding.")

    # 5. Run Stage 4: Morphological Cleaning
    final_output = clean_with_morphology(adaptive_bin)
    cv2.imwrite(os.path.join(RESULTS_DIR, "6_final_morphology.jpg"), final_output)
    print("[Step 5] Cleaned speckles & repaired letters using Morphological Opening/Closing.")

    # 6. Calculate Evaluation Metrics
    psnr_value = calculate_psnr(gray, final_output)
    contrast_before = np.std(gray)
    contrast_after = np.std(enhanced)
    cir_value = contrast_after / contrast_before

    print("\n---------------- FINAL RESULTS ----------------")
    print(f"Peak Signal-to-Noise Ratio (PSNR) : {psnr_value:.2f} dB")
    print(f"Contrast Improvement Ratio (CIR)  : {cir_value:.2f}x")
    print(f"All 6 output images saved in      : {RESULTS_DIR}")
    print("-----------------------------------------------\n")

    # 7. Display all 6 stages side-by-side using Matplotlib
    titles = [
        "1. Original Noisy & Shadowed",
        "2. Enhanced (Median + CLAHE)",
        "3. Canny Edges",
        "4. Global Otsu Threshold",
        "5. Local Adaptive Threshold",
        "6. Final Cleaned (Morphology)"
    ]
    images = [gray, enhanced, edges, otsu_bin, adaptive_bin, final_output]

    plt.figure(figsize=(12, 8))
    plt.suptitle(
        f"SmartScan - IVP Mini Project | PSNR: {psnr_value:.2f} dB",
        fontsize=14,
        fontweight="bold"
    )

    for i in range(6):
        plt.subplot(2, 3, i + 1)
        plt.imshow(images[i], cmap="gray")
        plt.title(titles[i], fontsize=10)
        plt.axis("off")

    plt.tight_layout()
    summary_path = os.path.join(RESULTS_DIR, "all_stages_comparison.png")
    plt.savefig(summary_path, dpi=150)
    print("Saved combined comparison chart at:", summary_path)
    plt.show()


if __name__ == "__main__":
    main()
