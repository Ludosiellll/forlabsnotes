# -*- coding: utf-8 -*-
import os
from playwright.sync_api import sync_playwright
from PIL import Image, ImageDraw, ImageFont

WORK_DIR = r"d:\1с лабы\ПСИП_ЛР4_Файлы"

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
    
    browser_img = Image.new("RGB", (full_w, full_h), "#f3f3f3")
    draw = ImageDraw.Draw(browser_img)
    
    # 1. Tab bar (y: 0 to 38)
    draw.rectangle([(0, 0), (full_w, 38)], fill="#e8eaed")
    
    # Tab shape
    tab_w = 280
    draw.rectangle([(8, 8), (tab_w, 38)], fill="#ffffff")
    draw.text((22, 14), tab_title, fill="#202124", font=FONT_TAB)
    draw.text((tab_w - 20, 14), "×", fill="#5f6368", font=FONT_TAB)
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
        
        full_index = os.path.join(WORK_DIR, "index.html")
        url_index = f"file:///{full_index.replace(os.sep, '/')}"
        
        # 1. Задание 1: Верхняя часть, шапка, шрифты, фон и демонстрация приоритетов
        page1 = browser.new_page(viewport={"width": 1020, "height": 680})
        page1.goto(url_index)
        temp_1 = os.path.join(WORK_DIR, "temp_screen1.png")
        page1.screenshot(path=temp_1)
        wrap_in_browser(temp_1, os.path.join(WORK_DIR, "screen_lr4_typography.png"), "Бобруйск — Туристический гид", url_index + "#typography")
        if os.path.exists(temp_1): os.remove(temp_1)
        page1.close()
        
        # 2. Задание 2: Стилизация ссылок (наведение курсора на одну из ссылок)
        page2 = browser.new_page(viewport={"width": 1020, "height": 550})
        page2.goto(url_index)
        page2.evaluate("document.getElementById('links-section').scrollIntoView()")
        # Наводим курсор на ссылку в меню или в карточке
        page2.hover(".links-demo-card a.text-link:first-child")
        temp_2 = os.path.join(WORK_DIR, "temp_screen2.png")
        page2.screenshot(path=temp_2)
        wrap_in_browser(temp_2, os.path.join(WORK_DIR, "screen_lr4_links.png"), "Стилизация ссылок (Hover)", url_index + "#links-section")
        if os.path.exists(temp_2): os.remove(temp_2)
        page2.close()
        
        # 3. Задание 3: Стилизованные списки
        page3 = browser.new_page(viewport={"width": 1020, "height": 520})
        page3.goto(url_index)
        page3.evaluate("document.getElementById('lists-section').scrollIntoView()")
        temp_3 = os.path.join(WORK_DIR, "temp_screen3.png")
        page3.screenshot(path=temp_3)
        wrap_in_browser(temp_3, os.path.join(WORK_DIR, "screen_lr4_lists.png"), "Стилизация списков", url_index + "#lists-section")
        if os.path.exists(temp_3): os.remove(temp_3)
        page3.close()
        
        # 4. Задание 4: Стилизованная форма бронирования
        page4 = browser.new_page(viewport={"width": 1020, "height": 620})
        page4.goto(url_index)
        page4.evaluate("document.getElementById('form-section').scrollIntoView()")
        temp_4 = os.path.join(WORK_DIR, "temp_screen4.png")
        page4.screenshot(path=temp_4)
        wrap_in_browser(temp_4, os.path.join(WORK_DIR, "screen_lr4_form.png"), "Стилизованная форма бронирования", url_index + "#form-section")
        if os.path.exists(temp_4): os.remove(temp_4)
        page4.close()
        
        # 5. Задания 5 и 6: Стилизованная таблица с зебровым эффектом
        page5 = browser.new_page(viewport={"width": 1020, "height": 600})
        page5.goto(url_index)
        page5.evaluate("document.getElementById('table-section').scrollIntoView()")
        # Наводим курсор на вторую строку таблицы для демонстрации hover подсветки
        page5.hover("table.hotels-table tbody tr:nth-child(2)")
        temp_5 = os.path.join(WORK_DIR, "temp_screen5.png")
        page5.screenshot(path=temp_5)
        wrap_in_browser(temp_5, os.path.join(WORK_DIR, "screen_lr4_table.png"), "Таблица с зебровым эффектом", url_index + "#table-section")
        if os.path.exists(temp_5): os.remove(temp_5)
        page5.close()
        
        browser.close()
    print("ALL LR4 SCREENSHOTS SUCCESSFULLY RENDERED AND SAVED!")

if __name__ == "__main__":
    render_all()