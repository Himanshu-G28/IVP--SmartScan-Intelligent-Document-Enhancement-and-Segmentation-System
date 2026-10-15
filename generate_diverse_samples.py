#!/usr/bin/env python3
"""
Generate a diverse suite of 5 realistic, degraded document benchmark images:
1. sample_1_academic_shadowed.jpg   - Research paper with heavy diagonal mobile shadow & salt-pepper noise
2. sample_2_tax_invoice.jpg         - Commercial tax invoice with blue banner, grid table, and green PAID stamp
3. sample_3_official_certificate.jpg - University certificate with gold border, red seal, and blue cursive signature
4. sample_4_book_spine_page.jpg     - Academic textbook page with severe curved spine crease shadow & bleed-through
5. sample_5_medical_prescription.jpg - Hospital prescription with red Rx symbol, doctor signature & sensor noise
"""

import os
import cv2
import numpy as np

def add_salt_pepper_noise(img, salt_prob=0.015, pepper_prob=0.015):
    noisy = img.copy()
    total_pixels = img.shape[0] * img.shape[1]
    
    # Salt
    num_salt = int(total_pixels * salt_prob)
    coords = [np.random.randint(0, i - 1, num_salt) for i in img.shape[:2]]
    noisy[tuple(coords)] = 255
    
    # Pepper
    num_pepper = int(total_pixels * pepper_prob)
    coords = [np.random.randint(0, i - 1, num_pepper) for i in img.shape[:2]]
    noisy[tuple(coords)] = 0
    return noisy

def generate_sample_1(output_path):
    """Academic Research Report with Heavy Diagonal Shadow & Noise"""
    h, w = 900, 680
    canvas = np.ones((h, w, 3), dtype=np.uint8) * 248
    font = cv2.FONT_HERSHEY_SIMPLEX
    
    # Header
    cv2.rectangle(canvas, (40, 35), (w - 40, 40), (60, 60, 60), -1)
    cv2.putText(canvas, "DEPARTMENT OF COMPUTER ENGINEERING | NMIMS MPSTME", (45, 65), font, 0.52, (30, 30, 30), 1, cv2.LINE_AA)
    cv2.putText(canvas, "Course: Image & Video Processing (702EX0E020)", (45, 90), font, 0.48, (80, 80, 80), 1, cv2.LINE_AA)
    cv2.putText(canvas, "Faculty In-Charge: Dr. Sachin Chavan", (45, 115), font, 0.48, (80, 80, 80), 1, cv2.LINE_AA)
    cv2.line(canvas, (40, 130), (w - 40, 130), (120, 120, 120), 1)
    
    # Title
    cv2.putText(canvas, "SmartScan: Document Enhancement Benchmark", (45, 165), font, 0.72, (15, 15, 15), 2, cv2.LINE_AA)
    cv2.putText(canvas, "Group Allocation: E235 (Parth), E236 (Divyansh), E250 (Himanshu)", (45, 195), font, 0.46, (70, 70, 70), 1, cv2.LINE_AA)
    
    # Body text
    body = [
        "1.0 INTRODUCTION & DEGRADATION MODELLING",
        "Document imaging via unconstrained handheld smartphones introduces severe",
        "optical degradations governed by the multiplicative Retinex formulation:",
        "    I_obs(x, y) = [ L(x, y) * R(x, y) ] + N_gaussian + N_impulse",
        "where L(x, y) denotes the low-frequency non-uniform illumination field,",
        "R(x, y) is the true surface reflectance containing textual glyphs, and",
        "N represents thermal sensor noise and impulse pixel dropouts.",
        "",
        "2.0 CLAHE & ADAPTIVE SEGMENTATION PERFORMANCE",
        "Standard global Otsu binarization fails when illumination gradients smear",
        "the intensity histogram into a unimodal distribution. By contrast, local",
        "adaptive Gaussian windowing dynamically tracks local background baselines,",
        "recovering 100% of characters without shadow blotching artifacts.",
        "",
        "3.0 MATHEMATICAL MORPHOLOGY RECONSTRUCTION",
        "Dual morphological opening and closing operators systematically eradicate",
        "isolated background noise specks while bridging broken character loops in",
        "degraded strokes, elevating downstream OCR accuracy from 62% to 98.4%."
    ]
    y = 235
    for line in body:
        if line.startswith("1.0") or line.startswith("2.0") or line.startswith("3.0"):
            cv2.putText(canvas, line, (45, y), font, 0.52, (20, 20, 20), 2, cv2.LINE_AA)
            y += 28
        else:
            cv2.putText(canvas, line, (45, y), font, 0.43, (50, 50, 50), 1, cv2.LINE_AA)
            y += 24

    # Apply severe diagonal shadow gradient (top-left bright, bottom-right heavily shadowed)
    Y, X = np.ogrid[:h, :w]
    shadow_map = 1.0 - 0.65 * ((X / w) * 0.45 + (Y / h) * 0.55)
    shadowed = (canvas.astype(np.float32) * shadow_map[:, :, np.newaxis]).astype(np.uint8)
    
    # Add salt & pepper noise
    final = add_salt_pepper_noise(shadowed, 0.015, 0.015)
    cv2.imwrite(output_path, final)
    print(f"[OK] Generated: {output_path}")

def generate_sample_2(output_path):
    """Commercial Tax Invoice with Blue Header, Table Grid & Green PAID Stamp"""
    h, w = 920, 680
    canvas = np.ones((h, w, 3), dtype=np.uint8) * 252
    font = cv2.FONT_HERSHEY_SIMPLEX

    # Blue Company Header
    cv2.rectangle(canvas, (40, 35), (w - 40, 115), (140, 70, 20), -1) # Dark Blue BGR
    cv2.putText(canvas, "APEX DIGITAL LOGISTICS PVT LTD", (60, 75), font, 0.72, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.putText(canvas, "Commercial Tax Invoice | GSTIN: 27AABCT8842K1Z9", (60, 100), font, 0.44, (220, 220, 220), 1, cv2.LINE_AA)

    # Invoice Details
    cv2.putText(canvas, "INVOICE TO:", (45, 145), font, 0.46, (90, 90, 90), 1, cv2.LINE_AA)
    cv2.putText(canvas, "NMIMS MPSTME Technology Lab", (45, 168), font, 0.54, (20, 20, 20), 2, cv2.LINE_AA)
    cv2.putText(canvas, "V.L. Mehta Road, Vile Parle (W), Mumbai", (45, 190), font, 0.44, (60, 60, 60), 1, cv2.LINE_AA)

    cv2.putText(canvas, "Invoice No : INV-2026-9810", (420, 145), font, 0.46, (30, 30, 30), 2, cv2.LINE_AA)
    cv2.putText(canvas, "Invoice Date: 14-Oct-2026", (420, 168), font, 0.44, (60, 60, 60), 1, cv2.LINE_AA)
    cv2.putText(canvas, "Payment Mode: NEFT / Bank Transfer", (420, 190), font, 0.44, (60, 60, 60), 1, cv2.LINE_AA)

    # Table Grid
    table_top = 225
    cv2.rectangle(canvas, (40, table_top), (w - 40, table_top + 32), (220, 220, 220), -1)
    cv2.rectangle(canvas, (40, table_top), (w - 40, table_top + 320), (100, 100, 100), 1)
    
    headers = [("ITEM DESCRIPTION", 55), ("HSN CODE", 340), ("QTY", 450), ("AMOUNT (INR)", 530)]
    for text, x in headers:
        cv2.putText(canvas, text, (x, table_top + 21), font, 0.44, (20, 20, 20), 2, cv2.LINE_AA)
    cv2.line(canvas, (40, table_top + 32), (w - 40, table_top + 32), (80, 80, 80), 1)

    items = [
        ("High-Speed Document Scanner Workstation", "8471", "02", "1,18,000.00"),
        ("Embedded GPU Acceleration Modules", "8542", "04", "84,500.00"),
        ("Optical Character Recognition Licenses", "9973", "01", "25,000.00"),
        ("Calibration Chart & Sensor Platen Grid", "9031", "05", "12,400.00"),
        ("Technical Support & Maintenance (1 Yr)", "9987", "01", "18,200.00")
    ]
    cur_y = table_top + 65
    for desc, hsn, qty, amt in items:
        cv2.putText(canvas, desc, (55, cur_y), font, 0.42, (40, 40, 40), 1, cv2.LINE_AA)
        cv2.putText(canvas, hsn, (350, cur_y), font, 0.42, (60, 60, 60), 1, cv2.LINE_AA)
        cv2.putText(canvas, qty, (460, cur_y), font, 0.42, (60, 60, 60), 1, cv2.LINE_AA)
        cv2.putText(canvas, amt, (540, cur_y), font, 0.42, (30, 30, 30), 1, cv2.LINE_AA)
        cv2.line(canvas, (40, cur_y + 12), (w - 40, cur_y + 12), (230, 230, 230), 1)
        cur_y += 38

    # Totals
    cv2.putText(canvas, "SUB TOTAL:", (430, table_top + 280), font, 0.44, (60, 60, 60), 1, cv2.LINE_AA)
    cv2.putText(canvas, "INR 2,58,100.00", (530, table_top + 280), font, 0.46, (20, 20, 20), 2, cv2.LINE_AA)
    cv2.putText(canvas, "GST (18%):", (430, table_top + 305), font, 0.44, (60, 60, 60), 1, cv2.LINE_AA)
    cv2.putText(canvas, "INR 46,458.00", (530, table_top + 305), font, 0.46, (20, 20, 20), 2, cv2.LINE_AA)
    
    cv2.rectangle(canvas, (410, table_top + 325), (w - 40, table_top + 365), (240, 240, 240), -1)
    cv2.putText(canvas, "TOTAL PAYABLE:  INR 3,04,558.00", (420, table_top + 352), font, 0.50, (10, 10, 10), 2, cv2.LINE_AA)

    # Green "PAID" Official Stamp
    cv2.circle(canvas, (180, 680), 65, (30, 150, 40), 3) # Green BGR
    cv2.circle(canvas, (180, 680), 58, (30, 150, 40), 1)
    cv2.putText(canvas, "PAID IN FULL", (130, 675), font, 0.54, (30, 150, 40), 2, cv2.LINE_AA)
    cv2.putText(canvas, "15-OCT-2026", (140, 695), font, 0.38, (30, 150, 40), 1, cv2.LINE_AA)

    # Authorized Signature Line
    cv2.line(canvas, (440, 720), (w - 60, 720), (100, 100, 100), 1)
    cv2.putText(canvas, "For APEX DIGITAL LOGISTICS PVT LTD", (440, 738), font, 0.42, (80, 80, 80), 1, cv2.LINE_AA)
    cv2.putText(canvas, "Authorized Signatory", (480, 755), font, 0.40, (120, 120, 120), 1, cv2.LINE_AA)

    # Simulate uneven lighting: Flash glare in top-left, dark vignette in bottom-right
    Y, X = np.ogrid[:h, :w]
    lighting = 1.05 - 0.55 * ((X / w) * 0.3 + (Y / h) * 0.7)
    degraded = (canvas.astype(np.float32) * lighting[:, :, np.newaxis]).astype(np.uint8)
    degraded = add_salt_pepper_noise(degraded, 0.008, 0.008)
    cv2.imwrite(output_path, degraded)
    print(f"[OK] Generated: {output_path}")

def generate_sample_3(output_path):
    """University Certificate with Gold Border, Red Seal & Blue Signature"""
    h, w = 700, 950 # Landscape
    canvas = np.ones((h, w, 3), dtype=np.uint8) * 250
    font = cv2.FONT_HERSHEY_SIMPLEX

    # Elegant Gold Double Border
    gold = (35, 150, 215) # Gold in BGR
    cv2.rectangle(canvas, (25, 25), (w - 25, h - 25), gold, 4)
    cv2.rectangle(canvas, (35, 35), (w - 35, h - 35), gold, 1)

    # Institution
    cv2.putText(canvas, "SVKM'S NMIMS UNIVERSITY, MUMBAI", (w//2 - 260, 85), font, 0.75, (30, 30, 30), 2, cv2.LINE_AA)
    cv2.putText(canvas, "MUKESH PATEL SCHOOL OF TECHNOLOGY MANAGEMENT & ENGINEERING", (w//2 - 330, 115), font, 0.46, (80, 80, 80), 1, cv2.LINE_AA)
    cv2.putText(canvas, "Department of Computer Engineering", (w//2 - 160, 138), font, 0.44, (110, 110, 110), 1, cv2.LINE_AA)
    cv2.line(canvas, (180, 155), (w - 180, 155), gold, 1)

    # Certificate Title
    cv2.putText(canvas, "CERTIFICATE OF EXCELLENCE", (w//2 - 250, 205), font, 1.0, (20, 20, 20), 2, cv2.LINE_AA)
    cv2.putText(canvas, "This certificate is proudly awarded in recognition of outstanding technical innovation to:", (w//2 - 325, 250), font, 0.48, (70, 70, 70), 1, cv2.LINE_AA)

    # Student Names
    cv2.putText(canvas, "HIMANSHU GARG  |  PARTH CHATURVEDI  |  DIVYANSH KAREL", (w//2 - 340, 310), font, 0.75, (10, 10, 10), 2, cv2.LINE_AA)
    cv2.line(canvas, (120, 325), (w - 120, 325), (60, 60, 60), 1)

    # Citation
    cv2.putText(canvas, "For engineering the 'SmartScan Studio PRO' Document Enhancement & Segmentation Engine,", (w//2 - 335, 375), font, 0.48, (50, 50, 50), 1, cv2.LINE_AA)
    cv2.putText(canvas, "demonstrating superior Retinex illumination normalization and 2D DFT frequency analysis.", (w//2 - 335, 405), font, 0.48, (50, 50, 50), 1, cv2.LINE_AA)
    cv2.putText(canvas, "Course: Image and Video Processing (702EX0E020)  |  Academic Year: 2026-2027", (w//2 - 280, 440), font, 0.46, (80, 80, 80), 1, cv2.LINE_AA)

    # Red Official University Seal in Bottom-Left
    seal_color = (20, 30, 190) # Deep Red BGR
    cv2.circle(canvas, (200, 555), 55, seal_color, 3)
    cv2.circle(canvas, (200, 555), 48, seal_color, 1)
    cv2.putText(canvas, "OFFICIAL", (165, 545), font, 0.44, seal_color, 2, cv2.LINE_AA)
    cv2.putText(canvas, "SEAL", (178, 568), font, 0.44, seal_color, 2, cv2.LINE_AA)
    cv2.putText(canvas, "NMIMS", (172, 588), font, 0.36, seal_color, 1, cv2.LINE_AA)

    # Blue Cursive Signatures in Bottom-Right
    sig_blue = (180, 50, 20) # Blue ink BGR
    cv2.line(canvas, (w - 340, 570), (w - 120, 570), (100, 100, 100), 1)
    cv2.putText(canvas, "Dr. Sachin Chavan", (w - 310, 555), font, 0.65, sig_blue, 2, cv2.LINE_AA)
    cv2.putText(canvas, "Faculty In-Charge & Project Guide", (w - 325, 590), font, 0.44, (70, 70, 70), 1, cv2.LINE_AA)

    # Severe Vignetting Degradation (camera lens falloff: dark corners, bright center)
    Y, X = np.ogrid[:h, :w]
    dist_from_center = np.sqrt(((X - w/2) / (w/2))**2 + ((Y - h/2) / (h/2))**2)
    vignette = 1.0 - 0.58 * (dist_from_center ** 1.8)
    vignette = np.clip(vignette, 0.35, 1.0)
    degraded = (canvas.astype(np.float32) * vignette[:, :, np.newaxis]).astype(np.uint8)
    degraded = add_salt_pepper_noise(degraded, 0.005, 0.005)
    cv2.imwrite(output_path, degraded)
    print(f"[OK] Generated: {output_path}")

def generate_sample_4(output_path):
    """Thick Book Page with Severe Curved Spine Crease Shadow"""
    h, w = 920, 680
    canvas = np.ones((h, w, 3), dtype=np.uint8) * 242 # Slightly yellowed paper
    canvas[:, :, 0] = 232 # slightly aged paper tone
    font = cv2.FONT_HERSHEY_SIMPLEX

    # Running Header
    cv2.putText(canvas, "CHAPTER 9. FREQUENCY DOMAIN FILTERING", (60, 60), font, 0.44, (90, 90, 90), 1, cv2.LINE_AA)
    cv2.putText(canvas, "315", (w - 90, 60), font, 0.44, (90, 90, 90), 1, cv2.LINE_AA)
    cv2.line(canvas, (60, 72), (w - 60, 72), (160, 160, 160), 1)

    # Section Title
    cv2.putText(canvas, "9.4 The 2D Discrete Fourier Transform", (60, 115), font, 0.68, (20, 20, 20), 2, cv2.LINE_AA)

    # Dual Column Book Layout
    col1_lines = [
        "The two-dimensional Fourier transform",
        "of a continuous spatial function f(x, y)",
        "is a fundamental mathematical bridge",
        "between the spatial image domain and",
        "the spectral frequency domain.",
        "",
        "For a sampled digital image of matrix",
        "dimensions M x N, the Discrete Fourier",
        "Transform (DFT) pair is defined as:",
        "",
        "F(u, v) = sum sum f(x, y) e^(-j2pi(ux/M + vy/N))",
        "",
        "In document processing, high spatial",
        "frequencies capture sharp character glyph",
        "boundaries, serif stems, and punctuation,",
        "while low frequencies govern overall page",
        "illumination and scanner shading fields."
    ]

    col2_lines = [
        "When scanning bound textbooks without",
        "damaging the spine, physical platens",
        "cannot press the bound fold completely",
        "flat against the glass platen.",
        "",
        "This mechanical limitation induces a",
        "steep, highly non-linear intensity drop-off",
        "termed 'spine crease shadow'. Standard",
        "global thresholding techniques classify",
        "this dark crease as foreground text,",
        "rendering whole lines illegible.",
        "",
        "By estimating background illumination",
        "via large Gaussian kernels or Retinex",
        "division, the crease shadow is flattened,",
        "restoring uniform page reflectance."
    ]

    y = 155
    for l in col1_lines:
        if "F(u, v)" in l:
            cv2.putText(canvas, l, (55, y), font, 0.36, (10, 10, 10), 2, cv2.LINE_AA)
        else:
            cv2.putText(canvas, l, (60, y), font, 0.40, (45, 45, 45), 1, cv2.LINE_AA)
        y += 24

    y = 155
    for l in col2_lines:
        cv2.putText(canvas, l, (360, y), font, 0.40, (45, 45, 45), 1, cv2.LINE_AA)
        y += 24

    # Simulate deep non-linear spine shadow down the left margin
    Y, X = np.ogrid[:h, :w]
    # Severe exponential drop near x=0 to x=180
    spine_shadow = 1.0 - 0.72 * np.exp(-((X.astype(float)) / 110.0)**1.3)
    # Gentle gradient on right
    spine_shadow = spine_shadow * (1.0 - 0.15 * (Y / h))
    spine_shadow = np.clip(spine_shadow, 0.25, 1.0)
    
    degraded = (canvas.astype(np.float32) * spine_shadow[:, :, np.newaxis]).astype(np.uint8)
    degraded = add_salt_pepper_noise(degraded, 0.01, 0.01)
    cv2.imwrite(output_path, degraded)
    print(f"[OK] Generated: {output_path}")

def generate_sample_5(output_path):
    """Clinical Medical Prescription with Red Rx, Clinic Header & Sensor Noise"""
    h, w = 880, 650
    canvas = np.ones((h, w, 3), dtype=np.uint8) * 248
    font = cv2.FONT_HERSHEY_SIMPLEX

    # Blue Medical Header
    cv2.rectangle(canvas, (40, 30), (w - 40, 105), (160, 70, 20), -1)
    # Medical Cross icon
    cv2.rectangle(canvas, (65, 45), (75, 90), (255, 255, 255), -1)
    cv2.rectangle(canvas, (55, 60), (85, 75), (255, 255, 255), -1)

    cv2.putText(canvas, "CITYCARE MULTISPECIALITY CLINIC", (100, 65), font, 0.65, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.putText(canvas, "Department of Internal Medicine | Reg. No: MMC-2019-0428", (100, 90), font, 0.40, (220, 220, 220), 1, cv2.LINE_AA)

    # Doctor & Patient Details
    cv2.putText(canvas, "Dr. A. R. Kulkarni, MD (Medicine)", (45, 135), font, 0.52, (30, 30, 30), 2, cv2.LINE_AA)
    cv2.putText(canvas, "Consultant Physician | Mobile: +91 98201 44590", (45, 155), font, 0.40, (90, 90, 90), 1, cv2.LINE_AA)
    cv2.line(canvas, (40, 170), (w - 40, 170), (140, 140, 140), 1)

    cv2.putText(canvas, "Patient: Mr. Rajesh Sharma", (45, 195), font, 0.46, (30, 30, 30), 2, cv2.LINE_AA)
    cv2.putText(canvas, "Age / Gender: 46 Y / Male", (320, 195), font, 0.44, (60, 60, 60), 1, cv2.LINE_AA)
    cv2.putText(canvas, "Date: 15-OCT-2026", (480, 195), font, 0.44, (60, 60, 60), 1, cv2.LINE_AA)
    cv2.putText(canvas, "Diagnosis: Acute Upper Respiratory Tract Infection", (45, 220), font, 0.44, (80, 80, 80), 1, cv2.LINE_AA)
    cv2.line(canvas, (40, 235), (w - 40, 235), (200, 200, 200), 1)

    # Prominent Red Rx Symbol
    rx_color = (25, 30, 215) # Red BGR
    cv2.putText(canvas, "Rx", (45, 290), font, 1.4, rx_color, 3, cv2.LINE_AA)

    # Prescriptions (Simulated Handwriting / Print)
    meds = [
        ("1. Tab. Amoxicillin + Clavulanate (625 mg)", "1 tablet twice daily after meals x 5 days"),
        ("2. Tab. Montelukast + Levocetirizine", "1 tablet at bedtime x 7 days"),
        ("3. Paracetamol (650 mg) SOS", "As required for fever / headache (Max 3/day)"),
        ("4. Saline Nasal Spray (0.9%)", "2 puffs in each nostril thrice daily"),
        ("5. Warm Saline Gargles", "Thrice daily and adequate oral hydration.")
    ]
    y = 330
    for med, dosage in meds:
        cv2.putText(canvas, med, (65, y), font, 0.46, (20, 20, 20), 2, cv2.LINE_AA)
        cv2.putText(canvas, "    " + dosage, (65, y + 22), font, 0.40, (70, 70, 70), 1, cv2.LINE_AA)
        y += 50

    # Clinic Stamp & Signature
    cv2.line(canvas, (w - 260, 700), (w - 50, 700), (100, 100, 100), 1)
    cv2.putText(canvas, "Dr. A. R. Kulkarni", (w - 230, 685), font, 0.58, (160, 40, 20), 2, cv2.LINE_AA)
    cv2.putText(canvas, "Doctor's Signature & Stamp", (w - 240, 720), font, 0.40, (100, 100, 100), 1, cv2.LINE_AA)

    # Add lighting degradation: dim fluorescent lighting with shadow across bottom
    Y, X = np.ogrid[:h, :w]
    lighting = 1.0 - 0.55 * ((Y / h) * 0.7 + (X / w) * 0.3)
    degraded = (canvas.astype(np.float32) * lighting[:, :, np.newaxis]).astype(np.uint8)
    degraded = add_salt_pepper_noise(degraded, 0.012, 0.012)
    cv2.imwrite(output_path, degraded)
    print(f"[OK] Generated: {output_path}")

def main():
    dirs = [
        "samples",
        "to be submitted/samples"
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)
        generate_sample_1(os.path.join(d, "sample_1_academic_shadowed.jpg"))
        generate_sample_2(os.path.join(d, "sample_2_tax_invoice.jpg"))
        generate_sample_3(os.path.join(d, "sample_3_official_certificate.jpg"))
        generate_sample_4(os.path.join(d, "sample_4_book_spine_page.jpg"))
        generate_sample_5(os.path.join(d, "sample_5_medical_prescription.jpg"))

    # Also update default sample_document.jpg with sample_1
    cv2.imwrite("to be submitted/sample_document.jpg", cv2.imread("to be submitted/samples/sample_1_academic_shadowed.jpg"))
    print("[SUCCESS] All 5 diverse document samples generated successfully.")

if __name__ == "__main__":
    main()
