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
    fprintf(' SmartScan Studio PRO - MATLAB Implementation\n');
    fprintf(' Faculty In-Charge: Dr. Sachin Chavan | NMIMS MPSTME\n');
    fprintf(' Team: Parth (E235), Divyansh (E236), Himanshu (E250 - Lead)\n');
    fprintf('========================================================================\n\n');

    % Determine current script directory
    script_dir = fileparts(mfilename('fullpath'));

    % Auto-detect image or fallback
    if nargin < 1 || isempty(image_path) || ~isfile(image_path)
        candidate_paths = {
            fullfile(script_dir, 'samples', 'sample_1_academic_shadowed.jpg'),
            fullfile(script_dir, 'sample_document.jpg'),
            fullfile(script_dir, 'samples', 'sample_2_tax_invoice.jpg'),
            fullfile(pwd, 'sample_document.jpg')
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
        img_color = imread(image_path);
        if size(img_color, 3) == 3
            gray = rgb2gray(img_color);
        else
            gray = img_color;
            img_color = cat(3, gray, gray, gray);
        end
        fprintf('[STAGE 0] Loaded input document: %s\n', image_path);
    else
        fprintf('  --> No input image specified. Generating synthetic degraded benchmark...\n');
        gray = uint8(ones(700, 520) * 245);
        [X, Y] = meshgrid(1:520, 1:700);
        shadow = 1.0 - 0.60 * ((X / 520) + (Y / 700)) / 2;
        gray = uint8(double(gray) .* shadow);
        gray = imnoise(gray, 'salt & pepper', 0.03);
        img_color = cat(3, gray, gray, gray);
    end

    %% STAGE 1: Preprocessing & Retinex Normalization (Parth Chaturvedi - E235)
    fprintf('[STAGE 1] Loading and preprocessing document image...\n');
    % 1A: 2D Median Filter (5x5) to eliminate impulse noise
    median_filtered = medfilt2(gray, [5 5]);

    % 1B: Retinex Background Illumination Estimation & Division Normalization
    bg = imgaussfilt(double(median_filtered), 30);
    norm_vals = min(max((double(median_filtered) ./ (bg + 1e-5)) * 250, 0), 255);
    
    % 1C: Paper White Calibration (snaps paper to 255, deepens ink)
    enhanced = uint8(255 * ((norm_vals / 228) .^ 1.35));
    enhanced(norm_vals >= 228) = 255;

    %% STAGE 2: Edge Detection & Boundary Analysis (Divyansh Karel - E236)
    fprintf('[STAGE 2] Canny optimal boundary and edge detection...\n');
    edges = edge(enhanced, 'canny', [0.08 0.25]);

    %% STAGE 3: Document Segmentation (Divyansh Karel - E236)
    fprintf('[STAGE 3] Document thresholding: Global Otsu vs Local Adaptive...\n');
    % Method A: Global Otsu on RAW gray image (Demonstrates catastrophic failure on shadow gradients)
    level = graythresh(gray);
    otsu_bin = imbinarize(gray, level);

    % Method B: Local Adaptive Thresholding (robust against local illumination variations)
    adaptive_bin = imbinarize(enhanced, 'adaptive', 'ForegroundPolarity', 'dark', 'Sensitivity', 0.55);

    %% STAGE 4: Mathematical Morphology (Himanshu Garg - E250)
    fprintf('[STAGE 4] Mathematical morphology: Dual Opening and Closing...\n');
    % Invert image: text foreground becomes logical 1
    inverted_adaptive = ~adaptive_bin;

    % Morphological Opening (2x2 rectangular SE): eliminates residual speckle noise
    se_open = strel('rectangle', [2 2]);
    opened = imopen(inverted_adaptive, se_open);

    % Morphological Closing (3x3 rectangular SE): bridges stroke gaps in broken letters
    se_close = strel('rectangle', [3 3]);
    closed = imclose(opened, se_close);

    % Invert back to document standard: black text on clean white canvas
    final_output = uint8(~closed) * 255;

    %% STAGE 5: Frequency Domain & Color HD Restoration (Himanshu Garg - E250)
    fprintf('[STAGE 5] Computing Fourier spectrum and True-Color HD Restoration...\n');
    % 2D Fast Fourier Transform
    F = fft2(double(gray));
    F_shift = fftshift(F);
    fourier_spectrum = log(1 + abs(F_shift));
    fourier_norm = mat2gray(fourier_spectrum);

    % Color HD Restoration in Lab space
    if size(img_color, 3) == 3
        hd_img = imresize(img_color, 2, 'lanczos3');
        lab = rgb2lab(hd_img);
        L = lab(:, :, 1);
        L_med = medfilt2(L, [3 3]);
        bg_L = imgaussfilt(L_med, 35);
        L_norm = min(max((L_med ./ (bg_L + 1e-5)) * 96, 0), 100);
        L_sharp = imsharpen(L_norm, 'Radius', 1.2, 'Amount', 1.6);
        lab(:, :, 1) = L_sharp;
        master_hd_color = lab2rgb(lab);
    else
        master_hd_color = repmat(final_output, [1 1 3]);
    end

    % Evaluation Metrics
    orig_mean = mean(double(gray(:)));
    rest_mean = mean(double(enhanced(:)));
    psnr_val = psnr(final_output, gray);
    cir_val = std(double(enhanced(:))) / (std(double(gray(:))) + 1e-5);

    fprintf('\n------------------------------------------------------------------------\n');
    fprintf(' EXECUTION BENCHMARKS & EVALUATION:\n');
    fprintf('  • Input Baseline Mean Intensity     : %.1f / 255 (Dark Shaded)\n', orig_mean);
    fprintf('  • Restored Output Mean Intensity    : %.1f / 255 (Pristine White)\n', rest_mean);
    fprintf('  • Peak Signal-to-Noise Ratio (PSNR) : %.2f dB\n', psnr_val);
    fprintf('  • Contrast Improvement Ratio (CIR) : %.2fx\n', cir_val);
    fprintf('------------------------------------------------------------------------\n\n');

    %% Visualization: Multi-Stage Comparative Display
    figure('Name', 'SmartScan Studio PRO - IVP Pipeline', 'NumberTitle', 'off', 'Position', [100 100 1350 800]);

    subplot(2, 4, 1); imshow(gray); title('1. Original Degraded');
    subplot(2, 4, 2); imshow(enhanced); title('2. Retinex Preprocessed');
    subplot(2, 4, 3); imshow(edges); title('3. Canny Edges');
    subplot(2, 4, 4); imshow(otsu_bin); title('4. Global Otsu (Failure)');
    subplot(2, 4, 5); imshow(adaptive_bin); title('5. Local Adaptive');
    subplot(2, 4, 6); imshow(final_output); title('6. Morphologically Cleaned');
    subplot(2, 4, 7); imshow(fourier_norm, []); colormap(gca, 'jet'); title('7. 2D FFT Spectrum');
    subplot(2, 4, 8); imshow(master_hd_color); title('8. Master Color HD Output');

    sgtitle(sprintf('SmartScan Studio PRO | Faculty: Dr. Sachin Chavan | Restored White Level: %.1f | PSNR: %.2f dB', rest_mean, psnr_val), ...
            'FontSize', 13, 'FontWeight', 'bold');

    fprintf('[SUCCESS] Pipeline executed successfully. Visual multi-stage figure rendered.\n');
end
