import os
import numpy as np
from PIL import Image

brain_dir = r"C:\Users\MSH\.gemini\antigravity\brain\b101f534-aa4a-4f8c-b34b-c53225e78601"
img1_path = os.path.join(brain_dir, "media__1775927166764.jpg")
img2_path = os.path.join(brain_dir, "media__1775927166795.jpg")
out_dir = r"C:\Users\MSH\.gemini\antigravity\scratch\telegram_bot_orders\webapp\assets"

def get_base(img_path, num_slices, index, out_name):
    img = Image.open(img_path).convert("RGBA")
    w, h = img.size
    slice_h = h // num_slices
    
    box = (10, index * slice_h + 10, int(w * 0.50), (index + 1) * slice_h - 10)
    block = img.crop(box)
    
    arr = np.array(block)
    bg_color = arr[5, 5, :3].astype(int)
    diff = np.abs(arr[:, :, :3] - bg_color)
    t_dist = np.sum(diff, axis=-1)
    
    alpha = np.where(t_dist > 50, 255, 0).astype(np.uint8)
    arr[:, :, 3] = alpha
    
    rows = np.any(alpha, axis=1)
    cols = np.any(alpha, axis=0)
    if np.any(rows):
        rmin, rmax = np.where(rows)[0][[0, -1]]
        cmin, cmax = np.where(cols)[0][[0, -1]]
        out_img = Image.fromarray(arr[rmin:rmax, cmin:cmax], 'RGBA')
        out_img.save(os.path.join(out_dir, out_name))
        print("Restored base:", out_name)

get_base(img1_path, 3, 1, "popcorn_clean_base.png") 
get_base(img2_path, 5, 0, "yubi_clean_base.png") 
