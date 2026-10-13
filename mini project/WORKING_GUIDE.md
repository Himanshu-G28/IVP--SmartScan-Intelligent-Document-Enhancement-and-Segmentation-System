# SmartScan – Super Simple Working Guide (Explain Like I'm 5!)

---

## 1. What is this project about? (The 5-Year-Old Story)

Imagine you wrote your homework on a piece of white paper, and you took a photo of it with your phone.
Uh-oh! Three bad things happened to the photo:
1. **A big dark shadow** fell on the paper because the room was dark.
2. **Tiny black and white dirt specks** (called "salt and pepper noise") got sprinkled all over the photo.
3. **Some letters look broken** or faded like an old stamp.

**SmartScan** is a smart computer program that acts like a **magic cleaning sponge**:
- It wipes away the dirt specks,
- It turns on a flashlight to erase the dark shadow, and
- It traces over the letters with a fresh black marker so the page looks brand-new and ready to print!

---

## 2. What files are inside the `mini project` folder?

We removed all the complicated extra files. Everything you need is right here:

1. **`main.py`** — **The ONLY code file!** All 4 steps of the project are written inside this single file in simple Python.
2. **`sample_document.jpg`** — The messy, shadowed, noisy input photo that our code will clean up.
3. **`results/`** — The folder where the computer saves the 6 step-by-step pictures showing how the messy photo becomes clean.
4. **`WORKING_GUIDE.md`** — This simple guide you are reading right now!

---

## 3. How does the code work? (The 4 Magic Steps)

Inside `main.py`, the work is divided among the 3 team members in **4 simple steps**:

### Step 1: Washing the Page — *Preprocessing (Parth Chaturvedi - E235)*
- **Grayscale**: First, we turn the photo into simple black, white, and gray shades so the computer doesn't have to worry about colors.
- **Median Filter (`cv2.medianBlur`)**: Think of this like brushing crumbs off a table. Every tiny dot looks at its neighbors—if a single black dot is surrounded by white paper, the computer turns it white!
- **Shadow Removal & CLAHE (`cv2.createCLAHE`)**: The computer finds the dark shadow and brightens just the dark parts so the whole page has even lighting.

### Step 2: Finding the Outlines — *Edge Detection (Divyansh Karel - E236)*
- **Canny Edge Detector (`cv2.Canny`)**: Like tracing a drawing with a pencil! The computer finds where light paper suddenly turns into dark ink, drawing thin white outlines around every letter.

### Step 3: Making Ink Pure Black & Paper Pure White — *Segmentation (Divyansh Karel - E236)*
Right now the photo still has shades of gray. We want **only TWO colors**: pure black ink (0) and pure white paper (255).
- **Try 1 – Global Otsu (`cv2.threshold`)**: Uses **one single brightness rule** for the whole page. *Problem*: If there is any leftover shadow, it accidentally paints the shadowed corner black!
- **Try 2 – Adaptive Thresholding (`cv2.adaptiveThreshold`)**: Uses a **smart local rule**—it checks one tiny square of the page at a time. That way, it cleanly picks out the letters everywhere on the page!

### Step 4: Final Polish & Score — *Morphology & PSNR (Himanshu Garg - E250)*
- **Morphological Opening (`MORPH_OPEN`)**: Like an eraser that rubs away any tiny leftover black specks floating on the white paper.
- **Morphological Closing (`MORPH_CLOSE`)**: Like a black marker that fills in tiny cracks inside broken letters so every letter is solid and smooth.
- **PSNR Score**: A quality score (measured in `dB`) that proves mathematically to the teacher that the image got cleaner.

---

## 4. How to Run This Project (Step-by-Step)

### Step 1: Open Terminal in the `mini project` folder
Open your Terminal (or VS Code terminal) and go inside the `mini project` folder:
```bash
cd "mini project"
```

### Step 2: Install the 3 basic Python libraries (One time only)
Copy and paste this command and press Enter:
```bash
pip3 install opencv-python numpy matplotlib
```

### Step 3: Run the project!
Copy and paste this command and press Enter:
```bash
python3 main.py
```

### What will happen when you run it?
1. The terminal will print each step (`[Step 1]` to `[Step 5]`) along with the **PSNR** and **Contrast Improvement** scores.
2. A window will pop up showing **all 6 images side-by-side** (from the messy original to the final clean document).
3. All 6 output images + the combined comparison chart (`all_stages_comparison.png`) will be saved inside the **`results/`** folder!

*(Tip: Want to test your own photo? Just replace `sample_document.jpg` with any photo of a page and run `python3 main.py` again!)*

---

## 5. Super Easy Viva Questions & Answers (For Exam Day)

**Q1: Why did you use a Median Filter instead of a normal blur (Gaussian filter)?**
> **Simple Answer**: Our document has tiny black-and-white dots called salt-and-pepper noise. A normal Gaussian blur smudges the whole page and makes letters blurry, whereas a Median filter completely removes the dots while keeping the letters sharp.

**Q2: What does CLAHE do?**
> **Simple Answer**: CLAHE stands for *Contrast Limited Adaptive Histogram Equalization*. Instead of brightening the whole page at once, it divides the page into small 8×8 boxes and improves contrast inside each box so shadowed text becomes clearly visible.

**Q3: Why did you include both Otsu Thresholding and Adaptive Thresholding?**
> **Simple Answer**: To compare them! Global Otsu picks only **one** cutoff number for the whole page, so it fails when one side of the page is darker than the other. Adaptive Thresholding calculates a separate cutoff for every small region (21×21 pixels), so it works even when there are shadows.

**Q4: What is the difference between Morphological Opening and Closing?**
> **Simple Answer**:
> - **Opening** (Erosion then Dilation) removes tiny unwanted noise dots from the background.
> - **Closing** (Dilation then Erosion) fills tiny gaps and connects broken strokes inside the letters.

**Q5: How do you check how well your project worked?**
> **Simple Answer**: We check two things:
> 1. **Visual comparison** of all 6 stages side-by-side.
> 2. **PSNR (Peak Signal-to-Noise Ratio)** and **Contrast Improvement Ratio (CIR)** printed by our program.
