@echo off
title Installation ERP A3H
color 0A

echo ============================================
echo        INSTALLATION ERP A3H
echo ============================================
echo.

:: -------------------------------------------------
:: Verification Python
:: -------------------------------------------------

python --version >nul 2>&1

IF %ERRORLEVEL% NEQ 0 (
    echo [ERREUR] Python n'est pas installe.
    echo Veuillez installer Python 3.11
    pause
    exit /b
)

echo [OK] Python detecte.
echo.

:: -------------------------------------------------
:: Creation environnement virtuel
:: -------------------------------------------------

IF NOT EXIST venv (
    echo Creation environnement virtuel...
    python -m venv venv
)

echo [OK] Environnement virtuel pret.
echo.

:: -------------------------------------------------
:: Activation environnement
:: -------------------------------------------------

call venv\Scripts\activate

:: -------------------------------------------------
:: Mise a jour pip
:: -------------------------------------------------

echo Mise a jour pip...
python -m pip install --upgrade pip

:: -------------------------------------------------
:: Installation dependances
:: -------------------------------------------------

echo Installation des dependances...
pip install -r requirements.txt

IF %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERREUR] Installation des dependances echouee.
    pause
    exit /b
)

echo.
echo [OK] Dependances installees.
echo.

:: -------------------------------------------------
:: Creation dossiers necessaires
:: -------------------------------------------------

IF NOT EXIST backups mkdir backups
IF NOT EXIST logs mkdir logs
IF NOT EXIST media mkdir media
IF NOT EXIST staticfiles mkdir staticfiles

echo [OK] Dossiers systeme crees.
echo.

:: -------------------------------------------------
:: Migrations Django
:: -------------------------------------------------

echo Application migrations...

python manage.py makemigrations
python manage.py migrate

IF %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERREUR] Probleme migrations.
    pause
    exit /b
)

echo.
echo [OK] Base de donnees initialisee.
echo.

:: -------------------------------------------------
:: Collect static
:: -------------------------------------------------

python manage.py collectstatic --noinput

echo.
echo [OK] Fichiers statiques prepares.
echo.

:: -------------------------------------------------
:: Creation superuser optionnelle
:: -------------------------------------------------

echo Voulez-vous creer un administrateur ?
choice /C ON /M "O = Oui / N = Non"

IF ERRORLEVEL 2 GOTO skipadmin
IF ERRORLEVEL 1 GOTO createsu

:createsu
python manage.py createsuperuser

:skipadmin

:: -------------------------------------------------
:: Fin
:: -------------------------------------------------

echo.
echo ============================================
echo     INSTALLATION TERMINEE AVEC SUCCES
echo ============================================
echo.

echo Pour lancer ERP :
echo.
echo call venv\Scripts\activate
echo python manage.py runserver
echo.

pause