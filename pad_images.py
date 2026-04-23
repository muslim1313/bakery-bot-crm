import os
from PIL import Image

def pad_image(img_path):
    try:
        img = Image.open(img_path).convert("RGBA")
    except Exception as e:
        print(f"Error opening {img_path}: {e}")
        return
        
    # Get the background color from top-left corner
    border_color = img.getpixel((5, 5))
    w, h = img.size
    
    # Increase canvas size by 45% to create a generous padding (zooms out the cookie)
    pad_w = int(w * 0.45)
    pad_h = int(h * 0.45)
    
    new_w = w + pad_w
    new_h = h + pad_h
    
    # Create new blank canvas with the background color
    new_img = Image.new("RGBA", (new_w, new_h), border_color)
    
    # Paste the original image exactly in the center
    new_img.paste(img, (pad_w // 2, pad_h // 2))
    
    # Overwrite the file
    new_img.save(img_path)
    print(f"Padded successfully: {img_path}")

# Hamma 6 ta rasmni kengaytirib, uzog'roqdan ko'rinadigan qilamiz
assets_dir = r"C:\Users\MSH\.gemini\antigravity\scratch\telegram_bot_orders\webapp\assets"
imgs = ['real1_2.png', 'real1_3.png', 'real2_1.png', 'real2_2.png', 'real2_3.png', 'real2_4.png']

desktop_dir = r"C:\Users\MSH\Desktop\Pecheniy_Namunalar\AI_version"

for name in imgs:
    pad_image(os.path.join(assets_dir, name))
    try:
        pad_image(os.path.join(desktop_dir, name))
    except:
        pass

print("Rasmlar muvaffaqiyatli 'zoom out' (kichraytirish) qilindi!")
