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
    draw.rectangle([(0, 0), (full_w, 38)], fill="#e8eaed")
    tab_w = 280
    draw.rectangle([(8, 8), (tab_w, 38)], fill="#ffffff")
    draw.text((22, 14), tab_title, fill="#202124", font=FONT_TAB)
    draw.text((tab_w - 20, 14), "×", fill="#5f6368", font=FONT_TAB)
    draw.text((tab_w + 12, 14), "+", fill="#5f6368", font=FONT_TAB)
    draw.line([(full_w - 80, 19), (full_w - 70, 19)], fill="#202124", width=1)
    draw.rectangle([(full_w - 55, 14), (full_w - 45, 24)], outline="#202124", width=1)
    draw.line([(full_w - 28, 14), (full_w - 18, 24)], fill="#202124", width=1)
    draw.line([(full_w - 18, 14), (full_w - 28, 24)], fill="#202124", width=1)
    draw.rectangle([(0, 38), (full_w, 75)], fill="#ffffff")
    draw.line([(0, 75), (full_w, 75)], fill="#e0e0e0", width=1)
    draw.text((14, 48), "←", fill="#5f6368", font=FONT_TAB)
    draw.text((36, 48), "→", fill="#b0b0b0", font=FONT_TAB)
    draw.text((58, 48), "⟳", fill="#5f6368", font=FONT_TAB)
    draw.rectangle([(82, 44), (full_w - 60, 68)], fill="#f1f3f4", outline="#dadce0")
    draw.text((95, 49), url_text, fill="#3c4043", font=FONT_URL)
    browser_img.paste(content_img, (0, header_h))
    browser_img.save(output_path, quality=95)

with sync_playwright() as p:
    browser = p.chromium.launch(channel="msedge", headless=True)
    full_index = os.path.join(WORK_DIR, "index.html")
    url_index = f"file:///{full_index.replace(os.sep, '/')}"
    page = browser.new_page(viewport={"width": 1020, "height": 620})
    page.goto(url_index)
    page.evaluate("window.scrollTo(0, 150)")
    page.hover("nav.main-nav a:nth-child(2)")
    temp = os.path.join(WORK_DIR, "temp_links.png")
    page.screenshot(path=temp)
    wrap_in_browser(temp, os.path.join(WORK_DIR, "screen_lr4_links.png"), "Стилизация ссылок (Hover)", url_index + "#links-section")
    if os.path.exists(temp): os.remove(temp)
    page.close()
    browser.close()
print("Re-rendered screen_lr4_links.png successfully!")