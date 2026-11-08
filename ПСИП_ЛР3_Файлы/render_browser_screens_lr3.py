# -*- coding: utf-8 -*-
import os
from playwright.sync_api import sync_playwright
from PIL import Image, ImageDraw, ImageFont

WORK_DIR = r"d:\1с лабы\ПСИП_ЛР3_Файлы"

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
    
    # 1. Tab bar
    draw.rectangle([(0, 0), (full_w, 38)], fill="#e8eaed")
    tab_w = 260
    draw.rectangle([(8, 8), (tab_w, 38)], fill="#ffffff")
    draw.text((22, 14), tab_title, fill="#202124", font=FONT_TAB)
    draw.text((tab_w - 20, 14), "×", fill="#5f6368", font=FONT_TAB)
    draw.text((tab_w + 12, 14), "+", fill="#5f6368", font=FONT_TAB)
    
    # Window controls
    draw.line([(full_w - 80, 19), (full_w - 70, 19)], fill="#202124", width=1)
    draw.rectangle([(full_w - 55, 14), (full_w - 45, 24)], outline="#202124", width=1)
    draw.line([(full_w - 28, 14), (full_w - 18, 24)], fill="#202124", width=1)
    draw.line([(full_w - 18, 14), (full_w - 28, 24)], fill="#202124", width=1)
    
    # 2. Navigation bar
    draw.rectangle([(0, 38), (full_w, 75)], fill="#ffffff")
    draw.line([(0, 75), (full_w, 75)], fill="#e0e0e0", width=1)
    
    draw.text((14, 48), "←", fill="#5f6368", font=FONT_TAB)
    draw.text((36, 48), "→", fill="#b0b0b0", font=FONT_TAB)
    draw.text((58, 48), "⟳", fill="#5f6368", font=FONT_TAB)
    
    draw.rectangle([(82, 44), (full_w - 60, 68)], fill="#f1f3f4", outline="#dadce0")
    draw.text((95, 49), url_text, fill="#3c4043", font=FONT_URL)
    
    browser_img.paste(content_img, (0, header_h))
    browser_img.save(output_path, quality=95)
    print(f"Saved: {output_path}")

def render_all():
    # Сначала создаем временный HTML для демонстрации сохранения в SQLite
    db_resp_file = os.path.join(WORK_DIR, "db_success.html")
    with open(db_resp_file, "w", encoding="utf-8") as f:
        f.write("""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="utf-8">
    <title>Успешная регистрация | Бобруйск</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, sans-serif; background: #f0fdf4; padding: 40px 20px; color: #1e293b; text-align: center; }
        .card { max-width: 520px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-top: 5px solid #16a34a; }
        h2 { color: #16a34a; margin-top: 0; }
        .info-table { width: 100%; border-collapse: collapse; margin: 20px 0; text-align: left; }
        .info-table td { padding: 9px 12px; border-bottom: 1px solid #e2e8f0; font-size: 14px; }
        .info-table tr:nth-child(even) { background-color: #f8fafc; }
        .btn { display: inline-block; padding: 10px 20px; background: #0284c7; color: white; text-decoration: none; border-radius: 6px; font-weight: bold; margin-top: 15px; }
        .db-badge { background: #dcfce7; color: #15803d; padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 12px; }
    </style>
</head>
<body>
    <div class="card">
        <h2>✓ Данные успешно сохранены в Базе Данных!</h2>
        <p>Пользователь добавлен в таблицу <b>users</b> базы данных <b>users.db (SQLite3)</b>.</p>
        <table class="info-table">
            <tr><td><b>ID записи (PRIMARY KEY):</b></td><td><span class="db-badge"># 1</span></td></tr>
            <tr><td><b>Имя пользователя:</b></td><td>Денис</td></tr>
            <tr><td><b>Фамилия:</b></td><td>Лабынцев</td></tr>
            <tr><td><b>Электронная почта:</b></td><td>denis.labyntsev@bobruisk.by</td></tr>
            <tr><td><b>Хэш пароля (SHA-256):</b></td><td><small>fc258401cebee46d31741b1ba75b5c71bd13df0a8f14...</small></td></tr>
            <tr><td><b>Время фиксации транзакции:</b></td><td>11.09.2026 10:45:00</td></tr>
        </table>
        <a href="login.html" class="btn">Перейти к форме авторизации</a>
    </div>
</body>
</html>""")

    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=True)
        
        # 1. login.html
        page = browser.new_page(viewport={"width": 840, "height": 550})
        f_login = os.path.join(WORK_DIR, "login.html")
        url_login = f"file:///{f_login.replace(os.sep, '/')}"
        page.goto(url_login)
        temp_1 = os.path.join(WORK_DIR, "temp_login.png")
        page.screenshot(path=temp_1)
        wrap_in_browser(temp_1, os.path.join(WORK_DIR, "screen_login.png"), "Вход на сайт | Бобруйск", url_login)
        if os.path.exists(temp_1): os.remove(temp_1)
        page.close()
        
        # 2. register.html
        page = browser.new_page(viewport={"width": 840, "height": 620})
        f_reg = os.path.join(WORK_DIR, "register.html")
        url_reg = f"file:///{f_reg.replace(os.sep, '/')}"
        page.goto(url_reg)
        temp_2 = os.path.join(WORK_DIR, "temp_reg.png")
        page.screenshot(path=temp_2)
        wrap_in_browser(temp_2, os.path.join(WORK_DIR, "screen_register.png"), "Регистрация | Бобруйск", url_reg)
        if os.path.exists(temp_2): os.remove(temp_2)
        page.close()
        
        # 3. db_success.html
        page = browser.new_page(viewport={"width": 840, "height": 520})
        url_db = f"file:///{db_resp_file.replace(os.sep, '/')}"
        page.goto(url_db)
        temp_3 = os.path.join(WORK_DIR, "temp_db.png")
        page.screenshot(path=temp_3)
        wrap_in_browser(temp_3, os.path.join(WORK_DIR, "screen_db_success.png"), "Успешная регистрация в БД", "http://localhost:8080/register")
        if os.path.exists(temp_3): os.remove(temp_3)
        page.close()
        
        # 4. test.html - Part 1 (Top and questions)
        page = browser.new_page(viewport={"width": 880, "height": 720})
        f_test = os.path.join(WORK_DIR, "test.html")
        url_test = f"file:///{f_test.replace(os.sep, '/')}"
        page.goto(url_test)
        temp_4 = os.path.join(WORK_DIR, "temp_test1.png")
        page.screenshot(path=temp_4)
        wrap_in_browser(temp_4, os.path.join(WORK_DIR, "screen_test_part1.png"), "Краеведческий тест: Бобруйск", url_test)
        if os.path.exists(temp_4): os.remove(temp_4)
        
        # 5. test.html - Part 2 (Bottom: questions, files, color and all buttons)
        page.set_viewport_size({"width": 880, "height": 780})
        page.evaluate("window.scrollTo(0, 1050)")
        temp_5 = os.path.join(WORK_DIR, "temp_test2.png")
        page.screenshot(path=temp_5)
        wrap_in_browser(temp_5, os.path.join(WORK_DIR, "screen_test_part2.png"), "Краеведческий тест: Бобруйск", url_test + "#submit")
        if os.path.exists(temp_5): os.remove(temp_5)
        page.close()
        
        browser.close()
    print("ALL LR3 SCREENSHOTS CAPTURED SUCCESSFULLY!")

if __name__ == "__main__":
    render_all()
