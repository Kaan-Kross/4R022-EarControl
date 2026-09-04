#!/bin/bash
# 4R022 Ear Control - Otomatik Build (Linux)
# =====================================================
# Bu betik Build/ klasöründedir; ilk iş olarak proje köküne (bir üst
# klasöre) geçer, ardından tüm işlemleri (sanal ortam, bağımlılıklar,
# derleme) proje kökünden yürütür. Nereden çalıştırılırsa çalıştırılsın
# (çift tık, terminal, başka bir dizinden çağırma) doğru şekilde çalışır.
#
# Sistem Python'unu kirletmemek ve modern Debian/Ubuntu'daki
# "externally-managed-environment" (PEP 668) kısıtlamasından
# etkilenmemek için, proje köküne özel bir sanal ortam (.venv)
# oluşturur ve tüm işlemleri onun içinde yapar.
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

VENV_DIR=".venv"

echo "============================================"
echo "  4R022 Ear Control - Otomatik Build"
echo "============================================"
echo "Proje kökü: $PROJECT_ROOT"
echo ""

if ! command -v python3 &> /dev/null; then
    echo "[HATA] python3 bulunamadi. Lutfen once Python 3.10+ kurun."
    exit 1
fi

if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    if ! command -v pactl &> /dev/null; then
        echo "[UYARI] 'pactl' bulunamadi. Uygulama-basina ses kontrolu icin gereklidir."
        echo "         Debian/Ubuntu: sudo apt install pulseaudio-utils"
    fi
fi

echo "[1/4] Sanal ortam (.venv) hazirlaniyor..."
if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR"
fi
# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"

echo ""
echo "[2/4] Bagimliliklar kuruluyor..."
python -m pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "[3/4] PyInstaller ile calistirilabilir dosya derleniyor..."
pyinstaller --noconfirm Build/4R022_EarControl.spec

deactivate

echo ""
echo "[4/4] Tamamlandi!"
echo "Cikti dosyasi: dist/4R022_EarControl"
echo "(Sanal ortam .venv proje kokunde kaldi; tekrar build alirken yeniden kullanilir.)"
echo ""
