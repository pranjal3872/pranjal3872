import os
import math
import random
import numpy as np
from PIL import Image, ImageEnhance, ImageOps, ImageFilter
from scipy.spatial.distance import cdist

def process_portrait(image_path, target_w=300, target_h=340):
    img = Image.open(image_path).convert("RGBA")
    
    # 1. Background segmentation / mask creation
    # Extract alpha or segment based on background color
    bg = Image.new("RGBA", img.size, (255, 255, 255, 255))
    alpha_composite = Image.alpha_composite(bg, img).convert("RGB")
    
    # Crop to head and shoulders framing
    w, h = alpha_composite.size
    # Focus on upper portion / center for head and shoulders
    crop_box = (int(w * 0.05), int(h * 0.05), int(w * 0.95), int(h * 0.95))
    cropped = alpha_composite.crop(crop_box)
    
    # Resize to 300x340
    resized = cropped.resize((target_w, target_h), Image.Resampling.LANCZOS)
    
    # Contrast 1.3x with autocontrast(cutoff=1) + UnsharpMask(radius=3, percent=140)
    gray = resized.convert("L")
    auto_gray = ImageOps.autocontrast(gray, cutoff=1)
    sharp_gray = auto_gray.filter(ImageFilter.UnsharpMask(radius=3, percent=140))
    enhancer = ImageEnhance.Contrast(sharp_gray)
    contrasted = enhancer.enhance(1.3)
    
    arr = np.array(contrasted, dtype=float)
    
    # Dark Mode Masking: segment subject from background
    # Background in photo is light/whiteish or uniform, subject is darker/medium
    # Subject mask: 1 where subject is, 0 for background
    # Background thresholding:
    bg_thresh = 220
    subject_mask = (arr < bg_thresh).astype(float)
    
    # 1-bit Floyd-Steinberg dither (serpentine order)
    # For Dark Mode: dots draw lit subject (bright parts of subject)
    # For Light Mode: dots draw dark parts of photo
    
    def floyd_steinberg_dither(input_arr, dark_mode=False, mask=None):
        h, w = input_arr.shape
        img_data = input_arr.copy()
        output = np.zeros((h, w), dtype=int)
        
        for y in range(h):
            # Serpentine scanning
            x_range = range(w) if y % 2 == 0 else range(w - 1, -1, -1)
            direction = 1 if y % 2 == 0 else -1
            
            for x in x_range:
                old_val = img_data[y, x]
                
                if dark_mode:
                    # In dark mode, lit/brighter parts of subject produce dots
                    # Range 0 (dark) to 255 (bright)
                    new_val = 255 if old_val > 128 else 0
                    if mask is not None and mask[y, x] == 0:
                        new_val = 0
                    output[y, x] = 1 if new_val == 255 else 0
                else:
                    # In light mode, darker parts produce dots
                    new_val = 0 if old_val < 128 else 255
                    output[y, x] = 1 if new_val == 0 else 0
                
                err = old_val - new_val
                
                # Distribute error
                if 0 <= x + direction < w:
                    img_data[y, x + direction] += err * (7 / 16)
                if y + 1 < h:
                    if 0 <= x - direction < w:
                        img_data[y + 1, x - direction] += err * (3 / 16)
                    img_data[y + 1, x] += err * (5 / 16)
                    if 0 <= x + direction < w:
                        img_data[y + 1, x + direction] += err * (1 / 16)
                        
        return output

    dots_dark = floyd_steinberg_dither(arr, dark_mode=True, mask=subject_mask)
    dots_light = floyd_steinberg_dither(arr, dark_mode=False)
    
    return dots_dark, dots_light, target_w, target_h

print("Testing portrait processing...")
dark_dots, light_dots, w, h = process_portrait("PROFILE2.png")
print(f"Dark dots count: {np.sum(dark_dots)}, Light dots count: {np.sum(light_dots)}")
