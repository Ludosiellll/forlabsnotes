# -*- coding: utf-8 -*-
import os
from playwright.sync_api import sync_playwright
from PIL import Image, ImageDraw, ImageFont

WORK_DIR = r"d:\1с лабы\ПСИП_ЛР5_Файлы"

try:
    FONT_TAB = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 12)
    FONT_URL = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 12)
except Exception:
    FONT_TAB = ImageFont.load_default()
    FONT_URL = ImageFont.load_default()

def wrap_in_browser(content_img_path, output_path, tab_title, url_text):
    content_img = Image.open(content_img_path)
    cw, ch = content_img.size
    header_h = 75
    full_w = cw
    full_h = ch + header_h
    
    browser_img = Image.new("RGB", (full_w, full_h), "#18181f")
    draw = ImageDraw.Draw(browser_img)
    
    # 1. Dark Chrome Tab bar (y: 0 to 38)
    draw.rectangle([(0, 0), (full_w, 38)], fill="#14141b")
    tab_w = 340
    draw.rectangle([(8, 8), (tab_w, 38)], fill="#22222d")
    draw.text((22, 14), tab_title, fill="#f1f5f9", font=FONT_TAB)
    draw.text((tab_w - 20, 14), "×", fill="#94a3b8", font=FONT_TAB)
    draw.text((tab_w + 12, 14), "+", fill="#94a3b8", font=FONT_TAB)
    
    # Window controls (minimize, maximize, close)
    draw.line([(full_w - 80, 19), (full_w - 70, 19)], fill="#94a3b8", width=1)
    draw.rectangle([(full_w - 55, 14), (full_w - 45, 24)], outline="#94a3b8", width=1)
    draw.line([(full_w - 28, 14), (full_w - 18, 24)], fill="#94a3b8", width=1)
    draw.line([(full_w - 18, 14), (full_w - 28, 24)], fill="#94a3b8", width=1)
    
    # 2. Dark Navigation bar (y: 38 to 75)
    draw.rectangle([(0, 38), (full_w, 75)], fill="#1c1c26")
    draw.line([(0, 75), (full_w, 75)], fill="#2b2b3b", width=1)
    
    draw.text((14, 48), "←", fill="#94a3b8", font=FONT_TAB)
    draw.text((36, 48), "→", fill="#555566", font=FONT_TAB)
    draw.text((58, 48), "⟳", fill="#94a3b8", font=FONT_TAB)
    
    # Address bar
    draw.rectangle([(82, 44), (full_w - 60, 68)], fill="#121218", outline="#323246")
    draw.text((95, 49), url_text, fill="#38bdf8", font=FONT_URL)
    
    browser_img.paste(content_img, (0, header_h))
    browser_img.save(output_path, quality=95)
    print(f"Saved: {output_path}")

with sync_playwright() as p:
    browser = p.chromium.launch(channel="msedge", headless=True)
    
    # Скриншот 1: index.html (Задание 1: Табличная сетка)
    idx_path = os.path.join(WORK_DIR, "index.html")
    url_idx = f"file:///{idx_path.replace(os.sep, '/')}"
    page1 = browser.new_page(viewport={"width": 1100, "height": 840})
    page1.goto(url_idx)
    page1.wait_for_timeout(300)
    temp1 = os.path.join(WORK_DIR, "temp_idx.png")
    page1.screenshot(path=temp1)
    wrap_in_browser(temp1, os.path.join(WORK_DIR, "screen_lr5_table_layout.png"), "Главная | Экстраординарная табличная сетка", url_idx)
    if os.path.exists(temp1): os.remove(temp1)
    page1.close()

    # Скриншот 2: positioning.html (Задание 2: Точное позиционирование)
    pos_path = os.path.join(WORK_DIR, "positioning.html")
    url_pos = f"file:///{pos_path.replace(os.sep, '/')}"
    page2 = browser.new_page(viewport={"width": 1100, "height": 840})
    page2.goto(url_pos)
    page2.wait_for_timeout(300)
    temp2 = os.path.join(WORK_DIR, "temp_pos.png")
    page2.screenshot(path=temp2)
    wrap_in_browser(temp2, os.path.join(WORK_DIR, "screen_lr5_positioning.png"), "Точное позиционирование CSS position", url_pos)
    if os.path.exists(temp2): os.remove(temp2)
    page2.close()

    browser.close()
print("LR5 screenshots rendered successfully!")