# Загрузка конфигурации из XML в базу с обновлением БД.
# Использование: load-config.ps1 <XML_DIR> [FILES] [skipdbupdate]
#   XML_DIR      — каталог с XML-файлами конфигурации
#   FILES        — (опционально) список файлов через запятую для частичной загрузки
#   skipdbupdate — (опционально) пропустить обновление конфигурации БД
# По умолчанию после загрузки выполняется обновление конфигурации БД.
# Требует .1c-devbase.ps1 в текущем каталоге.
param(
	[Parameter(Mandatory, Position = 0)][string]$XmlDir,
	[Parameter(Position = 1)][string]$Arg2,
	[Parameter(Position = 2)][string]$Arg3
)
. "$PSScriptRoot\_common.ps1"
$devBasePath = Get-DevBasePath; . $devBasePath

$files = ''
$skipUpdate = $false

# %2 может быть списком файлов ИЛИ "skipdbupdate"; %3 — только "skipdbupdate".
if ($Arg2 -ieq 'skipdbupdate') {
	$skipUpdate = $true
} elseif ($Arg2) {
	$files = $Arg2
}
if ($Arg3 -ieq 'skipdbupdate') {
	$skipUpdate = $true
}

$load = @()
if ($files) {
	$load = @('-files', $files, '-Format', 'Hierarchical')
	Write-Host 'Частичная загрузка конфигурации...'
	Write-Host "  Источник: $XmlDir"
	Write-Host "  Файлы: $files"
} else {
	Write-Host 'Полная загрузка конфигурации...'
	Write-Host "  Источник: $XmlDir"
}

$upd = @()
if (-not $skipUpdate) {
	$upd = @('/UpdateDBCfg')
	Write-Host '  Обновление БД: да'
} else {
	Write-Host '  Обновление БД: нет'
}

# --- ЗАЩИТА: Проверка на пустые заглушки форм <ChildItems/> и <ChildItems></ChildItems> ---
$emptyForms = Get-ChildItem -Path $XmlDir -Filter "Form.xml" -Recurse -ErrorAction SilentlyContinue |
	Where-Object { (Get-Content $_.FullName -Raw -Encoding UTF8) -match '<ChildItems\s*(/>|>\s*</ChildItems>)' }

if ($emptyForms) {
	Write-Host '[GUARD] Обнаружены формы с пустыми элементами интерфейса! Автоматическая компиляция...' -ForegroundColor Yellow
	$formCompileScript = Join-Path $PSScriptRoot "../../1c-metadata-manage/tools/1c-form-compile/scripts/form-compile.ps1"
	foreach ($ef in $emptyForms) {
		if (Test-Path $formCompileScript) {
			Write-Host "  Автокомпиляция элементов формы: $($ef.FullName)"
			try {
				& $formCompileScript -FromObject -OutputPath $ef.FullName
			} catch {
				Write-Error "КРИТИЧЕСКАЯ ОШИБКА: Сбой автокомпиляции формы $($ef.FullName): $($_.Exception.Message)"
				exit 1
			}
		} else {
			Write-Error "КРИТИЧЕСКАЯ ОШИБКА: Файл $($ef.FullName) содержит пустой ChildItems, а компилятор не найден! Загрузка отменена."
			exit 1
		}
	}
}

$code = Invoke-Designer (@('/LoadConfigFromFiles', $XmlDir) + $load + @('-updateConfigDumpInfo') + $upd)

if ($code -eq 0) {
	Write-Host 'Загрузка завершена успешно'
	exit 0
} else {
	Write-Host 'Ошибка загрузки'
	exit 1
}
