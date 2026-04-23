import os
import numpy as np
from PIL import Image, ImageFilter

def extract_cookies(img_path, num_slices, prefix, out_dir):
    try:
        img = Image.open(img_path).convert("RGBA")
    except Exception as e:
        print(f"Failed to open {img_path}: {e}")
        return []
        
    w, h = img.size
    slice_h = h // num_slices
    
    saved_paths = []
    
    for i in range(num_slices):
        box = (0, i * slice_h, int(w * 0.6), (i + 1) * slice_h)
        block = img.crop(box)
        
        arr = np.array(block)
        
        # bg_color can be sampled from the top corners
        bg_color1 = arr[5, 5, :3].astype(int)
        bg_color2 = arr[5, -5, :3].astype(int)
        bg_color = (bg_color1 + bg_color2) / 2
        
        diff = np.abs(arr[:, :, :3] - bg_color)
        t_dist = np.sum(diff, axis=-1)
        
        tolerance = 85
        alpha = np.where(t_dist > tolerance, 255, 0).astype(np.uint8)
        
        # Smoothing alpha mask using PIL
        mask_img = Image.fromarray(alpha, 'L')
        # Fill holes heuristically (simple morphological approach using blur/threshold)
        mask_img = mask_img.filter(ImageFilter.GaussianBlur(3))
        mask_arr = np.array(mask_img)
        alpha_smooth = np.where(mask_arr > 50, 255, 0).astype(np.uint8)
        
        arr[:, :, 3] = alpha_smooth
        
        rows = np.any(alpha_smooth, axis=1)
        cols = np.any(alpha_smooth, axis=0)
        if not np.any(rows):
            rmin, rmax = 0, alpha_smooth.shape[0]
            cmin, cmax = 0, alpha_smooth.shape[1]
        else:
            rmin, rmax = np.where(rows)[0][[0, -1]]
            cmin, cmax = np.where(cols)[0][[0, -1]]
            
        pad = 10
        rmin = max(0, rmin - pad)
        rmax = min(alpha_smooth.shape[0], rmax + pad)
        cmin = max(0, cmin - pad)
        cmax = min(alpha_smooth.shape[1], cmax + pad)
        
        cookie_arr = arr[rmin:rmax, cmin:cmax]
        out_img = Image.fromarray(cookie_arr, 'RGBA')
        
        out_path = os.path.join(out_dir, f"{prefix}_{i+1}.png")
        out_img.save(out_path)
        saved_paths.append(out_path)
        
    return saved_paths

brain_dir = r"C:\Users\MSH\.gemini\antigravity\brain\b101f534-aa4a-4f8c-b34b-c53225e78601"
img1_path = os.path.join(brain_dir, "media__1775927166764.jpg")
img2_path = os.path.join(brain_dir, "media__1775927166795.jpg")
out_dir = r"C:\Users\MSH\.gemini\antigravity\scratch\telegram_bot_orders\webapp\assets"

os.makedirs(out_dir, exist_ok=True)
p1 = extract_cookies(img1_path, 3, "real1", out_dir)
p2 = extract_cookies(img2_path, 5, "real2", out_dir)

print("Generated:")
for p in p1 + p2:
    print(p)
