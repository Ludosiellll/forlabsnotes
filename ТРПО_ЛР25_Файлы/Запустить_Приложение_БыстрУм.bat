@echo off
chcp 65001 >nul
title БыстрУм
cd /d "%~dp0App"
start "" "BystrUmAddModules.exe"
exit
