@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion
REM Script pour compiler et packager le plugin QGIS Chemins Ruraux

echo ========================================
echo  Compilation et packaging du plugin
echo ========================================
echo.

REM Etape 1 : Compilation
echo [1/4] Compilation des ressources et UI...
python compile_plugin.py
if %ERRORLEVEL% NEQ 0 (
    echo Erreur lors de la compilation
    exit /b 1
)
echo.

REM Etape 2 : Packaging
echo [2/4] Création du package ZIP...
python package.py
if %ERRORLEVEL% NEQ 0 (
    echo Erreur lors du packaging
    exit /b 1
)
echo.

REM Etape 3 : Publication sur GitHub
echo [3/4] Publication sur GitHub...
for /f "delims=" %%v in ('python -c "from version import __version__; print(__version__)"') do set VERSION=%%v
git add --all
git diff --cached --quiet
if !ERRORLEVEL! EQU 0 (
    echo Rien a committer - working tree propre
) else (
    git commit -m "Release v!VERSION!"
    if !ERRORLEVEL! NEQ 0 (
        echo Erreur lors du commit
        exit /b 1
    )
    git push
    if !ERRORLEVEL! NEQ 0 (
        echo Erreur lors du push
        exit /b 1
    )
    echo Push vers GitHub reussi
)
echo.

REM Etape 4 : Déploiement automatique dans QGIS
set QGIS_PLUGINS=%APPDATA%\QGIS\QGIS3\profiles\default\python\plugins\chemins_ruraux
echo [4/4] Déploiement vers %QGIS_PLUGINS%...
powershell -Command "$zip = Get-ChildItem 'd:\chemins_ruraux\releases\chemins_ruraux-*.zip' | Sort-Object LastWriteTime -Descending | Select-Object -First 1; if ($zip) { Expand-Archive -Path $zip.FullName -DestinationPath (Split-Path '%QGIS_PLUGINS%') -Force; Write-Host ('Deploye : ' + $zip.Name) } else { Write-Host 'ZIP non trouve'; exit 1 }"
if %ERRORLEVEL% GTR 7 (
    echo Erreur lors du déploiement
) else (
    echo Déploiement terminé avec succès !
)

echo.
echo ========================================
echo  Terminé !
echo ========================================
