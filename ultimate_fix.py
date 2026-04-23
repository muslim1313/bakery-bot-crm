import os
import glob
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import shutil

brain_dir = r"C:\Users\MSH\.gemini\antigravity\brain\b101f534-aa4a-4f8c-b34b-c53225e78601"
assets_dir = r"C:\Users\MSH\.gemini\antigravity\scratch\telegram_bot_orders\webapp\assets"
desktop_dir = r"C:\Users\MSH\Desktop\Pecheniy_Namunalar\AI_Final_Olmali_Theme"

os.makedirs(assets_dir, exist_ok=True)
os.makedirs(desktop_dir, exist_ok=True)

# Restore the 4 PERFECT ones immediately so they are exactly what the user liked.
good_ones = {
    "ai2_azbuka_*.png": "real1_3.png",
    "ai2_toplyonoe_*.png": "real2_2.png",
    "ai2_olmali_*.png": "real2_3.png",
    "ai2_yulduz_*.png": "real2_4.png",
}
for pat, out_name in good_ones.items():
    src = glob.glob(os.path.join(brain_dir, pat))[0]
    shutil.copy(src, os.path.join(assets_dir, out_name))
    shutil.copy(src, os.path.join(desktop_dir, out_name))

# Fix the 2 broken ones by extracting from pristine FIRST GENERATION and pasting into an empty Olmali-styled backdrop!
olmali_path = glob.glob(os.path.join(brain_dir, "ai2_olmali_*.png"))[0]
olmali_bg = Image.open(olmali_path).convert("RGBA")
w, h = olmali_bg.size

# Erase the apple cookie from the center by drawing a circle of the dark corner color
d = ImageDraw.Draw(olmali_bg)
edge_col = olmali_bg.getpixel((0,0))
radius = int(w * 0.35)
d.ellipse((w//2 - radius, h//2 - radius, w//2 + radius, h//2 + radius), fill=edge_col)

# Apply massive blur to smooth the erased area into a pristine flawless gradient matching the other photos!
empty_backdrop = olmali_bg.filter(ImageFilter.GaussianBlur(120))

def fix_cookie_composite(original_ai_pattern, out_name):
    # Load pristine first generation!
    src_cookie = glob.glob(os.path.join(brain_dir, original_ai_pattern))[0]
    img = Image.open(src_cookie).convert("RGBA")
    arr = np.array(img)
    
    # Extract
    bg_color = arr[10, 10, :3].astype(int)
    diff = np.abs(arr[:, :, :3] - bg_color)
    t_dist = np.sum(diff, axis=-1)
    
    # Very tight and accurate tolerance
    alpha = np.where(t_dist > 30, 255, 0).astype(np.uint8)
    mask = Image.fromarray(alpha, 'L').filter(ImageFilter.GaussianBlur(2))
    alpha_smooth = np.where(np.array(mask) > 50, 255, 0).astype(np.uint8)
    arr[:, :, 3] = alpha_smooth
    
    rows = np.any(alpha_smooth, axis=1)
    cols = np.any(alpha_smooth, axis=0)
    rmin, rmax = np.where(rows)[0][[0, -1]]
    cmin, cmax = np.where(cols)[0][[0, -1]]
    
    extracted = Image.fromarray(arr[rmin:rmax, cmin:cmax], 'RGBA')
    
    # Zoom out gracefully (e.g. 55% of canvas size)
    cw, ch = extracted.size
    scale = (h * 0.60) / max(cw, ch)
    new_cw, new_ch = int(cw * scale), int(ch * scale)
    shrunk_cookie = extracted.resize((new_cw, new_ch), Image.LANCZOS)
    
    offset_x = (w - new_cw) // 2
    offset_y = (h - new_ch) // 2
    
    # Paste into our pristine empty backdrop
    final_img = empty_backdrop.copy()
    final_img.paste(shrunk_cookie, (offset_x, offset_y), shrunk_cookie)
    
    final_img.save(os.path.join(assets_dir, out_name))
    final_img.save(os.path.join(desktop_dir, out_name))
    print(f"Successfully repaired and matched: {out_name}")

fix_cookie_composite("ai_popcorn_*.png", "real1_2.png")
fix_cookie_composite("ai_yubi_*.png", "real2_1.png")

print("BARCHASI MUKAMMAL TIKLANDI!")
