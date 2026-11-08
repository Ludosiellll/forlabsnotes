# -*- coding: utf-8 -*-
import os
from playwright.sync_api import sync_playwright
from PIL import Image, ImageDraw, ImageFont

WORK_DIR = r"d:\1с лабы\ПСИП_ЛР1_Файлы"

FONT_TAB = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 12)
FONT_URL = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 12)

def wrap_in_browser(content_img_path, output_path, tab_title, url_text):
    content_img = Image.open(content_img_path)
    cw, ch = content_img.size
    
    header_h = 75
    full_w = cw
    full_h = ch + header_h
    
    browser_img = Image.new("RGB", (full_w, full_h), "#f3f3f3")
    draw = ImageDraw.Draw(browser_img)
    
    # 1. Tab bar (y: 0 to 38)
    draw.rectangle([(0, 0), (full_w, 38)], fill="#e8eaed")
    
    # Tab shape
    tab_w = 220
    draw.rectangle([(8, 8), (tab_w, 38)], fill="#ffffff")
    draw.text((22, 14), tab_title, fill="#202124", font=FONT_TAB)
    # Close tab X
    draw.text((tab_w - 20, 14), "×", fill="#5f6368", font=FONT_TAB)
    
    # New tab +
    draw.text((tab_w + 12, 14), "+", fill="#5f6368", font=FONT_TAB)
    
    # Window controls
    draw.line([(full_w - 80, 19), (full_w - 70, 19)], fill="#202124", width=1) # Min
    draw.rectangle([(full_w - 55, 14), (full_w - 45, 24)], outline="#202124", width=1) # Max
    draw.line([(full_w - 28, 14), (full_w - 18, 24)], fill="#202124", width=1) # Close
    draw.line([(full_w - 18, 14), (full_w - 28, 24)], fill="#202124", width=1)
    
    # 2. Navigation bar (y: 38 to 75)
    draw.rectangle([(0, 38), (full_w, 75)], fill="#ffffff")
    draw.line([(0, 75), (full_w, 75)], fill="#e0e0e0", width=1)
    
    # Back / Forward / Refresh
    draw.text((14, 48), "←", fill="#5f6368", font=FONT_TAB)
    draw.text((36, 48), "→", fill="#b0b0b0", font=FONT_TAB)
    draw.text((58, 48), "⟳", fill="#5f6368", font=FONT_TAB)
    
    # Address bar
    draw.rectangle([(82, 44), (full_w - 60, 68)], fill="#f1f3f4", outline="#dadce0")
    draw.text((95, 49), url_text, fill="#3c4043", font=FONT_URL)
    
    # Paste rendered content
    browser_img.paste(content_img, (0, header_h))
    browser_img.save(output_path, quality=95)
    print(f"Saved: {output_path}")

def render_all():
    tasks = [
        ("task1.html", "Денис Лабынцев", "screen_task1.png", 800, 350),
        ("task2.html", "Лабынцев", "screen_task2.png", 800, 420),
        ("task3_sample1.html", "Задание 3 - Образец 1", "screen_task3_sample1.png", 800, 260),
        ("task3_sample2.html", "Задание 3 - Образец 2", "screen_task3_sample2.png", 800, 300),
        ("task4.html", "Лабынцев", "screen_task4.png", 900, 720),
        ("task5.html", "Любимая цитата", "screen_task5.png", 800, 300)
    ]
    
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=True)
        for html_file, title, png_name, w, h in tasks:
            full_html = os.path.join(WORK_DIR, html_file)
            temp_content = os.path.join(WORK_DIR, f"temp_{png_name}")
            final_png = os.path.join(WORK_DIR, png_name)
            
            page = browser.new_page(viewport={"width": w, "height": h})
            page.goto(f"file:///{full_html.replace(os.sep, '/')}")
            page.screenshot(path=temp_content)
            page.close()
            
            url_str = f"file:///{full_html.replace(os.sep, '/')}"
            wrap_in_browser(temp_content, final_png, title, url_str)
            if os.path.exists(temp_content):
                os.remove(temp_content)
                
        browser.close()
    print("ALL BROWSER SCREENSHOTS RENDERED SUCCESSFULLY!")

if __name__ == "__main__":
    render_all()
