import cv2
import numpy as np

def apply_sobel(image, ksize=3):
    """Apply Sobel operator to find horizontal and vertical gradients."""
    grad_x = cv2.Sobel(image, cv2.CV_64F, 1, 0, ksize=ksize)
    grad_y = cv2.Sobel(image, cv2.CV_64F, 0, 1, ksize=ksize)
    
    # Calculate magnitude
    magnitude = cv2.magnitude(grad_x, grad_y)
    magnitude = cv2.normalize(magnitude, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
    
    abs_grad_x = cv2.convertScaleAbs(grad_x)
    abs_grad_y = cv2.convertScaleAbs(grad_y)
    return magnitude, abs_grad_x, abs_grad_y

def apply_canny(image, low_threshold=50, high_threshold=150):
    """Apply Canny optimal edge detector."""
    return cv2.Canny(image, low_threshold, high_threshold)

def order_points(pts):
    """Order points: top-left, top-right, bottom-right, bottom-left"""
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    return rect

def detect_document_boundary(image):
    """Find the largest quadrilateral contour representing the document."""
    # Edge detection
    edges = apply_canny(image, 50, 200)
    
    # Find contours
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Sort by area
    contours = sorted(contours, key=cv2.contourArea, reverse=True)
    document_contour = None
    
    for c in contours:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)
        if len(approx) == 4:
            document_contour = approx
            break
            
    return document_contour, edges

def perspective_transform(image, contour):
    """Apply 4-point perspective transform to deskew the document."""
    if contour is None or len(contour) != 4:
        return image # Cannot transform
        
    pts = contour.reshape(4, 2)
    rect = order_points(pts)
    (tl, tr, br, bl) = rect
    
    # Compute widths & heights
    widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    maxWidth = max(int(widthA), int(widthB))
    
    heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    maxHeight = max(int(heightA), int(heightB))
    
    # Destination points
    dst = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]], dtype="float32")
        
    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
    
    return warped
