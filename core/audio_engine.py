"""
4R022 Ear Control - Ses Motoru (Facade)
==========================================
Bu modül, `audio_backends` paketinden çalışılan platforma uygun arka ucu
(Windows/Linux, desteklenmeyenlerde UnsupportedAudioBackend) seçer ve
dashboard/tray/main.py katmanlarına TEK ve platformdan bağımsız bir API
sunar. Üst katmanlar hiçbir zaman hangi işletim sisteminde çalıştığını
bilmek zorunda kalmaz.
"""

from __future__ import annotations

import sys
from typing import Callable, List, Optional

from .audio_backends import AppAudioSession, BackendCapabilities, get_backend
from .audio_backends.base import SYSTEM_SOUNDS_KEY

try:
    import psutil
except ImportError:
    psutil = None


class AudioEngine:
    """Platformdan bağımsız ses motoru — gerçek işi seçilen backend yapar."""

    def __init__(self) -> None:
        self._backend = get_backend()
        self.available = self._backend.available
        self.platform_name = self._backend.name
        self.capabilities: BackendCapabilities = self._backend.capabilities

    def set_error_handler(self, handler: Callable[[str], None]) -> None:
        self._backend.set_error_handler(handler)

    # -- Oturum tarama / ölçüm ---------------------------------------------
    def refresh_sessions(self) -> List[AppAudioSession]:
        return self._backend.refresh_sessions()

    def update_peaks(self) -> None:
        self._backend.update_peaks()

    def get_sessions(self) -> List[AppAudioSession]:
        return self._backend.get_sessions()

    # -- Kontrol -------------------------------------------------------------
    def set_volume(self, pid: int, level: float) -> bool:
        return self._backend.set_volume(pid, level)

    def set_mute(self, pid: int, muted: bool) -> bool:
        return self._backend.set_mute(pid, muted)

    def toggle_mute(self, pid: int) -> bool:
        return self._backend.toggle_mute(pid)

    def mute_all(self) -> None:
        self._backend.mute_all()

    def unmute_all(self) -> None:
        self._backend.unmute_all()


def is_eartrumpet_running() -> bool:
    """
    EarTrumpet.exe çalışıyor mu diye kontrol eder (yalnızca Windows'ta
    anlamlıdır; diğer platformlarda her zaman False döner).
    """
    if sys.platform != "win32" or psutil is None:
        return False
    try:
        for proc in psutil.process_iter(attrs=["name"]):
            name = (proc.info.get("name") or "").lower()
            if name == "eartrumpet.exe":
                return True
    except Exception:
        pass
    return False
