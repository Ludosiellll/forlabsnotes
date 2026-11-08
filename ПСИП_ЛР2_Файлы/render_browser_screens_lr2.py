# -*- coding: utf-8 -*-
import os
from playwright.sync_api import sync_playwright
from PIL import Image, ImageDraw, ImageFont

WORK_DIR = r"d:\1с лабы\ПСИП_ЛР2_Файлы"

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
    tab_w = 260
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
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=True)
        
        # 1. index.html - Top & Menu & Intro
        page = browser.new_page(viewport={"width": 960, "height": 620})
        full_index = os.path.join(WORK_DIR, "index.html")
        url_index = f"file:///{full_index.replace(os.sep, '/')}"
        page.goto(url_index)
        temp_1 = os.path.join(WORK_DIR, "temp_screen1.png")
        page.screenshot(path=temp_1)
        wrap_in_browser(temp_1, os.path.join(WORK_DIR, "screen_index_top.png"), "Города Беларуси: Бобруйск", url_index)
        if os.path.exists(temp_1): os.remove(temp_1)
        
        # 2. index.html - Lists and Multimedia
        page.evaluate("window.scrollTo(0, 480)")
        temp_2 = os.path.join(WORK_DIR, "temp_screen2.png")
        page.screenshot(path=temp_2)
        wrap_in_browser(temp_2, os.path.join(WORK_DIR, "screen_index_lists.png"), "Города Беларуси: Бобруйск", url_index + "#districts")
        if os.path.exists(temp_2): os.remove(temp_2)
        
        # 3. index.html - Developer Card
        card_elem = page.locator("a[name='developer']")
        # Scroll to heading
        page.evaluate("window.scrollTo(0, 1550)")
        temp_3 = os.path.join(WORK_DIR, "temp_screen3.png")
        page.set_viewport_size({"width": 960, "height": 650})
        page.screenshot(path=temp_3)
        wrap_in_browser(temp_3, os.path.join(WORK_DIR, "screen_index_card.png"), "Города Беларуси: Бобруйск", url_index + "#developer")
        if os.path.exists(temp_3): os.remove(temp_3)
        page.close()
        
        # 4. sights.html - Background image and table
        page_sights = browser.new_page(viewport={"width": 980, "height": 820})
        full_sights = os.path.join(WORK_DIR, "sights.html")
        url_sights = f"file:///{full_sights.replace(os.sep, '/')}"
        page_sights.goto(url_sights)
        temp_4 = os.path.join(WORK_DIR, "temp_screen4.png")
        page_sights.screenshot(path=temp_4)
        wrap_in_browser(temp_4, os.path.join(WORK_DIR, "screen_sights.png"), "Достопримечательности Бобруйска", url_sights)
        if os.path.exists(temp_4): os.remove(temp_4)
        page_sights.close()
        
        browser.close()
    print("ALL LR2 SCREENSHOTS CAPTURED AND WRAPPED SUCCESSFULLY!")

if __name__ == "__main__":
    render_all()
