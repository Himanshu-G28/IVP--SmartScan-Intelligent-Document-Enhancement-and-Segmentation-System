import cv2
import numpy as np

def convert_to_grayscale(image):
    """Convert an RGB image to grayscale."""
    if len(image.shape) == 3:
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return image

def apply_median_filter(image, kernel_size=5):
    """Apply 2D Median Filter to remove salt-and-pepper noise."""
    return cv2.medianBlur(image, kernel_size)

def normalize_illumination(image, block_size=75):
    """
    Estimate background illumination using a large morphological structural element
    (or Gaussian blur) and normalize the image to remove shadow gradients.
    """
    # Background approximation using a large Gaussian blur or Morphological Close/Open
    # Using Gaussian for smooth background estimation
    background = cv2.GaussianBlur(image, (block_size, block_size), 0)
    
    # Divide original by background to normalize (requires float32 conversion)
    float_img = image.astype(np.float32)
    float_bg = background.astype(np.float32) + 1  # Avoid division by zero
    
    normalized = (float_img / float_bg) * 255.0
    return np.clip(normalized, 0, 255).astype(np.uint8)

def apply_clahe(image, clip_limit=2.0, tile_grid_size=(8, 8)):
    """Apply Contrast-Limited Adaptive Histogram Equalization."""
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
    return clahe.apply(image)

def apply_gamma_correction(image, gamma=1.2):
    """Apply Power-Law (Gamma) Correction."""
    inv_gamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** inv_gamma) * 255
                      for i in np.arange(0, 256)]).astype("uint8")
    return cv2.LUT(image, table)
