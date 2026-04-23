from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os

def create_bot_avatar_exact_copy():
    # Fayl manzillari
    input_path = r"C:\Users\MSH\.gemini\antigravity\scratch\telegram_bot_orders\webapp\assets\logo.png"
    output_path = r"C:\Users\MSH\Desktop\UPLOAD_TO_GITHUB\bot_avatar.png"
    
    # Rasmni ochish
    img = Image.open(input_path).convert("RGBA")
    width, height = img.size
    
    # Alohida qatlam soya uchun (blur effektini berish uchun)
    shadow_layer = Image.new("RGBA", img.size, (0,0,0,0))
    sd = ImageDraw.Draw(shadow_layer)
    
    # Shriftni yuklash (Arial Bold - skrinshotdagiga juda yaqin)
    font_path = r"C:\Windows\Fonts\arialbd.ttf"
    font_size = 125 # O'lchamni rasmga qarab mosladik
    if os.path.exists(font_path):
        font = ImageFont.truetype(font_path, font_size)
    else:
        font = ImageFont.load_default()
    
    text = "SAXOVAT BARAKA"
    spacing = 2 # Harflar orasidagi masofa
    
    # Umumiy o'lchamni hisoblash
    total_width = 0
    for char in text:
        bbox = sd.textbbox((0, 0), char, font=font)
        total_width += (bbox[2] - bbox[0]) + spacing
    total_width -= spacing
    
    x = (width - total_width) / 2
    y = 665 # Aynan boshoqlar ustiga tushadigan pozitsiya
    
    # 1. TO'Q SOYA (Drop shadow)
    # Soya yozuvdan bir oz pastroqda va o'ngroqda
    shadow_offset_x = 0
    shadow_offset_y = 5
    current_x = x
    for char in text:
        sd.text((current_x + shadow_offset_x, y + shadow_offset_y), char, font=font, fill=(40, 30, 20, 180)) 
        bbox = sd.textbbox((0, 0), char, font=font)
        current_x += (bbox[2] - bbox[0]) + spacing
    
    # Soyani juda ozgina blur qilish (tabiiy chiqishi uchun)
    shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(radius=3))
    
    # 2. TOZA OQ MATN
    txt_layer = Image.new("RGBA", img.size, (0,0,0,0))
    td = ImageDraw.Draw(txt_layer)
    current_x = x
    for char in text:
        td.text((current_x, y), char, font=font, fill=(255, 255, 255, 255)) 
        bbox = td.textbbox((0, 0), char, font=font)
        current_x += (bbox[2] - bbox[0]) + spacing
    
    # Qatlamlarni birlashtirish: Fon + Soya + Oq Matn
    final_img = Image.alpha_composite(img, shadow_layer)
    final_img = Image.alpha_composite(final_img, txt_layer)
    
    # Saqlash
    final_img = final_img.convert("RGB")
    final_img.save(output_path, "PNG")
    print(f"To'liq nusxa (exact copy) yaratildi: {output_path}")

if __name__ == "__main__":
    create_bot_avatar_exact_copy()
