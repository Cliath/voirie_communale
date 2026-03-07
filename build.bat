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

REM Etape 4 : Commit, tag et push
echo [4/6] Publication sur GitHub (commit + tag)...
REM Recherche de git.exe (PATH systeme ou GitHub Desktop)
set GIT_EXE=
where git >nul 2>&1
if !ERRORLEVEL! EQU 0 (
    set GIT_EXE=git
) else (
    for /f "delims=" %%G in ('powershell -NoProfile -Command "Get-ChildItem \"$env:LOCALAPPDATA\GitHubDesktop\" -Recurse -Filter git.exe -ErrorAction SilentlyContinue | Select-Object -First 1 -ExpandProperty FullName"') do set GIT_EXE=%%G
)
if not defined GIT_EXE (
    echo AVERTISSEMENT : git non trouve, etapes GitHub ignorees
    goto :deploy
)
!GIT_EXE! add --all
!GIT_EXE! diff --cached --quiet
if !ERRORLEVEL! EQU 0 (
    echo Rien a committer - working tree propre
) else (
    set PYTHONUTF8=1
    python get_commit_message.py > .commit_msg.txt
    !GIT_EXE! commit -F .commit_msg.txt
    del .commit_msg.txt
    if !ERRORLEVEL! NEQ 0 (
        echo Erreur lors du commit
        exit /b 1
    )
)
REM Tag de version (ecrase si existant)
!GIT_EXE! tag -f v!VERSION!
!GIT_EXE! push
!GIT_EXE! push origin v!VERSION! --force
if !ERRORLEVEL! NEQ 0 (
    echo Erreur lors du push
    exit /b 1
)
echo Push et tag v!VERSION! envoyes vers GitHub
echo.

REM Etape 5 : GitHub Release avec le ZIP
echo [5/6] Creation de la GitHub Release v%VERSION%...
powershell -NoProfile -Command "$v='%VERSION%'; $zip='releases\voirie_communale-' + $v + '.zip'; $title='Voirie Communale v' + $v; gh release create ('v'+$v) $zip --title $title --generate-notes; if ($LASTEXITCODE -eq 0) { Write-Host ('GitHub Release v'+$v+' creee avec le ZIP') } else { Write-Host 'Erreur lors de la creation de la GitHub Release' }"
echo.

:deploy
REM Etape 6 : Deploiement automatique dans QGIS
set QGIS_PLUGINS=%APPDATA%\QGIS\QGIS3\profiles\default\python\plugins\voirie_communale
echo [6/6] Deploiement vers %QGIS_PLUGINS%...
powershell -Command "$zip = Get-ChildItem 'd:\voirie_communale\releases\voirie_communale-*.zip' | Sort-Object LastWriteTime -Descending | Select-Object -First 1; if ($zip) { Expand-Archive -Path $zip.FullName -DestinationPath (Split-Path '%QGIS_PLUGINS%') -Force; Write-Host ('Deploye : ' + $zip.Name) } else { Write-Host 'ZIP non trouve'; exit 1 }"
if %ERRORLEVEL% GTR 7 (
    echo Erreur lors du deploiement
) else (
    echo Deploiement termine avec succes !
)

echo.
echo ========================================
echo  Termine - v!VERSION!
echo ========================================

