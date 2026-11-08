# -*- coding: utf-8 -*-
"""
Скрипт рендеринга и автоматического захвата скриншотов веб-страницы
для Лабораторной работы №7 (ПСИП).
Использует Playwright и PIL для создания аккуратных скриншотов с темной рамкой браузера.
"""

import os
import sys
import time
from playwright.sync_api import sync_playwright
from PIL import Image, ImageDraw, ImageFont

WORK_DIR = r"d:\1с лабы\ПСИП_ЛР7_Файлы"

try:
    FONT_TITLE = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 13)
    FONT_SUB = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 11)
    FONT_BOLD = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 13)
except Exception:
    FONT_TITLE = ImageFont.load_default()
    FONT_SUB = ImageFont.load_default()
    FONT_BOLD = ImageFont.load_default()

def wrap_in_browser(content_img_path, output_path, title_text, url_text, section_badge):
    """Оборачивает скриншот в рамку браузера с адресной строкой."""
    content_img = Image.open(content_img_path)
    cw, ch = content_img.size
    header_h = 76
    full_w = cw
    full_h = ch + header_h

    frame = Image.new("RGB", (full_w, full_h), "#0f172a")
    draw = ImageDraw.Draw(frame)

    # 1. Верхняя панель вкладок (0..38px)
    draw.rectangle([(0, 0), (full_w, 38)], fill="#090d16")
    draw.ellipse([(14, 14), (22, 22)], fill="#ef4444")
    draw.ellipse([(28, 14), (36, 22)], fill="#f59e0b")
    draw.ellipse([(42, 14), (50, 22)], fill="#10b981")

    tab_w = min(420, full_w - 240)
    draw.rectangle([(70, 8), (70 + tab_w, 38)], fill="#1e293b")
    draw.text((84, 14), title_text[:42], fill="#f8fafc", font=FONT_TITLE)
    draw.text((70 + tab_w - 20, 14), "×", fill="#94a3b8", font=FONT_TITLE)
    draw.text((full_w - 210, 14), section_badge, fill="#38bdf8", font=FONT_BOLD)

    # 2. Панель адреса (38..76px)
    draw.rectangle([(0, 38), (full_w, 76)], fill="#1e293b")
    draw.line([(0, 76), (full_w, 76)], fill="#334155", width=1)
    draw.text((16, 48), "←", fill="#94a3b8", font=FONT_TITLE)
    draw.text((38, 48), "→", fill="#64748b", font=FONT_TITLE)
    draw.text((60, 48), "↻", fill="#94a3b8", font=FONT_TITLE)

    draw.rectangle([(84, 44), (full_w - 20, 70)], fill="#0f172a", outline="#475569")
    draw.text((98, 49), "🔒 " + url_text, fill="#38bdf8", font=FONT_SUB)

    # Вставка содержимого страницы
    frame.paste(content_img, (0, header_h))
    frame.save(output_path, quality=95)
    print(f"[OK] Сгенерирован скриншот: {output_path}")

def run():
    html_file = os.path.join(WORK_DIR, "index.html")
    file_url = f"file:///{html_file.replace(os.sep, '/')}"

    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=True)
        ctx = browser.new_context(viewport={"width": 1280, "height": 900}, device_scale_factor=1)
        page = ctx.new_page()

        print("[*] Загрузка страницы в браузере Edge...")
        page.goto(file_url, wait_until="networkidle")
        time.sleep(1) # Дать отработать начальной анимации

        # 1. Скриншот 1: Анимированный заголовок и Hero-блок
        raw_hero = os.path.join(WORK_DIR, "raw_hero.png")
        out_hero = os.path.join(WORK_DIR, "screen_lr7_hero.png")
        hero_elem = page.locator(".hero-section")
        hero_elem.screenshot(path=raw_hero)
        wrap_in_browser(raw_hero, out_hero, "Бобруйск Онлайн — Анимированный Hero", "https://bobruysk.guide/#hero", "Задание 6 • Заголовок")

        # 2. Скриншот 2: Простые анимации (@keyframes pulseGlow & floatBadge)
        raw_anim = os.path.join(WORK_DIR, "raw_anim.png")
        out_anim = os.path.join(WORK_DIR, "screen_lr7_animations.png")
        anim_elem = page.locator("#animations")
        anim_elem.screenshot(path=raw_anim)
        wrap_in_browser(raw_anim, out_anim, "Бобруйск Онлайн — Простые CSS анимации", "https://bobruysk.guide/#animations", "Задание 1 • Анимации")

        # 3. Скриншот 3: Анимация с эффектом параллакса
        raw_par = os.path.join(WORK_DIR, "raw_par.png")
        out_par = os.path.join(WORK_DIR, "screen_lr7_parallax.png")
        par_elem = page.locator("#parallax")
        par_elem.screenshot(path=raw_par)
        wrap_in_browser(raw_par, out_par, "Бобруйск Онлайн — Эффект параллакса", "https://bobruysk.guide/#parallax", "Задание 2 • Параллакс")

        # 4. Скриншот 4: Анимированное меню и выпадающий список (hover dropdown)
        raw_menu = os.path.join(WORK_DIR, "raw_menu.png")
        out_menu = os.path.join(WORK_DIR, "screen_lr7_menu.png")
        # Наводим курсор на dropdown элемент
        page.hover(".has-dropdown")
        time.sleep(0.5)
        header_elem = page.locator(".site-header")
        header_elem.screenshot(path=raw_menu)
        wrap_in_browser(raw_menu, out_menu, "Бобруйск Онлайн — Анимированное меню", "https://bobruysk.guide/#menu", "Задание 3 • Меню")

        # 5. Скриншот 5: Слайдер изображений
        raw_slider = os.path.join(WORK_DIR, "raw_slider.png")
        out_slider = os.path.join(WORK_DIR, "screen_lr7_slider.png")
        slider_elem = page.locator("#slider")
        slider_elem.screenshot(path=raw_slider)
        wrap_in_browser(raw_slider, out_slider, "Бобруйск Онлайн — Слайдер изображений", "https://bobruysk.guide/#slider", "Задание 5 • Слайдер")

        # 6. Скриншот 6: Анимированные кнопки (hover эффекты)
        raw_buttons = os.path.join(WORK_DIR, "raw_buttons.png")
        out_buttons = os.path.join(WORK_DIR, "screen_lr7_buttons.png")
        btn_elem = page.locator("#buttons")
        btn_elem.screenshot(path=raw_buttons)
        wrap_in_browser(raw_buttons, out_buttons, "Бобруйск Онлайн — Анимированные кнопки", "https://bobruysk.guide/#buttons", "Задание 4 • Кнопки")

        ctx.close()
        browser.close()

    # Удаление временных сырых файлов
    for raw in [raw_hero, raw_anim, raw_par, raw_menu, raw_slider, raw_buttons]:
        if os.path.exists(raw):
            os.remove(raw)

    print("[DONE] Все 6 скриншотов успешно созданы!")

if __name__ == "__main__":
    run()
