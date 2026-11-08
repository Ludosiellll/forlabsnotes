# -*- coding: utf-8 -*-
"""
tools/reload_and_dump_labs.py
Автоматическое обновление конфигураций баз данных Base1C из исходников src/
и чистая выгрузка архивов *.dt с синхронизацией на флешку E:\Программирование 1С\
"""

import os
import sys
import shutil
import tempfile
import subprocess

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

ONE_C = r"D:\1c_app\8.3.27.1508\bin\1cv8t.exe"
TEMP_DIR = tempfile.gettempdir()
LOG_PATH = os.path.join(TEMP_DIR, "1c_batch_op.log")

LABS = [
    {
        "name": "ЛР5.2",
        "lab_dir": r"d:\1с лабы\1С_ЛР5.2_Файлы",
        "dt_names": ["ОбработкаДокументовЛабынцев.dt", "Лабынцев.dt"],
        "flash_dir": r"E:\Программирование 1С\ЛР5.2"
    },
    {
        "name": "ЛР3",
        "lab_dir": r"d:\1с лабы\1С_ЛР3_Файлы",
        "dt_names": ["СправочникиЛабынцев.dt", "Лабынцев.dt"],
        "flash_dir": r"E:\Программирование 1С\ЛР3"
    },
    {
        "name": "ЛР2",
        "lab_dir": r"d:\1с лабы\1С_ЛР2_Файлы",
        "dt_names": ["ПодсистемыЛабынцев.dt", "Лабынцев.dt"],
        "flash_dir": r"E:\Программирование 1С\ЛР2"
    }
]

def run_1c(args):
    if os.path.exists(LOG_PATH):
        try:
            os.remove(LOG_PATH)
        except Exception:
            pass

    cmd = [ONE_C] + args + ["/Out", LOG_PATH]
    res = subprocess.run(cmd, capture_output=True)
    
    log_content = ""
    if os.path.exists(LOG_PATH):
        for enc in ["utf-8", "cp1251", "cp866"]:
            try:
                with open(LOG_PATH, "r", encoding=enc) as f:
                    log_content = f.read()
                break
            except Exception:
                continue
        try:
            os.remove(LOG_PATH)
        except Exception:
            pass

    return res.returncode, log_content.lstrip('\ufeff')

def process_lab(lab_info):
    name = lab_info["name"]
    lab_dir = lab_info["lab_dir"]
    base_dir = os.path.join(lab_dir, "Base1C")
    src_dir = os.path.join(lab_dir, "src")
    flash_dir = lab_info["flash_dir"]
    dt_names = lab_info["dt_names"]

    print("=" * 60)
    print(f"  Обработка {name}: {lab_dir}")
    print("=" * 60)

    # 1. Загрузка конфигурации из файлов и обновление конфигурации БД
    print(f"[{name}] Загрузка конфигурации из файлов и обновление конфигурации БД...")
    code, log = run_1c([
        "DESIGNER",
        "/F", base_dir,
        "/LoadConfigFromFiles", src_dir,
        "/UpdateDBCfg"
    ])
    if code != 0:
        print(f"[FAIL] Ошибка обновления базы {name} (код {code}):\n{log}")
        return False
    print(f"[OK] Конфигурация {name} успешно загружена и обновлена.")
    if log.strip():
        print("  Лог 1С:", log.strip())

    # 2. Выгрузка первого *.dt
    main_dt = os.path.join(lab_dir, dt_names[0])
    print(f"[{name}] Выгрузка информационной базы в {dt_names[0]}...")
    code, log = run_1c([
        "DESIGNER",
        "/F", base_dir,
        "/DumpIB", main_dt
    ])
    if code != 0:
        print(f"[FAIL] Ошибка выгрузки {main_dt} (код {code}):\n{log}")
        return False
    dt_size = os.path.getsize(main_dt)
    print(f"[OK] Архив {dt_names[0]} успешно создан: {dt_size} байт")

    # 3. Создание копии *.dt если задано второе имя (Лабынцев.dt)
    if len(dt_names) > 1:
        second_dt = os.path.join(lab_dir, dt_names[1])
        shutil.copyfile(main_dt, second_dt)
        print(f"[OK] Вторая копия {dt_names[1]} успешно создана: {os.path.getsize(second_dt)} байт")

    # 4. Синхронизация на флешку E:\Программирование 1С\
    if os.path.exists(r"E:\Программирование 1С"):
        os.makedirs(flash_dir, exist_ok=True)
        for dt_name in dt_names:
            src_dt = os.path.join(lab_dir, dt_name)
            dst_dt = os.path.join(flash_dir, dt_name)
            shutil.copyfile(src_dt, dst_dt)
            print(f"[OK] Зеркало на флешке создано: {dst_dt}")

    return True

def main():
    all_ok = True
    for lab in LABS:
        ok = process_lab(lab)
        if not ok:
            all_ok = False

    print("=" * 60)
    if all_ok:
        print("  ВСЕ БАЗЫ УСПЕШНО ОБНОВЛЕНЫ И ВЫГРУЖЕНЫ НА 100%!")
    else:
        print("  ОБНАРУЖЕНЫ ОШИБКИ ПРИ ОБРАБОТКЕ БАЗ 1С!")
    print("=" * 60)
    sys.exit(0 if all_ok else 1)

if __name__ == "__main__":
    main()
