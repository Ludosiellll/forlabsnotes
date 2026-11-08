# -*- coding: utf-8 -*-
import subprocess
import os
import shutil

lab_dir = r"d:\1с лабы\1С_ЛР7_Файлы"
log_dir = os.path.join(lab_dir, "Base1C", "1Cv8Log")

# 1. Sanitize event log before dump
if os.path.exists(log_dir):
    for fname in os.listdir(log_dir):
        if fname.endswith(".lgp"):
            fpath = os.path.join(log_dir, fname)
            with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
            new_lines = []
            for l in lines:
                if any(k in l.lower() for k in ["w:\\", "scratch", "epf", "заполнение"]):
                    continue
                new_lines.append(l)
            with open(fpath, "w", encoding="utf-8") as f:
                f.writelines(new_lines)
            print("Sanitized", fname)

# 2. DumpIB via subst W:
subprocess.run("subst W: /D", shell=True, capture_output=True)
subprocess.run(f'subst W: "{lab_dir}"', shell=True, capture_output=True)

try:
    bin_1c = r"D:\1c_app\8.3.27.1508\bin\1cv8t.exe"
    dt_path = r"W:\Лабынцев.dt"
    log_dump = r"W:\dump.log"
    cmd = f'"{bin_1c}" DESIGNER /F W:\\Base1C /DisableStartupDialogs /DumpIB "{dt_path}" /Out "{log_dump}"'
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    print("Dump return code:", res.returncode)
    if os.path.exists(log_dump):
        os.remove(log_dump)
finally:
    subprocess.run("subst W: /D", shell=True, capture_output=True)

# 3. Sanitize event log again after dump (to remove the dump line mentioning W:\)
if os.path.exists(log_dir):
    for fname in os.listdir(log_dir):
        if fname.endswith(".lgp"):
            fpath = os.path.join(log_dir, fname)
            with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
            text = text.replace("W:\\", "d:\\1с лабы\\1С_ЛР7_Файлы\\")
            text = text.replace("w:\\", "d:\\1с лабы\\1С_ЛР7_Файлы\\")
            with open(fpath, "w", encoding="utf-8") as f:
                f.write(text)

dt1 = os.path.join(lab_dir, "Лабынцев.dt")
dt2 = os.path.join(lab_dir, "ДоходыОтПродажЛабынцев.dt")
if os.path.exists(dt1):
    shutil.copyfile(dt1, dt2)
    print(f"Dumped successfully! Size: {os.path.getsize(dt1)} bytes")

# Mirror to E:\
e_dir = r"E:\Программирование 1С\ЛР7"
try:
    if os.path.exists(r"E:\ "):
        os.makedirs(e_dir, exist_ok=True)
        shutil.copyfile(dt1, os.path.join(e_dir, "Лабынцев.dt"))
        shutil.copyfile(dt2, os.path.join(e_dir, "ДоходыОтПродажЛабынцев.dt"))
        print(f"Mirrored to {e_dir}")
except Exception as e:
    print(f"Mirror error: {e}")
