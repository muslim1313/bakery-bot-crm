import os
import glob
from PIL import Image, ImageDraw, ImageFilter

brain_dir = r"C:\Users\MSH\.gemini\antigravity\brain\b101f534-aa4a-4f8c-b34b-c53225e78601"
assets_dir = r"C:\Users\MSH\.gemini\antigravity\scratch\telegram_bot_orders\webapp\assets"

mapping = {
    "ai_popcorn_*.png": "real1_2.png",
    "ai_azbuka_*.png": "real1_3.png",
    "ai_yubi_*.png": "real2_1.png",
    "ai_toplyonoe_*.png": "real2_2.png",
    "ai_olmali_*.png": "real2_3.png",
    "ai_yulduz_*.png": "real2_4.png",
}

needs_zoom_out = ["real1_2.png", "real1_3.png", "real2_1.png"]

for pattern, out_name in mapping.items():
    matched = glob.glob(os.path.join(brain_dir, pattern))
    if not matched:
        continue
    img_path = matched[0]
    
    img = Image.open(img_path).convert("RGBA")
    w, h = img.size
    
    if out_name in needs_zoom_out:
        # Shrink the cookie
        shrink_ratio = 0.65
        new_w = int(w * shrink_ratio)
        new_h = int(h * shrink_ratio)
        
        shrunk = img.resize((new_w, new_h), Image.LANCZOS)
        
        # Create a radial mask to softly blend the edges of the shrunken image
        mask = Image.new("L", (new_w, new_h), 0)
        draw = ImageDraw.Draw(mask)
        # Inner solid area
        margin = int(new_w * 0.15)
        draw.ellipse((margin, margin, new_w - margin, new_h - margin), fill=255)
        # Soft feather edge
        mask = mask.filter(ImageFilter.GaussianBlur(new_w * 0.1))
        
        shrunk.putalpha(mask)
        
        # Paste softly onto the ORIGINAL AI image (which acts as the perfect background)
        final_img = img.copy()
        offset_x = (w - new_w) // 2
        offset_y = (h - new_h) // 2
        final_img.paste(shrunk, (offset_x, offset_y), mask)
    else:
        # Just use original for others
        final_img = img

    # Restore alpha to standard RGB if needed, or keep RGBA
    out_path = os.path.join(assets_dir, out_name)
    final_img.save(out_path)
    
    desk_path = os.path.join(r"C:\Users\MSH\Desktop\Pecheniy_Namunalar\AI_version", out_name)
    try:
        final_img.save(desk_path)
    except:
        pass

print("Rasmlar mukammal tiklandi va faqat keraklilari ota silliq qilib kichraytirildi!")
