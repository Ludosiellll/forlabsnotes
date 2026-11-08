# -*- coding: utf-8 -*-
"""
Скрипт генерации трафика HTTP, TCP, UDP для Wireshark (ЛР18)
"""
import urllib.request
import socket
import time

def run():
    print("1. Отправка UDP (DNS-запрос)...")
    try:
        socket.gethostbyname("httpforever.com")
        print("   -> DNS успешно выполнен (UDP порт 53)")
    except Exception as e:
        print("   -> Ошибка DNS:", e)
    
    time.sleep(0.3)
    
    print("2. Отправка HTTP запросов (порт 80)...")
    urls = ["http://httpforever.com", "http://example.com"]
    for u in urls:
        try:
            req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) WiresharkLab/18.0"})
            with urllib.request.urlopen(req, timeout=5) as resp:
                print(f"   -> {u}: Код {resp.status} OK, прочитано {len(resp.read())} байт")
        except Exception as e:
            print(f"   -> Ошибка {u}:", e)
        time.sleep(0.3)

    print("=== Готово! Теперь в Wireshark введите фильтр 'http' и нажмите Enter ===")

if __name__ == "__main__":
    run()
