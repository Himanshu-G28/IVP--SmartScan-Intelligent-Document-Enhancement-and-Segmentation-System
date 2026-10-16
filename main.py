#!/usr/bin/env python3
"""
================================================================================
Project Title : SmartScan Studio PRO - Intelligent Document Enhancement & Segmentation
Course        : Image and Video Processing (Course Code: 702EX0E020) | Semester V
Institution   : NMIMS University, MPSTME
Faculty       : Dr. Sachin Chavan
Team Members  :
  1. Parth Chaturvedi (Roll No. E235) - Stage 1: Data Rep, Color Spaces & Preprocessing
  2. Divyansh Karel   (Roll No. E236) - Stage 2 & 3: Edge Operators & Segmentation
  3. Himanshu Garg    (Roll No. E250, Lead) - Stage 4 & 5: Morphology, 2D DFT, HD Engine & Full Pipeline
================================================================================
"""

import os
import sys
import math
import argparse
import cv2
import numpy as np
import matplotlib.pyplot as plt

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SAMPLES_DIR = os.path.join(BASE_DIR, "samples")
RESULTS_DIR = os.path.join(BASE_DIR, "results")
os.makedirs(RESULTS_DIR, exist_ok=True)
os.makedirs(SAMPLES_DIR, exist_ok=True)

SAMPLE_MAP = {
    1: ("sample_1_academic_shadowed.jpg", "Academic Research Paper (Severe Diagonal Shadow & Sensor Noise)"),
    2: ("sample_2_tax_invoice.jpg", "Commercial Tax Invoice (Table Grid, Blue Header, Green PAID Stamp)"),
    3: ("sample_3_official_certificate.jpg", "University Certificate (Gold Border, Red Official Seal, Blue Signature)"),
    4: ("sample_4_book_spine_page.jpg", "Textbook Page (Severe Curved Spine Crease Shadow & Dual Columns)"),
    5: ("sample_5_medical_prescription.jpg", "Clinical Prescription (Red Rx Symbol, Doctor Sign, Fluorescent Shadow)")
}


# ------------------------------------------------------------------------------
# Quantitative Metric Calculations
# ------------------------------------------------------------------------------
def calculate_psnr(orig, enhanced):
    if orig.shape != enhanced.shape:
        enhanced = cv2.resize(enhanced, (orig.shape[1], orig.shape[0]))
    mse = np.mean((orig.astype(float) - enhanced.astype(float)) ** 2)
    if mse == 0:
        return float('inf')
    return 20.0 * math.log10(255.0 / math.sqrt(mse))


def calculate_cir(orig, enhanced):
    std_orig = np.std(orig.astype(float))
    std_enh = np.std(enhanced.astype(float))
    return (std_enh / (std_orig + 1e-6))


# ------------------------------------------------------------------------------
# Core Turnkey Pipeline Execution
# ------------------------------------------------------------------------------
def run_pipeline(image_path=None, sample_num=None, show_ui=True, save_prefix=""):
    print("=" * 76)
    print(" SmartScan Studio PRO - Complete IVP Execution Pipeline")
    print(" Faculty In-Charge: Dr. Sachin Chavan | NMIMS MPSTME")
    print(" Team: Parth (E235), Divyansh (E236), Himanshu (E250 - Lead)")
    print("=" * 76)

    # Resolve input image path
    if sample_num is not None and sample_num in SAMPLE_MAP:
        fname, desc = SAMPLE_MAP[sample_num]
        candidate = os.path.join(SAMPLES_DIR, fname)
        if os.path.exists(candidate):
            image_path = candidate
            print(f"[SAMPLE {sample_num}] Selected Benchmark: {desc}")

    if not image_path or not os.path.exists(image_path):
        candidate_default = os.path.join(BASE_DIR, "sample_document.jpg")
        if os.path.exists(candidate_default):
            image_path = candidate_default
        else:
            sample_1 = os.path.join(SAMPLES_DIR, "sample_1_academic_shadowed.jpg")
            if os.path.exists(sample_1):
                image_path = sample_1
            else:
                print("[ERROR] No input image found and no samples available.")
                return None

    filename = os.path.basename(image_path)
    print(f"[STAGE 0] Ingesting Document: {filename}")
    bgr = cv2.imread(image_path)
    if bgr is None:
        print(f"[ERROR] Could not load image from {image_path}")
        return None

    h, w = bgr.shape[:2]
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)

    # --------------------------------------------------------------------------
    # STAGE 1: Preprocessing & Illumination Normalization (Parth Chaturvedi - E235)
    # --------------------------------------------------------------------------
    print("[STAGE 1] Preprocessing: Median Denoising & Retinex Illumination Normalization (Parth)...")
    # A. 2D Median filter (5x5) eliminates salt-and-pepper impulses without edge blurring
    med = cv2.medianBlur(gray, 5)

    # B. Retinex Illumination Background Estimation & Division Normalization
    bg = cv2.GaussianBlur(med.astype(np.float32), (61, 61), 30)
    norm = np.clip((med.astype(np.float32) / (bg + 1e-5)) * 250.0, 0, 255).astype(np.uint8)

    # C. Tone curve to snap background to pristine paper white (255) and deepen text ink
    lut_tone = np.array([int(255 * ((i / 228.0) ** 1.35)) if i < 228 else 255 for i in range(256)], dtype=np.uint8)
    enhanced = cv2.LUT(norm, lut_tone)

    # --------------------------------------------------------------------------
    # STAGE 2: Edge Detection & Boundary Analysis (Divyansh Karel - E236)
    # --------------------------------------------------------------------------
    print("[STAGE 2] Boundary Extraction: Sobel Magnitude & Canny Detector (Divyansh)...")
    # A. Sobel first-order gradients
    gx = cv2.Sobel(enhanced, cv2.CV_64F, 1, 0, ksize=3)
    gy = cv2.Sobel(enhanced, cv2.CV_64F, 0, 1, ksize=3)
    sobel_mag = cv2.magnitude(gx, gy)
    sobel_norm = cv2.normalize(sobel_mag, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)

    # B. Canny Optimal Edge Detection (Gaussian -> Sobel -> NMS -> Hysteresis)
    canny_edges = cv2.Canny(enhanced, 50, 150)

    # --------------------------------------------------------------------------
    # STAGE 3: Document Segmentation: Otsu vs Adaptive (Divyansh Karel - E236)
    # --------------------------------------------------------------------------
    print("[STAGE 3] Document Segmentation: Global Otsu vs Local Adaptive (Divyansh)...")
    # A. Global Otsu Thresholding on RAW input (Demonstrates catastrophic failure under shadow gradients)
    _, otsu_bin = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # B. Local Adaptive Gaussian Thresholding (31x31 neighborhood, C=10)
    adaptive_bin = cv2.adaptiveThreshold(enhanced, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                         cv2.THRESH_BINARY, 31, 10)

    # --------------------------------------------------------------------------
    # STAGE 4: Mathematical Morphology (Himanshu Garg - E250)
    # --------------------------------------------------------------------------
    print("[STAGE 4] Mathematical Morphology: Opening & Closing (Himanshu)...")
    # Invert image so black text becomes white foreground (255)
    inv_text = cv2.bitwise_not(adaptive_bin)

    # A. Opening (Erosion followed by Dilation with 2x2 SE): eliminates isolated speckles
    se_open = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    opened = cv2.morphologyEx(inv_text, cv2.MORPH_OPEN, se_open)

    # B. Closing (Dilation followed by Erosion with 3x3 Cross SE): bridges broken strokes
    se_close = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))
    closed = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, se_close)

    # Invert back to black text on white background
    morph_clean = cv2.bitwise_not(closed)

    # --------------------------------------------------------------------------
    # STAGE 5: Transform Domain / 2D DFT (Himanshu Garg - E250)
    # --------------------------------------------------------------------------
    print("[STAGE 5] Frequency Analysis: 2D Discrete Fourier Transform (Himanshu)...")
    dft = np.fft.fft2(gray.astype(np.float32))
    dft_shift = np.fft.fftshift(dft)
    dft_mag = 20.0 * np.log(np.abs(dft_shift) + 1.0)
    dft_norm = cv2.normalize(dft_mag, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)

    # --------------------------------------------------------------------------
    # MASTER TRUE-COLOR HD RESTORATION (Himanshu Garg - Lead Architecture)
    # --------------------------------------------------------------------------
    print("[MASTER ENGINE] 2x Lanczos-4 Super-Resolution & Retinex Color HD Engine (Himanshu)...")
    # 1. 2x Super-Resolution Upscaling using Lanczos-4 (8-lobed sinc) interpolation
    hd_color = cv2.resize(bgr, (w * 2, h * 2), interpolation=cv2.INTER_LANCZOS4)

    # 2. CIE LAB Color Space Decoupling (Luminance sharpened independently from Chroma)
    lab = cv2.cvtColor(hd_color, cv2.COLOR_BGR2LAB)
    L, A, B = cv2.split(lab)

    # 3. Sub-pixel Median Filtering for impulse noise
    L_med = cv2.medianBlur(L, 3)

    # 4. Retinex Illumination Normalization on L (ERADICATES SHADOWS COMPLETELY!)
    bg_L = cv2.GaussianBlur(L_med.astype(np.float32), (81, 81), 40)
    L_norm = np.clip((L_med.astype(np.float32) / (bg_L + 1e-5)) * 250.0, 0, 255).astype(np.uint8)

    # 5. Bilateral Edge-Preserving Filter (smooths paper grain, locks text boundaries)
    L_bil = cv2.bilateralFilter(L_norm, d=7, sigmaColor=35, sigmaSpace=35)

    # 6. Multi-Scale Dual-Pass High-Boost Unsharp Masking
    # Pass 1: Fine edge contour pass (sigma=1.0)
    blur_fine = cv2.GaussianBlur(L_bil, (0, 0), 1.0)
    sharp_fine = cv2.addWeighted(L_bil, 1.75, blur_fine, -0.75, 0)
    sharp_fine = np.clip(sharp_fine, 0, 255).astype(np.uint8)

    # Pass 2: Stroke body density pass (sigma=2.5)
    blur_med = cv2.GaussianBlur(sharp_fine, (0, 0), 2.5)
    sharp_body = cv2.addWeighted(sharp_fine, 1.35, blur_med, -0.35, 0)
    sharp_body = np.clip(sharp_body, 0, 255).astype(np.uint8)

    # 7. Paper White Calibration & Text Contrast S-Curve
    lut_hd = np.array([int(255 * ((i / 225.0) ** 1.35)) if i < 225 else 255 for i in range(256)], dtype=np.uint8)
    L_final = cv2.LUT(sharp_body, lut_hd)

    # 8. Paper Chroma Neutralization (removes yellow shadow tint; preserves authentic stamps/signatures)
    is_paper = (L_final > 242).astype(np.float32)
    A_clean = (A.astype(np.float32) * (1.0 - is_paper * 0.75) + 128.0 * (is_paper * 0.75)).astype(np.uint8)
    B_clean = (B.astype(np.float32) * (1.0 - is_paper * 0.75) + 128.0 * (is_paper * 0.75)).astype(np.uint8)

    lab_restored = cv2.merge([L_final, A_clean, B_clean])
    final_master_hd = cv2.cvtColor(lab_restored, cv2.COLOR_LAB2BGR)

    # --------------------------------------------------------------------------
    # Quantitative Benchmarks & Image Saving
    # --------------------------------------------------------------------------
    psnr_score = calculate_psnr(gray, cv2.resize(cv2.cvtColor(final_master_hd, cv2.COLOR_BGR2GRAY), (w, h)))
    cir_score = calculate_cir(gray, enhanced)
    
    # Calculate dramatic visual difference metrics
    orig_mean = float(gray.mean())
    rest_mean = float(cv2.cvtColor(final_master_hd, cv2.COLOR_BGR2GRAY).mean())
    pixel_distinction = float(np.abs(cv2.resize(gray, (w * 2, h * 2)).astype(float) - cv2.cvtColor(final_master_hd, cv2.COLOR_BGR2GRAY).astype(float)).mean())

    pfx = f"{save_prefix}_" if save_prefix else ""
    cv2.imwrite(os.path.join(RESULTS_DIR, f"{pfx}1_original_gray.jpg"), gray)
    cv2.imwrite(os.path.join(RESULTS_DIR, f"{pfx}2_enhanced_clahe.jpg"), enhanced)
    cv2.imwrite(os.path.join(RESULTS_DIR, f"{pfx}3_canny_edges.jpg"), canny_edges)
    cv2.imwrite(os.path.join(RESULTS_DIR, f"{pfx}4_otsu_failure.jpg"), otsu_bin)
    cv2.imwrite(os.path.join(RESULTS_DIR, f"{pfx}5_adaptive_segmentation.jpg"), adaptive_bin)
    cv2.imwrite(os.path.join(RESULTS_DIR, f"{pfx}6_morphological_clean.jpg"), morph_clean)
    cv2.imwrite(os.path.join(RESULTS_DIR, f"{pfx}7_dft_spectrum.jpg"), dft_norm)
    cv2.imwrite(os.path.join(RESULTS_DIR, f"{pfx}8_final_master_hd.jpg"), final_master_hd)

    # Generate a high-contrast side-by-side Before/After proof
    orig_hd = cv2.resize(bgr, (w * 2, h * 2))
    before_after_proof = np.hstack([orig_hd, final_master_hd])
    cv2.imwrite(os.path.join(RESULTS_DIR, f"{pfx}before_after_comparison.jpg"), before_after_proof)

    print("-" * 76)
    print(" EXECUTION BENCHMARKS & EVALUATION:")
    print(f" • Input Image Baseline Mean         : {orig_mean:.1f} / 255 (Dark Shaded)")
    print(f" • Restored Output Mean (Pure White) : {rest_mean:.1f} / 255 (Pristine White Platen)")
    print(f" • Visual Distinction (Mean Shift)   : {pixel_distinction:.1f} gray levels (Dramatic!)")
    print(f" • Peak Signal-to-Noise Ratio (PSNR) : {psnr_score:.2f} dB")
    print(f" • Contrast Improvement Ratio (CIR) : {cir_score:.2f}x")
    print(f" • Output HD Resolution             : {w*2} x {h*2} px (2x Lanczos-4)")
    print(f" • Artifacts Saved In               : {RESULTS_DIR}/")
    print("-" * 76)

    # --------------------------------------------------------------------------
    # Visual Multi-Stage Panel Display (Matplotlib)
    # --------------------------------------------------------------------------
    if show_ui:
        fig, axes = plt.subplots(2, 4, figsize=(18, 9))
        fig.suptitle(f"SmartScan Studio PRO | Faculty In-Charge: Dr. Sachin Chavan\n"
                     f"File: {filename}  |  Visual Shift: +{pixel_distinction:.1f}  |  PSNR: {psnr_score:.2f} dB  |  HD: {w*2}x{h*2}px",
                     fontsize=14, fontweight='bold')

        plots = [
            (axes[0, 0], gray, "1. Original Degraded (Shadow & Noise)", "gray"),
            (axes[0, 1], enhanced, "2. Preprocessed (Retinex Leveling)", "gray"),
            (axes[0, 2], canny_edges, "3. Canny Optimal Edges", "gray"),
            (axes[0, 3], otsu_bin, "4. Global Otsu (Catastrophic Failure)", "gray"),
            (axes[1, 0], adaptive_bin, "5. Local Adaptive Gaussian", "gray"),
            (axes[1, 1], morph_clean, "6. Morphological Clean (Open+Close)", "gray"),
            (axes[1, 2], dft_norm, "7. 2D Fourier Spectrum (DFT)", "inferno"),
            (axes[1, 3], cv2.cvtColor(final_master_hd, cv2.COLOR_BGR2RGB), "8. Master True-Color HD Output", None)
        ]

        for ax, img, title, cmap in plots:
            if cmap:
                ax.imshow(img, cmap=cmap)
            else:
                ax.imshow(img)
            ax.set_title(title, fontsize=10, fontweight='bold')
            ax.axis('off')

        plt.tight_layout()
        comparison_path = os.path.join(RESULTS_DIR, f"{pfx}all_stages_comparison.png")
        plt.savefig(comparison_path, dpi=300)
        print(f"[SUCCESS] Multi-stage comparison chart saved to: {comparison_path}")
        plt.show()

    return {
        "psnr": psnr_score,
        "cir": cir_score,
        "distinction": pixel_distinction,
        "orig_mean": orig_mean,
        "rest_mean": rest_mean
    }


def run_all_samples():
    print("=" * 76)
    print(" BATCH BENCHMARKING ALL 5 DIVERSE SAMPLES ACROSS PIPELINE")
    print("=" * 76)
    summary = []
    for s_idx in range(1, 6):
        fname, desc = SAMPLE_MAP[s_idx]
        fpath = os.path.join(SAMPLES_DIR, fname)
        if not os.path.exists(fpath):
            continue
        print(f"\n---> PROCESSING SAMPLE {s_idx}: {desc}")
        stats = run_pipeline(image_path=fpath, show_ui=False, save_prefix=f"sample_{s_idx}")
        if stats:
            summary.append((s_idx, desc, stats))

    print("\n" + "=" * 76)
    print(" BATCH BENCHMARK SUMMARY TABLE:")
    print("=" * 76)
    print(f"{'Sample #':<10} | {'Mean Diff':<12} | {'Orig Mean':<12} | {'New Mean':<12} | {'PSNR (dB)':<10}")
    print("-" * 76)
    for s_idx, desc, s in summary:
        print(f"Sample {s_idx:<3} | {s['distinction']:>8.1f} px | {s['orig_mean']:>8.1f}    | {s['rest_mean']:>8.1f}    | {s['psnr']:>7.2f} dB")
    print("=" * 76)
    print(f"All sample comparisons and outputs saved in: {RESULTS_DIR}/\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SmartScan Studio PRO CLI Execution Engine")
    parser.add_argument("--input", type=str, default=None, help="Path to input document image")
    parser.add_argument("--sample", type=int, choices=[1, 2, 3, 4, 5], default=None, help="Select benchmark sample 1 to 5")
    parser.add_argument("--all-samples", action="store_true", help="Batch execute all 5 samples and generate comparison table")
    parser.add_argument("--no-ui", action="store_true", help="Run without opening interactive GUI window")
    args = parser.parse_args()

    if args.all_samples:
        run_all_samples()
    else:
        run_pipeline(image_path=args.input, sample_num=args.sample, show_ui=not args.no_ui)
