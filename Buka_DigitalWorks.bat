@echo off
title Digital Works 3.0 Modded
cd /d "%~dp0"

if not exist ".undo_history" mkdir ".undo_history"
if not exist "laporan_screenshots" mkdir "laporan_screenshots"

REM Menjalankan aplikasi simulator Digital Works yang sudah dimodifikasi
start "" "%~dp0DigitalWorks.exe" %*
