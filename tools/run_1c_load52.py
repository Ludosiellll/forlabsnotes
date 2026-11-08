# -*- coding: utf-8 -*-
import subprocess
import os

one_c = r"D:\1c_app\8.3.27.1508\bin\1cv8t.exe"
base_dir = r"d:\1с лабы\1С_ЛР5.2_Файлы\Base1C"
src_dir = r"d:\1с лабы\1С_ЛР5.2_Файлы\src"
log_file = r"d:\1с лабы\1С_ЛР5.2_Файлы\load.log"

cmd = [
    one_c,
    "DESIGNER",
    "/F", base_dir,
    "/LoadConfigFromFiles", src_dir,
    "/UpdateDBCfg",
    "/Out", log_file
]

print("Executing 1C load config command...")
res = subprocess.run(cmd, capture_output=True)
print("Return code:", res.returncode)

if os.path.exists(log_file):
    try:
        with open(log_file, "r", encoding="cp1251") as f:
            print("Log content:\n", f.read())
    except Exception as e:
        with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
            print("Log content (utf-8):\n", f.read())
else:
    print("Log file not created!")
