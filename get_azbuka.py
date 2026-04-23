import os
import numpy as np
from PIL import Image, ImageFilter

brain_dir = r"C:\Users\MSH\.gemini\antigravity\brain\b101f534-aa4a-4f8c-b34b-c53225e78601"
img1_path = os.path.join(brain_dir, "media__1775927166764.jpg")
out_dir = r"C:\Users\MSH\.gemini\antigravity\scratch\telegram_bot_orders\webapp\assets"

def get_azbuka():
    img = Image.open(img1_path).convert("RGBA")
    w, h = img.size
    
    # It's the 3rd slice (index 2) of the 3-slice image
    slice_h = h // 3
    
    # We want it wider to not cut off letters, perhaps text is far on the right.
    # Let's crop up to 60% of width.
    box = (10, 2 * slice_h + 10, int(w * 0.65), 3 * slice_h - 10)
    block = img.crop(box)
    
    arr = np.array(block)
    
    bg_color = arr[5, 5, :3].astype(int)
    diff = np.abs(arr[:, :, :3] - bg_color)
    t_dist = np.sum(diff, axis=-1)
    
    alpha = np.where(t_dist > 50, 255, 0).astype(np.uint8)
    
    mask_img = Image.fromarray(alpha, 'L').filter(ImageFilter.GaussianBlur(1))
    alpha_smooth = np.where(np.array(mask_img) > 60, 255, 0).astype(np.uint8)
    arr[:, :, 3] = alpha_smooth
    
    rows = np.any(alpha_smooth, axis=1)
    cols = np.any(alpha_smooth, axis=0)
    
    if np.any(rows):
        rmin, rmax = np.where(rows)[0][[0, -1]]
        cmin, cmax = np.where(cols)[0][[0, -1]]
        cookie_arr = arr[rmin:rmax, cmin:cmax]
        out_img = Image.fromarray(cookie_arr, 'RGBA')
        
        out_path = os.path.join(out_dir, "real1_3.png")
        out_img.save(out_path)
        print("Azbuka saved fully.")

get_azbuka()
