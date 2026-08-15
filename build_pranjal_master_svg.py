import os
import sys
import math
import random
import numpy as np
from PIL import Image, ImageEnhance, ImageOps, ImageFilter
from scipy.spatial.distance import cdist
from scipy.optimize import linear_sum_assignment

print("Generating Master SVG & High-Definition Animation for Pranjal Shukla...")

def process_portrait(image_path, target_w=300, target_h=340, dark_mode=True):
    img = Image.open(image_path).convert("RGB")
    w, h = img.size
    
    crop_box = (int(w * 0.08), int(h * 0.04), int(w * 0.92), int(h * 0.92))
    cropped = img.crop(crop_box)
    
    resized = cropped.resize((target_w, target_h), Image.Resampling.LANCZOS)
    gray = resized.convert("L")
    
    auto_gray = ImageOps.autocontrast(gray, cutoff=1)
    sharp_gray = auto_gray.filter(ImageFilter.UnsharpMask(radius=3, percent=140))
    enhancer = ImageEnhance.Contrast(sharp_gray)
    contrasted = enhancer.enhance(1.3)
    
    arr = np.array(contrasted, dtype=float)
    subject_mask = (arr < 225)
    
    img_data = arr.copy()
    dots = []
    
    for y in range(target_h):
        serpentine = (y % 2 == 1)
        x_indices = range(target_w - 1, -1, -1) if serpentine else range(target_w)
        direction = -1 if serpentine else 1
        
        for x in x_indices:
            old_val = img_data[y, x]
            
            if dark_mode:
                new_val = 255 if old_val > 110 else 0
                if not subject_mask[y, x]:
                    new_val = 0
                is_dot = (new_val == 255)
            else:
                new_val = 0 if old_val < 135 else 255
                is_dot = (new_val == 0)
                
            err = old_val - new_val
            
            if is_dot:
                px = 45 + (x / target_w) * 340
                py = 125 + (y / target_h) * 430
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

def generate_python_logo_points(num_points=900, cx=215, cy=340, scale=110):
    pts = []
    for t in np.linspace(0, 2*np.pi, num_points // 2):
        r = scale * (0.6 + 0.25 * np.cos(2*t))
        pts.append((cx + r * np.cos(t) - 15, cy + r * np.sin(t) - 25))
    for t in np.linspace(0, 2*np.pi, num_points // 2):
        r = scale * (0.6 + 0.25 * np.sin(2*t))
        pts.append((cx + r * np.cos(t) + 15, cy + r * np.sin(t) + 25))
    return np.array(pts[:num_points])

def generate_react_logo_points(num_points=900, cx=215, cy=340, rx=110, ry=42):
    pts = []
    for t in np.linspace(0, 2*np.pi, 150):
        pts.append((cx + 22 * np.cos(t), cy + 22 * np.sin(t)))
    angles = [0, math.pi/3, 2*math.pi/3]
    pts_per_orbit = (num_points - 150) // 3
    for angle in angles:
        for t in np.linspace(0, 2*np.pi, pts_per_orbit):
            ex = rx * math.cos(t)
            ey = ry * math.sin(t)
            pts.append((cx + ex * math.cos(angle) - ey * math.sin(angle), cy + ex * math.sin(angle) + ey * math.cos(angle)))
    return np.array(pts[:num_points])

def generate_code_glyph_points(num_points=900, cx=215, cy=340):
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

def match_optimal_transport(source_pts, target_pts):
    cost_matrix = cdist(source_pts, target_pts, metric='euclidean')
    row_ind, col_ind = linear_sum_assignment(cost_matrix)
    return target_pts[col_ind]

def generate_master_svg(image_path, dark_mode=True, output_filename="dark.svg", handle="pranjal3872"):
    mode_str = "dark" if dark_mode else "light"
    bg_color = "#0A101F" if dark_mode else "#F8FAFC"
    border_color = "#22D3EE" if dark_mode else "#0891B2"
    text_color = "#E2E8F0" if dark_mode else "#0F172A"
    dim_text = "#94A3B8" if dark_mode else "#64748B"
    portrait_dot_color = "#A78BFA" if dark_mode else "#7C3AED"
    traveller_color = "#10B981"
    accent_color = "#10B981"
    card_bg = "#1E293B" if dark_mode else "#E2E8F0"

    portrait_dots = process_portrait(image_path, dark_mode=dark_mode)
    num_portrait = len(portrait_dots)

    np.random.seed(42)
    noisy_portrait = portrait_dots + np.random.normal(0, 4.0, portrait_dots.shape)
    y_coords = noisy_portrait[:, 1]
    band_assignments = np.digitize(y_coords, np.linspace(125, 555, 94))

    sample_indices = np.random.choice(num_portrait, size=min(900, num_portrait), replace=False)
    travellers_p0 = portrait_dots[sample_indices].copy()

    logo1 = generate_python_logo_points(num_points=len(travellers_p0))
    logo2 = generate_react_logo_points(num_points=len(travellers_p0))
    logo3 = generate_code_glyph_points(num_points=len(travellers_p0))

    travellers_l1 = match_optimal_transport(travellers_p0, logo1)
    travellers_l2 = match_optimal_transport(travellers_l1, logo2)
    travellers_l3 = match_optimal_transport(travellers_l2, logo3)

    intro_groups = []
    num_intro = 60
    shuffled_indices = list(range(num_portrait))
    random.seed(42)
    random.shuffle(shuffled_indices)
    
    group_size = int(math.ceil(num_portrait / num_intro))
    for g_i in range(num_intro):
        g_pts = portrait_dots[shuffled_indices[g_i*group_size : (g_i+1)*group_size]]
        if len(g_pts) == 0:
            continue
        path_d = " ".join([f"M{round(x,1)},{round(y,1)}h1.8v1.8h-1.8z" for x, y in g_pts])
        begin_delay = round((g_i / num_intro) * 1.8, 2)
        intro_groups.append(f'''
        <path d="{path_d}" fill="{portrait_dot_color}" opacity="0" shape-rendering="crispEdges">
            <animate attributeName="opacity" values="0;1" dur="0.4s" begin="{begin_delay}s" fill="freeze" />
        </path>''')

    intro_xml = "\n".join(intro_groups)

    traveller_paths = []
    for t_i in range(len(travellers_p0)):
        x0, y0 = travellers_p0[t_i]
        x1, y1 = travellers_l1[t_i]
        x2, y2 = travellers_l2[t_i]
        x3, y3 = travellers_l3[t_i]

        d_p0 = f"M{round(x0,1)},{round(y0,1)}h2.2v2.2h-2.2z"
        d_l1 = f"M{round(x1,1)},{round(y1,1)}h2.2v2.2h-2.2z"
        d_l2 = f"M{round(x2,1)},{round(y2,1)}h2.2v2.2h-2.2z"
        d_l3 = f"M{round(x3,1)},{round(y3,1)}h2.2v2.2h-2.2z"

        path_values = f"{d_p0}; {d_p0}; {d_l1}; {d_l1}; {d_l2}; {d_l2}; {d_l3}; {d_l3}; {d_p0}"
        opacity_values = "0; 0; 1; 1; 1; 1; 1; 1; 0"
        key_times = "0; 0.211; 0.303; 0.444; 0.535; 0.676; 0.768; 0.908; 1.0"

        traveller_paths.append(f'''
        <path d="{d_p0}" fill="{traveller_color}" opacity="0" shape-rendering="crispEdges">
            <animate attributeName="d" values="{path_values}" keyTimes="{key_times}" dur="14.2s" begin="3.2s" repeatCount="indefinite" />
            <animate attributeName="opacity" values="{opacity_values}" keyTimes="{key_times}" dur="14.2s" begin="3.2s" repeatCount="indefinite" />
        </path>''')

    travellers_xml = "\n".join(traveller_paths[::2])

    rows = [
        ("Subject", "Pranjal Shukla"),
        ("Role", "Software Engineer (AI & Full-Stack)"),
        ("Origin", "Ghaziabad, UP, India"),
        ("Education", "B.Tech CSE, AKGEC (2023 - 2027)"),
        ("Status", "Building RAG & AI Agents @ Mobcoder"),
        ("ToolChain", "VS Code · Git · Docker · Qdrant"),
        ("Core.Lang", "Java · Python · JavaScript · SQL · C++"),
        ("Core.Frontend", "React.js · HTML5/CSS3 · Bootstrap"),
        ("Core.Backend", "Node.js · Express.js · Spring Boot · FastAPI"),
        ("Core.Database", "MongoDB · PostgreSQL · Qdrant Vector DB"),
        ("Core.Infra", "LangChain · LangGraph · RAG · Groq"),
        ("Grid.Mail", "3872pranjalshukla@gmail.com"),
        ("Grid.LinkedIn", "in/pranjal3872"),
        ("Grid.GitHub", handle)
    ]

    info_xml = []
    start_y = 150
    line_height = 27

    for i, (label, val) in enumerate(rows):
        cur_y = start_y + (i * line_height)
        dot_leader = "." * max(4, int(42 - len(label) - len(val) * 0.8))
        
        row_str = f'''
        <text x="440" y="{cur_y}" font-family="Consolas, Monaco, monospace" font-size="14" fill="{dim_text}" textLength="280" lengthAdjust="spacingAndGlyphs">
            <tspan fill="{border_color}" font-weight="600">{label}</tspan>
            <tspan fill="{dim_text}" dx="6">{dot_leader}</tspan>
        </text>
        <text x="1125" y="{cur_y}" font-family="Consolas, Monaco, monospace" font-size="14" fill="{text_color}" font-weight="500" text-anchor="end" textLength="260" lengthAdjust="spacingAndGlyphs">{val}</text>'''
        info_xml.append(row_str)

    info_panel_str = "\n".join(info_xml)

    svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1180 610" width="100%" height="100%">
    <defs>
        <style>
            @keyframes pulse {{
                0% {{ opacity: 1; }}
                50% {{ opacity: 0.3; }}
                100% {{ opacity: 1; }}
            }}
            .live-dot {{ animation: pulse 2s infinite ease-in-out; }}
        </style>
        <linearGradient id="panelGrad_{mode_str}" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stop-color="{bg_color}" />
            <stop offset="100%" stop-color="{card_bg}" />
        </linearGradient>
    </defs>

    <rect x="10" y="10" width="1160" height="590" rx="12" fill="url(#panelGrad_{mode_str})" stroke="{border_color}" stroke-width="1.5" />

    <path d="M 10,22 A 12,12 0 0,1 22,10 L 1158,10 A 12,12 0 0,1 1170,22 L 1170,50 L 10,50 Z" fill="{card_bg}" stroke="{border_color}" stroke-width="1" />
    
    <circle cx="35" cy="30" r="6" fill="#EF4444" />
    <circle cx="55" cy="30" r="6" fill="#F59E0B" />
    <circle cx="75" cy="30" r="6" fill="#10B981" />

    <text x="590" y="34" font-family="Consolas, Monaco, monospace" font-size="14" fill="{dim_text}" text-anchor="middle" font-weight="600">profile.sh --live</text>

    <g transform="translate(1005, 20)">
        <rect x="0" y="0" width="145" height="22" rx="11" fill="{card_bg}" stroke="{border_color}" stroke-width="1" />
        <circle cx="14" cy="11" r="4" fill="#EF4444" class="live-dot" />
        <text x="24" y="15" font-family="Consolas, monospace" font-size="12" fill="#EF4444" font-weight="700">LIVE</text>
        <text x="60" y="15" font-family="Consolas, monospace" font-size="14" fill="{border_color}" font-weight="600">@{handle}</text>
    </g>

    <rect x="35" y="75" width="375" height="500" rx="8" fill="{bg_color}" stroke="{border_color}" stroke-width="1" stroke-dasharray="4 4" />
    <text x="50" y="98" font-family="Consolas, monospace" font-size="13" fill="{border_color}" font-weight="700" letter-spacing="1">VISUAL.MAP // PORTRAIT DITHER</text>
    <text x="390" y="98" font-family="Consolas, monospace" font-size="11" fill="{dim_text}" text-anchor="end">300x340 GRID</text>
    <line x1="35" y1="110" x2="410" y2="110" stroke="{border_color}" stroke-width="0.7" opacity="0.5" />

    <g>
        {intro_xml}
    </g>

    <g>
        {travellers_xml}
    </g>

    <rect x="425" y="75" width="720" height="500" rx="8" fill="{bg_color}" stroke="{border_color}" stroke-width="1" />
    <text x="440" y="98" font-family="Consolas, monospace" font-size="13" fill="{accent_color}" font-weight="700" letter-spacing="1">SYSTEM.INFO // CANDIDATE SPECIFICATION</text>
    <text x="1130" y="98" font-family="Consolas, monospace" font-size="11" fill="{dim_text}" text-anchor="end">STATUS: ACTIVE</text>
    <line x1="425" y1="110" x2="1145" y2="110" stroke="{border_color}" stroke-width="0.7" opacity="0.5" />

    {info_panel_str}

    <rect x="440" y="535" width="690" height="28" rx="4" fill="{card_bg}" opacity="0.7" />
    <text x="450" y="554" font-family="Consolas, monospace" font-size="13" fill="{accent_color}">
        $ <tspan fill="{text_color}">cat experience.log | grep "Mobcoder Intern"</tspan> <tspan fill="{border_color}" class="live-dot">█</tspan>
    </text>

</svg>'''

    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(svg_content)
    print(f"Master Pure SVG generated: {output_filename}")

if __name__ == "__main__":
    pranjal_photo = r"c:\Users\3872p\Documents\antigravity\cool-carson\PROFILE2.png"
    generate_master_svg(pranjal_photo, dark_mode=True, output_filename=r"c:\Users\3872p\Documents\antigravity\cool-carson\dark.svg", handle="pranjal3872")
    generate_master_svg(pranjal_photo, dark_mode=False, output_filename=r"c:\Users\3872p\Documents\antigravity\cool-carson\light.svg", handle="pranjal3872")
