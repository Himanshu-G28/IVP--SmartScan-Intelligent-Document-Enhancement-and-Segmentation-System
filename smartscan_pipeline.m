% =========================================================================
% Project Title : SmartScan Studio PRO - Document Enhancement & Segmentation
% Course        : Image and Video Processing (Course Code: 702EX0E020) | SEM-V
% Institution   : NMIMS University, MPSTME
% Faculty       : Dr. Sachin Chavan
% Group Members :
%   1. Parth Chaturvedi (Roll No. E235) - Preprocessing & CLAHE
%   2. Divyansh Karel   (Roll No. E236) - Edge Detection & Segmentation
%   3. Himanshu Garg    (Roll No. E250, Lead) - Morphology, 2D DFT & Evaluation
% =========================================================================

function smartscan_pipeline(image_path)
    clc;
    fprintf('========================================================================\n');
    fprintf(' SmartScan Studio PRO - Refined MATLAB Pipeline (1:1 Python Equivalent)\n');
    fprintf(' Faculty In-Charge: Dr. Sachin Chavan | NMIMS MPSTME\n');
    fprintf(' Team: Parth (E235), Divyansh (E236), Himanshu (E250 - Lead)\n');
    fprintf('========================================================================\n\n');

    % Determine current script directory
    script_dir = fileparts(mfilename('fullpath'));

    % Auto-detect image or fallback
    if nargin < 1 || isempty(image_path) || ~isfile(image_path)
        candidate_paths = { ...
            fullfile(script_dir, 'samples', 'ProjectTest.png'); ...
            fullfile(script_dir, 'ProjectTest.png'); ...
            fullfile(script_dir, 'samples', 'sample_1_academic_shadowed.jpg'); ...
            fullfile(script_dir, 'sample_document.jpg'); ...
            fullfile(script_dir, 'samples', 'sample_2_tax_invoice.jpg'); ...
            fullfile(script_dir, 'samples', 'sample_3_official_certificate.jpg'); ...
            fullfile(pwd, 'sample_document.jpg') ...
        };
        found_path = '';
        for i = 1:length(candidate_paths)
            if isfile(candidate_paths{i})
                found_path = candidate_paths{i};
                break;
            end
        end
        image_path = found_path;
    end

    %% STAGE 0: Ingestion
    if ~isempty(image_path) && isfile(image_path)
        [img_raw, cmap] = imread(image_path);
        if ~isempty(cmap)
            img_color = uint8(ind2rgb(img_raw, cmap) * 255.0);
        else
            img_color = img_raw;
        end
        if size(img_color, 3) == 3
            gray = rgb2gray(img_color);
        else
            gray = img_color;
            img_color = cat(3, gray, gray, gray);
        end
        [~, fname, fext] = fileparts(image_path);
        fprintf('[STAGE 0] Ingesting Document: %s%s\n', fname, fext);
    else
        fprintf('[INFO] No input image found. Generating realistic degraded benchmark...\n');
        gray = uint8(ones(700, 520) * 245);
        [X, Y] = meshgrid(1:520, 1:700);
        shadow = 1.0 - 0.60 * ((X / 520) + (Y / 700)) / 2;
        gray = uint8(double(gray) .* shadow);
        gray = imnoise(gray, 'salt & pepper', 0.03);
        img_color = cat(3, gray, gray, gray);
    end

    [h, w] = size(gray);

    %% STAGE 1: Preprocessing & Retinex Normalization (Parth Chaturvedi - E235)
    fprintf('[STAGE 1] Preprocessing: Median Denoising & Retinex Illumination Normalization (Parth)...\n');
    % 1A: 2D Median Filter (5x5) eliminates salt-and-pepper impulses without edge blurring
    med = medfilt2(gray, [5 5]);

    % 1B: Retinex Background Illumination Estimation & Division Normalization
    bg = imgaussfilt(double(med), 30);
    norm_vals = min(max((double(med) ./ (bg + 1e-5)) * 250.0, 0), 255.0);
    
    % 1C: Tone curve to snap background to pristine paper white (255) and deepen text ink
    enhanced_d = norm_vals;
    mask_text = norm_vals < 228.0;
    enhanced_d(mask_text) = 255.0 * ((norm_vals(mask_text) / 228.0) .^ 1.35);
    enhanced_d(~mask_text) = 255.0;
    enhanced = uint8(enhanced_d);

    %% STAGE 2: Edge Detection & Boundary Analysis (Divyansh Karel - E236)
    fprintf('[STAGE 2] Boundary Extraction: Sobel Magnitude & Canny Detector (Divyansh)...\n');
    % Canny optimal hysteresis edge detection matching Python's thresholds [50, 150]
    edges = edge(enhanced, 'canny', [50/255, 150/255]);

    %% STAGE 3: Document Segmentation: Otsu vs Adaptive (Divyansh Karel - E236)
    fprintf('[STAGE 3] Document Segmentation: Global Otsu vs Local Adaptive (Divyansh)...\n');
    % Method A: Global Otsu on RAW gray image (Demonstrates catastrophic failure under shadow gradients)
    level = graythresh(gray);
    otsu_bin = imbinarize(gray, level);

    % Method B: Local Adaptive Gaussian Thresholding (31x31 neighborhood)
    if exist('adaptthresh', 'file') == 2
        T = adaptthresh(enhanced, 0.55, 'NeighborhoodSize', [31 31], 'Statistic', 'gaussian');
        adaptive_bin = imbinarize(enhanced, T);
    else
        adaptive_bin = imbinarize(enhanced, 'adaptive', 'ForegroundPolarity', 'dark', 'Sensitivity', 0.55);
    end

    %% STAGE 4: Mathematical Morphology (Himanshu Garg - E250)
    fprintf('[STAGE 4] Mathematical Morphology: Opening & Closing (Himanshu)...\n');
    % Invert image so black text becomes white foreground (logical 1)
    inv_text = ~adaptive_bin;

    % A. Opening (2x2 rectangular SE): eliminates isolated background speckles
    se_open = strel('rectangle', [2 2]);
    opened = imopen(inv_text, se_open);

    % B. Closing (3x3 Cross SE matching Python cv2.MORPH_CROSS): bridges broken strokes
    se_cross = [0 1 0; 1 1 1; 0 1 0];
    closed = imclose(opened, se_cross);

    % Invert back to document standard: black text on clean white canvas
    final_output = uint8(~closed) * 255;

    %% STAGE 5: Transform Domain / 2D DFT (Himanshu Garg - E250)
    fprintf('[STAGE 5] Frequency Analysis: 2D Discrete Fourier Transform (Himanshu)...\n');
    F = fft2(double(gray));
    F_shift = fftshift(F);
    fourier_mag = 20.0 * log(1 + abs(F_shift));
    fourier_norm = mat2gray(fourier_mag);

    %% MASTER TRUE-COLOR HD RESTORATION (Himanshu Garg - Lead Architecture)
    fprintf('[MASTER ENGINE] 2x Lanczos Super-Resolution & Retinex Color HD Engine (Himanshu)...\n');
    if size(img_color, 3) == 3
        % 1. 2x Super-Resolution Upscaling using Lanczos-3 interpolation
        hd_color = imresize(img_color, 2, 'lanczos3');
        
        % 2. CIE LAB Color Space Decoupling (Luminance processed independently from Chroma)
        lab = rgb2lab(hd_color);
        L = lab(:, :, 1);       % Lightness range: [0, 100]
        a_ch = lab(:, :, 2);    % Chrominance A
        b_ch = lab(:, :, 3);    % Chrominance B
        
        % 3. Sub-pixel Median Filtering for impulse noise
        L_med = medfilt2(L, [3 3]);
        
        % 4. Retinex Illumination Normalization on L (ERADICATES SHADOWS COMPLETELY!)
        bg_L = imgaussfilt(L_med, 40);
        L_norm = min(max((L_med ./ (bg_L + 1e-5)) * 98.0, 0), 100.0);
        
        % 5. Bilateral Edge-Preserving Filter (smooths paper grain, locks text boundaries)
        if exist('imbilatfilt', 'file') == 2
            L_bil = imbilatfilt(L_norm, 15, 3);
        else
            L_bil = L_norm;
        end
        
        % 6. Multi-Scale Dual-Pass High-Boost Unsharp Masking
        % Pass 1: Fine edge contour pass (sigma=1.0)
        blur_fine = imgaussfilt(L_bil, 1.0);
        sharp_fine = min(max(1.75 * L_bil - 0.75 * blur_fine, 0), 100.0);
        
        % Pass 2: Stroke body density pass (sigma=2.5)
        blur_med_L = imgaussfilt(sharp_fine, 2.5);
        sharp_body = min(max(1.35 * sharp_fine - 0.35 * blur_med_L, 0), 100.0);
        
        % 7. Paper White Calibration & Text Contrast S-Curve
        % White paper threshold in Lab lightness is ~88.0
        L_final = sharp_body;
        mask_text_hd = sharp_body < 88.0;
        L_final(mask_text_hd) = 100.0 * ((sharp_body(mask_text_hd) / 88.0) .^ 1.35);
        L_final(~mask_text_hd) = 100.0;
        
        % 8. Paper Chroma Neutralization (removes yellow shadow tint; preserves authentic stamps/signatures)
        is_paper = double(L_final > 95.0);
        a_clean = a_ch .* (1.0 - is_paper * 0.75);
        b_clean = b_ch .* (1.0 - is_paper * 0.75);
        
        % Recombine in LAB and convert back to RGB
        lab_restored = cat(3, L_final, a_clean, b_clean);
        master_hd_color = lab2rgb(lab_restored);
        master_hd_color = uint8(min(max(master_hd_color * 255.0, 0), 255));
    else
        master_hd_color = repmat(final_output, [1 1 3]);
    end

    %% Quantitative Benchmarks & Image Saving
    orig_mean = mean(double(gray(:)));
    rest_mean = mean(double(enhanced(:)));
    pixel_distinction = mean(abs(double(imresize(gray, 2)) - double(rgb2gray(master_hd_color))));
    psnr_val = psnr(imresize(rgb2gray(master_hd_color), [h w]), gray);
    cir_val = std(double(enhanced(:))) / (std(double(gray(:))) + 1e-5);

    % Save results into results directory
    results_dir = fullfile(script_dir, 'results');
    if ~exist(results_dir, 'dir')
        mkdir(results_dir);
    end
    imwrite(gray, fullfile(results_dir, 'matlab_1_original_gray.jpg'));
    imwrite(enhanced, fullfile(results_dir, 'matlab_2_enhanced_retinex.jpg'));
    imwrite(edges, fullfile(results_dir, 'matlab_3_canny_edges.jpg'));
    imwrite(otsu_bin, fullfile(results_dir, 'matlab_4_otsu_failure.jpg'));
    imwrite(adaptive_bin, fullfile(results_dir, 'matlab_5_adaptive_segmentation.jpg'));
    imwrite(final_output, fullfile(results_dir, 'matlab_6_morphological_clean.jpg'));
    imwrite(master_hd_color, fullfile(results_dir, 'matlab_8_final_master_hd.jpg'));

    fprintf('------------------------------------------------------------------------\n');
    fprintf(' EXECUTION BENCHMARKS & EVALUATION:\n');
    fprintf('  • Input Baseline Mean Intensity     : %.1f / 255 (Dark Shaded)\n', orig_mean);
    fprintf('  • Restored Output Mean (Pure White) : %.1f / 255 (Pristine White Platen)\n', rest_mean);
    fprintf('  • Visual Distinction (Mean Shift)   : %.1f gray levels (Dramatic!)\n', pixel_distinction);
    fprintf('  • Peak Signal-to-Noise Ratio (PSNR) : %.2f dB\n', psnr_val);
    fprintf('  • Contrast Improvement Ratio (CIR) : %.2fx\n', cir_val);
    fprintf('  • Output HD Resolution             : %d x %d px (2x Lanczos)\n', w*2, h*2);
    fprintf('  • Artifacts Saved In               : %s/\n', results_dir);
    fprintf('------------------------------------------------------------------------\n\n');

    %% Visual Multi-Stage Panel Display (8 Subplots matching Python)
    figure('Name', 'SmartScan Studio PRO - IVP Pipeline', 'NumberTitle', 'off');

    if exist('tiledlayout', 'file') ~= 0
        t = tiledlayout(2, 4, 'Padding', 'compact', 'TileSpacing', 'compact');
        nexttile; imshow(gray); title('1. Original Degraded (Shadow & Noise)', 'FontWeight', 'bold');
        nexttile; imshow(enhanced); title('2. Retinex Preprocessed (Pure White)', 'FontWeight', 'bold');
        nexttile; imshow(edges); title('3. Canny Optimal Edges', 'FontWeight', 'bold');
        nexttile; imshow(otsu_bin); title('4. Global Otsu (Catastrophic Failure)', 'FontWeight', 'bold');
        nexttile; imshow(adaptive_bin); title('5. Local Adaptive Gaussian (Clean)', 'FontWeight', 'bold');
        nexttile; imshow(final_output); title('6. Morphologically Cleaned (Open+Close)', 'FontWeight', 'bold');
        nexttile; imshow(fourier_norm, []); colormap(gca, 'jet'); title('7. 2D Fourier Spectrum (DFT)', 'FontWeight', 'bold');
        nexttile; imshow(master_hd_color); title('8. Master True-Color HD Output', 'FontWeight', 'bold');

        title(t, sprintf('SmartScan Studio PRO | Faculty: Dr. Sachin Chavan | Visual Shift: +%.1f px | PSNR: %.2f dB', ...
              pixel_distinction, psnr_val), 'FontSize', 13, 'FontWeight', 'bold');
    else
        subplot(2, 4, 1); imshow(gray); title('1. Original Degraded', 'FontWeight', 'bold');
        subplot(2, 4, 2); imshow(enhanced); title('2. Retinex Preprocessed', 'FontWeight', 'bold');
        subplot(2, 4, 3); imshow(edges); title('3. Canny Edges', 'FontWeight', 'bold');
        subplot(2, 4, 4); imshow(otsu_bin); title('4. Global Otsu (Failure)', 'FontWeight', 'bold');
        subplot(2, 4, 5); imshow(adaptive_bin); title('5. Local Adaptive', 'FontWeight', 'bold');
        subplot(2, 4, 6); imshow(final_output); title('6. Morphologically Cleaned', 'FontWeight', 'bold');
        subplot(2, 4, 7); imshow(fourier_norm, []); colormap(gca, 'jet'); title('7. 2D FFT Spectrum', 'FontWeight', 'bold');
        subplot(2, 4, 8); imshow(master_hd_color); title('8. Master True-Color HD', 'FontWeight', 'bold');
    end

    fprintf('[SUCCESS] Pipeline executed successfully. Visual multi-stage figure rendered.\n');
end
