from PIL import Image, ImageDraw, ImageFont
import os

def add_text_to_logo():
    # Fayl manzillari
    input_path = r"C:\Users\MSH\.gemini\antigravity\scratch\telegram_bot_orders\webapp\assets\logo.png"
    output_path = r"C:\Users\MSH\Desktop\UPLOAD_TO_GITHUB\logo.png"
    
    # Rasmni ochish
    img = Image.open(input_path).convert("RGBA")
    width, height = img.size
    
    # Draw obyektini yaratish
    draw = ImageDraw.Draw(img)
    
    # Shriftni yuklash (Windows tizimidagi Arial Bold ishlatamiz)
    font_path = r"C:\Windows\Fonts\arialbd.ttf"
    if not os.path.exists(font_path):
        # Agar Arial topilmasa, default shrift
        font_size = 80
        font = ImageFont.load_default()
    else:
        font_size = 90
        font = ImageFont.truetype(font_path, font_size)
    
    text = "SAXOVAT BARAKA"
    
    # Matn o'lchamini hisoblash
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Pozitsiya: Pastdan bir oz teparoqda, markazda
    x = (width - text_width) / 2
    y = height - text_height - 100
    
    # Soyasini qo'shish (App-dagi shadow kabi)
    shadow_offset = 4
    shadow_color = (0, 0, 0, 100) # Yarim shaffof qora
    draw.text((x + shadow_offset, y + shadow_offset), text, font=font, fill=shadow_color)
    
    # Asosiy matn (Tilla-to'q rang yoki ilovadagi kabi to'q rang)
    # Logo o'zi tilla rangda bo'lgani uchun, yozuvni ham unga moslab to'qroq qo'ng'ir-tilla qilamiz
    text_color = (130, 85, 30, 255) # To'q jigar rang (logo bilan uyg'un)
    
    draw.text((x, y), text, font=font, fill=text_color)
    
    # RGB formatiga qaytarib saqlash (PNG uchun)
    img = img.convert("RGB")
    img.save(output_path, "PNG")
    print(f"Rasm muvaffaqiyatli saqlandi: {output_path}")

if __name__ == "__main__":
    add_text_to_logo()
