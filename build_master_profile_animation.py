import os
import sys
import math
import random
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageOps, ImageFilter
from scipy.optimize import linear_sum_assignment
from scipy.spatial.distance import cdist

print("Initializing Master Profile Animation Generator...")

# ---------------------------------------------------------
# 1. DITHER PORTRAIT EXTRACTION
# ---------------------------------------------------------
def extract_portrait_dots(image_path, target_w=200, target_h=225, dark_mode=True):
    img = Image.open(image_path).convert("RGBA")
    bg = Image.new("RGBA", img.size, (255, 255, 255, 255))
    comp = Image.alpha_composite(bg, img).convert("RGB")
    
    w, h = comp.size
    crop_box = (int(w * 0.08), int(h * 0.04), int(w * 0.92), int(h * 0.92))
    cropped = comp.crop(crop_box)
    
    resized = cropped.resize((target_w, target_h), Image.Resampling.LANCZOS)
    gray = resized.convert("L")
    auto_gray = ImageOps.autocontrast(gray, cutoff=1)
    sharp_gray = auto_gray.filter(ImageFilter.UnsharpMask(radius=3, percent=140))
    enhancer = ImageEnhance.Contrast(sharp_gray)
    contrasted = enhancer.enhance(1.3)
    
    arr = np.array(contrasted, dtype=float)
    img_data = arr.copy()
    dots = []
    
    for y in range(target_h):
        serpentine = (y % 2 == 1)
        x_indices = range(target_w - 1, -1, -1) if serpentine else range(target_w)
        direction = -1 if serpentine else 1
        
        for x in x_indices:
            old_val = img_data[y, x]
            
            if dark_mode:
                new_val = 255 if old_val > 120 else 0
                if arr[y, x] > 230:
                    new_val = 0
                is_dot = (new_val == 255)
            else:
                new_val = 0 if old_val < 135 else 255
                is_dot = (new_val == 0)
                
            err = old_val - new_val
            
            if is_dot:
                px = 65 + (x / target_w) * 330
                py = 135 + (y / target_h) * 410
                dots.append((round(px, 1), round(py, 1)))
                
            if 0 <= x + direction < target_w:
                img_data[y, x + direction] += err * (7 / 16)
            if y + 1 < target_h:
                if 0 <= x - direction < target_w:
                    img_data[y + 1, x - direction] += err * (3 / 16)
                img_data[y + 1, x] += err * (5 / 16)
                if 0 <= x + direction < target_w:
                    img_data[y + 1, x + direction] += err * (1 / 16)
                    
    return np.array(dots)

# ---------------------------------------------------------
# 2. LOGO SHAPE POINT GENERATORS (~900 DOTS EACH)
# ---------------------------------------------------------
def generate_python_logo_points(num_points=900, cx=230, cy=340, scale=110):
    pts = []
    for t in np.linspace(0, 2*np.pi, num_points // 2):
        r = scale * (0.6 + 0.25 * np.cos(2*t))
        x = cx + r * np.cos(t) - 15
        y = cy + r * np.sin(t) - 25
        pts.append((x, y))
    for t in np.linspace(0, 2*np.pi, num_points // 2):
        r = scale * (0.6 + 0.25 * np.sin(2*t))
        x = cx + r * np.cos(t) + 15
        y = cy + r * np.sin(t) + 25
        pts.append((x, y))
    return np.array(pts[:num_points])

def generate_react_logo_points(num_points=900, cx=230, cy=340, rx=110, ry=42):
    pts = []
    for t in np.linspace(0, 2*np.pi, 150):
        r = 22
        pts.append((cx + r * np.cos(t), cy + r * np.sin(t)))
    angles = [0, math.pi/3, 2*math.pi/3]
    pts_per_orbit = (num_points - 150) // 3
    for angle in angles:
        for t in np.linspace(0, 2*np.pi, pts_per_orbit):
            ex = rx * math.cos(t)
            ey = ry * math.sin(t)
            rot_x = cx + ex * math.cos(angle) - ey * math.sin(angle)
            rot_y = cy + ex * math.sin(angle) + ey * math.cos(angle)
            pts.append((rot_x, rot_y))
    return np.array(pts[:num_points])

def generate_code_glyph_points(num_points=900, cx=230, cy=340, size=100):
    pts = []
    l_pts = num_points // 3
    for t in np.linspace(0, 1, l_pts // 2):
        pts.append((cx - 70 + t * 45, cy - 60 + t * 60))
        pts.append((cx - 25 - t * 45, cy + t * 60))
    s_pts = num_points // 3
    for t in np.linspace(0, 1, s_pts):
        pts.append((cx + 15 - t * 30, cy - 70 + t * 140))
    r_pts = num_points - len(pts)
    for t in np.linspace(0, 1, r_pts // 2):
        pts.append((cx + 30 + t * 45, cy - 60 + t * 60))
        pts.append((cx + 75 - t * 45, cy + t * 60))
    return np.array(pts[:num_points])

# ---------------------------------------------------------
# 3. OPTIMAL TRANSPORT MATCHING BETWEEN SHAPES
# ---------------------------------------------------------
def match_optimal_transport(source_pts, target_pts):
    cost_matrix = cdist(source_pts, target_pts, metric='euclidean')
    row_ind, col_ind = linear_sum_assignment(cost_matrix)
    return target_pts[col_ind]

# ---------------------------------------------------------
# 4. MASTER ANIMATION PIPELINE GENERATOR (SMIL & GIF)
# ---------------------------------------------------------
def run_master_pipeline(dark_mode=True):
    mode_str = "dark" if dark_mode else "light"
    print(f"\n--- Processing Master Animation ({mode_str.upper()} MODE) ---")
    
    portrait_dots = extract_portrait_dots("PROFILE2.png", dark_mode=dark_mode)
    num_portrait = len(portrait_dots)

    np.random.seed(42)
    sample_indices = np.random.choice(num_portrait, size=900, replace=False)
    travellers_p0 = portrait_dots[sample_indices].copy()

    logo1_raw = generate_python_logo_points(num_points=900)
    logo2_raw = generate_react_logo_points(num_points=900)
    logo3_raw = generate_code_glyph_points(num_points=900)

    travellers_l1 = match_optimal_transport(travellers_p0, logo1_raw)
    travellers_l2 = match_optimal_transport(travellers_l1, logo2_raw)
    travellers_l3 = match_optimal_transport(travellers_l2, logo3_raw)

    noisy_portrait = portrait_dots + np.random.normal(0, 4.0, portrait_dots.shape)
    y_coords = noisy_portrait[:, 1]
    band_assignments = np.digitize(y_coords, np.linspace(135, 545, 94))

    l1_centroid = np.mean(travellers_l1, axis=0)

    width, height = 1180, 610
    bg_color = (10, 16, 31) if dark_mode else (248, 250, 252)
    card_bg = (30, 41, 59) if dark_mode else (226, 232, 240)
    border_color = (34, 211, 238) if dark_mode else (8, 145, 178)
    text_color = (226, 232, 240) if dark_mode else (15, 23, 42)
    dim_text = (148, 163, 184) if dark_mode else (100, 116, 139)
    portrait_dot_color = (167, 139, 250) if dark_mode else (124, 58, 237)
    traveller_color = (16, 185, 129)
    accent_color = (16, 185, 129)
    red_color = (239, 68, 68)

    try:
        font_mono = ImageFont.truetype("consola.ttf", 13)
        font_small = ImageFont.truetype("consola.ttf", 11)
        font_title = ImageFont.truetype("consolab.ttf", 14)
    except:
        font_mono = font_small = font_title = ImageFont.load_default()

    rows = [
        ("Subject", "Pranjal Shukla"),
        ("Role", "Software Engineer (AI & Full-Stack)"),
        ("Origin", "Ghaziabad, UP, India"),
        ("Education", "B.Tech CSE, AKGEC (2023 - 2027)"),
        ("Status", "Building RAG & AI Agents @ Mobcoder"),
        ("ToolChain", "VS Code · Git · Docker · Qdrant"),
        ("Core.Lang", "Java · Python · JavaScript · SQL · C++"),
        ("Core.Frontend", "React.js · HTML5/CSS3 · Bootstrap"),
        ("Core.Backend", "Node.js · Express · Spring Boot · FastAPI"),
        ("Core.Database", "MongoDB · PostgreSQL · Qdrant Vector DB"),
        ("Core.Infra", "LangChain · LangGraph · RAG · Groq"),
        ("Grid.Mail", "3872pranjalshukla@gmail.com"),
        ("Grid.LinkedIn", "in/pranjal3872"),
        ("Grid.GitHub", "pranjal3872")
    ]

    total_frames = 30
    gif_frames = []

    for frame_idx in range(total_frames):
        t_phase = frame_idx / total_frames

        img = Image.new("RGB", (width, height), bg_color)
        draw = ImageDraw.Draw(img)

        draw.rounded_rectangle([10, 10, 1170, 600], radius=12, fill=bg_color, outline=border_color, width=2)
        draw.rounded_rectangle([10, 10, 1170, 50], radius=12, fill=card_bg, outline=border_color, width=1)
        draw.rectangle([10, 30, 1170, 50], fill=card_bg)
        draw.line([10, 50, 1170, 50], fill=border_color, width=1)

        draw.ellipse([30, 24, 42, 36], fill=(239, 68, 68))
        draw.ellipse([50, 24, 62, 36], fill=(245, 158, 11))
        draw.ellipse([70, 24, 82, 36], fill=(16, 185, 129))
        draw.text((590, 24), "profile.sh --live", fill=dim_text, font=font_title, anchor="mt")

        draw.rounded_rectangle([1010, 20, 1145, 42], radius=11, fill=card_bg, outline=border_color, width=1)
        pulse = abs(math.sin(t_phase * 2 * math.pi))
        live_dot = (int(239*(0.4+0.6*pulse)), int(68*(0.4+0.6*pulse)), int(68*(0.4+0.6*pulse)))
        draw.ellipse([1020, 27, 1028, 35], fill=live_dot)
        draw.text((1034, 25), "LIVE", fill=red_color, font=font_small)
        draw.text((1070, 25), "@pranjal3872", fill=border_color, font=font_small)

        draw.rounded_rectangle([35, 75, 410, 575], radius=8, fill=bg_color, outline=border_color, width=1)
        draw.text((50, 88), "VISUAL.MAP // PORTRAIT DITHER", fill=border_color, font=font_small)
        draw.text((390, 88), "200x225 GRID", fill=dim_text, font=font_small, anchor="ra")
        draw.line([35, 105, 410, 105], fill=border_color, width=1)

        if t_phase < 0.2:
            drift_factor = 0.0
            portrait_alpha = 1.0
        elif t_phase < 0.8:
            prog = (t_phase - 0.2) / 0.6
            drift_factor = 0.42 * math.sin(prog * math.pi)
            portrait_alpha = 1.0 - 0.7 * math.sin(prog * math.pi)
        else:
            drift_factor = 0.0
            portrait_alpha = 1.0

        for b_id in range(1, 95):
            band_mask = (band_assignments == b_id)
            if not np.any(band_mask):
                continue
            b_dots = portrait_dots[band_mask]
            
            vec = (l1_centroid - np.mean(b_dots, axis=0)) * drift_factor
            translated_dots = b_dots + vec
            
            if random.random() < portrait_alpha:
                for x, y in translated_dots[::2]:
                    draw.rectangle([x, y, x + 1.8, y + 1.8], fill=portrait_dot_color)

        if t_phase >= 0.2:
            if t_phase < 0.4:
                interp = (t_phase - 0.2) / 0.2
                cur_travellers = (1 - interp) * travellers_p0 + interp * travellers_l1
            elif t_phase < 0.6:
                interp = (t_phase - 0.4) / 0.2
                cur_travellers = (1 - interp) * travellers_l1 + interp * travellers_l2
            elif t_phase < 0.8:
                interp = (t_phase - 0.6) / 0.2
                cur_travellers = (1 - interp) * travellers_l2 + interp * travellers_l3
            else:
                interp = (t_phase - 0.8) / 0.2
                cur_travellers = (1 - interp) * travellers_l3 + interp * travellers_p0

            for tx, ty in cur_travellers:
                draw.rectangle([tx, ty, tx + 2.2, ty + 2.2], fill=traveller_color)

        # SYSTEM.INFO Panel (x=425 to 1145)
        draw.rounded_rectangle([425, 75, 1145, 575], radius=8, fill=bg_color, outline=border_color, width=1)
        draw.text((440, 88), "SYSTEM.INFO // CANDIDATE SPECIFICATION", fill=accent_color, font=font_small)
        draw.text((1130, 88), "STATUS: ACTIVE", fill=dim_text, font=font_small, anchor="ra")
        draw.line([425, 105, 1145, 105], fill=border_color, width=1)

        start_y = 130
        line_height = 28
        for r_i, (label, val) in enumerate(rows):
            cur_y = start_y + (r_i * line_height)
            
            # Left label
            draw.text((440, cur_y), label, fill=border_color, font=font_mono)
            
            # Right-aligned value locked at x=1125 (guaranteeing 20px padding inside 1145 right border)
            draw.text((1125, cur_y), val, fill=text_color, font=font_mono, anchor="ra")
            
            # Compute leader dots between label and value
            try:
                l_bbox = draw.textbbox((440, cur_y), label, font=font_mono)
                v_bbox = draw.textbbox((1125, cur_y), val, font=font_mono, anchor="ra")
                leader_start = l_bbox[2] + 10
                leader_end = v_bbox[0] - 10
                if leader_end > leader_start + 20:
                    dots_num = int((leader_end - leader_start) / 8)
                    dot_str = "." * dots_num
                    draw.text((leader_start, cur_y), dot_str, fill=dim_text, font=font_mono)
            except:
                pass

        # Terminal Footer
        draw.rounded_rectangle([440, 530, 1130, 560], radius=4, fill=card_bg)
        cursor_str = "█" if frame_idx % 2 == 0 else " "
        draw.text((450, 538), f"$ cat experience.log | grep 'Mobcoder Intern' {cursor_str}", fill=accent_color, font=font_mono)

        gif_frames.append(img)

    gif_filename = f"{mode_str}.gif"
    gif_frames[0].save(
        gif_filename,
        save_all=True,
        append_images=gif_frames[1:],
        duration=140,
        loop=0
    )
    print(f"Master animation GIF saved to {gif_filename}!")

if __name__ == "__main__":
    run_master_pipeline(dark_mode=True)
    run_master_pipeline(dark_mode=False)
