import cv2
import numpy as np

def get_structuring_element(shape='rect', ksize=(3, 3)):
    """Create morphological structuring element."""
    if shape == 'ellipse':
        return cv2.getStructuringElement(cv2.MORPH_ELLIPSE, ksize)
    elif shape == 'cross':
        return cv2.getStructuringElement(cv2.MORPH_CROSS, ksize)
    else:
        return cv2.getStructuringElement(cv2.MORPH_RECT, ksize)

def apply_opening(image, ksize=(3,3), shape='rect'):
    """
    Morphological Opening (Erosion followed by Dilation).
    Useful for removing small noise (salt/speckles) in the background.
    Note: For text, background is white and text is black.
    """
    kernel = get_structuring_element(shape, ksize)
    # Opening on inverted image (where text is white) removes small white noise
    inverted = cv2.bitwise_not(image)
    opened = cv2.morphologyEx(inverted, cv2.MORPH_OPEN, kernel)
    return cv2.bitwise_not(opened)

def apply_closing(image, ksize=(3,3), shape='rect'):
    """
    Morphological Closing (Dilation followed by Erosion).
    Useful for bridging small gaps and discontinuities in text strokes.
    """
    kernel = get_structuring_element(shape, ksize)
    # Closing on inverted image closes gaps in white text
    inverted = cv2.bitwise_not(image)
    closed = cv2.morphologyEx(inverted, cv2.MORPH_CLOSE, kernel)
    return cv2.bitwise_not(closed)

def apply_dilation(image, ksize=(2,2)):
    """Simple morphological dilation to thicken text strokes."""
    kernel = get_structuring_element('rect', ksize)
    inverted = cv2.bitwise_not(image)
    dilated = cv2.dilate(inverted, kernel, iterations=1)
    return cv2.bitwise_not(dilated)
