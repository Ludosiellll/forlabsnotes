import os
import shutil
import zipfile
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

desktop = os.path.join(os.environ['USERPROFILE'], 'Desktop')
out_zip = os.path.join(desktop, 'AI_OS_1C_Labs_Full.zip')

print(f"[*] Начало создания полного архива для друга: {out_zip}")

source_dir = r"d:\1с лабы"
ai_os_bin = os.path.join(os.environ['LOCALAPPDATA'], 'AI OS', 'bin')

exclude_dirs = {'.venv', '__pycache__', '.git'}
exclude_exts = {'.lck', '.cfl', '.tmp'}

setup_bat = r"""@echo off
chcp 65001 >nul
echo ======================================================================
echo   НАСТРОЙКА AI OS, MGI-MIND И ВСЕХ СКИЛЛОВ ДЛЯ ВАШЕГО КОМПЬЮТЕРА
echo ======================================================================
echo.

echo [*] Шаг 1: Копирование бинарников MGI-Mind и Codebase-Memory...
set "TARGET_BIN=%LOCALAPPDATA%\AI OS\bin"
if not exist "%TARGET_BIN%" mkdir "%TARGET_BIN%"
if exist "%~dp0AI_OS_Binaries" (
    copy /Y "%~dp0AI_OS_Binaries\*.*" "%TARGET_BIN%\" >nul
    echo [+] Бинарники памяти MGI-Mind успешно установлены в %TARGET_BIN%
)

echo [*] Шаг 2: Настройка .mcp.json под ваше имя пользователя...
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
    "$mcpFile = Join-Path '%~dp0' '.mcp.json';" ^
    "if (Test-Path $mcpFile) {" ^
    "    $content = [System.IO.File]::ReadAllText($mcpFile, [System.Text.Encoding]::UTF8);" ^
    "    $fixed = $content -replace 'C:\\\\Users\\\\[^\\\\]+\\\\AppData\\\\Local\\\\AI OS', ('C:\\Users\\' + $env:USERNAME + '\\AppData\\Local\\AI OS' -replace '\\', '\\\\');" ^
    "    $fixed = $fixed -replace 'd:\\\\1с лабы', ('%~dp0'.TrimEnd('\') -replace '\\', '\\\\');" ^
    "    [System.IO.File]::WriteAllText($mcpFile, $fixed, [System.Text.Encoding]::UTF8);" ^
    "    Write-Host '[+] Конфигурация MCP адаптирована под пользователя ' $env:USERNAME -ForegroundColor Green;" ^
    "}"

echo [*] Шаг 3: Снятие блокировок Windows (Mark-of-the-Web)...
powershell -NoProfile -ExecutionPolicy Bypass -Command "Get-ChildItem -Path '%~dp0' -Recurse -File | Unblock-File -ErrorAction SilentlyContinue"

echo.
echo ======================================================================
echo   ГОТОВО! ВСЕ СКИЛЛЫ, ХУКИ И ПАМЯТЬ АКТИВИРОВАНЫ!
echo ======================================================================
echo Теперь просто откройте эту папку в вашем ИИ-редакторе:
echo   - Antigravity, Cursor, Claude Code или VS Code
echo ИИ автоматически получит все функции, память MGI-Mind и скиллы.
echo.
pause
"""

with zipfile.ZipFile(out_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
    print("[1/3] Упаковка рабочего пространства '1с лабы'...")
    for root, dirs, files in os.walk(source_dir):
        dirs[:] = [d for d in dirs if d not in exclude_dirs and not d.startswith('.venv')]
        
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in exclude_exts:
                continue
            
            full_path = os.path.join(root, file)
            # Skip python venv inside tools
            if r"1c-syntax-mcp\.venv" in full_path:
                continue
                
            rel_path = os.path.relpath(full_path, source_dir)
            zf.write(full_path, arcname=rel_path)

    print("[2/3] Добавление бинарников MGI-Mind и Codebase-Memory...")
    if os.path.exists(ai_os_bin):
        for file in os.listdir(ai_os_bin):
            full_path = os.path.join(ai_os_bin, file)
            if os.path.isfile(full_path):
                zf.write(full_path, arcname=os.path.join("AI_OS_Binaries", file))

    print("[3/3] Добавление файла автонастройки '1_НАЖМИ_МЕНЯ_ДЛЯ_НАСТРОЙКИ.bat'...")
    zf.writestr("1_НАЖМИ_МЕНЯ_ДЛЯ_НАСТРОЙКИ.bat", setup_bat.encode('utf-8-sig'))

size_mb = round(os.path.getsize(out_zip) / (1024 * 1024), 2)
print(f"\n[SUCCESS] Архив успешно создан:")
print(f"Путь: {out_zip}")
print(f"Размер: {size_mb} МБ")
