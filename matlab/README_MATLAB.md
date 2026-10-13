# MATLAB SmartScan Implementation

This folder contains the MATLAB equivalent of the SmartScan pipeline. This is provided to ensure compliance with the **IVP (702EX0E020)** syllabus which frequently relies on MATLAB's Image Processing Toolbox.

## Prerequisites
- MATLAB R2023b / R2024a (as specified in your Phase-1 doc)
- Image Processing Toolbox

## How to run
1. Open MATLAB.
2. Navigate to this `matlab/` folder or add it to your path.
3. Run the pipeline in the Command Window by passing an image path:

```matlab
smartscan_pipeline('../samples/synthetic_degraded.jpg')
```

## Functions mapped to IVP Syllabus
- `rgb2gray`: Unit 1
- `medfilt2`, `adapthisteq`, `imsubtract`: Unit 2 (Image Enhancement)
- `edge(..., 'canny')`: Unit 5 (Edge Detection)
- `imbinarize(..., 'adaptive')`, `graythresh`: Unit 6 (Segmentation)
- `imopen`, `imclose`, `strel`: Unit 4 (Morphological Image Processing)
