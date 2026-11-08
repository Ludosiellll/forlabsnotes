# -*- coding: utf-8 -*-
"""
Скрипт рендеринга и автоматического захвата скриншотов адаптивного сайта
для Лабораторной работы №6 (ПСИП).
Тестируемые разрешения:
1. Desktop: 1280 x 800 px
2. Tablet:  768 x 1024 px
3. Mobile:   375 x 812 px
"""

import os
import sys
from playwright.sync_api import sync_playwright
from PIL import Image, ImageDraw, ImageFont

WORK_DIR = r"d:\1с лабы\ПСИП_ЛР6_Файлы"

try:
    FONT_TITLE = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 13)
    FONT_SUB = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 11)
    FONT_BOLD = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 13)
except Exception:
    FONT_TITLE = ImageFont.load_default()
    FONT_SUB = ImageFont.load_default()
    FONT_BOLD = ImageFont.load_default()

def wrap_in_browser(content_img_path, output_path, title_text, url_text, device_badge):
    """Оборачивает скриншот в стилизованную темную рамку современного браузера."""
    content_img = Image.open(content_img_path)
    cw, ch = content_img.size
    header_h = 76
    full_w = cw
    full_h = ch + header_h
    
    frame = Image.new("RGB", (full_w, full_h), "#0f172a")
    draw = ImageDraw.Draw(frame)
    
    # 1. Верхняя панель вкладок (0..38px)
    draw.rectangle([(0, 0), (full_w, 38)], fill="#090d16")
    
    # Окно управления (кнопки)
    draw.ellipse([(12, 14), (20, 22)], fill="#ef4444")
    draw.ellipse([(26, 14), (34, 22)], fill="#f59e0b")
    draw.ellipse([(40, 14), (48, 22)], fill="#10b981")
    
    if full_w > 500:
        # Для десктопа и планшета: вкладка + бейдж справа
        tab_w = min(360, full_w - 220)
        draw.rectangle([(68, 8), (68 + tab_w, 38)], fill="#1e293b")
        draw.text((80, 14), title_text[:38], fill="#f8fafc", font=FONT_TITLE)
        draw.text((68 + tab_w - 20, 14), "×", fill="#94a3b8", font=FONT_TITLE)
        draw.text((full_w - 170, 14), device_badge, fill="#38bdf8", font=FONT_BOLD)
    else:
        # Для мобильного экрана (375px): аккуратный статус-бейдж по центру
        draw.text((60, 13), device_badge, fill="#38bdf8", font=FONT_BOLD)
        draw.text((full_w - 65, 14), "9:41", fill="#94a3b8", font=FONT_SUB)
    
    # 2. Панель адреса (38..76px)
    draw.rectangle([(0, 38), (full_w, 76)], fill="#1e293b")
    draw.line([(0, 76), (full_w, 76)], fill="#334155", width=1)
    
    if full_w > 500:
        draw.text((14, 48), "←", fill="#94a3b8", font=FONT_TITLE)
        draw.text((36, 48), "→", fill="#64748b", font=FONT_TITLE)
        draw.text((58, 48), "↻", fill="#94a3b8", font=FONT_TITLE)
        draw.rectangle([(82, 44), (full_w - 20, 70)], fill="#0f172a", outline="#475569")
        draw.text((95, 49), url_text, fill="#38bdf8", font=FONT_SUB)
    else:
        # Компактная мобильная адресная строка
        draw.rectangle([(16, 44), (full_w - 16, 70)], fill="#0f172a", outline="#475569")
        draw.text((28, 49), "🔒 " + url_text, fill="#38bdf8", font=FONT_SUB)
    
    # Вставка содержимого страницы
    frame.paste(content_img, (0, header_h))
    frame.save(output_path, quality=95)
    print(f"[OK] Сгенерирован скриншот: {output_path}")

def run():
    html_file = os.path.join(WORK_DIR, "index.html")
    file_url = f"file:///{html_file.replace(os.sep, '/')}"
    
    raw_desktop = os.path.join(WORK_DIR, "raw_desktop.png")
    raw_tablet = os.path.join(WORK_DIR, "raw_tablet.png")
    raw_mobile = os.path.join(WORK_DIR, "raw_mobile.png")
    
    out_desktop = os.path.join(WORK_DIR, "screen_lr6_desktop_1280.png")
    out_tablet = os.path.join(WORK_DIR, "screen_lr6_tablet_768.png")
    out_mobile = os.path.join(WORK_DIR, "screen_lr6_mobile_375.png")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=True)
        
        # 1. Desktop: 1280 x 800
        print("[*] Рендеринг Desktop 1280x800...")
        ctx_desktop = browser.new_context(viewport={"width": 1280, "height": 800}, device_scale_factor=1)
        page_desktop = ctx_desktop.new_page()
        page_desktop.goto(file_url, wait_until="networkidle")
        page_desktop.screenshot(path=raw_desktop, clip={"x": 0, "y": 0, "width": 1280, "height": 820})
        ctx_desktop.close()
        
        # 2. Tablet: 768 x 1024
        print("[*] Рендеринг Tablet 768x1024...")
        ctx_tablet = browser.new_context(viewport={"width": 768, "height": 1024}, device_scale_factor=1)
        page_tablet = ctx_tablet.new_page()
        page_tablet.goto(file_url, wait_until="networkidle")
        page_tablet.screenshot(path=raw_tablet, clip={"x": 0, "y": 0, "width": 768, "height": 1050})
        ctx_tablet.close()
        
        # 3. Mobile: 375 x 812
        print("[*] Рендеринг Mobile 375x812...")
        ctx_mobile = browser.new_context(viewport={"width": 375, "height": 812}, device_scale_factor=1, is_mobile=True)
        page_mobile = ctx_mobile.new_page()
        page_mobile.goto(file_url, wait_until="networkidle")
        page_mobile.screenshot(path=raw_mobile, clip={"x": 0, "y": 0, "width": 375, "height": 920})
        ctx_mobile.close()
        
        browser.close()
        
    wrap_in_browser(raw_desktop, out_desktop, "Бобруйск — Туристический портал", file_url, "DESKTOP 1280×800")
    wrap_in_browser(raw_tablet, out_tablet, "Бобруйск (Планшет)", "http://localhost:8080/tablet", "TABLET 768×1024")
    wrap_in_browser(raw_mobile, out_mobile, "Бобруйск (Смартфон)", "http://localhost:8080/mobile", "MOBILE 375×812")
    
    # Очистка временных raw-файлов
    for raw in [raw_desktop, raw_tablet, raw_mobile]:
        if os.path.exists(raw):
            os.remove(raw)

if __name__ == "__main__":
    run()
