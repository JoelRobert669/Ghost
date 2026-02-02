@echo off
setlocal EnableDelayedExpansion

REM Check for Admin privileges
NET SESSION >nul 2>&1
if %errorLevel% neq 0 (
    echo Requesting Administrator privileges...
    powershell -Command "Start-Process '%0' -Verb RunAs"
    exit /b
)

echo ==================================================
echo       Wake-on-LAN Configuration Utility
echo ==================================================
echo.

REM 1. Disable Fast Startup (Hybrid Sleep)
echo [1/3] Disabling Windows Fast Startup...
reg add "HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Session Manager\Power" /v HiberbootEnabled /t REG_DWORD /d 0 /f
if %errorlevel% equ 0 (
    echo       - Fast Startup disabled successfully.
) else (
    echo       ! Failed to disable Fast Startup.
)
echo.

REM 2. Configure Network Adapters using PowerShell
echo [2/3] Configuring Network Adapters...
echo       (This may briefly interrupt your network connection)
echo.

powershell -Command ^
    "Get-NetAdapter -Physical | Where-Object { $_.Status -eq 'Up' } | ForEach-Object { "^
    "   Write-Host '   Configuring adapter: ' $_.Name; "^
    "   try { "^
    "       Set-NetAdapterPowerManagement -Name $_.Name -WakeOnMagicPacket Enabled -ErrorAction Stop; "^
    "       Write-Host '       - Power Management: Enabled WakeOnMagicPacket'; "^
    "   } catch { Write-Host '       ! Failed to set Power Management settings'; } "^
    "   try { "^
    "       Set-NetAdapterAdvancedProperty -Name $_.Name -DisplayName '*WakeOnMagicPacket*' -DisplayValue 'Enabled' -ErrorAction SilentlyContinue; "^
    "       Set-NetAdapterAdvancedProperty -Name $_.Name -DisplayName 'Wake on Magic Packet' -DisplayValue 'Enabled' -ErrorAction SilentlyContinue; "^
    "       Set-NetAdapterAdvancedProperty -Name $_.Name -DisplayName 'Wake on pattern match' -DisplayValue 'Enabled' -ErrorAction SilentlyContinue; "^
    "       Write-Host '       - Advanced Driver Properties: Attempted to enable'; "^
    "   } catch { } "^
    "}"

echo.

REM 3. Reminder about BIOS
echo [3/3] IMPORTANT REMINDER
echo ==================================================
echo Windows settings are now configured!
echo.
echo HOWEVER, you MUST still check your BIOS/UEFI settings.
echo This script CANNOT change BIOS settings.
echo.
echo 1. Output this message.
echo 2. Restart computer and press Del/F2.
echo 3. Enable 'Wake on LAN' in BIOS Power settings.
echo ==================================================
echo.
pause
