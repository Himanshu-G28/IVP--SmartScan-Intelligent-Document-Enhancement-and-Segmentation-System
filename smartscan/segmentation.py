import cv2
import numpy as np

def apply_global_otsu(image):
    """
    Apply Global Otsu's Thresholding.
    Computes a single threshold that minimizes intra-class variance.
    """
    _, th_otsu = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return th_otsu

def apply_adaptive_gaussian(image, block_size=21, C=10):
    """
    Apply Local Adaptive Thresholding (Gaussian).
    Computes a threshold for each pixel based on the Gaussian weighted sum of the local neighborhood.
    """
    # Block size must be odd
    if block_size % 2 == 0:
        block_size += 1
        
    return cv2.adaptiveThreshold(
        image, 255, 
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY, 
        block_size, C)

def apply_adaptive_mean(image, block_size=21, C=10):
    """
    Apply Local Adaptive Thresholding (Mean).
    Computes a threshold for each pixel based on the mean of the local neighborhood.
    """
    if block_size % 2 == 0:
        block_size += 1
        
    return cv2.adaptiveThreshold(
        image, 255, 
        cv2.ADAPTIVE_THRESH_MEAN_C, 
        cv2.THRESH_BINARY, 
        block_size, C)
