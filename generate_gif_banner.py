import os
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageOps, ImageFilter

def create_dither_grid(image_path, target_w=200, target_h=225, dark_mode=True):
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
                    
    return dots

def build_banner_gif(dark_mode=True, output_filename="dark.gif"):
    width, height = 1180, 610
    
    bg_color = (10, 16, 31) if dark_mode else (248, 250, 252)
    card_bg = (30, 41, 59) if dark_mode else (226, 232, 240)
    border_color = (34, 211, 238) if dark_mode else (8, 145, 178)
    text_color = (226, 232, 240) if dark_mode else (15, 23, 42)
    dim_text = (148, 163, 184) if dark_mode else (100, 116, 139)
    portrait_dot_color = (167, 139, 250) if dark_mode else (124, 58, 237)
    accent_color = (16, 185, 129)
    red_color = (239, 68, 68)

    dots = create_dither_grid("PROFILE2.png", dark_mode=dark_mode)
    print(f"Generating GIF animation frames for {output_filename} ({len(dots)} dots)...")

    # Font setup (use default PIL font or Consolas if available)
    try:
        font_mono = ImageFont.truetype("consola.ttf", 14)
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
        ("ToolChain", "VS Code · Git · Docker · Qdrant · Postman"),
        ("Core.Lang", "Java · Python · JavaScript · SQL · C++"),
        ("Core.Frontend", "React.js · HTML5/CSS3 · Bootstrap"),
        ("Core.Backend", "Node.js · Express · Spring Boot · FastAPI"),
        ("Core.Database", "MongoDB · PostgreSQL · Qdrant Vector DB"),
        ("Core.Infra", "LangChain · LangGraph · RAG · Vercel · Groq"),
        ("Grid.Mail", "3872pranjalshukla@gmail.com"),
        ("Grid.LinkedIn", "pranjal-shukla"),
        ("Grid.GitHub", "pranjal3872")
    ]

    frames = []
    num_frames = 15 # smooth looping animation frames

    for f_idx in range(num_frames):
        img = Image.new("RGB", (width, height), bg_color)
        draw = ImageDraw.Draw(img)

        # Outer Window Frame
        draw.rounded_rectangle([10, 10, 1170, 600], radius=12, fill=bg_color, outline=border_color, width=2)
        # Header Bar
        draw.rounded_rectangle([10, 10, 1170, 50], radius=12, fill=card_bg, outline=border_color, width=1)
        draw.rectangle([10, 30, 1170, 50], fill=card_bg) # fill bottom corners of header
        draw.line([10, 50, 1170, 50], fill=border_color, width=1)

        # Control Buttons
        draw.ellipse([30, 24, 42, 36], fill=(239, 68, 68))
        draw.ellipse([50, 24, 62, 36], fill=(245, 158, 11))
        draw.ellipse([70, 24, 82, 36], fill=(16, 185, 129))

        # Title
        draw.text((590, 24), "profile.sh --live", fill=dim_text, font=font_title, anchor="mt")

        # Handle Pill & Pulsing Live dot
        draw.rounded_rectangle([1010, 20, 1145, 42], radius=11, fill=card_bg, outline=border_color, width=1)
        
        # Pulsing opacity logic
        pulse_val = abs(math.sin(f_idx * math.pi / num_frames))
        live_dot_color = (int(239 * (0.4 + 0.6 * pulse_val)), int(68 * (0.4 + 0.6 * pulse_val)), int(68 * (0.4 + 0.6 * pulse_val)))
        draw.ellipse([1020, 27, 1028, 35], fill=live_dot_color)
        draw.text((1034, 25), "LIVE", fill=red_color, font=font_small)
        draw.text((1070, 25), "@pranjal3872", fill=border_color, font=font_small)

        # Left Box: VISUAL.MAP Frame
        draw.rounded_rectangle([35, 75, 410, 575], radius=8, fill=bg_color, outline=border_color, width=1)
        draw.text((50, 88), "VISUAL.MAP // PORTRAIT DITHER", fill=border_color, font=font_small)
        draw.text((390, 88), "200x225 GRID", fill=dim_text, font=font_small, anchor="ra")
        draw.line([35, 105, 410, 105], fill=border_color, width=1)

        # Draw Dither Portrait Dots
        for i, (x, y) in enumerate(dots):
            # Subtle shimmer/reveal animation across frames
            if (i % num_frames) <= f_idx:
                draw.rectangle([x, y, x + 1.6, y + 1.6], fill=portrait_dot_color)

        # Right Box: SYSTEM.INFO Readout
        draw.rounded_rectangle([425, 75, 1145, 575], radius=8, fill=bg_color, outline=border_color, width=1)
        draw.text((440, 88), "SYSTEM.INFO // CANDIDATE SPECIFICATION", fill=accent_color, font=font_small)
        draw.text((1130, 88), "STATUS: ACTIVE", fill=dim_text, font=font_small, anchor="ra")
        draw.line([425, 105, 1145, 105], fill=border_color, width=1)

        # Info Lines
        start_y = 130
        line_height = 28
        for r_i, (label, val) in enumerate(rows):
            cur_y = start_y + (r_i * line_height)
            dots_count = max(4, int(42 - len(label) - len(val) * 0.8))
            dot_leader = "." * dots_count
            
            draw.text((440, cur_y), label, fill=border_color, font=font_mono)
            draw.text((560, cur_y), dot_leader, fill=dim_text, font=font_mono)
            draw.text((820, cur_y), val, fill=text_color, font=font_mono)

        # Terminal Footer
        draw.rounded_rectangle([440, 530, 1130, 560], radius=4, fill=card_bg)
        cursor_str = "█" if f_idx % 2 == 0 else " "
        draw.text((450, 538), f"$ cat experience.log | grep 'Mobcoder Intern' {cursor_str}", fill=accent_color, font=font_mono)

        frames.append(img)

    frames[0].save(
        output_filename,
        save_all=True,
        append_images=frames[1:],
        duration=120, # 120ms per frame
        loop=0
    )
    print(f"Successfully generated animated GIF: {output_filename}")

if __name__ == "__main__":
    build_banner_gif(dark_mode=True, output_filename="dark.gif")
    build_banner_gif(dark_mode=False, output_filename="light.gif")
