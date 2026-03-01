@echo off
chcp 65001 > nul
REM Script pour compiler et packager le plugin QGIS Chemins Ruraux

echo ========================================
echo  Compilation et packaging du plugin
echo ========================================
echo.

REM Etape 1 : Compilation
echo [1/2] Compilation des ressources et UI...
python compile_plugin.py
if %ERRORLEVEL% NEQ 0 (
    echo Erreur lors de la compilation
    pause
    exit /b 1
)
echo.

REM Etape 2 : Packaging
echo [2/2] Création du package ZIP...
python package.py
if %ERRORLEVEL% NEQ 0 (
    echo Erreur lors du packaging
    pause
    exit /b 1
)

echo.

REM Etape 3 (optionnelle) : Déploiement dans QGIS (push-only, sens unique)
set QGIS_PLUGINS=%APPDATA%\QGIS\QGIS3\profiles\default\python\plugins\chemins_ruraux
echo [Optionnel] Déployer dans QGIS ? (O/N)
set /p DEPLOY="> "
if /I "%DEPLOY%"=="O" (
    echo.
    echo [3/3] Déploiement vers %QGIS_PLUGINS%...
    powershell -Command "$zip = Get-ChildItem 'd:\chemins_ruraux\releases\chemins_ruraux-*.zip' | Sort-Object LastWriteTime -Descending | Select-Object -First 1; if ($zip) { Expand-Archive -Path $zip.FullName -DestinationPath (Split-Path '%QGIS_PLUGINS%') -Force; Write-Host ('Deploye : ' + $zip.Name) } else { Write-Host 'ZIP non trouve'; exit 1 }"
    if %ERRORLEVEL% GTR 7 (
        echo Erreur lors du déploiement
    ) else (
        echo Déploiement terminé avec succès !
    )
) else (
    echo Déploiement ignoré.
)

echo.
echo ========================================
echo  Terminé !
echo ========================================
pause
