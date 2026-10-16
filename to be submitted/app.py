from flask import Flask, render_template, request, jsonify
import os, cv2, time, base64, math
import numpy as np

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'samples'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# ─────────────────────────────────────────────
# UTILITY: encode any image to base64 JPEG
# ─────────────────────────────────────────────
def b64(img):
    if img is None:
        return ""
    if len(img.shape) == 2:
        encode = img
    else:
        encode = img
    _, buf = cv2.imencode('.jpg', encode, [cv2.IMWRITE_JPEG_QUALITY, 93])
    return base64.b64encode(buf).decode('utf-8')

# ─────────────────────────────────────────────
# METRICS
# ─────────────────────────────────────────────
def psnr(img1, img2):
    if img1.shape != img2.shape:
        img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))
    mse = np.mean((img1.astype(float) - img2.astype(float)) ** 2)
    if mse == 0:
        return float('inf')
    return 20 * math.log10(255.0 / math.sqrt(mse))

def cir(orig, enhanced):
    s_orig = np.std(orig)
    s_enh  = np.std(enhanced)
    return s_enh / s_orig if s_orig != 0 else float('inf')

# ─────────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────────
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'})

    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No file selected'})

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'current_upload.jpg')
    file.save(filepath)

    start = time.time()

    # ── Load ────────────────────────────────
    bgr    = cv2.imread(filepath)
    gray   = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    h, w   = gray.shape
    R      = {}

    # ════════════════════════════════════════════════════════
    # CATEGORY 1 — DATA REPRESENTATION
    # ════════════════════════════════════════════════════════
    R['original_color'] = b64(bgr)
    R['grayscale']      = b64(gray)
    _, binary_simple    = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    R['binary']         = b64(binary_simple)

    # ════════════════════════════════════════════════════════
    # CATEGORY 2 — COLOUR SPACES
    # ════════════════════════════════════════════════════════
    hsv   = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    R['hsv_h'] = b64(hsv[:, :, 0])
    R['hsv_s'] = b64(hsv[:, :, 1])
    R['hsv_v'] = b64(hsv[:, :, 2])

    ycrcb = cv2.cvtColor(bgr, cv2.COLOR_BGR2YCrCb)
    R['ycrcb_y']  = b64(ycrcb[:, :, 0])
    R['ycrcb_cr'] = b64(ycrcb[:, :, 1])
    R['ycrcb_cb'] = b64(ycrcb[:, :, 2])

    R['digital_negative'] = b64(255 - gray)

    # ════════════════════════════════════════════════════════
    # CATEGORY 3 — POINT PROCESSING
    # ════════════════════════════════════════════════════════
    # Log transform: s = c * log(1 + r)
    log_img = np.log1p(gray.astype(np.float32))
    log_img = cv2.normalize(log_img, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    R['log_transform'] = b64(log_img)

    # Power-law (Gamma) — γ = 0.5 brightens dark regions
    table_05  = np.array([((i / 255.0) ** 0.5) * 255 for i in range(256)]).astype(np.uint8)
    R['gamma_brighten'] = b64(cv2.LUT(gray, table_05))

    # Power-law (Gamma) — γ = 2.0 darkens highlights
    table_20  = np.array([((i / 255.0) ** 2.0) * 255 for i in range(256)]).astype(np.uint8)
    R['gamma_darken'] = b64(cv2.LUT(gray, table_20))

    # Contrast stretch — map [min,max] → [0,255]
    mn, mx = float(gray.min()), float(gray.max())
    cs = ((gray.astype(np.float32) - mn) / (mx - mn + 1e-6) * 255).astype(np.uint8)
    R['contrast_stretch'] = b64(cs)

    # Intensity Slicing — highlight mid-grey band (100–180)
    sliced = np.where((gray >= 100) & (gray <= 180), 255, 0).astype(np.uint8)
    R['intensity_slice'] = b64(sliced)

    # ════════════════════════════════════════════════════════
    # CATEGORY 4 — HISTOGRAM PROCESSING
    # ════════════════════════════════════════════════════════
    R['hist_eq'] = b64(cv2.equalizeHist(gray))

    clahe_obj = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    clahe_img = clahe_obj.apply(gray)
    R['clahe'] = b64(clahe_img)

    # ════════════════════════════════════════════════════════
    # CATEGORY 5 — SPATIAL FILTERING (Smoothing & Sharpening)
    # ════════════════════════════════════════════════════════
    R['gaussian_blur']  = b64(cv2.GaussianBlur(gray, (7, 7), 0))
    R['median_filter']  = b64(cv2.medianBlur(gray, 5))
    R['bilateral']      = b64(cv2.bilateralFilter(gray, 9, 75, 75))

    # Unsharp masking sharpening: sharpened = 1.5*original - 0.5*blurred
    blur_sharp = cv2.GaussianBlur(clahe_img, (0, 0), 2.0)
    sharpened  = cv2.addWeighted(clahe_img, 1.5, blur_sharp, -0.5, 0)
    sharpened  = np.clip(sharpened, 0, 255).astype(np.uint8)
    R['unsharp_mask'] = b64(sharpened)

    # Laplacian-based sharpening: f' = f - ∇²f
    lap_kernel  = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
    lap_sharp   = cv2.filter2D(gray, -1, lap_kernel)
    R['laplacian_sharp'] = b64(lap_sharp)

    # ════════════════════════════════════════════════════════
    # CATEGORY 6 — EDGE DETECTION
    # ════════════════════════════════════════════════════════
    # Sobel
    gx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
    gy = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
    R['sobel_x']        = b64(cv2.convertScaleAbs(gx))
    R['sobel_y']        = b64(cv2.convertScaleAbs(gy))
    sobel_mag           = cv2.magnitude(gx, gy)
    R['sobel_combined'] = b64(cv2.normalize(sobel_mag, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8))

    # Prewitt
    prewitt_kx = np.array([[1, 0, -1], [1, 0, -1], [1, 0, -1]], dtype=np.float32)
    prewitt_ky = np.array([[1, 1, 1], [0, 0, 0], [-1, -1, -1]], dtype=np.float32)
    px  = cv2.filter2D(gray, cv2.CV_64F, prewitt_kx)
    py  = cv2.filter2D(gray, cv2.CV_64F, prewitt_ky)
    prewitt_mag = np.sqrt(px ** 2 + py ** 2)
    R['prewitt'] = b64(cv2.normalize(prewitt_mag, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8))

    # Laplacian of Gaussian (LoG)
    gaussian_for_log = cv2.GaussianBlur(gray, (5, 5), 0)
    lap              = cv2.Laplacian(gaussian_for_log, cv2.CV_64F)
    R['laplacian']   = b64(cv2.convertScaleAbs(lap))

    # Canny
    R['canny'] = b64(cv2.Canny(sharpened, 50, 150))

    # ════════════════════════════════════════════════════════
    # CATEGORY 7 — MORPHOLOGICAL OPERATIONS
    # ════════════════════════════════════════════════════════
    _, morph_bin = cv2.threshold(sharpened, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    k3 = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    k5 = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))

    R['dilation']      = b64(cv2.dilate(morph_bin, k3))
    R['erosion']       = b64(cv2.erode(morph_bin, k3))
    R['opening']       = b64(cv2.morphologyEx(morph_bin, cv2.MORPH_OPEN,  k3))
    R['closing']       = b64(cv2.morphologyEx(morph_bin, cv2.MORPH_CLOSE, k3))
    R['morph_grad']    = b64(cv2.morphologyEx(morph_bin, cv2.MORPH_GRADIENT, k3))
    R['tophat']        = b64(cv2.morphologyEx(morph_bin, cv2.MORPH_TOPHAT,   k5))
    R['blackhat']      = b64(cv2.morphologyEx(morph_bin, cv2.MORPH_BLACKHAT, k5))

    # Grayscale morphology
    R['gray_dilation'] = b64(cv2.dilate(gray, k3))
    R['gray_erosion']  = b64(cv2.erode(gray, k3))

    # ════════════════════════════════════════════════════════
    # CATEGORY 8 — SEGMENTATION
    # ════════════════════════════════════════════════════════
    _, otsu = cv2.threshold(sharpened, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    R['otsu'] = b64(otsu)

    adap_gauss = cv2.adaptiveThreshold(sharpened, 255,
                    cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 10)
    R['adaptive_gaussian'] = b64(adap_gauss)

    adap_mean = cv2.adaptiveThreshold(sharpened, 255,
                    cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 31, 10)
    R['adaptive_mean'] = b64(adap_mean)

    # ════════════════════════════════════════════════════════
    # CATEGORY 9 — FREQUENCY DOMAIN (DFT)
    # ════════════════════════════════════════════════════════
    dft        = np.fft.fft2(gray.astype(np.float32))
    dft_shift  = np.fft.fftshift(dft)
    magnitude  = 20 * np.log(np.abs(dft_shift) + 1)
    R['dft']   = b64(cv2.normalize(magnitude, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8))

    # High-pass filter (remove low frequencies → edge image from frequency domain)
    mask_hp    = np.ones(gray.shape, np.uint8)
    cy, cx     = h // 2, w // 2
    cv2.circle(mask_hp, (cx, cy), min(h, w) // 8, 0, -1)
    dft_hp     = dft_shift * mask_hp
    idft_hp    = np.abs(np.fft.ifft2(np.fft.ifftshift(dft_hp)))
    R['dft_highpass'] = b64(cv2.normalize(idft_hp, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8))

    # Low-pass filter (smooth)
    mask_lp    = np.zeros(gray.shape, np.uint8)
    cv2.circle(mask_lp, (cx, cy), min(h, w) // 4, 1, -1)
    dft_lp     = dft_shift * mask_lp
    idft_lp    = np.abs(np.fft.ifft2(np.fft.ifftshift(dft_lp)))
    R['dft_lowpass'] = b64(cv2.normalize(idft_lp, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8))

    # ════════════════════════════════════════════════════════
    # FINAL HD ENHANCED OUTPUT — Master True-Color Restoration
    # Master True-Color High-Definition Document Restoration:
    # 1. 2× Lanczos-4 Super-Resolution Upscaling (doubles pixel density first)
    # 2. Sub-pixel rank-order median filtering (removes impulse noise without stroke loss)
    # 3. CIE LAB color decoupling (luminance sharpened independently from chroma)
    # 4. Bilateral edge-preserving filtering (locks crisp text contours)
    # 5. Adaptive contrast equalization (CLAHE) for deep, rich text ink
    # 6. Multi-scale high-boost unsharp masking (fine edge pass + stroke body pass)
    # ════════════════════════════════════════════════════════
    hd_color = cv2.resize(bgr, (w * 2, h * 2), interpolation=cv2.INTER_LANCZOS4)
    lab = cv2.cvtColor(hd_color, cv2.COLOR_BGR2LAB)
    L, A, B = cv2.split(lab)

    L_med = cv2.medianBlur(L, 3)

    # Retinex Illumination Background Estimation & Division Normalization (Eradicates Shadows)
    bg_L = cv2.GaussianBlur(L_med.astype(np.float32), (81, 81), 40)
    L_norm = np.clip((L_med.astype(np.float32) / (bg_L + 1e-5)) * 250.0, 0, 255).astype(np.uint8)

    # Bilateral edge-preserving filter (smooths paper grain, locks crisp text contours)
    L_bil = cv2.bilateralFilter(L_norm, d=7, sigmaColor=35, sigmaSpace=35)

    # Multi-scale high-boost unsharp masking (fine edge contour + stroke body density)
    blur_fine = cv2.GaussianBlur(L_bil, (0, 0), 1.0)
    sharp_fine = cv2.addWeighted(L_bil, 1.75, blur_fine, -0.75, 0)
    sharp_fine = np.clip(sharp_fine, 0, 255).astype(np.uint8)

    blur_med = cv2.GaussianBlur(sharp_fine, (0, 0), 2.5)
    sharp_body = cv2.addWeighted(sharp_fine, 1.35, blur_med, -0.35, 0)
    sharp_body = np.clip(sharp_body, 0, 255).astype(np.uint8)

    # Paper white calibration & deep text density tone curve
    lut_hd = np.array([int(255 * ((i / 225.0) ** 1.35)) if i < 225 else 255 for i in range(256)], dtype=np.uint8)
    L_final = cv2.LUT(sharp_body, lut_hd)

    # Paper chroma neutralization (removes yellow shadow tint; preserves stamps and signatures)
    is_paper = (L_final > 242).astype(np.float32)
    A_clean = (A.astype(np.float32) * (1.0 - is_paper * 0.75) + 128.0 * (is_paper * 0.75)).astype(np.uint8)
    B_clean = (B.astype(np.float32) * (1.0 - is_paper * 0.75) + 128.0 * (is_paper * 0.75)).astype(np.uint8)

    lab_restored = cv2.merge([L_final, A_clean, B_clean])
    final_hd = cv2.cvtColor(lab_restored, cv2.COLOR_LAB2BGR)
    R['final_hd'] = b64(final_hd)

    # ─── Metrics ──────────────────────────────
    psnr_val = psnr(gray, L_final)
    cir_val  = cir(gray, L_final)
    elapsed  = round(time.time() - start, 2)

    R['metrics'] = {
        'psnr':        f"{psnr_val:.2f} dB",
        'cir':         f"{cir_val:.2f}×",
        'time':        f"{elapsed}s",
        'resolution':  f"{w * 2} × {h * 2} px",
        'outputs':     len([k for k in R if k != 'metrics'])
    }

    return jsonify(R)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
