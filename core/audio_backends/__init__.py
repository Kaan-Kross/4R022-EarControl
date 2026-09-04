"""
4R022 Ear Control - Ses Arka Uçları Paketi
=============================================
`get_backend()` çağrıldığında, çalışılan işletim sistemine göre doğru arka
ucu seçip döndürür.

Desteklenen platformlar: Windows ve Linux (PulseAudio/PipeWire `pactl`).
macOS bu sürümde artık desteklenmiyor: uygulama başına ses kontrolü için
genel bir sistem API'si sunmadığından ve tek işlevi olan "Ana Ses"
kontrolü de bu sürümde kaldırıldığından, macOS'ta anlamsız/boş bir
uygulama sunmak yerine `UnsupportedAudioBackend` ile durum kullanıcıya
açıkça bildirilir.
"""

from __future__ import annotations

import sys

from .base import (
    AppAudioSession,
    AudioBackendBase,
    BackendCapabilities,
    SYSTEM_SOUNDS_KEY,
    UnsupportedAudioBackend,
)


def get_backend() -> AudioBackendBase:
    if sys.platform == "win32":
        from .windows_backend import WindowsAudioBackend

        return WindowsAudioBackend()
    elif sys.platform.startswith("linux"):
        from .linux_backend import LinuxAudioBackend

        return LinuxAudioBackend()
    else:
        # macOS (darwin) ve diğer desteklenmeyen platformlar
        return UnsupportedAudioBackend()


__all__ = [
    "get_backend",
    "AppAudioSession",
    "AudioBackendBase",
    "BackendCapabilities",
    "SYSTEM_SOUNDS_KEY",
    "UnsupportedAudioBackend",
]
