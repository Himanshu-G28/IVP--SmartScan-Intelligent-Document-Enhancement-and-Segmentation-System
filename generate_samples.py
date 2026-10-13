import cv2
import numpy as np
import os

def create_synthetic_document(output_path):
    """Creates a synthetic degraded document image."""
    # Create white canvas
    img = np.ones((800, 600), dtype=np.uint8) * 255
    
    # Add text
    font = cv2.FONT_HERSHEY_SIMPLEX
    texts = [
        "PROJECT PHASE-I",
        "SmartScan System",
        "IVP Mini Project",
        "Group Members:",
        "Parth Chaturvedi (E235)",
        "Divyansh Karel (E236)",
        "Himanshu Garg (E250)",
        "",
        "This is a simulated document",
        "containing various degradations:",
        "- Illumination gradients",
        "- Salt and pepper noise",
        "- Broken text strokes"
    ]
    
    y = 50
    for text in texts:
        cv2.putText(img, text, (50, y), font, 0.8, (0, 0, 0), 2, cv2.LINE_AA)
        y += 40
        
    # Simulate broken strokes (Morphological degradation)
    kernel = np.ones((2, 2), np.uint8)
    img = cv2.dilate(img, kernel, iterations=1) # Dilation on black text makes it thinner/broken
    
    # Apply synthetic shadow gradient (Non-uniform illumination)
    shadow = np.zeros_like(img, dtype=np.float32)
    for i in range(img.shape[0]):
        for j in range(img.shape[1]):
            # Gradient from top-left (bright) to bottom-right (dark)
            shadow[i, j] = 1.0 - 0.6 * ((i/img.shape[0]) + (j/img.shape[1]))/2
            
    img_shadowed = (img * shadow).astype(np.uint8)
    
    # Add salt and pepper noise
    noise = np.random.randint(0, 255, img.shape)
    img_noisy = img_shadowed.copy()
    img_noisy[noise < 5] = 0   # Pepper
    img_noisy[noise > 250] = 255 # Salt
    
    cv2.imwrite(output_path, img_noisy)
    print(f"Saved synthetic document to {output_path}")

if __name__ == "__main__":
    os.makedirs("samples", exist_ok=True)
    create_synthetic_document("samples/synthetic_degraded.jpg")
    
    # Create a simple clean baseline
    clean = np.ones((800, 600), dtype=np.uint8) * 255
    cv2.putText(clean, "Clean Reference Document", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 2)
    cv2.imwrite("samples/clean_baseline.jpg", clean)
