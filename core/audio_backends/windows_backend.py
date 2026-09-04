"""
4R022 Ear Control - Windows Ses Arka Ucu (pycaw)
===================================================
Windows Core Audio API'lerini `pycaw` ve `comtypes` üzerinden kullanarak
her uygulamanın (audio session) sesini ayrı ayrı okur ve kontrol eder.
Bu, desteklenen platformlar arasında en eksiksiz desteğe sahip olan arka
uçtur: gerçek zamanlı ses ölçümü (peak meter), uygulama başına ses ve
sessize alma tam olarak desteklenir.

Önemli notlar:
- COM nesneleri oluşturuldukları thread'e (apartment) bağlıdır. Bu yüzden
  tüm pycaw çağrıları UI thread'inde (QTimer ile) yapılır; ayrı bir
  QThread'den çağrılmaz. Bu, "0x8001010E" gibi apartment hatalarını önler.
- EarTrumpet veya Windows Ses Karıştırıcısı gibi başka araçlar da aynı
  ISimpleAudioVolume arayüzünü kullanır; hepsi aynı sistem durumunu okuyup
  yazdığından ve exclusive lock almadığından, bu araçlarla çakışma olmaz.
"""

from __future__ import annotations

from typing import List, Optional

from .base import AudioBackendBase, AppAudioSession, BackendCapabilities

try:
    from pycaw.pycaw import AudioUtilities, IAudioMeterInformation

    PYCAW_AVAILABLE = True
except ImportError:
    PYCAW_AVAILABLE = False

try:
    import psutil
except ImportError:
    psutil = None


class WindowsAudioBackend(AudioBackendBase):
    name = "windows"
    capabilities = BackendCapabilities(
        per_app_volume=True,
        per_app_mute=True,
        peak_metering=True,
        limitation_note_key=None,
    )

    def __init__(self) -> None:
        super().__init__()
        self.available = PYCAW_AVAILABLE

    # ------------------------------------------------------------------ #
    def refresh_sessions(self) -> List[AppAudioSession]:
        if not self.available:
            return []

        try:
            raw_sessions = AudioUtilities.GetAllSessions()
        except Exception as exc:
            self._report_error(f"Oturum listesi alınamadı: {exc}")
            return list(self._sessions.values())

        seen_pids = set()

        for session in raw_sessions:
            try:
                ctl = session._ctl  # IAudioSessionControl2
                if ctl is None:
                    continue
                pid = session.ProcessId
                is_system = pid == 0

                simple_volume = session.SimpleAudioVolume
                if simple_volume is None:
                    continue

                meter = self._get_meter(ctl)

                if is_system:
                    process_name = "__system_sounds__"
                    display_name = "system"
                    exe_path = None
                else:
                    process_name, exe_path = self._resolve_process(pid)
                    if process_name is None:
                        continue
                    display_name = self.friendly_name(process_name)

                seen_pids.add(pid)

                existing = self._sessions.get(pid)
                if existing is None:
                    existing = AppAudioSession(
                        pid=pid,
                        process_name=process_name,
                        display_name=display_name,
                        exe_path=exe_path,
                        is_system=is_system,
                    )
                    self._sessions[pid] = existing

                existing._native_ref = simple_volume
                existing._meter_ref = meter
                try:
                    existing.volume = float(simple_volume.GetMasterVolume())
                    existing.muted = bool(simple_volume.GetMute())
                except Exception:
                    pass

            except Exception:
                continue

        for pid in list(self._sessions.keys()):
            if pid not in seen_pids:
                del self._sessions[pid]

        return list(self._sessions.values())

    def _get_meter(self, ctl):
        try:
            return ctl.QueryInterface(IAudioMeterInformation)
        except Exception:
            return None

    def _resolve_process(self, pid: int):
        if psutil is None:
            return f"pid_{pid}.exe", None
        try:
            proc = psutil.Process(pid)
            name = proc.name()
            try:
                exe_path = proc.exe()
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                exe_path = None
            return name, exe_path
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return None, None

    # ------------------------------------------------------------------ #
    def update_peaks(self) -> None:
        for sess in self._sessions.values():
            meter = sess._meter_ref
            if meter is None:
                sess.peak = 0.0
                continue
            try:
                sess.peak = float(meter.GetPeakValue())
            except Exception:
                sess.peak = 0.0

    # ------------------------------------------------------------------ #
    def set_volume(self, pid: int, level: float) -> bool:
        level = max(0.0, min(1.0, level))
        sess = self._sessions.get(pid)
        if sess is None or sess._native_ref is None:
            return False
        try:
            sess._native_ref.SetMasterVolume(level, None)
            sess.volume = level
            if level > 0 and sess.muted:
                sess._native_ref.SetMute(False, None)
                sess.muted = False
            return True
        except Exception as exc:
            self._report_error(f"Ses ayarlanamadı ({sess.display_name}): {exc}")
            return False

    def set_mute(self, pid: int, muted: bool) -> bool:
        sess = self._sessions.get(pid)
        if sess is None or sess._native_ref is None:
            return False
        try:
            sess._native_ref.SetMute(muted, None)
            sess.muted = muted
            return True
        except Exception as exc:
            self._report_error(f"Sessize alma başarısız ({sess.display_name}): {exc}")
            return False


def is_eartrumpet_running() -> bool:
    """EarTrumpet.exe çalışıyor mu diye kontrol eder (yalnızca Windows)."""
    if psutil is None:
        return False
    try:
        for proc in psutil.process_iter(attrs=["name"]):
            name = (proc.info.get("name") or "").lower()
            if name == "eartrumpet.exe":
                return True
    except Exception:
        pass
    return False
