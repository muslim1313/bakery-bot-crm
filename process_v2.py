import os
import numpy as np
from PIL import Image, ImageFilter

def get_tight_crop(img_path, num_slices, prefix, out_dir, desktop_dir):
    try:
        img = Image.open(img_path).convert("RGBA")
    except Exception as e:
        print(f"Error {e}")
        return
        
    w, h = img.size
    slice_h = h // num_slices
    
    for i in range(num_slices):
        img_name = f"{prefix}_{i+1}"
        requested = ['real1_2', 'real1_3', 'real2_1', 'real2_2', 'real2_3', 'real2_4']
        if img_name not in requested:
            continue
            
        # VERY TIGHT CROP ON THE LEFT SIDE TO AVOID ALL TEXT
        left_bound = 10
        # Cookie is on the left, let's limit width to strictly a square based on slice_h, 
        # or max 35% of the total width to guarantee no text.
        right_bound = int(min(slice_h * 1.5, w * 0.40)) 
        top_bound = i * slice_h + 10
        bottom_bound = (i + 1) * slice_h - 10
        
        box = (left_bound, top_bound, right_bound, bottom_bound)
        block = img.crop(box)
        
        arr = np.array(block)
        
        bg_color1 = arr[5, 5, :3].astype(int)
        bg_color2 = arr[-5, 5, :3].astype(int)
        bg_color = (bg_color1 + bg_color2) / 2
        
        diff = np.abs(arr[:, :, :3] - bg_color)
        t_dist = np.sum(diff, axis=-1)
        
        tolerance = 65
        alpha = np.where(t_dist > tolerance, 255, 0).astype(np.uint8)
        
        # Smooth alpha
        mask_img = Image.fromarray(alpha, 'L').filter(ImageFilter.GaussianBlur(2))
        alpha_smooth = np.where(np.array(mask_img) > 60, 255, 0).astype(np.uint8)
        arr[:, :, 3] = alpha_smooth
        
        rows = np.any(alpha_smooth, axis=1)
        cols = np.any(alpha_smooth, axis=0)
        if not np.any(rows):
            rmin, rmax = 0, alpha_smooth.shape[0]
            cmin, cmax = 0, alpha_smooth.shape[1]
        else:
            rmin, rmax = np.where(rows)[0][[0, -1]]
            cmin, cmax = np.where(cols)[0][[0, -1]]
            
        cookie_arr = arr[rmin:rmax, cmin:cmax]
        out_img = Image.fromarray(cookie_arr, 'RGBA')
        
        assets_out = os.path.join(out_dir, f"{img_name}.png")
        desktop_out = os.path.join(desktop_dir, f"{img_name}.png")
        
        out_img.save(assets_out)
        out_img.save(desktop_out)

brain_dir = r"C:\Users\MSH\.gemini\antigravity\brain\b101f534-aa4a-4f8c-b34b-c53225e78601"
img1_path = os.path.join(brain_dir, "media__1775927166764.jpg")
img2_path = os.path.join(brain_dir, "media__1775927166795.jpg")
out_dir = r"C:\Users\MSH\.gemini\antigravity\scratch\telegram_bot_orders\webapp\assets"
desktop_dir = r"C:\Users\MSH\Desktop\Pecheniy_Namunalar"

os.makedirs(out_dir, exist_ok=True)
get_tight_crop(img1_path, 3, "real1", out_dir, desktop_dir)
get_tight_crop(img2_path, 5, "real2", out_dir, desktop_dir)

print("Images tightly cropped and saved!")
