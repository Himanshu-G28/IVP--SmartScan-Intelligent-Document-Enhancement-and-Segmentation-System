# SmartScan – Intelligent Document Enhancement & Segmentation System

Welcome to the **SmartScan** IVP mini-project. This system enhances degraded, noisy, and shadowed document images and prepares them for OCR and archiving.

## Installation & Setup

1. **Prerequisites**: Ensure you have Python 3 installed.
2. **Install requirements**:
   ```bash
   pip install flask opencv-python numpy matplotlib
   ```
3. **Generate Sample Data**: (First-time only)
   Run this script to generate synthetic test images in the `samples/` directory:
   ```bash
   python generate_samples.py
   ```

## How to Run the Project

### Option 1: Web Interface (Recommended)
Launch the interactive web dashboard:
```bash
python app.py
```
Then open your web browser and go to: `http://127.0.0.1:5000`

### Option 2: Command Line (CLI)
Process an image directly from the terminal and save the step-by-step outputs in the `results/` folder:
```bash
python run_cli.py --input samples/synthetic_degraded.jpg
```

### Option 3: MATLAB
If you need to show the code working in MATLAB for your lab exam, navigate to the `matlab/` folder and read the `README_MATLAB.md` instructions.

## Read the Working Guide!
Please read `WORKING_GUIDE.md` for a complete breakdown of the math, theory, and **Viva/Exam Questions and Answers**.
