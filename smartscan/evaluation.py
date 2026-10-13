import cv2
import numpy as np
import math

def calculate_psnr(img1, img2):
    """
    Calculate Peak Signal-to-Noise Ratio (PSNR) between two images.
    PSNR = 10 * log10(MAX^2 / MSE)
    """
    if img1.shape != img2.shape:
        # Resize img2 to match img1 for evaluation purposes
        img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))
        
    mse = np.mean((img1.astype(float) - img2.astype(float)) ** 2)
    if mse == 0:
        return float('inf')
        
    max_pixel = 255.0
    psnr = 20 * math.log10(max_pixel / math.sqrt(mse))
    return psnr

def calculate_contrast(image):
    """
    Calculate simple RMS contrast of an image.
    RMS Contrast is the standard deviation of pixel intensities.
    """
    return np.std(image)

def contrast_improvement_ratio(original, enhanced):
    """
    Calculate Contrast Improvement Ratio (CIR).
    """
    c_orig = calculate_contrast(original)
    c_enh = calculate_contrast(enhanced)
    if c_orig == 0:
        return float('inf')
    return c_enh / c_orig
