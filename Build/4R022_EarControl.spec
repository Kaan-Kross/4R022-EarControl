# -*- mode: python ; coding: utf-8 -*-
"""
4R022 Ear Control - PyInstaller Derleme Tarifi (Spec)
========================================================
Bu dosya, proje kökünden `pyinstaller --noconfirm Build/4R022_EarControl.spec`
komutuyla çalıştırılır. Build/build.bat (Windows) / Build/build.sh
(Linux) betikleri bunu otomatik olarak, doğru çalışma dizininden çağırır
— elle komut yazmanıza gerek yoktur.

Önemli: Bu dosya `Build/` klasöründe, giriş noktası ise `Main/main.py`
dosyasındadır. Bu yüzden tüm yollar, PROJE KÖKÜNE göre (mevcut çalışma
dizini / current working directory) hesaplanır — build betikleri her
zaman önce proje köküne `cd` yapar.

Bu sürüm yalnızca Windows ve Linux'u hedefler (macOS artık desteklenmiyor).
Windows'ta `assets/app.ico` gömülür; Linux'ta ikon exe içine gömülmez
(.desktop dosyası ayrı ele alınır), yalnızca `assets/` klasörü veri
olarak dahil edilir.

NOT: Önceki sürümde bu dosyada PYZ/EXE blokları YANLIŞLIKLA iki kez
tanımlanmıştı (kopyala-yapıştır hatası) — işlevsel bir çökmeye yol
açmıyordu (ikinci tanım birinciyi sessizce geçersiz kılıyordu) ama
derlemeyi gereksiz yere iki kez tekrarlayıp yavaşlatıyordu. Bu sürümde
düzeltildi; her blok yalnızca bir kez tanımlanır.
"""

import os
import sys

block_cipher = None

# Build betikleri bu spec'i her zaman proje kökünden çalıştırır; bu yüzden
# os.path.abspath(".") güvenle proje kökünü verir.
PROJECT_ROOT = os.path.abspath(".")
MAIN_SCRIPT = os.path.join(PROJECT_ROOT, "Main", "main.py")
ASSETS_DIR = os.path.join(PROJECT_ROOT, "assets")

if sys.platform == "win32":
    icon_file = os.path.join(ASSETS_DIR, "app.ico")
else:
    icon_file = None  # Linux .desktop simgeleri ayrı ele alınır, exe içine gömülmez

a = Analysis(
    [MAIN_SCRIPT],
    pathex=[PROJECT_ROOT],  # "core" paketinin bulunabilmesi için proje kökü eklenir
    binaries=[],
    datas=[(ASSETS_DIR, "assets")],
    hiddenimports=[
        "core.audio_backends.windows_backend",
        "core.audio_backends.linux_backend",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="4R022_EarControl",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,          # Arka planda çalışan bir GUI uygulaması, konsol penceresi açılmaz
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_file,
)
