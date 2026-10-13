# Working Guide: SmartScan (IVP Mini Project)

This guide provides the theory, mathematical explanations, and expected Viva (oral exam) questions for the project.

## 1. Syllabus Mapping (IVP Course 702EX0E020)
* **Unit 2 (Enhancement)**: Median Filtering, CLAHE, Histogram Equalization, Gamma Correction.
* **Unit 4 (Morphology)**: Erosion, Dilation, Opening, Closing.
* **Unit 5 (Edges)**: Sobel, Canny edge detection.
* **Unit 6 (Segmentation)**: Global Otsu Thresholding, Local Adaptive Thresholding.

## 2. Theoretical Pipeline & Mathematical Concepts

### Stage 1: Preprocessing (Parth Chaturvedi)
- **Median Filter**: A non-linear digital filter that replaces each pixel with the median of neighboring pixels. **Math**: $v(m,n) = \text{median}\{y(m-k, n-l), (k,l) \in W\}$. It effectively removes impulsive/salt-and-pepper noise without blurring edges.
- **Illumination Normalization**: Divides the original image by a heavily blurred version of itself to eliminate shadow gradients.
- **CLAHE (Contrast-Limited Adaptive Histogram Equalization)**: Unlike global histogram equalization which over-amplifies noise in flat regions, CLAHE operates on small tiles (e.g., $8 \times 8$). It clips the histogram at a predefined limit to prevent noise amplification before distributing the clipped pixels.

### Stage 2: Edge Detection (Divyansh Karel)
- **Sobel Operator**: First-order derivative approximation. Uses two $3 \times 3$ kernels to calculate approximations of the derivatives in horizontal ($G_x$) and vertical ($G_y$) directions.
- **Canny Edge Detector**: A multi-stage algorithm:
  1. Gaussian blur to remove noise.
  2. Gradient calculation (Sobel).
  3. Non-maximum suppression (thins edges to 1-pixel wide).
  4. Hysteresis Thresholding (uses a high and low threshold to track strong edges and discard weak noise edges).

### Stage 3: Segmentation (Divyansh Karel)
- **Global Otsu's Method**: Iterates through all possible threshold values and calculates a measure of spread for the pixel levels each side of the threshold. The goal is to maximize the between-class variance ($\sigma_B^2$). *Why it fails*: Under heavy shadow, the background in one area is darker than the text in a bright area, making a single global threshold impossible.
- **Local Adaptive Thresholding**: Calculates the threshold for a small region around each pixel (using a Gaussian weighted mean). This local handling perfectly segments text even if half the page is covered in a deep shadow!

### Stage 4: Morphological Post-Processing (Himanshu Garg)
- **Structuring Element (SE)**: A matrix that identifies the pixel in the image being processed and defines the neighborhood used in processing.
- **Morphological Opening**: $A \circ B = (A \ominus B) \oplus B$ (Erosion followed by Dilation). Used to remove small isolated objects (speckle noise).
- **Morphological Closing**: $A \bullet B = (A \oplus B) \ominus B$ (Dilation followed by Erosion). Used to bridge small gaps and discontinuities in text strokes.

### Stage 5: Evaluation
- **PSNR (Peak Signal-to-Noise Ratio)**: Evaluates quality. 
  $PSNR = 10 \cdot \log_{10}(\frac{MAX_I^2}{MSE})$. Higher PSNR means better restoration.

---

## 3. Top 10 Viva Questions & Answers

**Q1: Why did you use a Median Filter instead of a Gaussian Filter in preprocessing?**
**Answer (Parth)**: Document scans frequently suffer from salt-and-pepper noise (impulsive noise from the scanner sensor). A Gaussian filter is a linear low-pass filter that blurs edges and only smears the noise. A Median filter is non-linear and perfectly removes salt-and-pepper noise while preserving the sharp edges of the text.

**Q2: What is CLAHE and how does it differ from standard Histogram Equalization?**
**Answer (Parth)**: Standard HE operates globally on the entire image. If a document has a white background with a small dark shadow, global HE will wash out the entire image. CLAHE (Contrast-Limited Adaptive Histogram Equalization) splits the image into small tiles (e.g., 8x8) and equalizes them locally. The \"Contrast-Limited\" part clips high peaks in the histogram to prevent noise over-amplification in empty white background areas.

**Q3: How does the Canny Edge Detector work?**
**Answer (Divyansh)**: Canny is a 4-step optimal edge detector. First, it smooths the image with a Gaussian filter. Second, it computes gradient magnitudes and directions (using Sobel). Third, it applies Non-Maximum Suppression to thin the edges to a single pixel line. Finally, it uses Hysteresis Thresholding with two thresholds (low and high) to link strong edges and eliminate false weak edges.

**Q4: In your segmentation stage, you show Otsu failing. Why does Otsu fail?**
**Answer (Divyansh)**: Otsu is a global thresholding method. It assumes a bimodal histogram (one peak for text, one for background) and finds a single threshold value for the entire image. In degraded documents with a shadow gradient, the background in the shadowed region is darker than the text in the bright region. A single global threshold cannot separate text from background in both regions simultaneously.

**Q5: What is the solution to Otsu's failure?**
**Answer (Divyansh)**: Local Adaptive Thresholding. Instead of a single global threshold, we calculate a unique threshold for *every pixel* based on the mean (or Gaussian weighted mean) of its local $N \times N$ neighborhood. This adapts to the changing illumination across the document.

**Q6: What is Morphological Opening and why did you use it?**
**Answer (Himanshu)**: Morphological Opening is Erosion followed by Dilation. In our project, after binarization, there are often tiny isolated black dots (pepper noise) in the white background. Erosion shrinks these dots until they disappear. The subsequent Dilation restores the valid text strokes back to their original size.

**Q7: What is Morphological Closing and what problem does it solve?**
**Answer (Himanshu)**: Closing is Dilation followed by Erosion. Degraded or old documents often have text characters with broken, fractured strokes. Dilation expands the strokes to bridge those small gaps, and then Erosion thins the strokes back to normal thickness, leaving the gaps permanently sealed.

**Q8: How did you measure the performance of your system?**
**Answer (Himanshu)**: We calculated the Peak Signal-to-Noise Ratio (PSNR) and the Contrast Improvement Ratio (CIR). PSNR uses Mean Squared Error (MSE) to quantitatively measure how much noise was removed relative to the maximum possible pixel value. We also provided visual comparative metrics (side-by-side stages) in our UI to visually prove the pipeline's effectiveness.

**Q9: If you wanted to extract text after this pipeline, what would be the next step?**
**Answer (Team)**: The next step would be OCR (Optical Character Recognition) using an engine like Tesseract. Our SmartScan pipeline is precisely the necessary pre-processing stage required to feed clean, binarized text to an OCR engine for accurate digital archiving.
