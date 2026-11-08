# -*- coding: utf-8 -*-
import os
import sqlite3
import hashlib
from datetime import datetime
from http.server import HTTPServer, SimpleHTTPRequestHandler
import urllib.parse

WORK_DIR = r"d:\1с лабы\ПСИП_ЛР3_Файлы"
DB_PATH = os.path.join(WORK_DIR, "users.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Таблица пользователей
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    # Таблица результатов тестов
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS test_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT,
            email TEXT,
            phone TEXT,
            foundation_year INTEGER,
            river TEXT,
            rating_scale INTEGER,
            essay TEXT,
            submitted_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()
    print("Database initialized:", DB_PATH)

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def register_user(first_name, last_name, email, password):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    pwd_hash = hash_password(password)
    try:
        cursor.execute("""
            INSERT INTO users (first_name, last_name, email, password_hash)
            VALUES (?, ?, ?, ?)
        """, (first_name, last_name, email, pwd_hash))
        conn.commit()
        user_id = cursor.lastrowid
        print(f"User added: ID={user_id}, Name={first_name} {last_name}, Email={email}")
        return True, user_id, None
    except sqlite3.IntegrityError as e:
        return False, None, "Пользователь с таким email уже существует!"
    finally:
        conn.close()

def save_test(full_name, email, phone, year, river, scale, essay):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO test_results (full_name, email, phone, foundation_year, river, rating_scale, essay)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (full_name, email, phone, year, river, scale, essay))
    conn.commit()
    test_id = cursor.lastrowid
    conn.close()
    return test_id

class LabHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=WORK_DIR, **kwargs)

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length).decode('utf-8')
        params = urllib.parse.parse_qs(post_data)

        if self.path == "/register":
            first_name = params.get('first_name', [''])[0]
            last_name = params.get('last_name', [''])[0]
            email = params.get('email', [''])[0]
            password = params.get('password', [''])[0]

            success, user_id, err = register_user(first_name, last_name, email, password)

            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()

            if success:
                html_resp = f"""
                <!DOCTYPE html>
                <html lang="ru">
                <head>
                    <meta charset="utf-8">
                    <title>Успешная регистрация | Бобруйск</title>
                    <style>
                        body {{ font-family: 'Segoe UI', Tahoma, sans-serif; background: #f0fdf4; padding: 40px; color: #1e293b; text-align: center; }}
                        .card {{ max-width: 500px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-top: 5px solid #16a34a; }}
                        h2 {{ color: #16a34a; }}
                        .info-table {{ width: 100%; border-collapse: collapse; margin: 20px 0; text-align: left; }}
                        .info-table td {{ padding: 8px; border-bottom: 1px solid #e2e8f0; font-size: 14px; }}
                        .btn {{ display: inline-block; padding: 10px 20px; background: #0284c7; color: white; text-decoration: none; border-radius: 6px; font-weight: bold; margin-top: 15px; }}
                    </style>
                </head>
                <body>
                    <div class="card">
                        <h2>Данные успешно сохранены в Базе Данных!</h2>
                        <p>Учетная запись зарегистрирована в SQLite базе <b>users.db</b>.</p>
                        <table class="info-table">
                            <tr><td><b>ID записи в БД:</b></td><td>{user_id}</td></tr>
                            <tr><td><b>Имя и Фамилия:</b></td><td>{first_name} {last_name}</td></tr>
                            <tr><td><b>Электронная почта:</b></td><td>{email}</td></tr>
                            <tr><td><b>Статус:</b></td><td>Активен (SHA-256 хэширован)</td></tr>
                            <tr><td><b>Дата и время:</b></td><td>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</td></tr>
                        </table>
                        <a href="/login.html" class="btn">Перейти к форме авторизации</a>
                    </div>
                </body>
                </html>
                """
            else:
                html_resp = f"<h2>Ошибка: {err}</h2><a href='/register.html'>Вернуться назад</a>"

            self.wfile.write(html_resp.encode('utf-8'))

        elif self.path == "/test_submit":
            name = params.get('fullname', [''])[0]
            email = params.get('email', [''])[0]
            phone = params.get('phone', [''])[0]
            year = params.get('foundation_year', [0])[0]
            river = params.get('river', [''])[0]
            scale = params.get('scale', [5])[0]
            essay = params.get('essay', [''])[0]

            test_id = save_test(name, email, phone, year, river, scale, essay)

            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            resp = f"""
            <!DOCTYPE html>
            <html lang="ru"><head><meta charset="utf-8"><title>Тест принят</title>
            <style>body {{ font-family: sans-serif; background: #eff6ff; padding: 40px; text-align: center; }}
            .box {{ max-width: 500px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; border-top: 5px solid #0284c7; }}
            </style></head><body>
            <div class="box">
                <h2 style="color: #0284c7;">Результаты теста успешно приняты!</h2>
                <p>Участник: <b>{name}</b></p>
                <p>ID записи в БД: <b>{test_id}</b></p>
                <p>Ваши ответы зафиксированы в базе данных портала.</p>
                <a href="/test.html" style="color: #0284c7;">Пройти тест повторно</a>
            </div>
            </body></html>
            """
            self.wfile.write(resp.encode('utf-8'))
        else:
            self.send_error(404, "Page Not Found")

def run_server(port=8080):
    init_db()
    server_address = ('', port)
    httpd = HTTPServer(server_address, LabHandler)
    print(f"Server started at http://localhost:{port}/")
    return httpd

if __name__ == "__main__":
    init_db()
    # Регистрируем тестового пользователя Дениса Лабынцева
    register_user("Денис", "Лабынцев", "denis.labyntsev@bobruisk.by", "Secr3t_Bobr!2026")
    print("Database ready for demonstration.")
