@echo off
title ERP A3H
color 0B

echo ============================================
echo             ERP A3H
echo ============================================
echo.

:: -------------------------------------------------
:: Verification environnement
:: -------------------------------------------------

IF NOT EXIST venv (
    echo [ERREUR] Environnement virtuel introuvable.
    echo Lancez install.bat d'abord.
    pause
    exit /b
)

:: -------------------------------------------------
:: Activation virtualenv
:: -------------------------------------------------

call venv\Scripts\activate

:: -------------------------------------------------
:: Verification base SQLite
:: -------------------------------------------------

IF NOT EXIST db.sqlite3 (
    echo [ERREUR] Base de donnees introuvable.
    pause
    exit /b
)

echo [OK] Base detectee.
echo.

:: -------------------------------------------------
:: Ouverture navigateur automatique
:: -------------------------------------------------

start http://127.0.0.1:8000

:: -------------------------------------------------
:: Lancement serveur Django
:: -------------------------------------------------

echo Demarrage ERP...
echo.
echo Ne fermez pas cette fenetre.
echo.

python manage.py runserver 127.0.0.1:8000

pause