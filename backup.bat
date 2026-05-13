@echo off
title Sauvegarde ERP A3H
color 0A

echo ============================================
echo         SAUVEGARDE ERP A3H
echo ============================================
echo.

:: -------------------------------------------------
:: Creation dossier backups
:: -------------------------------------------------

IF NOT EXIST backups (
    mkdir backups
)

:: -------------------------------------------------
:: Date format YYYY-MM-DD
:: -------------------------------------------------

for /f %%i in ('powershell -NoProfile -Command "Get-Date -Format yyyy-MM-dd_HH-mm-ss"') do set datetime=%%i

:: -------------------------------------------------
:: Nom fichier backup
:: -------------------------------------------------

set backupfile=backups\db_%datetime%.sqlite3

:: -------------------------------------------------
:: Verification DB
:: -------------------------------------------------

IF NOT EXIST db.sqlite3 (
    echo [ERREUR] Base de donnees introuvable.
    pause
    exit /b
)

:: -------------------------------------------------
:: Copie DB
:: -------------------------------------------------

copy db.sqlite3 %backupfile%

IF %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERREUR] Sauvegarde echouee.
    pause
    exit /b
)

echo.
echo [OK] Sauvegarde terminee :
echo %backupfile%
echo.

pause