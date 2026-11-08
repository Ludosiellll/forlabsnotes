@echo off
chcp 65001 >nul

echo Запуск проверки сети...
echo Имя компьютера: %computername% > net_report.txt
echo Дата и время проверки: %date% %time% >> net_report.txt
echo. >> net_report.txt

echo 1. Конфигурация сетевых адаптеров: >> net_report.txt
ipconfig /all >> net_report.txt
echo. >> net_report.txt

echo 2. Проверка связи с внешним сервером (8.8.8.8): >> net_report.txt
ping -n 2 8.8.8.8 >> net_report.txt
echo. >> net_report.txt

echo 3. Проверка DNS и доступа к сайту (ya.ru): >> net_report.txt
ping -n 2 ya.ru >> net_report.txt

echo Проверка завершена.
echo Результаты сохранены в файл net_report.txt
pause
