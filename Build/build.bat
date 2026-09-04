@echo off
setlocal
title 4R022 Ear Control - Windows Build
color 0C

rem Bu betik Build\ klasorundedir; once proje kokune (bir ust klasore) gecer,
rem ardindan tum islemleri (sanal ortam, bagimliliklar, derleme) proje
rem kokunden yurutur. Cift tik ile veya terminalden calistirilabilir.
cd /d "%~dp0.."

set VENV_DIR=.venv

echo ============================================
echo   4R022 Ear Control - Otomatik Build (.exe)
echo ============================================
echo Proje koku: %CD%
echo.

where python >nul 2>nul
if errorlevel 1 (
    echo [HATA] Python bulunamadi. Lutfen once Python 3.10+ kurun ve PATH'e ekleyin.
    pause
    exit /b 1
)

echo [1/4] Sanal ortam (.venv) hazirlaniyor...
if not exist "%VENV_DIR%\Scripts\activate.bat" (
    python -m venv "%VENV_DIR%"
)
call "%VENV_DIR%\Scripts\activate.bat"

echo.
echo [2/4] Bagimliliklar kuruluyor...
python -m pip install --upgrade pip >nul
pip install -r requirements.txt
if errorlevel 1 (
    echo [HATA] Bagimlilik kurulumu basarisiz oldu.
    call "%VENV_DIR%\Scripts\deactivate.bat"
    pause
    exit /b 1
)

echo.
echo [3/4] PyInstaller ile .exe derleniyor...
pyinstaller --noconfirm Build\4R022_EarControl.spec
if errorlevel 1 (
    echo [HATA] Derleme basarisiz oldu.
    call "%VENV_DIR%\Scripts\deactivate.bat"
    pause
    exit /b 1
)

call "%VENV_DIR%\Scripts\deactivate.bat"

echo.
echo [4/4] Tamamlandi!
echo Cikti dosyasi: dist\4R022_EarControl.exe
echo (Sanal ortam .venv proje kokunde kaldi; bir sonraki build'de tekrar kullanilir.)
echo.
pause
