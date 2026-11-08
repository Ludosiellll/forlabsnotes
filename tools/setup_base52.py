# -*- coding: utf-8 -*-
import os

target_dir = r"d:\1с лабы\1С_ЛР5.2_Файлы"

# 1. Запуск_1С_Предприятие.bat
bat_ent = os.path.join(target_dir, "Запуск_1С_Предприятие.bat")
with open(bat_ent, "w", encoding="cp1251") as f:
    f.write('@echo off\nstart "" "D:\\1c_app\\8.3.27.1508\\bin\\1cv8t.exe" ENTERPRISE /F "%~dp0Base1C"\n')

# 2. Запуск_Конфигуратор.bat
bat_cfg = os.path.join(target_dir, "Запуск_Конфигуратор.bat")
with open(bat_cfg, "w", encoding="cp1251") as f:
    f.write('@echo off\nstart "" "D:\\1c_app\\8.3.27.1508\\bin\\1cv8t.exe" DESIGNER /F "%~dp0Base1C"\n')

# 3. Регистрация в ibases.v8i
appdata = os.environ.get("APPDATA", "")
v8i_path = os.path.join(appdata, "1C", "1CEStart", "ibases.v8i")
if os.path.exists(v8i_path):
    with open(v8i_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    entry_tag = "[ЛР5.2 Лабынцев]"
    if entry_tag not in content:
        new_entry = (
            f"\n[ЛР5.2 Лабынцев]\n"
            f'Connect=File="{os.path.join(target_dir, "Base1C")}";\n'
            f"ID=52000000-0000-0000-0000-000000000052\n"
            f"OrderInList=1\n"
            f"Folder=/\n"
            f"OrderInTree=1\n"
            f"External=0\n"
            f"ClientConnectionSpeed=Normal\n"
            f"App=Auto\n"
            f"DefaultVersion=8.3.27.1508\n"
        )
        with open(v8i_path, "a", encoding="utf-8") as f:
            f.write(new_entry)
        print("[OK] База зарегистрирована в ibases.v8i под именем 'ЛР5.2 Лабынцев'!")
    else:
        print("[OK] База уже зарегистрирована в ibases.v8i.")

print("[OK] Батники созданы успешно!")
