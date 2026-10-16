================================================================================
SMARTSCAN STUDIO PRO - INTELLIGENT DOCUMENT ENHANCEMENT & SEGMENTATION SYSTEM
Course        : Image and Video Processing (Course Code: 702EX0E020) | Semester V
Institution   : SVKM's NMIMS University, MPSTME, Mumbai
Faculty Guide : Dr. Sachin Chavan, Associate Professor (Computer Engineering)
Team Members  :
  1. Parth Chaturvedi (Roll No. E235) - Preprocessing, Median Filtering & CLAHE
  2. Divyansh Karel   (Roll No. E236) - Edge Detection, Otsu vs Adaptive Segmentation
  3. Himanshu Garg    (Roll No. E250, Lead) - Morphology, 2D DFT & Master HD Engine
================================================================================

PROJECT REPOSITORY (GITHUB):
https://github.com/himanshugarg-01/SmartScan-Studio-PRO

--------------------------------------------------------------------------------
SUBMISSION FILE MANIFEST:
--------------------------------------------------------------------------------
1. SmartScan_Project_Report.docx
   - Comprehensive project report formatted strictly in Times New Roman, 
     pure Black & White styling, with embedded result figures, mathematical 
     proofs, 5-sample batch benchmark table, and IEEE references.

2. SmartScan_Project_Presentation.pptx
   - Professional 12-slide Computer Science project presentation covering 
     problem statement, architecture, Otsu failure vs Adaptive success, 
     Master 2x HD Lanczos-4 engine, and quantitative benchmarks.

3. smartscan_pipeline.m
   - Self-contained, single-file MATLAB executable script. Automatically detects 
     sample documents, executes all 5 stages, computes PSNR and CIR, and 
     displays an 8-panel comparative figure.

4. main.py
   - Standalone Python CLI execution engine. Executes all 5 stages + Master 
     True-Color HD Retinex engine, computes quantitative metrics, and saves 
     high-resolution results into results/.

5. app.py (with templates/ and static/)
   - Full-stack interactive Web Studio running on Flask (localhost:5000) 
     with live drag-and-drop document upload, real-time before/after comparison 
     sliders, and 7 curriculum module inspection tabs.

6. samples/
   - Suite of 5 realistic degraded benchmark document images covering:
     * Sample 1: Academic Paper (Diagonal Shadow & Sensor Noise)
     * Sample 2: Commercial Tax Invoice (Table Grid, Blue Banner, Green PAID Stamp)
     * Sample 3: University Certificate (Gold Border, Red Seal, Blue Signature)
     * Sample 4: Textbook Spine Page (Severe Curved Spine Crease Shadow)
     * Sample 5: Clinical Prescription (Red Rx Symbol, Doctor Sign, Fluorescent Noise)

7. requirements.txt
   - Minimal Python dependencies list (opencv-python, numpy, flask, matplotlib).

--------------------------------------------------------------------------------
HOW TO EXECUTE THE CODE:
--------------------------------------------------------------------------------
A. MATLAB Execution:
   1. Open MATLAB and set current folder to this directory.
   2. In MATLAB Command Window, type:
      >> smartscan_pipeline
   3. Or test with any specific sample:
      >> smartscan_pipeline('samples/sample_2_tax_invoice.jpg')

B. Python CLI Pipeline Execution:
   1. Install dependencies (if not already installed):
      pip install -r requirements.txt
   2. Run default pipeline with interactive visual display:
      python3 main.py
   3. Run on a specific demo benchmark (1 to 5):
      python3 main.py --sample 2
   4. Batch execute all 5 benchmarks:
      python3 main.py --all-samples --no-ui

C. Interactive Web Studio Execution:
   1. Launch local server:
      python3 app.py
   2. Open browser and visit:
      http://localhost:5000
   3. Upload any document image to inspect all stages interactively.
================================================================================
