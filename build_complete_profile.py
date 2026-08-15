import os
import sys
import numpy as np
from PIL import Image, ImageEnhance, ImageOps, ImageFilter

def build_dither_dots(image_path, dark_mode=True, grid_w=300, grid_h=340):
    img = Image.open(image_path).convert("RGBA")
    
    bg = Image.new("RGBA", img.size, (255, 255, 255, 255))
    comp = Image.alpha_composite(bg, img).convert("RGB")
    
    w, h = comp.size
    crop_box = (int(w * 0.08), int(h * 0.04), int(w * 0.92), int(h * 0.92))
    cropped = comp.crop(crop_box)
    
    grid_w, grid_h = 200, 225
    resized = cropped.resize((grid_w, grid_h), Image.Resampling.LANCZOS)
    
    gray = resized.convert("L")
    auto_gray = ImageOps.autocontrast(gray, cutoff=1)
    sharp_gray = auto_gray.filter(ImageFilter.UnsharpMask(radius=3, percent=140))
    enhancer = ImageEnhance.Contrast(sharp_gray)
    contrasted = enhancer.enhance(1.3)
    
    arr = np.array(contrasted, dtype=float)
    img_data = arr.copy()
    dots = []
    
    for y in range(grid_h):
        serpentine = (y % 2 == 1)
        x_indices = range(grid_w - 1, -1, -1) if serpentine else range(grid_w)
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
                px = 65 + (x / grid_w) * 330
                py = 135 + (y / grid_h) * 410
                dots.append((round(px, 1), round(py, 1)))
                
            if 0 <= x + direction < grid_w:
                img_data[y, x + direction] += err * (7 / 16)
            if y + 1 < grid_h:
                if 0 <= x - direction < grid_w:
                    img_data[y + 1, x - direction] += err * (3 / 16)
                img_data[y + 1, x] += err * (5 / 16)
                if 0 <= x + direction < grid_w:
                    img_data[y + 1, x + direction] += err * (1 / 16)
                    
    return dots

def generate_svg(dark_mode=True):
    bg_color = "#0A101F" if dark_mode else "#F8FAFC"
    border_color = "#22D3EE" if dark_mode else "#0891B2"
    text_color = "#E2E8F0" if dark_mode else "#0F172A"
    dim_text = "#94A3B8" if dark_mode else "#64748B"
    portrait_dot_color = "#A78BFA" if dark_mode else "#7C3AED"
    accent_color = "#10B981"
    card_bg = "#1E293B" if dark_mode else "#E2E8F0"
    
    dots = build_dither_dots("PROFILE2.png", dark_mode=dark_mode)
    print(f"Generated {len(dots)} dither dots for {'dark' if dark_mode else 'light'} mode SVG.")
    
    chunk_size = 800
    path_tags = []
    
    for i in range(0, len(dots), chunk_size):
        chunk = dots[i:i + chunk_size]
        path_d = " ".join([f"M{x},{y}h1.8v1.8h-1.8z" for x, y in chunk])
        path_tags.append(f'<path d="{path_d}" fill="{portrait_dot_color}" shape-rendering="crispEdges" />')

    path_xml = "\n        ".join(path_tags)

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
    
    info_xml = []
    start_y = 175
    line_height = 27
    
    for i, (label, val) in enumerate(rows):
        cur_y = start_y + (i * line_height)
        dot_leader = "." * max(4, int(42 - len(label) - len(val) * 0.8))
        
        row_str = f"""
        <text x="440" y="{cur_y}" font-family="Consolas, Monaco, monospace" font-size="13.5" fill="{dim_text}">
            <tspan fill="{border_color}" font-weight="600">{label}</tspan>
            <tspan fill="{dim_text}" dx="6">{dot_leader}</tspan>
        </text>
        <text x="1125" y="{cur_y}" font-family="Consolas, Monaco, monospace" font-size="13.5" fill="{text_color}" font-weight="500" text-anchor="end">{val}</text>"""
        info_xml.append(row_str)
        
    info_panel_str = "\n".join(info_xml)
    
    svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1180 610" width="100%" height="100%">
    <defs>
        <style>
            @keyframes pulse {{
                0% {{ opacity: 1; }}
                50% {{ opacity: 0.3; }}
                100% {{ opacity: 1; }}
            }}
            .live-dot {{ animation: pulse 2s infinite ease-in-out; }}
        </style>
        <linearGradient id="panelGrad_{'dark' if dark_mode else 'light'}" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stop-color="{bg_color}" />
            <stop offset="100%" stop-color="{card_bg}" />
        </linearGradient>
    </defs>

    <!-- Outer Window Frame -->
    <rect x="10" y="10" width="1160" height="590" rx="12" fill="url(#panelGrad_{'dark' if dark_mode else 'light'})" stroke="{border_color}" stroke-width="1.5" />

    <!-- Terminal Header Bar -->
    <path d="M 10,22 A 12,12 0 0,1 22,10 L 1158,10 A 12,12 0 0,1 1170,22 L 1170,50 L 10,50 Z" fill="{card_bg}" stroke="{border_color}" stroke-width="1" />
    
    <!-- Window Control Buttons -->
    <circle cx="35" cy="30" r="6" fill="#EF4444" />
    <circle cx="55" cy="30" r="6" fill="#F59E0B" />
    <circle cx="75" cy="30" r="6" fill="#10B981" />

    <!-- Window Title -->
    <text x="590" y="34" font-family="Consolas, Monaco, monospace" font-size="14" fill="{dim_text}" text-anchor="middle" font-weight="600">profile.sh --live</text>

    <!-- Live Status Indicator & Handle Pill -->
    <g transform="translate(1010, 20)">
        <rect x="0" y="0" width="135" height="22" rx="11" fill="{card_bg}" stroke="{border_color}" stroke-width="1" />
        <circle cx="14" cy="11" r="4" fill="#EF4444" class="live-dot" />
        <text x="24" y="15" font-family="Consolas, monospace" font-size="11" fill="#EF4444" font-weight="700">LIVE</text>
        <text x="60" y="15" font-family="Consolas, monospace" font-size="11" fill="{border_color}" font-weight="600">@pranjal3872</text>
    </g>

    <!-- Left Box: VISUAL.MAP Frame -->
    <rect x="35" y="75" width="375" height="500" rx="8" fill="{bg_color}" stroke="{border_color}" stroke-width="1" stroke-dasharray="4 4" />
    <text x="50" y="98" font-family="Consolas, monospace" font-size="12" fill="{border_color}" font-weight="700" letter-spacing="1">VISUAL.MAP // PORTRAIT DITHER</text>
    <text x="390" y="98" font-family="Consolas, monospace" font-size="11" fill="{dim_text}" text-anchor="end">200x225 GRID</text>
    <line x1="35" y1="110" x2="410" y2="110" stroke="{border_color}" stroke-width="0.7" opacity="0.5" />

    <!-- Dithered Portrait Dots (Chunked Paths) -->
    <g>
        {path_xml}
    </g>

    <!-- Right Box: SYSTEM.INFO Readout -->
    <rect x="425" y="75" width="720" height="500" rx="8" fill="{bg_color}" stroke="{border_color}" stroke-width="1" />
    <text x="440" y="98" font-family="Consolas, monospace" font-size="12" fill="{accent_color}" font-weight="700" letter-spacing="1">SYSTEM.INFO // CANDIDATE SPECIFICATION</text>
    <text x="1130" y="98" font-family="Consolas, monospace" font-size="11" fill="{dim_text}" text-anchor="end">STATUS: ACTIVE</text>
    <line x1="425" y1="110" x2="1145" y2="110" stroke="{border_color}" stroke-width="0.7" opacity="0.5" />

    <!-- Info Lines -->
    {info_panel_str}

    <!-- Terminal Footer -->
    <rect x="440" y="535" width="690" height="28" rx="4" fill="{card_bg}" opacity="0.7" />
    <text x="450" y="554" font-family="Consolas, monospace" font-size="12" fill="{accent_color}">
        $ <tspan fill="{text_color}">cat experience.log | grep "Mobcoder Intern"</tspan> <tspan fill="{border_color}" class="live-dot">█</tspan>
    </text>

</svg>"""

    file_name = "dark.svg" if dark_mode else "light.svg"
    with open(file_name, "w", encoding="utf-8") as f:
        f.write(svg_content)
    print(f"Successfully created {file_name}!")

if __name__ == "__main__":
    generate_svg(dark_mode=True)
    generate_svg(dark_mode=False)
