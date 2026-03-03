@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion
REM Script pour compiler et packager le plugin QGIS Voirie Communale
REM Usage : build.bat [patch|minor|major]   (defaut : patch)

set BUMP=%1
if "!BUMP!"=="" set BUMP=patch
if /i "!BUMP!" NEQ "patch" if /i "!BUMP!" NEQ "minor" if /i "!BUMP!" NEQ "major" (
    echo Usage : build.bat [patch^|minor^|major]
    exit /b 1
)

echo ========================================
echo  Compilation et packaging du plugin
echo ========================================
echo.

REM Etape 1 : Increment de version
echo [1/4] Increment de version (!BUMP!)...
for /f "delims=" %%v in ('python bump_version.py !BUMP!') do set VERSION=%%v
if !ERRORLEVEL! NEQ 0 (
    echo Erreur lors de l'increment de version
    exit /b 1
)
echo Nouvelle version : !VERSION!
echo.

REM Etape 2 : Compilation
echo [2/4] Compilation des ressources et UI...
python compile_plugin.py
if !ERRORLEVEL! NEQ 0 (
    echo Erreur lors de la compilation
    exit /b 1
)
echo.

REM Etape 3 : Packaging
echo [3/4] Creation du package ZIP...
python package.py
if !ERRORLEVEL! NEQ 0 (
    echo Erreur lors du packaging
    exit /b 1
)
echo.

REM Etape 4 : Publication sur GitHub
echo [4/4] Publication sur GitHub...
git add --all
git diff --cached --quiet
if !ERRORLEVEL! EQU 0 (
    echo Rien a committer - working tree propre
) else (
    set PYTHONUTF8=1
    python get_commit_message.py > .commit_msg.txt
    git commit -F .commit_msg.txt
    del .commit_msg.txt
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

REM Etape 5 : Deploiement automatique dans QGIS
set QGIS_PLUGINS=%APPDATA%\QGIS\QGIS3\profiles\default\python\plugins\chemins_ruraux
echo [5/5] Deploiement vers %QGIS_PLUGINS%...
powershell -Command "$zip = Get-ChildItem 'd:\chemins_ruraux\releases\chemins_ruraux-*.zip' | Sort-Object LastWriteTime -Descending | Select-Object -First 1; if ($zip) { Expand-Archive -Path $zip.FullName -DestinationPath (Split-Path '%QGIS_PLUGINS%') -Force; Write-Host ('Deploye : ' + $zip.Name) } else { Write-Host 'ZIP non trouve'; exit 1 }"
if %ERRORLEVEL% GTR 7 (
    echo Erreur lors du deploiement
) else (
    echo Deploiement termine avec succes !
)

echo.
echo ========================================
echo  Termine - v!VERSION!
echo ========================================

