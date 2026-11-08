@echo off
chcp 65001 >nul
echo ======================================================================
echo    СОЗДАНИЕ ЧИСТОГО АРХИВА ПРОЕКТА ДЛЯ ПЕРЕДАЧИ ДРУГУ
echo ======================================================================
echo.

REM 1. Проверка запущенных процессов 1С
tasklist /fi "imagename eq 1cv8.exe" 2>nul | find /i "1cv8.exe" >nul
if %errorlevel% equ 0 (
    echo [ВНИМАНИЕ] Обнаружен запущенный процесс 1C (1cv8.exe)!
    echo Пожалуйста, закройте 1С:Предприятие и Конфигуратор перед архивацией,
    echo чтобы база данных скопировалась без блокировок.
    echo.
    pause
)

tasklist /fi "imagename eq 1cv8c.exe" 2>nul | find /i "1cv8c.exe" >nul
if %errorlevel% equ 0 (
    echo [ВНИМАНИЕ] Обнаружен запущенный тонкий клиент 1C (1cv8c.exe)!
    echo Пожалуйста, закройте 1С:Предприятие перед архивацией.
    echo.
    pause
)

echo [*] Формирование архива проекта...
echo     Исключаются: временные файлы, кэши, тяжелый .venv (150 МБ)
echo.

set "OUT_ZIP=%USERPROFILE%\Desktop\1c_labs_full.zip"
if not exist "%USERPROFILE%\Desktop" (
    set "OUT_ZIP=D:\1c_labs_full.zip"
)

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
    "$source = 'd:\1с лабы';" ^
    "$dest = '%OUT_ZIP%';" ^
    "if (Test-Path $dest) { Remove-Item $dest -Force };" ^
    "Write-Host 'Упаковка файлов в архив... Пожалуйста, подождите.';" ^
    "$exclude = @('*\tools\1c-syntax-mcp\.venv\*', '*\__pycache__\*', '*.lck', '*.cfl', '*.tmp');" ^
    "$files = Get-ChildItem -Path $source -Recurse -File | Where-Object { $item = $_; -not ($exclude | Where-Object { $item.FullName -like $_ }) };" ^
    "$tempDir = Join-Path $env:TEMP ('1c_export_' + [System.Guid]::NewGuid().ToString('N'));" ^
    "New-Item -ItemType Directory -Path $tempDir | Out-Null;" ^
    "try {" ^
    "    foreach ($f in $files) {" ^
    "        $rel = $f.FullName.Substring($source.Length).TrimStart('\', '/');" ^
    "        $target = Join-Path $tempDir $rel;" ^
    "        $dir = [System.IO.Path]::GetDirectoryName($target);" ^
    "        if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null };" ^
    "        Copy-Item $f.FullName -Destination $target -Force;" ^
    "    };" ^
    "    Compress-Archive -Path (Join-Path $tempDir '*') -DestinationPath $dest -CompressionLevel Optimal;" ^
    "} finally {" ^
    "    Remove-Item $tempDir -Recurse -Force -ErrorAction SilentlyContinue;" ^
    "};" ^
    "$sizeMB = [math]::Round((Get-Item $dest).Length / 1MB, 2);" ^
    "Write-Host 'Архив успешно создан: ' $dest ' (' $sizeMB ' МБ)' -ForegroundColor Green;"

echo.
echo ======================================================================
echo Архив готов! Вы можете передать его другу через Telegram или диск.
echo ======================================================================
pause
