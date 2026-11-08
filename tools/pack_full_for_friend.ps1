$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$desktop = [Environment]::GetFolderPath("Desktop")
$outZip = Join-Path $desktop "AI_OS_1C_Labs_Full.zip"
if (Test-Path $outZip) { Remove-Item $outZip -Force }

$tempDir = Join-Path $env:TEMP ("ai_os_pack_" + [System.Guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path $tempDir -Force | Out-Null

try {
    Write-Host "[1/4] Копирование рабочего пространства '1с лабы'..." -ForegroundColor Cyan
    $source = "d:\1с лабы"
    $excludePatterns = @(
        "*\tools\1c-syntax-mcp\.venv\*",
        "*\__pycache__\*",
        "*.lck",
        "*.cfl",
        "*.tmp",
        "*.log"
    )

    $files = Get-ChildItem -Path $source -Recurse -File | Where-Object {
        $filePath = $_.FullName
        $matched = $false
        foreach ($pat in $excludePatterns) {
            if ($filePath -like $pat) { $matched = $true; break }
        }
        -not $matched
    }

    foreach ($f in $files) {
        $rel = $f.FullName.Substring($source.Length).TrimStart('\', '/')
        $target = Join-Path $tempDir $rel
        $parent = [System.IO.Path]::GetDirectoryName($target)
        if (-not (Test-Path $parent)) { New-Item -ItemType Directory -Path $parent -Force | Out-Null }
        Copy-Item -LiteralPath $f.FullName -Destination $target -Force
    }

    Write-Host "[2/4] Копирование бинарников MGI-Mind и Codebase-Memory..." -ForegroundColor Cyan
    $aiOsBin = "C:\Users\denis\AppData\Local\AI OS\bin"
    $targetBin = Join-Path $tempDir "AI_OS_Binaries"
    New-Item -ItemType Directory -Path $targetBin -Force | Out-Null

    if (Test-Path $aiOsBin) {
        Get-ChildItem -Path $aiOsBin -File | ForEach-Object {
            Copy-Item -LiteralPath $_.FullName -Destination $targetBin -Force
        }
    }

    Write-Host "[3/4] Создание 1-кликового скрипта установки для друга..." -ForegroundColor Cyan
    $setupBatContent = @"
@echo off
chcp 65001 >nul
echo ======================================================================
echo   НАСТРОЙКА AI OS, MGI-MIND И 1С-СКИЛЛОВ ДЛЯ ВАШЕГО КОМПЬЮТЕРА
echo ======================================================================
echo.
echo [*] Шаг 1: Установка бинарников MGI-Mind и Codebase-Memory...
set "TARGET_BIN=%LOCALAPPDATA%\AI OS\bin"
if not exist "%TARGET_BIN%" mkdir "%TARGET_BIN%"
if exist "%~dp0AI_OS_Binaries" (
    copy /Y "%~dp0AI_OS_Binaries\*.*" "%TARGET_BIN%\" >nul
    echo [+] Модули памяти и семантического анализа успешно скопированы в %TARGET_BIN%
)

echo [*] Шаг 2: Настройка файла .mcp.json под ваше имя пользователя...
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
    "`$mcpFile = Join-Path '%~dp0' '.mcp.json';" ^
    "if (Test-Path `$mcpFile) {" ^
    "    `$content = Get-Content `$mcpFile -Raw -Encoding UTF8;" ^
    "    `$fixed = `$content -replace 'C:\\\\Users\\\\[^\\\\]+\\\\AppData\\\\Local\\\\AI OS', ('C:\\Users\\' + `$env:USERNAME + '\\AppData\\Local\\AI OS' -replace '\\', '\\\\');" ^
    "    `$fixed = `$fixed -replace 'd:\\\\1с лабы', ('%~dp0'.TrimEnd('\') -replace '\\', '\\\\');" ^
    "    [System.IO.File]::WriteAllText(`$mcpFile, `$fixed, [System.Text.Encoding]::UTF8);" ^
    "    Write-Host '[+] Конфигурация .mcp.json адаптирована под пользователя ' `$env:USERNAME -ForegroundColor Green;" ^
    "}"

echo [*] Шаг 3: Разблокировка файлов (снятие Mark-of-the-Web)...
powershell -NoProfile -ExecutionPolicy Bypass -Command "Get-ChildItem -Path '%~dp0' -Recurse -File | Unblock-File -ErrorAction SilentlyContinue"

echo.
echo ======================================================================
echo   ГОТОВО! ВСЕ ФУНКЦИИ И СКИЛЛЫ АКТИВИРОВАНЫ!
echo ======================================================================
echo Теперь просто откройте эту папку в вашем ИИ-редакторе:
echo   - Antigravity, Cursor, Claude Code или VS Code
echo ИИ автоматически получит все скиллы по 1С, память MGI-Mind и правила.
echo.
pause
"@
    [System.IO.File]::WriteAllText((Join-Path $tempDir "1_НАЖМИ_МЕНЯ_ДЛЯ_НАСТРОЙКИ.bat"), $setupBatContent, [System.Text.Encoding]::UTF8)

    Write-Host "[4/4] Сжатие в финальный ZIP-архив: $outZip..." -ForegroundColor Cyan
    Compress-Archive -Path (Join-Path $tempDir "*") -DestinationPath $outZip -CompressionLevel Optimal

    $sizeMB = [math]::Round((Get-Item $outZip).Length / 1MB, 2)
    Write-Host ""
    Write-Host "======================================================================" -ForegroundColor Green
    Write-Host "УСПЕХ! Полный архив готов:" -ForegroundColor Green
    Write-Host "$outZip ($sizeMB МБ)" -ForegroundColor Yellow
    Write-Host "======================================================================" -ForegroundColor Green

} finally {
    Remove-Item $tempDir -Recurse -Force -ErrorAction SilentlyContinue
}
