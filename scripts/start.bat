@echo off
title Eskimo Auto Test - Startup
color 0A

echo ========================================
echo   ESKIMO AUTO TEST - STARTUP
echo ========================================
echo.

echo [1/2] Kiem tra emulator...
adb devices | findstr "emulator"
if errorlevel 1 (
    echo.
    echo [!] Emulator chua bat! Hay mo Android Studio va khoi dong emulator truoc.
    echo.
    pause
    exit
)
echo [OK] Emulator san sang!
echo.

echo [2/2] Khoi dong Appium Server...
echo [OK] Appium dang chay tai http://127.0.0.1:4723
echo [!] Giu nguyen cua so nay khi chay test!
echo.
echo ========================================
appium
