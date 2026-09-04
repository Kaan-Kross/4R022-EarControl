"""
4R022 Ear Control - Kaynak (Asset) Yol Çözümleyici
=====================================================
`assets/` klasörünün mutlak yolunu, hem kaynaktan doğrudan çalıştırmada
(`python Main/main.py`) hem de PyInstaller ile paketlenmiş ('frozen')
halde aynı şekilde bulur. Main/main.py'deki `resource_path()` ile aynı
mantığı kullanır; bu modül sayesinde `core` katmanındaki dosyalar
(dashboard.py gibi) `Main` paketine bağımlı olmadan kaynaklara erişebilir
(daha önce bu mantık yalnızca main.py'de vardı ve tekrarlanamıyordu).
"""

from __future__ import annotations

import os
import sys

# core/assets.py -> core/ -> proje kökü
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def assets_dir() -> str:
    """PyInstaller ile paketlenmişse sys._MEIPASS içindeki, değilse proje
    kökündeki assets/ klasörünün mutlak yolunu döndürür."""
    base = getattr(sys, "_MEIPASS", _PROJECT_ROOT)
    return os.path.join(base, "assets")


def asset_path(*parts: str) -> str:
    """assets/ klasörü altındaki bir dosyanın mutlak yolunu döndürür.
    Örn: asset_path("logo_full.png") -> .../assets/logo_full.png"""
    return os.path.join(assets_dir(), *parts)
