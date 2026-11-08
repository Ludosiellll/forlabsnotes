if (Test-Path 'W:\') { subst W: /D }
subst W: 'd:\1с лабы\1С_ЛР5_Файлы'

# 1. Build EPF
Start-Process 'D:\1c_app\8.3.27.1508\bin\1cv8t.exe' -ArgumentList 'DESIGNER /F W:\Base1C /LoadExternalDataProcessorOrReportFromFiles W:\epf_post_src\ПроведениеДокументов.xml W:\ПроведениеДокументов.epf /Out W:\epf_build.log' -Wait
if (Test-Path 'W:\epf_build.log') { Get-Content 'W:\epf_build.log' -Encoding Default }

# 2. Run EPF in Enterprise to post all documents
Start-Process 'D:\1c_app\8.3.27.1508\bin\1cv8t.exe' -ArgumentList 'ENTERPRISE /F W:\Base1C /Execute W:\ПроведениеДокументов.epf /DisableStartupMessages' -Wait

# 3. Dump updated IB
Start-Process 'D:\1c_app\8.3.27.1508\bin\1cv8t.exe' -ArgumentList 'DESIGNER /F W:\Base1C /DumpIB W:\ФормыЛабынцев.dt /Out W:\dump.log' -Wait
Copy-Item 'W:\ФормыЛабынцев.dt' 'W:\Лабынцев.dt' -Force

subst W: /D

# Check logs
if (Test-Path 'd:\1c_post_log.txt') { Get-Content 'd:\1c_post_log.txt' -Encoding UTF8 }
if (Test-Path 'd:\1c_post_err.txt') { Get-Content 'd:\1c_post_err.txt' -Encoding UTF8 }

# Copy to flash drive
if (Test-Path 'E:\Программирование 1С\ЛР5') {
    Copy-Item 'd:\1с лабы\1С_ЛР5_Файлы\ФормыЛабынцев.dt' 'E:\Программирование 1С\ЛР5\ФормыЛабынцев.dt' -Force
    Copy-Item 'd:\1с лабы\1С_ЛР5_Файлы\Лабынцев.dt' 'E:\Программирование 1С\ЛР5\Лабынцев.dt' -Force
    Write-Host 'Copied both .dt files to E:\ drive successfully'
}
