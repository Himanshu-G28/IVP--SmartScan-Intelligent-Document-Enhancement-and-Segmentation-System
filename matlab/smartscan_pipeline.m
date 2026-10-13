% =========================================================================
% Project Title : SmartScan - Document Enhancement and Segmentation System
% Course        : Image and Video Processing (IVP) Mini Project
% Group Members : E235 (Parth), E236 (Divyansh), E250 (Himanshu)
% =========================================================================

function smartscan_pipeline(image_path)
    % Get the folder where this .m file is located
    script_dir = fileparts(mfilename('fullpath'));

    % Automatically find the sample image even if no path (or a wrong path) is given
    if nargin < 1 || isempty(image_path) || ~isfile(image_path)
        candidate_paths = {
            fullfile(script_dir, 'sample_document.jpg'),
            fullfile(script_dir, 'synthetic_degraded.jpg'),
            fullfile(script_dir, '..', 'samples', 'synthetic_degraded.jpg'),
            fullfile(pwd, 'sample_document.jpg'),
            fullfile(pwd, 'samples', 'synthetic_degraded.jpg'),
            fullfile(pwd, 'mini project', 'sample_document.jpg')
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

    %% 1. Load Image & Preprocessing (Parth Chaturvedi - E235)
    fprintf('Stage 1: Preprocessing & Contrast Enhancement...\n');
    if ~isempty(image_path) && isfile(image_path)
        img = imread(image_path);
        if size(img, 3) == 3
            gray = rgb2gray(img);
        else
            gray = img;
        end
    else
        % Fallback: generate a synthetic shadowed & noisy image if file is missing
        gray = uint8(ones(600, 500) * 240);
        [X, Y] = meshgrid(1:500, 1:600);
        shadow = 1.0 - 0.55 * ((X / 500) + (Y / 600)) / 2;
        gray = uint8(double(gray) .* shadow);
        gray = imnoise(gray, 'salt & pepper', 0.03);
    end

    % Step 1A: 2D Median Filter (5x5) to remove salt-and-pepper noise
    median_filtered = medfilt2(gray, [5 5]);

    % Step 1B: Illumination Normalization to remove dark background shadows
    bg = imgaussfilt(double(median_filtered), 25);
    normalized = uint8(min(max((double(median_filtered) ./ (bg + 1)) * 255, 0), 255));

    % Step 1C: CLAHE (Contrast-Limited Adaptive Histogram Equalization)
    enhanced = adapthisteq(normalized, 'NumTiles', [8 8], 'ClipLimit', 0.02);

    %% 2. Edge Detection (Divyansh Karel - E236)
    fprintf('Stage 2: Canny Edge Detection...\n');
    edges = edge(enhanced, 'canny');

    %% 3. Document Segmentation / Thresholding (Divyansh Karel - E236)
    fprintf('Stage 3: Segmentation (Global Otsu vs Local Adaptive)...\n');
    % Method A: Global Otsu Thresholding
    level = graythresh(enhanced);
    otsu_bin = imbinarize(enhanced, level);

    % Method B: Local Adaptive Thresholding (handles uneven shadows)
    adaptive_bin = imbinarize(enhanced, 'adaptive', 'ForegroundPolarity', 'dark', 'Sensitivity', 0.55);

    %% 4. Morphological Post-Processing (Himanshu Garg - E250)
    fprintf('Stage 4: Morphological Opening & Closing...\n');
    % Invert image so black text becomes white foreground (1) for morphology
    inverted_adaptive = ~adaptive_bin;

    % Morphological Opening (removes small isolated background noise specks)
    se_open = strel('rectangle', [2 2]);
    opened = imopen(inverted_adaptive, se_open);

    % Morphological Closing (bridges small gaps inside broken letters)
    se_close = strel('rectangle', [3 3]);
    closed = imclose(opened, se_close);

    % Invert back so text is black (0) on white paper (255)
    final_output = uint8(~closed) * 255;

    %% 5. Evaluation & Display (Himanshu Garg - E250)
    psnr_val = psnr(final_output, gray);
    cir_val = std(double(enhanced(:))) / std(double(gray(:)));

    fprintf('\n--- SmartScan Evaluation Metrics ---\n');
    fprintf('PSNR                       : %.2f dB\n', psnr_val);
    fprintf('Contrast Improvement Ratio : %.2fx\n', cir_val);
    fprintf('------------------------------------\n');

    % Display all 6 stages side-by-side
    figure('Name', 'SmartScan IVP Mini Project', 'NumberTitle', 'off', 'Position', [100 100 1200 750]);

    subplot(2,3,1); imshow(gray);         title('1. Original Noisy & Shadowed');
    subplot(2,3,2); imshow(enhanced);     title('2. Enhanced (Median + CLAHE)');
    subplot(2,3,3); imshow(edges);        title('3. Canny Edges');
    subplot(2,3,4); imshow(otsu_bin);     title('4. Global Otsu Threshold');
    subplot(2,3,5); imshow(adaptive_bin); title('5. Local Adaptive Threshold');
    subplot(2,3,6); imshow(final_output); title('6. Final Cleaned (Morphology)');

    sgtitle(sprintf('SmartScan Pipeline | PSNR: %.2f dB | CIR: %.2fx', psnr_val, cir_val));
    disp('Pipeline executed successfully!');
end
