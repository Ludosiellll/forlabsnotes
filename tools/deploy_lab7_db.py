# -*- coding: utf-8 -*-
import subprocess
import os
import time

def run_cmd(cmd):
    print("Running:", cmd)
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    print("STDOUT:", res.stdout)
    if res.stderr:
        print("STDERR:", res.stderr)
    return res.returncode

def deploy():
    # 1. unmount W: if mounted
    subprocess.run("subst W: /D", shell=True, capture_output=True)

    # 2. mount W:
    target_dir = r"d:\1с лабы\1С_ЛР7_Файлы"
    rc = run_cmd(f'subst W: "{target_dir}"')
    if rc != 0:
        print("Failed to mount W:")
        return

    try:
        # Create infobase
        bin_1c = r"D:\1c_app\8.3.27.1508\bin\1cv8t.exe"
        ib_dir = r"W:\Base1C"
        src_dir = r"W:\src"
        log_create = r"W:\create_ib.log"
        log_load = r"W:\load_cfg.log"

        if os.path.exists(log_create):
            os.remove(log_create)
        if os.path.exists(log_load):
            os.remove(log_load)

        print("--- Step 1: CREATEINFOBASE ---")
        cmd_create = f'"{bin_1c}" CREATEINFOBASE File="{ib_dir}" /Out "{log_create}"'
        rc = run_cmd(cmd_create)
        print("Create IB Return Code:", rc)
        if os.path.exists(log_create):
            with open(log_create, "r", encoding="cp1251", errors="replace") as f:
                print("Create IB Log:\n", f.read())

        print("--- Step 2: LoadConfigFromFiles & UpdateDBCfg ---")
        cmd_load = f'"{bin_1c}" DESIGNER /F "{ib_dir}" /DisableStartupDialogs /LoadConfigFromFiles "{src_dir}" /UpdateDBCfg /Out "{log_load}"'
        rc = run_cmd(cmd_load)
        print("Load Config Return Code:", rc)
        if os.path.exists(log_load):
            with open(log_load, "r", encoding="cp1251", errors="replace") as f:
                print("Load Config Log:\n", f.read())

    finally:
        subprocess.run("subst W: /D", shell=True, capture_output=True)
        print("Unmounted W:")

if __name__ == "__main__":
    deploy()
