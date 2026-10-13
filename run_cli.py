import cv2
import argparse
import time
import os
import math
import numpy as np

def psnr(img1, img2):
    if img1.shape != img2.shape:
        img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))
    mse = np.mean((img1.astype(float) - img2.astype(float)) ** 2)
    if mse == 0:
        return float('inf')
    return 20 * math.log10(255.0 / math.sqrt(mse))

def cir(orig, enhanced):
    s_orig = np.std(orig)
    s_enh = np.std(enhanced)
    return s_enh / s_orig if s_orig != 0 else float('inf')

def main():
    parser = argparse.ArgumentParser(description="SmartScan Comprehensive IVP Suite CLI")
    parser.add_argument('--input', type=str, default='samples/synthetic_degraded.jpg', help='Path to input image')
    parser.add_argument('--output_dir', type=str, default='results', help='Directory to save outputs')
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    bgr = cv2.imread(args.input)
    if bgr is None:
        print(f"Error: Cannot load image {args.input}")
        return

    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape

    print("Executing Complete IVP Syllabus Processing Suite...")

    # 1. Data Rep
    cv2.imwrite(f"{args.output_dir}/1_grayscale.jpg", gray)
    _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    cv2.imwrite(f"{args.output_dir}/2_binary.jpg", binary)

    # 2. Color Spaces
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    cv2.imwrite(f"{args.output_dir}/3_hsv_v.jpg", hsv[:, :, 2])
    ycrcb = cv2.cvtColor(bgr, cv2.COLOR_BGR2YCrCb)
    cv2.imwrite(f"{args.output_dir}/4_ycrcb_y.jpg", ycrcb[:, :, 0])
    cv2.imwrite(f"{args.output_dir}/5_negative.jpg", 255 - gray)

    # 3. Point Transformations
    log_img = np.log1p(gray.astype(np.float32))
    log_img = cv2.normalize(log_img, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    cv2.imwrite(f"{args.output_dir}/6_log_transform.jpg", log_img)

    table_05 = np.array([((i / 255.0) ** 0.5) * 255 for i in range(256)]).astype(np.uint8)
    cv2.imwrite(f"{args.output_dir}/7_gamma_05.jpg", cv2.LUT(gray, table_05))

    mn, mx = float(gray.min()), float(gray.max())
    cs = ((gray.astype(np.float32) - mn) / (mx - mn + 1e-6) * 255).astype(np.uint8)
    cv2.imwrite(f"{args.output_dir}/8_contrast_stretch.jpg", cs)

    # 4. Histograms & Filters
    cv2.imwrite(f"{args.output_dir}/9_hist_equalized.jpg", cv2.equalizeHist(gray))
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(gray)
    cv2.imwrite(f"{args.output_dir}/10_clahe.jpg", clahe)
    cv2.imwrite(f"{args.output_dir}/11_median_filter.jpg", cv2.medianBlur(gray, 5))

    # 5. Edge Extraction
    gx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
    gy = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
    sobel_mag = cv2.magnitude(gx, gy)
    cv2.imwrite(f"{args.output_dir}/12_sobel.jpg", cv2.normalize(sobel_mag, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8))
    cv2.imwrite(f"{args.output_dir}/13_canny.jpg", cv2.Canny(clahe, 50, 150))

    # 6. Morphology
    _, mbin = cv2.threshold(clahe, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    k3 = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    cv2.imwrite(f"{args.output_dir}/14_opening.jpg", cv2.morphologyEx(mbin, cv2.MORPH_OPEN, k3))
    cv2.imwrite(f"{args.output_dir}/15_closing.jpg", cv2.morphologyEx(mbin, cv2.MORPH_CLOSE, k3))

    # 7. Segmentation
    cv2.imwrite(f"{args.output_dir}/16_otsu_segmentation.jpg", mbin)
    adap = cv2.adaptiveThreshold(clahe, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 10)
    cv2.imwrite(f"{args.output_dir}/17_adaptive_segmentation.jpg", adap)

    # 8. Frequency Domain
    dft = np.fft.fft2(gray.astype(np.float32))
    dft_shift = np.fft.fftshift(dft)
    mag = 20 * np.log(np.abs(dft_shift) + 1)
    cv2.imwrite(f"{args.output_dir}/18_dft_spectrum.jpg", cv2.normalize(mag, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8))

    # 9. Master HD Restoration (Stage 4 Himanshu Garg)
    bilateral = cv2.bilateralFilter(gray, 9, 75, 75)
    clahe_hd = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(bilateral)
    nlm = cv2.fastNlMeansDenoising(clahe_hd, None, h=7, templateWindowSize=7, searchWindowSize=21)
    blur_hd = cv2.GaussianBlur(nlm, (0, 0), 1.5)
    sharp_hd = cv2.addWeighted(nlm, 2.0, blur_hd, -1.0, 0)
    sharp_hd = np.clip(sharp_hd, 0, 255).astype(np.uint8)
    mask_hd = cv2.adaptiveThreshold(sharp_hd, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 10)
    final_clean = np.where(mask_hd == 255, 255, sharp_hd).astype(np.uint8)
    final_hd = cv2.resize(final_clean, (w * 2, h * 2), interpolation=cv2.INTER_LANCZOS4)
    cv2.imwrite(f"{args.output_dir}/19_final_master_hd.jpg", final_hd)

    psnr_val = psnr(gray, final_clean)
    cir_val = cir(gray, sharp_hd)

    print("\n--- Summary Benchmarks ---")
    print(f"PSNR Gain: {psnr_val:.2f} dB")
    print(f"Contrast Improvement Ratio: {cir_val:.2f}x")
    print(f"HD Output Resolution: {w * 2} x {h * 2} px (2x Lanczos4)")
    print(f"All 19 textbook representations generated and saved to '{args.output_dir}/'")

if __name__ == "__main__":
    main()
