"""
4R022 Ear Control - Ses Motoru Temel Sınıfları (Base)
========================================================
Windows ve Linux arka uçlarının (backend) uyduğu ortak veri yapısı ve
arayüz (interface) burada tanımlanır. Her platform kendi dosyasında
(windows_backend.py / linux_backend.py) bu arayüzü uygular; üst katman
(dashboard, tray, main) hangi platformda çalıştığını hiç bilmeden aynı
API'yi kullanır. Desteklenmeyen platformlarda (ör. macOS) `UnsupportedAudioBackend`
devreye girer (bkz. aşağı).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional

SYSTEM_SOUNDS_KEY = "__system_sounds__"


@dataclass
class AppAudioSession:
    """Tek bir uygulamanın ses oturumunu temsil eder (platformdan bağımsız)."""

    pid: int
    process_name: str          # örn: "chrome.exe" / "firefox" / "Music"
    display_name: str          # kullanıcıya gösterilecek isim
    exe_path: Optional[str]
    volume: float = 0.0        # 0.0 - 1.0
    muted: bool = False
    peak: float = 0.0          # 0.0 - 1.0 anlık ses seviyesi (desteklenmiyorsa 0)
    is_system: bool = False

    # Platforma özel dahili referanslar (COM nesnesi, pulsectl sink-input id, vb.)
    _native_ref: object = field(default=None, repr=False, compare=False)
    _meter_ref: object = field(default=None, repr=False, compare=False)

    def key(self) -> str:
        return SYSTEM_SOUNDS_KEY if self.is_system else self.process_name.lower()


@dataclass
class BackendCapabilities:
    """Bir arka ucun neyi destekleyip desteklemediğini belirtir."""

    per_app_volume: bool = True
    per_app_mute: bool = True
    peak_metering: bool = True
    limitation_note_key: Optional[str] = None  # i18n anahtarı (varsa kullanıcıya gösterilir)


class AudioBackendBase:
    """Tüm platform arka uçlarının uyguladığı ortak arayüz."""

    name = "base"
    capabilities = BackendCapabilities()

    def __init__(self) -> None:
        self._sessions: Dict[int, AppAudioSession] = {}
        self._on_error: Optional[Callable[[str], None]] = None
        self.available = False

    def set_error_handler(self, handler: Callable[[str], None]) -> None:
        self._on_error = handler

    def _report_error(self, message: str) -> None:
        if self._on_error:
            try:
                self._on_error(message)
            except Exception:
                pass

    # -- Alt sınıfların uygulaması gereken metodlar -------------------------
    def refresh_sessions(self) -> List[AppAudioSession]:
        raise NotImplementedError

    def update_peaks(self) -> None:
        raise NotImplementedError

    def set_volume(self, pid: int, level: float) -> bool:
        raise NotImplementedError

    def set_mute(self, pid: int, muted: bool) -> bool:
        raise NotImplementedError

    # -- Ortak yardımcı metodlar (tüm backend'ler için aynı) ----------------
    def toggle_mute(self, pid: int) -> bool:
        sess = self._sessions.get(pid)
        if sess is None:
            return False
        return self.set_mute(pid, not sess.muted)

    def mute_all(self) -> None:
        for pid in list(self._sessions.keys()):
            self.set_mute(pid, True)

    def unmute_all(self) -> None:
        for pid in list(self._sessions.keys()):
            self.set_mute(pid, False)

    def get_sessions(self) -> List[AppAudioSession]:
        return list(self._sessions.values())

    @staticmethod
    def friendly_name(process_name: str) -> str:
        name = process_name
        if name.lower().endswith(".exe"):
            name = name[:-4]
        name = name.replace("_", " ").replace("-", " ")
        return name.strip().title() if name.strip() else process_name


class UnsupportedAudioBackend(AudioBackendBase):
    """
    Desteklenmeyen bir platformda (ör. macOS) çalışıldığında kullanılan
    "boş" arka uç. Sessizce başka bir platformun komutlarını (ör. Linux'ta
    `pactl`) çağırmaya çalışıp anlaşılmaz hatalar üretmek yerine, açıkça
    "bu platform desteklenmiyor" durumunu bildirir; dashboard/tray bu
    durumu `limitation_note_key` üzerinden kullanıcıya net bir şekilde
    gösterir.
    """

    name = "unsupported"
    capabilities = BackendCapabilities(
        per_app_volume=False,
        per_app_mute=False,
        peak_metering=False,
        limitation_note_key="platform_note_unsupported",
    )

    def __init__(self) -> None:
        super().__init__()
        self.available = False

    def refresh_sessions(self) -> List[AppAudioSession]:
        return []

    def update_peaks(self) -> None:
        pass

    def set_volume(self, pid: int, level: float) -> bool:
        return False

    def set_mute(self, pid: int, muted: bool) -> bool:
        return False
