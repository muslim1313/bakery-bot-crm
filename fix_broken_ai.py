import os
from PIL import Image, ImageDraw, ImageFilter

assets_dir = r"C:\Users\MSH\.gemini\antigravity\scratch\telegram_bot_orders\webapp\assets"

def create_olmali_composite(cookie_filename, out_filename):
    cookie_path = os.path.join(assets_dir, cookie_filename)
    
    try:
        cookie = Image.open(cookie_path).convert("RGBA")
    except Exception as e:
        print(f"Error opening {cookie_path}: {e}")
        return
        
    # Create 1024x1024 premium slate background
    W, H = 1024, 1024
    bg = Image.new("RGBA", (W, H), (15, 23, 42, 255)) # #0f172a (dark slate baseline)
    
    # Create a soft spotlight in the center (simulating the studio lighting of Olmali theme)
    light = Image.new("RGBA", (W, H), (0,0,0,0))
    draw = ImageDraw.Draw(light)
    radius = int(W * 0.45)
    draw.ellipse((W//2 - radius, H//2 - radius, W//2 + radius, H//2 + radius), fill=(35, 45, 65, 255))
    
    # High gaussian blur to make the spotlight hyper-realistic and seamless
    light = light.filter(ImageFilter.GaussianBlur(120))
    bg.alpha_composite(light)
    
    # Resize cookie to be elegantly zoomed out.
    cw, ch = cookie.size
    scale = (H * 0.55) / max(ch, cw)
    new_cw, new_ch = int(cw * scale), int(ch * scale)
    shrunk_cookie = cookie.resize((new_cw, new_ch), Image.LANCZOS)
    
    offset_x = (W - new_cw) // 2
    offset_y = (H - new_ch) // 2
    
    # Paste cookie centered using its transparent mask
    bg.paste(shrunk_cookie, (offset_x, offset_y), shrunk_cookie)
    
    out_path = os.path.join(assets_dir, out_filename)
    bg.save(out_path)
    print("Saved beautiful studio composite to", out_path)
    
    # Provide to desktop as well
    desktop_dir = r"C:\Users\MSH\Desktop\Pecheniy_Namunalar\AI_Final_Olmali_Theme"
    try:
        bg.save(os.path.join(desktop_dir, out_filename))
    except:
        pass

create_olmali_composite("popcorn_clean_base.png", "real1_2.png")
create_olmali_composite("yubi_clean_base.png", "real2_1.png")
