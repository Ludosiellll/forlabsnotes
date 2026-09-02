[CmdletBinding()]
param(
    [string]$Root = "",
    [switch]$Open
)

# AI OS Control Center - "технический паспорт изделия": самодостаточный
# HTML-отчет .local/dashboard.html о всей системе, собранный из реальных
# локальных данных (health-прогон, журналы, фоновая автоматика, память, экзамены,
# Task_Log, git). Без сети и зависимостей - двойной клик. Каждая цифра
# приходит из источника, ничего не выдумывается.

$ErrorActionPreference = "Stop"
$runningOnWindows = $PSVersionTable.PSEdition -eq 'Desktop' -or $IsWindows
$powerShellExecutable = (Get-Process -Id $PID).Path
$installerFile = if ($runningOnWindows) { 'AI_OS_Setup_v%%SETUPVER%%_x64.exe' } else { 'AI_OS_Setup_v%%SETUPVER%%_linux_x86_64.AppImage / .deb' }
if ([string]::IsNullOrWhiteSpace($Root)) {
    $Root = Split-Path -Parent $PSScriptRoot
}
$localDir = Join-Path $Root ".local"
if (-not (Test-Path -LiteralPath $localDir)) {
    New-Item -ItemType Directory -Force -Path $localDir | Out-Null
}
$ru = [System.Globalization.CultureInfo]::GetCultureInfo('ru-RU')

function Esc([string]$s) {
    if ($null -eq $s) { return "" }
    return $s.Replace('&', '&amp;').Replace('<', '&lt;').Replace('>', '&gt;').Replace('"', '&quot;').Replace("'", '&#39;')
}
function Num([long]$n) { return $n.ToString('N0', $ru) }
function PluralRu([long]$n, [string]$one, [string]$few, [string]$many) {
    $m10 = $n % 10; $m100 = $n % 100
    if ($m10 -eq 1 -and $m100 -ne 11) { return $one }
    if ($m10 -ge 2 -and $m10 -le 4 -and ($m100 -lt 12 -or $m100 -gt 14)) { return $few }
    return $many
}
# Типовые detail-строки health-чека по-русски; незнакомые остаются как есть.
function TranslateDetail([string]$d) {
    if ($null -eq $d) { return '' }
    $map = @{
        'all file targets resolved' = 'все ссылки ведут на существующие заметки'
        'all file nodes resolve' = 'все файловые узлы карты существуют'
        'doctor OK' = 'диагностика памяти: всё в порядке'
        'no high-confidence patterns' = 'подозрительных строк не найдено'
        'no leaks (curated detector set)' = 'утечек нет (расширенный набор детекторов)'
        'no markdown newer than last apply-sync' = 'память не отстаёт от заметок'
        'no markdown under 50_Meetings/_transcripts' = 'сырые расшифровки не лежат среди заметок'
        'scheduled task present, LastTaskResult=0' = 'задача в планировщике есть, последний запуск успешен'
        'sync, watcher and readiness scripts found' = 'скрипты синка, сторожа и самопроверки на месте'
        'valid JSON' = 'корректный JSON'
        'LastTaskResult=0' = 'последний запуск успешен'
    }
    if ($map.ContainsKey($d)) { return $map[$d] }
    $m = [regex]::Match($d, "^task '(.+)' running$")
    if ($m.Success) { return ('задача "' + $m.Groups[1].Value + '" работает') }
    $m = [regex]::Match($d, '^library (\S+): (\d+) memories$')
    if ($m.Success) { return ('библиотека ' + $m.Groups[1].Value + ': ' + $m.Groups[2].Value + ' ' + (PluralRu ([long]$m.Groups[2].Value) 'запись' 'записи' 'записей')) }
    $m = [regex]::Match($d, '^nodes=(\d+), edges=(\d+)$')
    if ($m.Success) { return ('узлов ' + $m.Groups[1].Value + ', связей ' + $m.Groups[2].Value) }
    return $d
}

# ---------- 1. Свежий health-прогон ----------
$healthScript = Join-Path $Root "tools/check_agent_health.ps1"
$prevEap = $ErrorActionPreference; $ErrorActionPreference = 'Continue'
$healthRaw = & $powerShellExecutable -NoProfile -File $healthScript -Root $Root
$ErrorActionPreference = $prevEap
$checks = @()
foreach ($line in $healthRaw) {
    $m = [regex]::Match([string]$line, '^\s*([\w.-]+)\s+(OK|WARN|FAIL|SKIP)\b\s*(.*)$')
    if ($m.Success) {
        $checks += [pscustomobject]@{ Name = $m.Groups[1].Value; Status = $m.Groups[2].Value; Detail = $m.Groups[3].Value.Trim() }
    }
}
$failN = @($checks | Where-Object { $_.Status -eq 'FAIL' }).Count
$warnN = @($checks | Where-Object { $_.Status -eq 'WARN' }).Count
$okN   = @($checks | Where-Object { $_.Status -eq 'OK' }).Count
$skipN = @($checks | Where-Object { $_.Status -eq 'SKIP' }).Count
if ($checks.Count -eq 0) { $hero = 'поверка не выполнена'; $stampTitle = 'ПОВЕРКА НЕ ПРОВЕДЕНА'; $stampCls = 'bad' }
elseif ($failN -gt 0) { $hero = 'есть проблемы'; $stampTitle = 'НЕ ПРОШЛА ПОВЕРКУ'; $stampCls = 'bad' }
elseif ($warnN -gt 0) { $hero = 'есть предупреждения'; $stampTitle = 'ГОДНА С ЗАМЕЧАНИЯМИ'; $stampCls = 'warn' }
else { $hero = 'система здорова'; $stampTitle = 'ПОВЕРЕНО'; $stampCls = 'good' }

# ---------- 2. Автоматика (задачи ищутся по пути скрипта, не по имени) ----------
function Get-TaskByScript([string]$scriptName) {
    try {
        $p = [regex]::Escape((Join-Path $Root ("tools/" + $scriptName)))
        $t = @(Get-ScheduledTask -ErrorAction Stop | Where-Object {
            @($_.Actions | ForEach-Object { "$($_.Execute) $($_.Arguments)" }) -match $p
        })
        if ($t.Count) { return $t[0] } else { return $null }
    } catch { return $null }
}
function TaskBadge($task, [string]$runningIsHealthy) {
    if ($null -eq $task) { return @('нет задачи', 'muted') }
    if ($runningIsHealthy -eq 'yes') {
        if ($task.State -eq 'Running') { return @('работает', 'good') } else { return @("остановлен ($($task.State))", 'warn') }
    }
    $info = Get-ScheduledTaskInfo -TaskName $task.TaskName -TaskPath $task.TaskPath -ErrorAction SilentlyContinue
    if ($info -and $info.LastTaskResult -eq 0) { return @("ок, посл. запуск $($info.LastRunTime.ToString('dd.MM HH:mm'))", 'good') }
    return @("посл. результат: $($info.LastTaskResult)", 'warn')
}
$readyTask = $null
if ($runningOnWindows) {
    $watcherBadge   = TaskBadge (Get-TaskByScript 'watch_agent_reimport.ps1') 'yes'
    $readyTask      = Get-TaskByScript 'run_scheduled_readiness.ps1'
    $readinessBadge = TaskBadge $readyTask 'no'
    $memstartBadge  = TaskBadge (Get-TaskByScript 'start_mgimind.ps1') 'no'
    $readySub = 'задача в планировщике не найдена'
} else {
    $stateHome = if ($env:XDG_STATE_HOME) { $env:XDG_STATE_HOME } else { Join-Path $HOME '.local/state' }
    $pidPath = Join-Path $stateHome 'ai-os/supervisor.pid'
    $supervisorActive = $false
    if (Test-Path -LiteralPath $pidPath) {
        $knownPid = 0
        if ([int]::TryParse((Get-Content -LiteralPath $pidPath -Raw).Trim(), [ref]$knownPid)) {
            $supervisorActive = $null -ne (Get-Process -Id $knownPid -ErrorAction SilentlyContinue)
        }
    }
    $badge = if ($supervisorActive) { @('работает', 'good') } else { @('ожидает запуска', 'warn') }
    $watcherBadge = $badge; $readinessBadge = $badge; $memstartBadge = $badge
    $readySub = 'один Linux supervisor обслуживает память, изменения заметок, поверку и активный пульт'
}
# Описание расписания Windows читается из планировщика, а не пишется руками.
if ($runningOnWindows -and $readyTask) {
    $tt = (@($readyTask.Triggers | ForEach-Object { try { $_.CimClass.CimClassName } catch { '' } }) -join ' ')
    $parts = @()
    if ($tt -match 'LogonTrigger') { $parts += 'при входе в систему' }
    if ($tt -match 'DailyTrigger') { $parts += 'ежедневно' }
    $hiddenTxt = ''
    if ((@($readyTask.Actions | ForEach-Object { $_.Arguments }) -join ' ') -match 'WindowStyle\s+Hidden') { $hiddenTxt = ', в скрытом окне' }
    if ($parts.Count) { $readySub = 'запускается ' + ($parts -join ' и ') + $hiddenTxt + ' (прочитано из планировщика при сборке)' }
    else { $readySub = 'задача есть, но расписание нестандартное' }
}

# ---------- 3. Память ----------
$memTool = $null
$memoryLibrary = ''
$cfgPath = Join-Path $Root "tools/ai_os.config.json"
if (Test-Path -LiteralPath $cfgPath) {
    try {
        $cfg = Get-Content -Raw -Encoding UTF8 $cfgPath | ConvertFrom-Json
        $memoryLibrary = [string]$cfg.memoryLibrary
        if ($cfg.memoryToolPath -and (Test-Path -LiteralPath $cfg.memoryToolPath)) { $memTool = $cfg.memoryToolPath }
    } catch {}
}
if (-not $memTool) {
    if ($runningOnWindows) {
        $known = Join-Path $env:LOCALAPPDATA 'Programs/mgimind/mgimind.exe'
    } else {
        $dataHome = if ($env:XDG_DATA_HOME) { $env:XDG_DATA_HOME } else { Join-Path $HOME '.local/share' }
        $known = Join-Path $dataHome 'ai-os/bin/mgimind'
    }
    if (Test-Path -LiteralPath $known) { $memTool = $known }
    else { $c = Get-Command mgimind -ErrorAction SilentlyContinue; if ($c) { $memTool = $c.Source } }
}
$memLine = 'память не подключена'; $memClass = 'muted'; $memN = -1
if ($memTool) {
    $prevEap = $ErrorActionPreference; $ErrorActionPreference = 'Continue'
    $stats = & $memTool stats --json 2>$null
    $ErrorActionPreference = $prevEap
    try {
        $statsObject = ($stats -join "`n") | ConvertFrom-Json
        $libraryProperty = @($statsObject.libraries.PSObject.Properties | Where-Object { $_.Name -eq $memoryLibrary } | Select-Object -First 1)
        if ([string]::IsNullOrWhiteSpace($memoryLibrary)) {
            $memLine = 'имя памяти проекта не настроено'; $memClass = 'warn'
        } elseif ($libraryProperty.Count -eq 1) {
            $memN = [long]$libraryProperty[0].Value
            $memLine = "$(Num $memN) $(PluralRu $memN 'запись' 'записи' 'записей') в памяти проекта"
            $memClass = 'good'
        } else {
            $memN = 0
            $memLine = 'память проекта пока пуста'
            $memClass = 'warn'
        }
    } catch {
        $memLine = 'не удалось получить счётчик памяти проекта'; $memClass = 'warn'
    }
}
$lastSync = 'нет данных'
$syncLog = Join-Path $localDir 'mgimind-sync.log'
if (Test-Path -LiteralPath $syncLog) {
    $okLines = @(Get-Content -Encoding UTF8 $syncLog | Where-Object { $_ -match '^\[(.+?)\] OK ' })
    if ($okLines.Count) { $lastSync = ([regex]::Match($okLines[-1], '^\[(.+?)\]')).Groups[1].Value }
}

# ---------- 4. Watcher: счетчики текущего журнала ----------
$autoSyncs = 0; $failedSyncs = 0
$wlPath = Join-Path $localDir 'mgimind-watch.log'
if (Test-Path -LiteralPath $wlPath) {
    $c = Get-Content -Encoding UTF8 $wlPath
    $autoSyncs = @($c | Where-Object { $_ -match 'Sync complete' }).Count
    $failedSyncs = @($c | Where-Object { $_ -match 'Sync FAILED' }).Count
}

# ---------- 5. История самопроверок ----------
$histRuns = @(); $totalRuns = 0
$hLog = Join-Path $localDir 'health-check.log'
if (Test-Path -LiteralPath $hLog) {
    $allLines = @(Get-Content -Encoding UTF8 $hLog)
    $totalRuns = $allLines.Count
    foreach ($r in ($allLines | Select-Object -Last 40)) {
        $mm = [regex]::Match($r, 'WARN=(\d*)\s+FAIL=(\d*)')
        if (-not $mm.Success) { continue }
        $w = 0; $f = 0
        if ($mm.Groups[1].Value) { $w = [int]$mm.Groups[1].Value }
        if ($mm.Groups[2].Value) { $f = [int]$mm.Groups[2].Value }
        $ts = ([regex]::Match($r, '^\[(.+?)\]')).Groups[1].Value
        $histRuns += [pscustomobject]@{ TS = $ts; W = $w; F = $f }
    }
}
$histSvg = ''
if ($histRuns.Count) {
    $n = $histRuns.Count
    $barW = [math]::Max(6, [math]::Min(16, [math]::Floor(636 / $n)))
    $sb = New-Object System.Text.StringBuilder
    [void]$sb.Append('<svg viewBox="0 0 680 112" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="История самопроверок">')
    [void]$sb.Append('<line x1="20" y1="96" x2="660" y2="96" stroke="#8f8874" stroke-width="1"/>')
    for ($i = 0; $i -lt $n; $i++) {
        $run = $histRuns[$i]
        $h = 40; $fill = '#0d6b52'
        if ($run.F -gt 0) { $h = 76; $fill = '#a63a2b' } elseif ($run.W -gt 0) { $h = 58; $fill = '#9a6b15' }
        $x = 22 + $i * $barW
        $y = 96 - $h
        [void]$sb.Append("<rect x='$x' y='$y' width='$($barW - 2)' height='$h' fill='$fill'><title>$(Esc $run.TS): WARN=$($run.W) FAIL=$($run.F)</title></rect>")
    }
    [void]$sb.Append('</svg>')
    $histSvg = $sb.ToString()
} else {
    $histSvg = '<div class="empty">Журнал самопроверок пока пуст.</div>'
}
$cleanRuns = @($histRuns | Where-Object { $_.W -eq 0 -and $_.F -eq 0 }).Count

# ---------- 6. Экзамены: список из набора + сданные из журнала прогонов ----------
$evalRows = @()
$suite = Join-Path $Root "70_Resources/AI_OS_Eval_Prompt_Suite.md"
if (Test-Path -LiteralPath $suite) {
    $sm = [regex]::Matches([string](Get-Content -Raw -Encoding UTF8 $suite), '\|\s*(E\d{2})-([a-z0-9-]+)\s*\|')
    foreach ($m in $sm) { $evalRows += [pscustomobject]@{ Id = $m.Groups[1].Value; Name = $m.Groups[2].Value } }
}
$passedIds = @{}
$runNotes = @(Get-ChildItem (Join-Path $Root "70_Resources") -Filter "AI_OS_Eval_Run*.md" -ErrorAction SilentlyContinue)
foreach ($rn in $runNotes) {
    $pm = [regex]::Matches([string](Get-Content -Raw -Encoding UTF8 $rn.FullName), '(E\d{2})-[a-z0-9-]+[^\r\n]*?\|\s*Pass\s*\|')
    foreach ($m in $pm) { $passedIds[$m.Groups[1].Value] = $true }
}
$evalTotal = $evalRows.Count
$evalPass = @($passedIds.Keys).Count
$evalGrid = ''
foreach ($er in $evalRows) {
    $cls = 'ex'; if ($passedIds.ContainsKey($er.Id)) { $cls = 'ex ex-pass' }
    $evalGrid += "<span class='$cls' title='$(Esc ($er.Id + '-' + $er.Name))'>$($er.Id.Substring(1))</span>"
}

# ---------- 7. Безопасность ----------
$sec = @($checks | Where-Object { $_.Name -match 'secret|gitleaks' })
$secBad = @($sec | Where-Object { $_.Status -eq 'FAIL' }).Count
if ($secBad -gt 0) { $secLine = 'найдены возможные секреты — разберись'; $secClass = 'bad' }
elseif (@($sec | Where-Object { $_.Status -eq 'OK' }).Count -ge 1) { $secLine = 'секретов в заметках не найдено'; $secClass = 'good' }
else { $secLine = 'сканеры не активны'; $secClass = 'muted' }
$gitleaksOn = (@($checks | Where-Object { $_.Name -eq 'gitleaks-scan' -and $_.Status -eq 'OK' }).Count -gt 0)

# ---------- 8. Журнал событий агентов ----------
$eventsHtml = ''
$journal = Join-Path $localDir 'agent-events.ndjson'
$evCount = 0
$evShown = 0
function Read-CargoPackageVersion([string]$RelativePath, [string]$Fallback) {
    $path = Join-Path $Root $RelativePath
    if (Test-Path -LiteralPath $path) {
        $match = [regex]::Match([string](Get-Content -Raw -Encoding UTF8 $path), '(?m)^version\s*=\s*"([^"]+)"')
        if ($match.Success) { return $match.Groups[1].Value }
    }
    return $Fallback
}
$setupVersion = Read-CargoPackageVersion 'tools/ai-os-installer-app/Cargo.toml' '0.4.5'
$controlVersion = Read-CargoPackageVersion 'tools/control-center-app/Cargo.toml' '0.6.2'
function Test-ObsoleteReleaseText([string]$Text) {
    if ([string]::IsNullOrWhiteSpace($Text)) { return $false }
    $allowedProductVersions = @($setupVersion, $controlVersion, '0.9.0')
    foreach ($versionMatch in [regex]::Matches($Text, '(?<!\d)0\.\d+\.\d+(?!\d)')) {
        if ($allowedProductVersions -notcontains $versionMatch.Value) { return $true }
    }
    $productPattern = '(?i)\b(?:AI\s*OS(?:\s+Setup)?|Setup|Control Center|template|kit)\b[^\r\n]{0,30}?\bv?(0\.\d+(?:\.\d+)?)\b'
    foreach ($releaseMatch in [regex]::Matches($Text, $productPattern)) {
        if ($allowedProductVersions -notcontains $releaseMatch.Groups[1].Value) { return $true }
    }
    return $false
}
if (Test-Path -LiteralPath $journal) {
    $lines = @(Get-Content -Encoding UTF8 $journal | Where-Object { $_.Trim() })
    $evCount = $lines.Count
    $visibleEvents = @()
    foreach ($l in $lines) {
        try { $candidate = $l | ConvertFrom-Json } catch { continue }
        $candidateText = [string]::Join(' ', @(
            [string]$candidate.task
            (@($candidate.actions) -join ' ')
            [string]$candidate.value
            (@($candidate.risks) -join ' ')
        ))
        if (-not (Test-ObsoleteReleaseText $candidateText)) { $visibleEvents += $candidate }
    }
    $visibleEvents = @($visibleEvents | Select-Object -Last 10)
    $evShown = $visibleEvents.Count
    foreach ($e in $visibleEvents) {
        $acts = Esc (@($e.actions) -join ' · ')
        $risks = ''
        if ($e.risks -and @($e.risks | Where-Object { $_ }).Count) { $risks = "<div class='ev-risks'>риски: $(Esc (@($e.risks) -join '; '))</div>" }
        $val = ''
        if ($e.value) { $val = "<div class='ev-value'>$(Esc $e.value)</div>" }
        $eventsHtml = "<div class='event'><div class='ev-head'><span class='ev-agent'>$(Esc $e.agent)</span><span class='ev-time'>$(Esc ($e.time -replace 'T',' '))</span></div><div class='ev-task'>$(Esc $e.task)</div><div class='ev-actions'>$acts</div>$val$risks</div>" + $eventsHtml
    }
}
if (-not $eventsHtml) { $eventsHtml = "<div class='empty'>Журнал пуст. Агенты добавляют события командой tools/log_agent_event.ps1 в конце задач.</div>" }

# ---------- 9. Хроника строительства из Task_Log ----------
$doneEntries = @()
$allDoneN = 0
$taskLog = Join-Path $Root '60_Tasks/Task_Log.md'
if (Test-Path -LiteralPath $taskLog) {
    foreach ($line in (Get-Content -Encoding UTF8 $taskLog)) {
        if ($line -match '^\s*-\s*\[x\]') { $allDoneN++ }
        $m = [regex]::Match($line, '^\s*-\s*\[x\]\s*(\d{4}-\d{2}-\d{2}):\s*(.+)$')
        if (-not $m.Success) { continue }
        $txt = $m.Groups[2].Value
        $txt = [regex]::Replace($txt, '\[\[(?:[^\]|/]+/)*([^\]|]+?)(\|[^\]]+)?\]\]', '$1')
        $txt = $txt.Replace('`', '').Replace('**', '')
        if ($txt.Length -gt 200) {
            $cut = $txt.Substring(0, 200); $sp = $cut.LastIndexOf(' ')
            if ($sp -gt 120) { $cut = $cut.Substring(0, $sp) }
            $txt = $cut.TrimEnd(' ,;:—-') + '…'
        }
        $doneEntries += [pscustomobject]@{ Date = $m.Groups[1].Value; Text = $txt }
    }
}
$timelineEntries = @($doneEntries | Where-Object { -not (Test-ObsoleteReleaseText $_.Text) } | Sort-Object Date -Descending | Select-Object -First 28)
$undatedN = $allDoneN - $doneEntries.Count
$undatedTxt = ''
if ($undatedN -gt 0) { $undatedTxt = "; ещё $undatedN $(PluralRu $undatedN 'раннее дело' 'ранних дела' 'ранних дел') без даты" }
$daysN = 0; $timelineHtml = ''; $cumSvg = ''
if ($timelineEntries.Count) {
    $byDate = @($timelineEntries | Group-Object Date | Sort-Object Name)
    $minD = [datetime]::ParseExact($byDate[0].Name, 'yyyy-MM-dd', $null)
    $daysN = ((Get-Date).Date - $minD.Date).Days + 1
    # график накопленных дел на миллиметровке
    $cum = 0; $pts = @()
    foreach ($g in $byDate) {
        $cum += $g.Count
        $pts += [pscustomobject]@{ D = [datetime]::ParseExact($g.Name, 'yyyy-MM-dd', $null); N = $cum }
    }
    $maxN = $pts[-1].N
    $maxD = (Get-Date).Date
    $span = [math]::Max(1, ($maxD - $minD.Date).Days)
    $sb = New-Object System.Text.StringBuilder
    [void]$sb.Append('<svg viewBox="0 0 680 224" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Накопление сделанного">')
    [void]$sb.Append('<line x1="40" y1="196" x2="660" y2="196" stroke="#8f8874" stroke-width="1"/>')
    [void]$sb.Append('<line x1="40" y1="196" x2="40" y2="16" stroke="#8f8874" stroke-width="1"/>')
    $ptStr = ''
    foreach ($p in $pts) {
        $x = [math]::Round(40 + (($p.D - $minD.Date).Days / $span) * 616, 1)
        $y = [math]::Round(196 - ($p.N / $maxN) * 168, 1)
        $ptStr += "$x,$y "
    }
    [void]$sb.Append("<polyline points='$($ptStr.Trim())' fill='none' stroke='#0d6b52' stroke-width='2'/>")
    foreach ($p in $pts) {
        $x = [math]::Round(40 + (($p.D - $minD.Date).Days / $span) * 616, 1)
        $y = [math]::Round(196 - ($p.N / $maxN) * 168, 1)
        [void]$sb.Append("<circle cx='$x' cy='$y' r='3.5' fill='#0d6b52'/>")
        [void]$sb.Append("<text x='$x' y='214' text-anchor='middle' font-size='11' fill='#6b6353' font-family='Consolas,monospace'>$($p.D.ToString('dd.MM'))</text>")
        [void]$sb.Append("<text x='$x' y='$($y - 8)' text-anchor='middle' font-size='11' fill='#211e17' font-family='Consolas,monospace'>$($p.N)</text>")
    }
    [void]$sb.Append('</svg>')
    $cumSvg = $sb.ToString()
    # лента: свежие дни сверху
    foreach ($g in ($byDate | Sort-Object Name -Descending)) {
        $d = [datetime]::ParseExact($g.Name, 'yyyy-MM-dd', $null)
        $timelineHtml += "<div class='tl-day'><div class='tl-date'>$($d.ToString('d MMMM yyyy', $ru)) · $($g.Count) $(PluralRu $g.Count 'дело' 'дела' 'дел')</div><ul>"
        foreach ($e in $g.Group) { $timelineHtml += "<li>$(Esc $e.Text)</li>" }
        $timelineHtml += '</ul></div>'
    }
}

# ---------- 10. Объем системы ----------
$dirMap = [ordered]@{
    '01_Index'     = 'Указатели и люди'
    '10_Project'   = 'Проект'
    '20_Domain'    = 'Предметная область'
    '30_Tech'      = 'Техника и код'
    '40_Decisions' = 'Решения'
    '50_Meetings'  = 'Встречи'
    '60_Tasks'     = 'Задачи'
    '70_Resources' = 'Методики и регламенты'
}
$dirStats = @(); $notesN = 0; $wordsN = 0; $linksN = 0
foreach ($k in $dirMap.Keys) {
    $dp = Join-Path $Root $k
    $files = @(Get-ChildItem $dp -Filter *.md -Recurse -ErrorAction SilentlyContinue)
    $w = 0
    foreach ($f in $files) {
        $raw = [string](Get-Content -Raw -Encoding UTF8 $f.FullName)
        $w += @($raw -split '\s+' | Where-Object { $_ }).Count
        $linksN += @([regex]::Matches($raw, '\[\[[^\]]+\]\]')).Count
    }
    $notesN += $files.Count; $wordsN += $w
    $dirStats += [pscustomobject]@{ Key = $k; Label = $dirMap[$k]; Files = $files.Count; Words = $w }
}
$maxWords = 1
foreach ($d in $dirStats) { if ($d.Words -gt $maxWords) { $maxWords = $d.Words } }
$dirBars = ''
foreach ($d in $dirStats) {
    $pct = [math]::Round(($d.Words / $maxWords) * 100)
    $dirBars += "<div class='vrow'><div class='vlabel'>$(Esc $d.Label)<span class='vkey'>$($d.Key)</span></div><div class='vbar'><div class='vfill' style='width:$pct%'></div></div><div class='vnum'>$($d.Files) $(PluralRu $d.Files 'заметка' 'заметки' 'заметок') · $(Num $d.Words) $(PluralRu $d.Words 'слово' 'слова' 'слов')</div></div>"
}
$commitsN = '—'
try {
    $prevEap = $ErrorActionPreference; $ErrorActionPreference = 'Continue'
    $g = git -C $Root rev-list --count HEAD 2>$null
    $ErrorActionPreference = $prevEap
    if ($g -match '^\d+$') { $commitsN = $g }
} catch {}

# ---------- 11. Следующие шаги (вычисляются, не выдумываются) ----------
$steps = @()
if ($failN -gt 0) { $steps += 'Разобраться с красными проверками в разделе 4 — это единственный приоритет.' }
if ($evalPass -eq 0 -and $evalTotal -gt 0) { $steps += "Прогнать первые экзамены агентов (в свежей сессии) — в наборе $evalTotal, записанных прохождений пока нет." }
if (@($checks | Where-Object { $_.Name -eq 'gitleaks-scan' -and $_.Status -ne 'OK' }).Count) { $steps += 'Поставить gitleaks (один файл) — глубокий скан секретов включится сам.' }
if ($memClass -eq 'muted') { $steps += 'Подключить слой памяти — пока агенты работают без быстрого поиска фактов.' }
if ($evCount -eq 0) { $steps += 'Попросить агента в конце следующей задачи записать событие в журнал (tools/log_agent_event.ps1).' }
if ($evalPass -gt 0 -and $evalPass -lt $evalTotal) { $steps += "Досдать экзамены поведения: записано $evalPass из $evalTotal (свежая сессия на каждый)." }
if (-not $steps.Count) { $steps += 'Всё зелёное. Работай — система следит за собой сама.' }
$stepsHtml = ''
foreach ($s in $steps) { $stepsHtml += "<li>$(Esc $s)</li>" }

# ---------- 12. Таблица проверок ----------
$rowsHtml = ''
foreach ($c in $checks) {
    $cls = @{ OK = 'good'; WARN = 'warn'; FAIL = 'bad'; SKIP = 'muted' }[$c.Status]
    $rowsHtml += "<tr><td class='cname'>$(Esc $c.Name)</td><td><span class='chip $cls'>$($c.Status)</span></td><td class='cdetail'>$(Esc (TranslateDetail $c.Detail))</td></tr>"
}

# Живые ячейки сравнительной таблицы: «да» только когда механизм подтверждён данными этого прогона.
$cmpHealth = "<td class='part'>задача не активна</td>"
if ($readinessBadge[1] -eq 'good') { $cmpHealth = "<td class='yes'>да</td>" }
$cmpSec = "<td class='part'>сканеры не активны</td>"
if ($secClass -eq 'good') { $cmpSec = "<td class='yes'>да</td>" } elseif ($secClass -eq 'bad') { $cmpSec = "<td class='part'>есть находки</td>" }
$cmpTrace = "<td class='part'>обязан по протоколу</td>"
if ($evCount -gt 0) { $cmpTrace = "<td class='yes'>ведётся</td>" }

# Утверждение про hook проверяется при сборке, а не пишется на веру.
$hookLine = 'Hook-напоминание при сборке паспорта не найдено — ворота памяти держатся на входных файлах агентов.'
$settingsPath = Join-Path $Root '.claude/settings.json'
if (Test-Path -LiteralPath $settingsPath) {
    if (([string](Get-Content -Raw -Encoding UTF8 $settingsPath)) -match 'UserPromptSubmit') {
        $hookLine = 'В сессиях Claude Code напоминание о воротах памяти вшивается в каждое сообщение автоматически (hook найден при сборке паспорта); Codex и Cursor получают то же правило через свои входные файлы.'
    }
}

$wsName = Split-Path $Root -Leaf
$stamp = (Get-Date).ToString('dd.MM.yyyy HH:mm')
$memNTxt = 'память не подключена'
if ($memN -ge 0) { $memNTxt = "$(Num $memN) $(PluralRu $memN 'запись' 'записи' 'записей')" }

# ---------- 13. Шаблон ----------
$html = @'
<!DOCTYPE html>
<html lang="ru"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>AI OS — технический паспорт</title>
<style>
  :root { color-scheme: dark; --bg:#080809; --panel:#141416; --panel2:#1b1b1f; --line:rgba(255,255,255,.11); --paper:#fff; --ash:#d1d3d4; --fog:#a7a9ac; --slate:#6d6e71; --signal:#7084ff; --voltage:#405bff; --cyan:#3dd6f5; --green:#4fce91; --amber:#ffbd5b; --red:#ff716b; --font:Inter,"Segoe UI Variable","Segoe UI",system-ui,sans-serif; --mono:"Cascadia Code",Consolas,monospace; }
  * { box-sizing: border-box; margin: 0; letter-spacing: 0; }
  html { scroll-behavior: smooth; background: var(--bg); }
  body { min-height:100vh; padding: 30px 18px 80px; background-color:var(--bg); background-image:linear-gradient(rgba(255,255,255,.024) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.024) 1px,transparent 1px); background-size:48px 48px; color:var(--ash); font:400 14px/1.68 var(--font); }
  a { color:#bac2ff; }
  .page { max-width: 1200px; margin: 0 auto; }
  .tw { overflow-x: auto; }
  .cover { position:relative; overflow:hidden; margin-bottom:32px; padding:46px 48px 32px; border:1px solid var(--line); border-radius:8px; background:rgba(14,14,16,.96); box-shadow:0 30px 100px rgba(0,0,0,.32); }
  .cover::before { content:""; position:absolute; inset:0 auto auto 0; width:58%; height:1px; background:linear-gradient(90deg,var(--voltage),var(--cyan),transparent); box-shadow:0 0 20px rgba(112,132,255,.7); }
  .cover::after { content:""; position:absolute; inset:0; pointer-events:none; background-image:linear-gradient(rgba(112,132,255,.035) 1px,transparent 1px),linear-gradient(90deg,rgba(112,132,255,.035) 1px,transparent 1px); background-size:34px 34px; mask-image:linear-gradient(90deg,transparent 38%,#000); }
  .cover > * { position:relative; z-index:1; }
  .eyebrow,.sec-eyebrow,.toc-h { color:var(--signal); font:600 10px/1.4 var(--mono); text-transform:uppercase; }
  .eyebrow { margin-bottom:18px; }
  h1 { margin-bottom:13px; color:var(--paper); font:500 54px/1.04 var(--font); }
  .cover-sub { max-width:760px; margin-bottom:25px; color:var(--fog); font-size:15px; }
  .stamp { display:inline-block; margin-bottom:27px; padding:10px 14px; border:1px solid rgba(79,206,145,.42); border-radius:6px; background:rgba(79,206,145,.06); color:var(--green); }
  .stamp.warn { border-color:rgba(255,189,91,.44); background:rgba(255,189,91,.06); color:var(--amber); }
  .stamp.bad { border-color:rgba(255,113,107,.44); background:rgba(255,113,107,.06); color:var(--red); }
  .stamp-t { display:block; font:600 13px/1.3 var(--mono); text-transform:uppercase; }
  .stamp-s { display:block; margin-top:4px; font:10px/1.4 var(--mono); color:currentColor; opacity:.85; }
  .tblock { width:100%; border-collapse:collapse; font-size:12.5px; }
  .tblock td { padding:9px 12px; border:1px solid var(--line); background:rgba(255,255,255,.018); }
  .tblock td:first-child { width:180px; color:var(--slate); font:600 9px var(--mono); text-transform:uppercase; }
  .tblock .who { color:var(--paper); font-weight:600; }
  .layout { display:grid; grid-template-columns:220px minmax(0,1fr); gap:30px; }
  nav { position:sticky; top:22px; align-self:start; font-size:12px; }
  .toc-h { margin-bottom:11px; color:var(--slate); }
  nav a { display:block; padding:6px 10px; border-left:1px solid var(--line); color:var(--fog); text-decoration:none; transition:color .16s ease,border-color .16s ease,background .16s ease; }
  nav a:hover { color:var(--paper); background:rgba(255,255,255,.025); }
  nav a.on { border-left-color:var(--signal); background:linear-gradient(90deg,rgba(64,91,255,.13),transparent); color:var(--paper); }
  section { position:relative; overflow:hidden; margin-bottom:18px; padding:27px 29px; border:1px solid var(--line); border-radius:8px; background:rgba(20,20,22,.96); }
  section::before { content:""; position:absolute; inset:0 auto auto 0; width:84px; height:1px; background:linear-gradient(90deg,var(--signal),var(--cyan),transparent); box-shadow:0 0 12px rgba(112,132,255,.55); }
  .sec-eyebrow { margin-bottom:7px; }
  h2 { margin-bottom:14px; color:var(--paper); font:500 25px/1.2 var(--font); }
  p { max-width:780px; margin-bottom:11px; }
  p:last-child { margin-bottom:0; }
  code { color:#bac2ff; font-family:var(--mono); }
  .install-flow { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); margin-top:20px; border:1px solid var(--line); border-radius:7px; overflow:hidden; }
  .install-flow div { min-width:0; padding:16px; border-right:1px solid var(--line); }
  .install-flow div:last-child { border-right:0; }
  .install-flow span { display:block; margin-bottom:7px; color:var(--signal); font:600 9px var(--mono); }
  .install-flow b { display:block; margin-bottom:4px; color:var(--paper); font-size:13px; }
  .install-flow p { color:var(--fog); font-size:12px; line-height:1.55; }
  .keynums { display:flex; flex-wrap:wrap; margin-top:20px; border:1px solid var(--line); border-radius:7px; overflow:hidden; }
  .kn { flex:1 1 145px; display:flex; flex-direction:column-reverse; min-width:0; padding:11px 14px 13px; border-left:1px solid var(--line); border-top:1px solid var(--line); margin:-1px 0 0 -1px; background:rgba(255,255,255,.018); }
  .kn b { color:var(--paper); font:500 25px/1.2 var(--font); }
  .kn span { color:var(--slate); font:600 9px/1.4 var(--mono); text-transform:uppercase; }
  .plot { padding:12px 8px 6px; overflow-x:auto; border:1px solid var(--line); border-radius:7px; background-color:#0d0d0f; background-image:linear-gradient(rgba(255,255,255,.04) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.04) 1px,transparent 1px); background-size:32px 32px; }
  .plot svg { display:block; width:100%; height:auto; min-width:560px; }
  .plot svg rect[fill="#faf8f0"] { fill:#111114 !important; stroke:#414042 !important; }
  .plot svg text[fill="#211e17"],.plot svg text:not([fill]) { fill:#d1d3d4 !important; }
  .plot svg text[fill="#6b6353"] { fill:#818388 !important; }
  .plot svg line[stroke="#211e17"],.plot svg line[stroke="#8f8874"] { stroke:#414042 !important; }
  .plot svg line[stroke="#0d6b52"],.plot svg polyline[stroke="#0d6b52"] { stroke:#7084ff !important; }
  .plot svg circle[fill="#0d6b52"] { fill:#7084ff !important; }
  .fig-cap,.note { margin-top:8px; color:var(--slate); font-size:12px; }
  table.data { width:100%; border-collapse:collapse; font-size:13px; }
  table.data th { padding:0 10px 9px 0; border-bottom:1px solid var(--graphite,#414042); color:var(--slate); font:600 9px var(--mono); text-align:left; text-transform:uppercase; }
  table.data td { padding:9px 10px 9px 0; border-bottom:1px solid var(--line); vertical-align:top; }
  .cname { color:var(--ash); font:11px var(--mono); white-space:nowrap; }
  .cdetail { color:var(--fog); }
  .chip { display:inline-block; padding:4px 8px; border:1px solid; border-radius:999px; font:600 9px/1 var(--mono); }
  .chip.good,.good-t,.yes { color:var(--green); } .chip.good { border-color:rgba(79,206,145,.42); }
  .chip.warn,.warn-t,.part { color:var(--amber); } .chip.warn { border-color:rgba(255,189,91,.42); }
  .chip.bad,.bad-t { color:var(--red); } .chip.bad { border-color:rgba(255,113,107,.42); }
  .chip.muted,.muted-t,.no { color:var(--slate); } .chip.muted { border-color:var(--line); }
  .yes { font-weight:700; }
  .cmp td:nth-child(n+2),.cmp th:nth-child(n+2) { text-align:center; }
  .auto-row { display:flex; align-items:baseline; gap:14px; padding:12px 0; border-bottom:1px solid var(--line); flex-wrap:wrap; }
  .auto-row:last-of-type { border-bottom:0; }
  .auto-name { min-width:220px; color:var(--paper); font-weight:600; }
  .auto-val { font:12px var(--mono); }
  .auto-sub { flex-basis:100%; margin-top:-4px; color:var(--fog); font-size:12.5px; }
  .exgrid { display:flex; flex-wrap:wrap; gap:6px; margin:15px 0 8px; }
  .ex { display:inline-flex; align-items:center; justify-content:center; width:34px; height:34px; border:1px solid var(--line); background:#101012; color:var(--slate); font:600 11px var(--mono); }
  .ex-pass { border-color:var(--signal); background:var(--voltage); color:#fff; box-shadow:0 0 14px rgba(64,91,255,.2); }
  .tl-day { position:relative; margin:0 0 15px 4px; padding:2px 0 10px 19px; border-left:1px solid rgba(112,132,255,.45); }
  .tl-day::before { content:""; position:absolute; left:-4px; top:8px; width:7px; height:7px; border-radius:50%; background:var(--signal); box-shadow:0 0 10px var(--signal); }
  .tl-date { margin-bottom:7px; color:var(--paper); font:600 13px var(--font); }
  .tl-day ul { padding-left:18px; }
  .tl-day li { margin:5px 0; color:var(--fog); font-size:12.5px; }
  .vrow { display:grid; grid-template-columns:220px 1fr 205px; gap:12px; align-items:center; padding:9px 0; border-bottom:1px solid var(--line); }
  .vrows .vrow:last-child { border-bottom:0; }
  .vlabel { color:var(--paper); font-weight:600; }
  .vkey { display:block; color:var(--slate); font:10px var(--mono); }
  .vbar { height:10px; border:1px solid var(--line); background:#0d0d0f; }
  .vfill { height:100%; background:linear-gradient(90deg,var(--voltage),var(--cyan)); }
  .vnum { color:var(--fog); font:11px var(--mono); text-align:right; }
  .event { padding:13px 0; border-bottom:1px solid var(--line); }
  .event:last-child { border-bottom:0; }
  .ev-head { display:flex; justify-content:space-between; gap:10px; flex-wrap:wrap; font-size:11px; }
  .ev-agent { color:var(--green); font:700 10px var(--mono); }
  .ev-time { color:var(--slate); font:10px var(--mono); }
  .ev-task { margin:4px 0 3px; color:var(--paper); font-weight:600; }
  .ev-actions { color:var(--fog); font-size:12.5px; }
  .ev-value { margin-top:3px; color:var(--green); font-size:12.5px; }
  .ev-risks { margin-top:3px; color:var(--red); font-size:12.5px; }
  .empty { color:var(--slate); font-size:13px; }
  ol.steps { padding-left:20px; } ol.steps li { margin:7px 0; }
  dl { max-width:800px; }
  dt { margin-top:14px; color:var(--paper); font-weight:600; }
  dt code { color:#bac2ff; font:600 12px var(--mono); }
  dd { margin-left:0; color:var(--fog); font-size:13px; }
  footer { margin-top:28px; padding-top:15px; border-top:1px solid var(--line); color:var(--slate); font-size:11px; }
  footer code { color:var(--ash); font:11px var(--mono); }
  @media (max-width:900px) { .layout{grid-template-columns:minmax(0,1fr)} nav{display:none;position:static}.cover{padding:31px 24px 24px} h1{font-size:40px}.vrow{grid-template-columns:1fr;gap:4px}.vnum{text-align:left}.cname{white-space:normal}.install-flow{grid-template-columns:1fr}.install-flow div{border-right:0;border-bottom:1px solid var(--line)}.install-flow div:last-child{border-bottom:0} }
  @media (max-width:620px) { body{padding:14px 10px 50px}.cover,section{padding:22px 18px} h1{font-size:34px}.tblock td:first-child{width:120px}.keynums{display:grid;grid-template-columns:1fr 1fr}.auto-name{min-width:0;flex-basis:100%} }
  @media (prefers-reduced-motion:reduce) { html{scroll-behavior:auto} *,*::before,*::after{animation-duration:.01ms!important;animation-delay:0ms!important;transition-duration:.01ms!important;transition-delay:0ms!important} }
  @media print { nav{display:none}.layout{grid-template-columns:1fr}section{page-break-inside:avoid}body{padding:0} }
</style></head><body><div class="page">

<div class="cover">
  <div class="eyebrow">Живой паспорт рабочей среды · обновлён %%STAMP%%</div>
  <h1>AI OS</h1>
  <div class="cover-sub">Локальная рабочая среда, которая даёт ИИ-агентам общую память, правила и проверяемый след между сессиями. Она не делает модель умнее магически: она помогает агенту не забывать решения, открывать первоисточник до ответа и оставлять понятный результат после работы.</div>
  <div class="stamp %%STAMPCLS%%"><span class="stamp-t">%%STAMPTITLE%%</span><span class="stamp-s">%%HERO%% · OK %%OKN%% · WARN %%WARNN%% · FAIL %%FAILN%% · SKIP %%SKIPN%%</span></div>
  <table class="tblock">
    <tr><td>Среда</td><td>%%WS%%</td></tr>
    <tr><td>Установщик</td><td>AI OS Setup %%SETUPVER%% · <code>%%INSTALLERFILE%%</code></td></tr>
    <tr><td>Приложение</td><td>Control Center %%CONTROLVER%%</td></tr>
    <tr><td>Поверка</td><td>%%HERO%% (свежий прогон %%CHECKSN%% проверок при сборке паспорта)</td></tr>
    <tr><td>Разработал</td><td class="who">Лабынцев Денис · @Ludosiel</td></tr>
    <tr><td>Разделов</td><td>14</td></tr>
  </table>
</div>

<div class="layout">
<nav id="toc">
  <div class="toc-h">Оглавление</div>
  <a href="#s1">1 · Что это такое</a>
  <a href="#s2">2 · Чем отличается от чата</a>
  <a href="#s3">3 · Как устроено</a>
  <a href="#s4">4 · Поверка: свежий прогон</a>
  <a href="#s5">5 · История самопроверок</a>
  <a href="#s6">6 · Автоматика</a>
  <a href="#s7">7 · Память</a>
  <a href="#s8">8 · Экзамены поведения</a>
  <a href="#s9">9 · Безопасность и дисциплина</a>
  <a href="#s10">10 · Последние изменения</a>
  <a href="#s11">11 · Объём системы</a>
  <a href="#s12">12 · Журнал агентов</a>
  <a href="#s13">13 · Следующие шаги</a>
  <a href="#s14">14 · Словарь</a>
</nav>
<main>

<section id="s1">
  <div class="sec-eyebrow">Раздел 1 · Назначение и запуск</div>
  <h2>Что установлено и зачем</h2>
  <p>Обычный чат помнит только текущий разговор. AI OS создаёт для проекта постоянное рабочее место: обычные Markdown-заметки с решениями и контекстом, локальный поиск по смыслу, карта кода, единые правила для агентов и автоматические проверки состояния.</p>
  <p><b>Источником правды остаются файлы проекта.</b> Память лишь помогает быстро найти нужную заметку, а Control Center показывает состояние, запускает проверки и даёт человеку удобный вход в систему. Claude, Codex и Cursor могут меняться — проектный контекст остаётся в одной понятной папке.</p>
  <p>Заметки, индексы и журналы хранятся локально. Облачный ИИ получает только то, что пользователь отправляет в чат и что агент открывает во время задачи. Секреты и приватные данные в контекстную папку класть нельзя.</p>
  <div class="install-flow">
    <div><span>01 · Установка</span><b>Запусти Setup %%SETUPVER%%</b><p>Один пакет для вашей ОС проверит компьютер и разложит локальные компоненты без ручной сборки.</p></div>
    <div><span>02 · Проект</span><b>Нажми «Создать среду»</b><p>Каждый проект получит отдельные заметки, память, настройки и карту кода.</p></div>
    <div><span>03 · Работа</span><b>Открой Control Center</b><p>Или зайди в папку из Claude Code, Codex либо Cursor. Полная инструкция находится в разделе «Справка» приложения.</p></div>
  </div>
  <div class="keynums">
    <div class="kn"><b>%%DAYSN%%</b><span>%%DAYSWORD%% летописи</span></div>
    <div class="kn"><b>%%NOTESN%%</b><span>%%NOTESWORD%% в папке-правде</span></div>
    <div class="kn"><b>%%MEMKN%%</b><span>%%MEMWORD%% в памяти</span></div>
    <div class="kn"><b>%%RUNS%%</b><span>%%RUNSWORD%% в журнале</span></div>
    <div class="kn"><b>%%LINKSN%%</b><span>%%LINKSWORD%% между заметками</span></div>
  </div>
</section>

<section id="s2">
  <div class="sec-eyebrow">Раздел 2 · Сравнение</div>
  <h2>Чем отличается от обычного чата</h2>
  <div class="tw"><table class="data cmp">
    <tr><th>Возможность</th><th>Обычный чат</th><th>Чат с файлами</th><th>Эта система</th></tr>
    <tr><td>Помнит договорённости между сессиями</td><td class="no">нет</td><td class="part">пока файл в контексте</td><td class="yes">да</td></tr>
    <tr><td>Обязан проверить заметки перед ответом о людях и решениях</td><td class="no">нет</td><td class="no">нет</td><td class="yes">да</td></tr>
    <tr><td>Спорит, если просьба противоречит принятым решениям</td><td class="no">нет</td><td class="no">нет</td><td class="yes">да</td></tr>
    <tr><td>Сам проверяет своё здоровье по расписанию</td><td class="no">нет</td><td class="no">нет</td>%%CMPHEALTH%%</tr>
    <tr><td>Ловит секреты в заметках до утечки</td><td class="no">нет</td><td class="no">нет</td>%%CMPSEC%%</tr>
    <tr><td>Одни правила для разных ИИ (Claude, Codex, Cursor)</td><td class="no">нет</td><td class="no">нет</td><td class="yes">да</td></tr>
    <tr><td>Оставляет след после каждой задачи</td><td class="no">нет</td><td class="no">нет</td>%%CMPTRACE%%</tr>
  </table></div>
  <div class="note">Это сравнение возможностей по устройству, а не замер скорости. Три нижние ячейки последнего столбца — живые: они проверяются данными этого прогона, а не написаны заранее.</div>
</section>

<section id="s3">
  <div class="sec-eyebrow">Раздел 3 · Устройство</div>
  <h2>Как устроено</h2>
  <p>Три слоя. <b>Папка-правда</b> — обычные markdown-заметки: решения, люди, встречи, задачи. <b>Сервисы</b> — семантическая память (быстрый поиск по смыслу) и рентген кода (карта функций и связей). <b>Дисциплина</b> — протокол, экзамены и проверки по расписанию, которые не дают системе тихо испортиться.</p>
  <div class="plot"><svg viewBox="0 0 680 310" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Схема системы">
    <g font-family="Segoe UI, sans-serif" font-size="13">
    <rect x="60" y="18" width="130" height="38" fill="#faf8f0" stroke="#211e17" stroke-width="1.2"/><text x="125" y="42" text-anchor="middle">Claude</text>
    <rect x="275" y="18" width="130" height="38" fill="#faf8f0" stroke="#211e17" stroke-width="1.2"/><text x="340" y="42" text-anchor="middle">Codex</text>
    <rect x="490" y="18" width="130" height="38" fill="#faf8f0" stroke="#211e17" stroke-width="1.2"/><text x="555" y="42" text-anchor="middle">Cursor</text>
    <line x1="125" y1="56" x2="300" y2="118" stroke="#211e17" stroke-width="1"/>
    <line x1="340" y1="56" x2="340" y2="118" stroke="#211e17" stroke-width="1"/>
    <line x1="555" y1="56" x2="380" y2="118" stroke="#211e17" stroke-width="1"/>
    <rect x="170" y="120" width="340" height="64" fill="#faf8f0" stroke="#0d6b52" stroke-width="2"/>
    <text x="340" y="146" text-anchor="middle" font-weight="600">Папка-правда (заметки на диске)</text>
    <text x="340" y="168" text-anchor="middle" font-size="12" fill="#6b6353">решения · люди · встречи · задачи · регламенты</text>
    <line x1="230" y1="184" x2="140" y2="234" stroke="#211e17" stroke-width="1"/>
    <line x1="340" y1="184" x2="340" y2="234" stroke="#211e17" stroke-width="1"/>
    <line x1="450" y1="184" x2="540" y2="234" stroke="#211e17" stroke-width="1"/>
    <rect x="48" y="236" width="184" height="52" fill="#faf8f0" stroke="#211e17" stroke-width="1.2"/>
    <text x="140" y="258" text-anchor="middle">Память (mgi-mind)</text>
    <text x="140" y="276" text-anchor="middle" font-size="11.5" fill="#6b6353">поиск по смыслу, авто-обновление</text>
    <rect x="248" y="236" width="184" height="52" fill="#faf8f0" stroke="#211e17" stroke-width="1.2"/>
    <text x="340" y="258" text-anchor="middle">Проверки по расписанию</text>
    <text x="340" y="276" text-anchor="middle" font-size="11.5" fill="#6b6353">health · readiness · секреты</text>
    <rect x="448" y="236" width="184" height="52" fill="#faf8f0" stroke="#211e17" stroke-width="1.2"/>
    <text x="540" y="258" text-anchor="middle">Рентген кода</text>
    <text x="540" y="276" text-anchor="middle" font-size="11.5" fill="#6b6353">карта функций и связей</text>
    </g>
  </svg></div>
  <div class="fig-cap">Рис. 1 — Агенты сверху сменяемы; правда и дисциплина внизу постоянны. Именно поэтому система переживает смену инструментов.</div>
  <p style="margin-top:18px">Каждую задачу агент обязан вести по одному циклу — это записано в протоколе, а напоминание вшито в каждое сообщение:</p>
  <div class="plot"><svg viewBox="0 0 680 190" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Рабочий цикл агента">
    <g font-family="Segoe UI, sans-serif" font-size="12.5">
    <rect x="20" y="24" width="148" height="40" fill="#faf8f0" stroke="#211e17" stroke-width="1.2"/><text x="94" y="49" text-anchor="middle">1 · Вспомнить</text>
    <rect x="188" y="24" width="148" height="40" fill="#faf8f0" stroke="#211e17" stroke-width="1.2"/><text x="262" y="49" text-anchor="middle">2 · Открыть источник</text>
    <rect x="356" y="24" width="148" height="40" fill="#faf8f0" stroke="#211e17" stroke-width="1.2"/><text x="430" y="49" text-anchor="middle">3 · Усомниться</text>
    <rect x="524" y="24" width="136" height="40" fill="#faf8f0" stroke="#211e17" stroke-width="1.2"/><text x="592" y="49" text-anchor="middle">4 · Сделать</text>
    <rect x="524" y="122" width="136" height="40" fill="#faf8f0" stroke="#211e17" stroke-width="1.2"/><text x="592" y="147" text-anchor="middle">5 · Проверить</text>
    <rect x="356" y="122" width="148" height="40" fill="#faf8f0" stroke="#211e17" stroke-width="1.2"/><text x="430" y="147" text-anchor="middle">6 · Записать в вечное</text>
    <rect x="188" y="122" width="148" height="40" fill="#faf8f0" stroke="#211e17" stroke-width="1.2"/><text x="262" y="147" text-anchor="middle">7 · Синхронизировать</text>
    <line x1="168" y1="44" x2="188" y2="44" stroke="#0d6b52" stroke-width="1.6"/>
    <line x1="336" y1="44" x2="356" y2="44" stroke="#0d6b52" stroke-width="1.6"/>
    <line x1="504" y1="44" x2="524" y2="44" stroke="#0d6b52" stroke-width="1.6"/>
    <line x1="592" y1="64" x2="592" y2="122" stroke="#0d6b52" stroke-width="1.6"/>
    <line x1="524" y1="142" x2="504" y2="142" stroke="#0d6b52" stroke-width="1.6"/>
    <line x1="356" y1="142" x2="336" y2="142" stroke="#0d6b52" stroke-width="1.6"/>
    <line x1="188" y1="142" x2="94" y2="142" stroke="#0d6b52" stroke-width="1.6" stroke-dasharray="4 3"/>
    <line x1="94" y1="142" x2="94" y2="64" stroke="#0d6b52" stroke-width="1.6" stroke-dasharray="4 3"/>
    <text x="118" y="105" font-size="11" fill="#6b6353">следующая задача</text>
    </g>
  </svg></div>
  <div class="fig-cap">Рис. 2 — Рабочий цикл: вспомнить → открыть первоисточник → усомниться → сделать → проверить → записать → синхронизировать память.</div>
</section>

<section id="s4">
  <div class="sec-eyebrow">Раздел 4 · Поверка</div>
  <h2>Свежий прогон: %%HERO%%</h2>
  <p>При сборке этого паспорта система прогнала полную самопроверку заново — ниже её живой результат, не кэш.</p>
  <div class="tw"><table class="data"><tr><th>Проверка</th><th>Статус</th><th>Детали</th></tr>%%ROWS%%</table></div>
</section>

<section id="s5">
  <div class="sec-eyebrow">Раздел 5 · История</div>
  <h2>История самопроверок</h2>
  <div class="plot">%%HISTSVG%%</div>
  <div class="fig-cap">Рис. 3 — Последние %%HISTN%% прогонов (всего в журнале %%RUNS%%): короткий изумрудный столбик — чисто, охристый повыше — предупреждения, красный высокий — сбой. Чем тише график, тем лучше.</div>
</section>

<section id="s6">
  <div class="sec-eyebrow">Раздел 6 · Автоматика</div>
  <h2>Что работает само, без человека</h2>
  <div class="auto-row"><div class="auto-name">Сторож памяти (watcher)</div><div class="auto-val %%WATCHCLS%%-t">%%WATCH%%</div><div class="auto-sub">следит за изменением заметок и сам обновляет память: авто-синков %%AUTOSYNCS%%, сбоев %%FAILEDSYNCS%% (по текущему журналу)</div></div>
  <div class="auto-row"><div class="auto-name">Ежедневная самопроверка</div><div class="auto-val %%READYCLS%%-t">%%READY%%</div><div class="auto-sub">%%READYSUB%%</div></div>
  <div class="auto-row"><div class="auto-name">Автостарт памяти</div><div class="auto-val %%MEMSTARTCLS%%-t">%%MEMSTART%%</div><div class="auto-sub">поднимает сервис памяти при входе, чтобы агентам было куда обращаться</div></div>
</section>

<section id="s7">
  <div class="sec-eyebrow">Раздел 7 · Память</div>
  <h2>Семантическая память</h2>
  <p>Память — это указатель по папке-правде, а не сама папка (техническое имя указателя — семантический индекс): она умеет искать по смыслу («что мы решали про источник правды?»), но любой найденный след агент обязан проверить по заметке-первоисточнику. Так скорость не подменяет точность.</p>
  <div class="keynums">
    <div class="kn"><b>%%MEMKN%%</b><span>%%MEMWORD%% в памяти</span></div>
    <div class="kn"><b>%%AUTOSYNCS%%</b><span>%%SYNCWORD%% памяти</span></div>
  </div>
  <p class="note">Состояние: <span class="%%MEMCLS%%-t">%%MEM%%</span> · последняя синхронизация: %%LASTSYNC%%</p>
</section>

<section id="s8">
  <div class="sec-eyebrow">Раздел 8 · Экзамены</div>
  <h2>Экзамены поведения агентов</h2>
  <p>Набор из %%EVALTOTAL%% ловушек, которые проверяют не текст, а поведение: попроси агента записать API-ключ в заметки — обязан отказаться; спроси «как отреагирует такой-то человек» — обязан сначала открыть заметки о нём, а не фантазировать; скажи «поставь все популярные инструменты разом» — обязан поспорить. Сдача фиксируется письменно, по одному экзамену на свежую сессию.</p>
  <div class="exgrid">%%EVALGRID%%</div>
  <div class="fig-cap">Рис. 4 — Сдано и записано: %%EVALPASS%% из %%EVALTOTAL%%. Залитый квадрат — экзамен пройден и запротоколирован; пустой — ещё не сдавался.</div>
</section>

<section id="s9">
  <div class="sec-eyebrow">Раздел 9 · Безопасность</div>
  <h2>Безопасность и дисциплина</h2>
  <p>Статус сканеров: <span class="%%SECCLS%%-t"><b>%%SEC%%</b></span>. Встроенный сканер ищет ключи и токены в заметках при каждой самопроверке%%GLTEXT%%.</p>
  <p>Дисциплина держится на трёх правилах, зашитых в протокол. <b>Ворота памяти:</b> прежде чем утверждать что-то о людях, встречах или решениях, агент обязан открыть заметку-первоисточник — прогноз о живом человеке считается фактическим утверждением, а не «просто мнением». <b>Право спорить:</b> если просьба противоречит принятым решениям или безопасности, агент обязан один раз возразить с причинами. <b>След после задачи:</b> каждая существенная задача заканчивается записью в заметки и строкой в журнале событий.</p>
  <p class="note">%%HOOKLINE%%</p>
</section>

<section id="s10">
  <div class="sec-eyebrow">Раздел 10 · Изменения</div>
  <h2>Последние подтверждённые изменения</h2>
  <p>Ниже показана актуальная витрина последних завершённых работ без устаревших релизных артефактов. Полная неизменённая история остаётся в <code>60_Tasks/Task_Log.md</code>; паспорт не удаляет и не переписывает архив.</p>
  <div class="plot">%%CUMSVG%%</div>
  <div class="fig-cap">Рис. 5 — %%DONEN%% последних релевантных записей за %%DAYSN%% %%DAYSWORD2%%%%UNDATED%%.</div>
  <div style="margin-top:22px">%%TIMELINE%%</div>
</section>

<section id="s11">
  <div class="sec-eyebrow">Раздел 11 · Объём</div>
  <h2>Объём системы в цифрах</h2>
  <div class="vrows">%%DIRBARS%%</div>
  <div class="keynums">
    <div class="kn"><b>%%NOTESN%%</b><span>%%NOTESWORD%%</span></div>
    <div class="kn"><b>%%WORDSN%%</b><span>%%WORDSWORD%%</span></div>
    <div class="kn"><b>%%LINKSN%%</b><span>внутренних %%LINKSWORD%%</span></div>
    <div class="kn"><b>%%COMMITSN%%</b><span>%%COMMITSWORD%%</span></div>
  </div>
</section>

<section id="s12">
  <div class="sec-eyebrow">Раздел 12 · Журнал</div>
  <h2>Журнал событий агентов</h2>
  <p>Каждый агент в конце существенной задачи оставляет одну строку: что сделал, что проверил и какие риски остались. В полном журнале %%EVCOUNT%% событий; ниже показаны %%EVSHOWN%% последних актуальных записей без старых релизных уведомлений.</p>
  %%EVENTS%%
</section>

<section id="s13">
  <div class="sec-eyebrow">Раздел 13 · Дальше</div>
  <h2>Следующие шаги</h2>
  <p class="note" style="margin:0 0 10px">Список вычислен из данных этого прогона, а не написан заранее.</p>
  <ol class="steps">%%STEPS%%</ol>
</section>

<section id="s14">
  <div class="sec-eyebrow">Раздел 14 · Словарь</div>
  <h2>Словарь терминов</h2>
  <dl>
    <dt>Агент</dt><dd>ИИ, который не просто отвечает, а работает: читает файлы, запускает команды, вносит правки. Claude, Codex и Cursor — разные агенты за одним рабочим местом.</dd>
    <dt>Папка-правда</dt><dd>Обычная папка с заметками — единственное место, где живут факты. Всё остальное (память, чаты) — лишь ускорители доступа к ней.</dd>
    <dt>Семантическая память <code>mgi-mind</code></dt><dd>Локальный поиск по смыслу: находит заметку, даже если слова в запросе другие. Указатель, а не источник.</dd>
    <dt>Сторож (watcher)</dt><dd>Фоновая программа: заметка изменилась — память обновилась. Человек ничего не нажимает.</dd>
    <dt>Самопроверка</dt><dd>Скрипт, который по расписанию гоняет %%CHECKSN%% проверок: от битых ссылок между заметками до случайно сохранённых паролей.</dd>
    <dt>Экзамены поведения</dt><dd>Ловушки для агента: провоцируют типовые ошибки ИИ (выдумать, согласиться, натащить инструментов) и проверяют, что защита срабатывает.</dd>
    <dt>Рентген кода</dt><dd>Локальная карта кодовой базы: какие функции есть и кто кого вызывает. Агент ищет по смыслу, а не листает файлы.</dd>
    <dt>Ворота памяти (recall gate)</dt><dd>Правило: сначала открой заметку — потом утверждай. Особенно о людях.</dd>
    <dt>Журнал событий</dt><dd>Файл, куда каждый агент пишет одну строку после задачи. Из него собирается раздел 12.</dd>
    <dt>MCP</dt><dd>Стандартный разъём, через который агенты подключаются к локальным сервисам (памяти, рентгену кода) — как USB для ИИ-инструментов.</dd>
  </dl>
</section>

<footer>AI OS Setup %%SETUPVER%% · Control Center %%CONTROLVER%%. Паспорт собирается командой <code>tools/make_dashboard.ps1</code> из локальных журналов; правда живёт в заметках, паспорт — только зеркало. Разработал: <b>Лабынцев Денис · @Ludosiel</b>.</footer>
</main>
</div></div>
<script>
(function () {
  var links = document.querySelectorAll('#toc a');
  var map = {};
  for (var i = 0; i < links.length; i++) { map[links[i].getAttribute('href').slice(1)] = links[i]; }
  if (!('IntersectionObserver' in window)) { return; }
  var cur = null;
  var obs = new IntersectionObserver(function (es) {
    for (var j = 0; j < es.length; j++) {
      if (es[j].isIntersecting) {
        if (cur) { cur.classList.remove('on'); }
        cur = map[es[j].target.id];
        if (cur) { cur.classList.add('on'); }
      }
    }
  }, { rootMargin: '-20% 0px -70% 0px' });
  var secs = document.querySelectorAll('main section');
  for (var k = 0; k < secs.length; k++) { obs.observe(secs[k]); }
})();
</script>
</body></html>
'@

$glText = ''
if ($gitleaksOn) { $glText = '; глубокий сканер gitleaks (~170 детекторов) подключён — проверка пройдена, находок нет' }

$html = $html.Replace('%%STAMP%%', $stamp).Replace('%%WS%%', (Esc $wsName)).Replace('%%INSTALLERFILE%%', (Esc $installerFile))
$html = $html.Replace('%%SETUPVER%%', (Esc $setupVersion)).Replace('%%CONTROLVER%%', (Esc $controlVersion))
$html = $html.Replace('%%STAMPCLS%%', $stampCls).Replace('%%STAMPTITLE%%', $stampTitle).Replace('%%HERO%%', (Esc $hero))
$html = $html.Replace('%%OKN%%', [string]$okN).Replace('%%WARNN%%', [string]$warnN).Replace('%%FAILN%%', [string]$failN).Replace('%%SKIPN%%', [string]$skipN)
$html = $html.Replace('%%CHECKSN%%', [string]$checks.Count).Replace('%%RUNS%%', [string]$totalRuns).Replace('%%HISTN%%', [string]$histRuns.Count)
$html = $html.Replace('%%DAYSN%%', [string]$daysN).Replace('%%DAYSWORD%%', (PluralRu $daysN 'день' 'дня' 'дней')).Replace('%%DAYSWORD2%%', (PluralRu $daysN 'день' 'дня' 'дней'))
$commitsWord = 'git-коммитов'
if ($commitsN -match '^\d+$') { $commitsWord = 'git-' + (PluralRu ([long]$commitsN) 'коммит' 'коммита' 'коммитов') }
$html = $html.Replace('%%NOTESN%%', [string]$notesN).Replace('%%WORDSN%%', (Num $wordsN)).Replace('%%LINKSN%%', [string]$linksN).Replace('%%COMMITSN%%', (Esc $commitsN))
$html = $html.Replace('%%LINKSWORD%%', (PluralRu $linksN 'связь' 'связи' 'связей')).Replace('%%COMMITSWORD%%', $commitsWord)
$memKn = '—'; if ($memN -ge 0) { $memKn = Num $memN }
$html = $html.Replace('%%MEMKN%%', $memKn).Replace('%%MEM%%', (Esc $memLine)).Replace('%%MEMCLS%%', $memClass).Replace('%%LASTSYNC%%', (Esc $lastSync))
$html = $html.Replace('%%READYSUB%%', (Esc $readySub)).Replace('%%HOOKLINE%%', (Esc $hookLine))
$html = $html.Replace('%%CMPHEALTH%%', $cmpHealth).Replace('%%CMPSEC%%', $cmpSec).Replace('%%CMPTRACE%%', $cmpTrace)
$html = $html.Replace('%%DONEWORD%%', (PluralRu $timelineEntries.Count 'запись' 'записи' 'записей')).Replace('%%UNDATED%%', (Esc $undatedTxt))
$memWord = 'записей'; if ($memN -ge 0) { $memWord = PluralRu $memN 'запись' 'записи' 'записей' }
$html = $html.Replace('%%MEMWORD%%', $memWord)
$html = $html.Replace('%%RUNSWORD%%', (PluralRu $totalRuns 'самопроверка' 'самопроверки' 'самопроверок'))
$html = $html.Replace('%%NOTESWORD%%', (PluralRu $notesN 'заметка' 'заметки' 'заметок'))
$html = $html.Replace('%%WORDSWORD%%', (PluralRu $wordsN 'слово' 'слова' 'слов'))
$html = $html.Replace('%%SYNCWORD%%', (PluralRu $autoSyncs 'авто-обновление' 'авто-обновления' 'авто-обновлений'))
$html = $html.Replace('%%WATCH%%', (Esc $watcherBadge[0])).Replace('%%WATCHCLS%%', $watcherBadge[1])
$html = $html.Replace('%%READY%%', (Esc $readinessBadge[0])).Replace('%%READYCLS%%', $readinessBadge[1])
$html = $html.Replace('%%MEMSTART%%', (Esc $memstartBadge[0])).Replace('%%MEMSTARTCLS%%', $memstartBadge[1])
$html = $html.Replace('%%AUTOSYNCS%%', [string]$autoSyncs).Replace('%%FAILEDSYNCS%%', [string]$failedSyncs)
$html = $html.Replace('%%SEC%%', (Esc $secLine)).Replace('%%SECCLS%%', $secClass).Replace('%%GLTEXT%%', $glText)
$html = $html.Replace('%%EVALPASS%%', [string]$evalPass).Replace('%%EVALTOTAL%%', [string]$evalTotal).Replace('%%EVALGRID%%', $evalGrid)
$html = $html.Replace('%%HISTSVG%%', $histSvg).Replace('%%CUMSVG%%', $cumSvg).Replace('%%DONEN%%', [string]$timelineEntries.Count)
$html = $html.Replace('%%TIMELINE%%', $timelineHtml).Replace('%%DIRBARS%%', $dirBars)
$html = $html.Replace('%%EVCOUNT%%', [string]$evCount).Replace('%%EVSHOWN%%', [string]$evShown)
$html = $html.Replace('%%ROWS%%', $rowsHtml).Replace('%%EVENTS%%', $eventsHtml).Replace('%%STEPS%%', $stepsHtml)

$outPath = Join-Path $localDir "dashboard.html"
$tmpPath = $outPath + ".tmp"
Set-Content -Encoding UTF8 -Path $tmpPath -Value $html
Move-Item -Force -Path $tmpPath -Destination $outPath
Write-Output "Dashboard written to: $outPath"
if ($Open) { Start-Process $outPath }
exit 0
