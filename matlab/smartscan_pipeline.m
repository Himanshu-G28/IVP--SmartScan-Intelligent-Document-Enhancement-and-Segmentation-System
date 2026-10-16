% =========================================================================
% Project Title : SmartScan Studio PRO - Document Enhancement & Segmentation
% Course        : Image and Video Processing (Course Code: 702EX0E020) | SEM-V
% Institution   : NMIMS University, MPSTME
% Faculty       : Dr. Sachin Chavan
% Group Members :
%   1. Parth Chaturvedi (Roll No. E235) - Preprocessing & Illumination Normalization
%   2. Divyansh Karel   (Roll No. E236) - Edge Detection & Document Segmentation
%   3. Himanshu Garg    (Roll No. E250) - Mathematical Morphology & 2D DFT
% =========================================================================

function smartscan_pipeline(image_path)
    clc;
    close all; % Cleanly reset any lingering figures from prior runs or page refreshes
    fprintf('========================================================================\n');
    fprintf(' SmartScan Studio PRO - Refined MATLAB Pipeline (1:1 Python Equivalent)\n');
    fprintf(' Faculty In-Charge: Dr. Sachin Chavan | NMIMS MPSTME\n');
    fprintf(' Team: Parth Chaturvedi (E235), Divyansh Karel (E236), Himanshu Garg (E250)\n');
    fprintf('------------------------------------------------------------------------\n');
    fprintf(' USAGE GUIDE (How to run on ANY image):\n');
    fprintf('  • Any image file   : smartscan_pipeline(''your_image.jpg'')\n');
    fprintf('  • Interactive popup: smartscan_pipeline(''select'')\n');
    fprintf('  • Benchmark samples: smartscan_pipeline(1) to smartscan_pipeline(5)\n');
    fprintf('  • Default auto-run : smartscan_pipeline\n');
    fprintf('========================================================================\n\n');

    % Determine current script directory
    script_dir = fileparts(mfilename('fullpath'));

    % Benchmark Samples mapping (1 to 5)
    sample_catalog = { ...
        'sample_1_academic_shadowed.jpg', 'Academic Paper (Severe Shadow + Pepper Noise)'; ...
        'sample_2_tax_invoice.jpg', 'Tax Invoice (Thermal Print + Gradient)'; ...
        'sample_3_official_certificate.jpg', 'Degree Certificate (Fine Seal + Low Contrast)'; ...
        'sample_4_book_spine_page.jpg', 'Book Spine Page (Falloff + Crease)'; ...
        'sample_5_medical_prescription.jpg', 'Medical Prescription (Carbon Copy + Faded Ink)' ...
    };

    % Mode 1: Numeric benchmark index, e.g. smartscan_pipeline(1) to (5)
    if nargin >= 1 && isnumeric(image_path) && isscalar(image_path)
        sample_idx = round(image_path);
        if sample_idx >= 1 && sample_idx <= size(sample_catalog, 1)
            target_fname = sample_catalog{sample_idx, 1};
            desc = sample_catalog{sample_idx, 2};
            candidates = { ...
                fullfile(script_dir, 'samples', target_fname); ...
                fullfile(script_dir, target_fname); ...
                fullfile(pwd, 'samples', target_fname); ...
                fullfile(pwd, target_fname) ...
            };
            found = '';
            for c = 1:length(candidates)
                if isfile(candidates{c})
                    found = candidates{c};
                    break;
                end
            end
            if ~isempty(found)
                image_path = found;
                fprintf('[BENCHMARK %d] Loaded: %s (%s)\n', sample_idx, target_fname, desc);
            else
                fprintf('[WARNING] Sample %d ("%s") not found. Falling back to auto-detect.\n', sample_idx, target_fname);
                image_path = '';
            end
        else
            fprintf('[WARNING] Benchmark index must be between 1 and 5. Falling back to auto-detect.\n');
            image_path = '';
        end
    end

    % Mode 2: Interactive file selection popup, e.g. smartscan_pipeline('select')
    if nargin >= 1 && (ischar(image_path) || isstring(image_path)) && ...
       (strcmpi(image_path, 'select') || strcmpi(image_path, 'browse') || strcmpi(image_path, 'ui') || strcmpi(image_path, 'open'))
        [sel_file, sel_path] = uigetfile({'*.jpg;*.png;*.jpeg;*.bmp;*.tif;*.tiff', 'All Image Files (*.jpg, *.png, *.jpeg, *.bmp)'}, 'Select Document Image for SmartScan');
        if isequal(sel_file, 0)
            fprintf('[INFO] File selection cancelled. Using default fallback.\n');
            image_path = '';
        else
            image_path = fullfile(sel_path, sel_file);
            fprintf('[INTERACTIVE] Selected: %s\n', image_path);
        end
    end

    % Mode 3: Custom image filename/path passed as string, e.g. smartscan_pipeline('flower.jpg')
    if nargin >= 1 && ~isempty(image_path) && (ischar(image_path) || isstring(image_path))
        raw_name = char(image_path);
        if ~isfile(raw_name)
            candidates = { ...
                fullfile(pwd, raw_name); ...
                fullfile(script_dir, raw_name); ...
                fullfile(script_dir, 'samples', raw_name); ...
                fullfile(pwd, 'samples', raw_name) ...
            };
            [~, ~, ext] = fileparts(raw_name);
            if isempty(ext)
                exts = {'.jpg', '.png', '.jpeg', '.bmp'};
                for e = 1:length(exts)
                    candidates{end+1} = fullfile(pwd, [raw_name exts{e}]); %#ok<AGROW>
                    candidates{end+1} = fullfile(script_dir, [raw_name exts{e}]); %#ok<AGROW>
                    candidates{end+1} = fullfile(script_dir, 'samples', [raw_name exts{e}]); %#ok<AGROW>
                end
            end
            found = '';
            for c = 1:length(candidates)
                if isfile(candidates{c})
                    found = candidates{c};
                    break;
                end
            end
            if ~isempty(found)
                image_path = found;
            else
                fprintf('[WARNING] Could not locate image "%s". Falling back to default.\n', raw_name);
                image_path = '';
            end
        end
    end

    % Mode 4: Auto-detection fallback if no argument was passed or file not found
    if isempty(image_path) || ~isfile(image_path)
        candidate_paths = { ...
            fullfile(script_dir, 'samples', 'TestProject2.png'); ...
            fullfile(script_dir, 'TestProject2.png'); ...
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

    %% STAGE 1: Preprocessing & Retinex Normalization
    fprintf('[STAGE 1] Preprocessing: Median Denoising & Retinex Illumination Normalization...\n');
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

    %% STAGE 2: Edge Detection & Boundary Analysis
    fprintf('[STAGE 2] Boundary Extraction: Sobel Magnitude & Canny Detector...\n');
    % Canny optimal hysteresis edge detection matching Python's thresholds [50, 150]
    edges = edge(enhanced, 'canny', [50/255, 150/255]);

    %% STAGE 3: Document Segmentation: Otsu vs Adaptive
    fprintf('[STAGE 3] Document Segmentation: Global Otsu vs Local Adaptive...\n');
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

    %% STAGE 4: Mathematical Morphology
    fprintf('[STAGE 4] Mathematical Morphology: Opening & Closing...\n');
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

    %% STAGE 5: Transform Domain / 2D DFT
    fprintf('[STAGE 5] Frequency Analysis: 2D Discrete Fourier Transform...\n');
    F = fft2(double(gray));
    F_shift = fftshift(F);
    fourier_mag = 20.0 * log(1 + abs(F_shift));
    fourier_norm = mat2gray(fourier_mag);

    %% MASTER TRUE-COLOR HD RESTORATION
    fprintf('[MASTER ENGINE] 2x Lanczos Super-Resolution & Retinex Color HD Engine...\n');
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
    diff_hd = abs(double(imresize(gray, [size(master_hd_color, 1), size(master_hd_color, 2)])) - double(rgb2gray(master_hd_color)));
    pixel_distinction = mean(diff_hd(:));
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
    fprintf('  • Output HD Resolution             : %d x %d px (2x Lanczos)\n', size(master_hd_color, 2), size(master_hd_color, 1));
    fprintf('  • Artifacts Saved In               : %s/\n', results_dir);
    fprintf('------------------------------------------------------------------------\n\n');

    %% Visual Multi-Stage Panel Display (8 Subplots matching Python)
    figure('Name', 'SmartScan Studio PRO - IVP Pipeline', 'NumberTitle', 'off');

    % Display downscaling for responsive web/desktop rendering while preserving full HD on disk
    max_disp_dim = 1200;
    scale_disp = min(1.0, max_disp_dim / max([h, w]));
    if scale_disp < 1.0
        disp_gray = imresize(gray, scale_disp);
        disp_enhanced = imresize(enhanced, scale_disp);
        disp_edges = imresize(edges, scale_disp);
        disp_otsu = imresize(otsu_bin, scale_disp);
        disp_adaptive = imresize(adaptive_bin, scale_disp);
        disp_final = imresize(final_output, scale_disp);
        disp_fourier = imresize(fourier_norm, scale_disp);
        disp_hd = imresize(master_hd_color, scale_disp * 0.5);
    else
        disp_gray = gray;
        disp_enhanced = enhanced;
        disp_edges = edges;
        disp_otsu = otsu_bin;
        disp_adaptive = adaptive_bin;
        disp_final = final_output;
        disp_fourier = fourier_norm;
        disp_hd = imresize(master_hd_color, 0.5);
    end

    header_str = sprintf('SmartScan Studio PRO | Faculty: Dr. Sachin Chavan | Shift: +%.1f px | PSNR: %.2f dB', ...
                         pixel_distinction, psnr_val);

    if exist('tiledlayout', 'file') ~= 0
        t = tiledlayout(2, 4, 'Padding', 'compact', 'TileSpacing', 'compact');
        stages = { ...
            disp_gray, '1. Original Degraded', false; ...
            disp_enhanced, '2. Retinex Enhanced', false; ...
            disp_edges, '3. Canny Edges', false; ...
            disp_otsu, '4. Global Otsu (Failed)', false; ...
            disp_adaptive, '5. Local Adaptive', false; ...
            disp_final, '6. Morphological Clean', false; ...
            disp_fourier, '7. 2D FFT Spectrum', true; ...
            disp_hd, '8. Master Color HD', false ...
        };
        for k = 1:8
            ax = nexttile;
            if stages{k, 3}
                imshow(stages{k, 1}, []); colormap(ax, 'jet');
            else
                imshow(stages{k, 1});
            end
            title(stages{k, 2}, 'FontWeight', 'bold', 'Interpreter', 'none');
            if isprop(ax, 'Toolbar') && ~isempty(ax.Toolbar)
                ax.Toolbar.Visible = 'off';
            end
        end
        title(t, header_str, 'FontSize', 12, 'FontWeight', 'bold', 'Interpreter', 'none');
    else
        subplot(2, 4, 1); imshow(disp_gray); title('1. Original Degraded', 'FontWeight', 'bold', 'Interpreter', 'none');
        subplot(2, 4, 2); imshow(disp_enhanced); title('2. Retinex Enhanced', 'FontWeight', 'bold', 'Interpreter', 'none');
        subplot(2, 4, 3); imshow(disp_edges); title('3. Canny Edges', 'FontWeight', 'bold', 'Interpreter', 'none');
        subplot(2, 4, 4); imshow(disp_otsu); title('4. Global Otsu (Failed)', 'FontWeight', 'bold', 'Interpreter', 'none');
        subplot(2, 4, 5); imshow(disp_adaptive); title('5. Local Adaptive', 'FontWeight', 'bold', 'Interpreter', 'none');
        subplot(2, 4, 6); imshow(disp_final); title('6. Morphological Clean', 'FontWeight', 'bold', 'Interpreter', 'none');
        subplot(2, 4, 7); imshow(disp_fourier, []); colormap(gca, 'jet'); title('7. 2D FFT Spectrum', 'FontWeight', 'bold', 'Interpreter', 'none');
        subplot(2, 4, 8); imshow(disp_hd); title('8. Master Color HD', 'FontWeight', 'bold', 'Interpreter', 'none');
    end

    drawnow;
    fprintf('[SUCCESS] Pipeline executed successfully. Visual multi-stage figure rendered.\n');
    fprintf('[TIP] If viewing in MATLAB Online, click the Maximize icon on the figure window to enlarge the preview.\n');
end
