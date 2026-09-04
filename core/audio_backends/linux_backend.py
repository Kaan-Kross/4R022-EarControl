"""
4R022 Ear Control - Linux Ses Arka Ucu (pactl)
=================================================
Linux'ta uygulama başına ses kontrolü, PulseAudio (ve onunla uyumlu
PipeWire "pipewire-pulse" katmanı) üzerinden `pactl` komut satırı aracı
kullanılarak sağlanır. Ekstra bir Python paketine ihtiyaç duymaz; sadece
stdlib `subprocess` kullanılır — 4R022 projelerindeki "stdlib öncelikli,
eksik bağımlılıkta çökmeme" prensibiyle uyumludur. PulseAudio doğrudan
veya PipeWire'ın `pipewire-pulse` uyumluluk katmanı üzerinden çalışan
neredeyse tüm modern dağıtımlarda (Ubuntu, Fedora, Debian, Arch, Pop!_OS,
Mint vb.) `pactl` zaten kurulu gelir.

Çoklu akış (multi-stream) desteği:
Chrome/Firefox gibi bazı uygulamalar HER SEKME/PENCERE için ayrı bir
"sink input" oluşturur ve bunların hepsi AYNI process ID'sine (pid) sahip
olabilir. Önceki sürüm, aynı pid'e ait yalnızca SON görülen sink-input'u
takip ediyordu; bu da ses/sessize alma değişikliğinin o uygulamanın
yalnızca bir akışına uygulanıp diğerlerine uygulanmamasına (ör. bir
Chrome sekmesi sessize alınırken diğerlerinin çalmaya devam etmesine)
neden oluyordu. Bu sürümde her pid, kendisine ait TÜM sink-input
indekslerinin bir listesiyle eşleştirilir; ses/sessize alma işlemleri bu
listedeki her akışa uygulanır — tıpkı Windows/EarTrumpet'teki uygulama
bazlı birleşik davranış gibi.

Sınırlama — Ses Ölçer (Peak Meter):
PulseAudio'nun senkron kontrol arayüzü (pactl) gerçek zamanlı bir "peak"
değeri vermez; bunun için ayrı bir monitor stream'e bağlanıp ham ses
örneklerini okumak gerekir (ek ses G/Ç bağımlılığı gerektirir). Bunun
yerine, oturumun o an sesi açık ve çalıyor (corked=no) olup olmadığına
göre, ayarlı ses seviyesini temel alan bir "aktiflik göstergesi" sunulur.
Bu, gerçek RMS/peak ölçümü DEĞİLDİR; sadece "bu uygulama şu an ses
çıkarıyor" bilgisini görsel olarak yansıtır.
"""

from __future__ import annotations

import re
import shutil
import subprocess
from typing import Dict, List, Optional

from .base import AudioBackendBase, AppAudioSession, BackendCapabilities

try:
    import psutil
except ImportError:
    psutil = None

_PACTL = shutil.which("pactl")


def _run(args: List[str]) -> Optional[str]:
    if not _PACTL:
        return None
    try:
        result = subprocess.run(
            [_PACTL] + args,
            capture_output=True,
            text=True,
            timeout=2.0,
        )
        if result.returncode != 0:
            return None
        return result.stdout
    except (subprocess.TimeoutExpired, OSError):
        return None


def _parse_sink_inputs(raw: str) -> List[Dict[str, str]]:
    """`pactl list sink-inputs` metin çıktısını ayrıştırır."""
    if not raw:
        return []

    entries: List[Dict[str, str]] = []
    blocks = re.split(r"\n(?=Sink Input #)", raw.strip())

    for block in blocks:
        if not block.startswith("Sink Input #"):
            continue
        entry: Dict[str, str] = {}

        m = re.search(r"Sink Input #(\d+)", block)
        if not m:
            continue
        entry["index"] = m.group(1)

        m = re.search(r"Mute:\s*(yes|no)", block)
        entry["mute"] = m.group(1) if m else "no"

        # "Volume: front-left: 45000 /  69% / ..." -> ilk yüzdeyi al
        m = re.search(r"Volume:.*?(\d+)%", block)
        entry["volume_pct"] = m.group(1) if m else "100"

        m = re.search(r"Corked:\s*(yes|no)", block)
        entry["corked"] = m.group(1) if m else "no"

        for prop_key, dest in (
            ("application.name", "app_name"),
            ("application.process.id", "pid"),
            ("application.process.binary", "binary"),
            ("application.icon_name", "icon_name"),
        ):
            m = re.search(rf'{re.escape(prop_key)} = "([^"]*)"', block)
            if m:
                entry[dest] = m.group(1)

        entries.append(entry)

    return entries


class LinuxAudioBackend(AudioBackendBase):
    name = "linux"
    capabilities = BackendCapabilities(
        per_app_volume=True,
        per_app_mute=True,
        peak_metering=True,  # yaklaşık (bkz. modül başı not)
        limitation_note_key="platform_note_linux_meter",
    )

    def __init__(self) -> None:
        super().__init__()
        self.available = _PACTL is not None
        # pid -> o pid'e ait TÜM sink-input indekslerinin listesi
        # (bkz. modül başındaki "Çoklu akış desteği" notu)
        self._indexes_by_pid: Dict[int, List[str]] = {}

    # ------------------------------------------------------------------ #
    def refresh_sessions(self) -> List[AppAudioSession]:
        if not self.available:
            return []

        raw = _run(["list", "sink-inputs"])
        entries = _parse_sink_inputs(raw or "")

        seen_pids = set()
        indexes_by_pid: Dict[int, List[str]] = {}
        # pid başına birleşik durum: herhangi bir akış sessizde değilse ve
        # çalıyorsa "aktif" kabul edilir; ses seviyesi akışların ortalaması
        aggregate: Dict[int, Dict[str, float]] = {}

        for entry in entries:
            try:
                sink_index = entry["index"]
                pid_str = entry.get("pid")
                # PID yoksa (bazı sistem sesleri), sink index'i sanal pid olarak kullan
                pid = int(pid_str) if pid_str and pid_str.isdigit() else -int(sink_index) - 1000

                binary = entry.get("binary") or entry.get("app_name") or f"app_{sink_index}"
                display = entry.get("app_name") or self.friendly_name(binary)
                exe_path = self._resolve_exe_path(pid_str)

                volume = max(0.0, min(1.0, int(entry.get("volume_pct", "100")) / 100.0))
                muted = entry.get("mute") == "yes"
                corked = entry.get("corked") == "yes"

                seen_pids.add(pid)
                indexes_by_pid.setdefault(pid, []).append(sink_index)

                agg = aggregate.setdefault(pid, {"vol_sum": 0.0, "count": 0, "any_active": False,
                                                    "all_muted": True, "binary": binary,
                                                    "display": display, "exe_path": exe_path})
                agg["vol_sum"] += volume
                agg["count"] += 1
                agg["all_muted"] = agg["all_muted"] and muted
                agg["any_active"] = agg["any_active"] or (not muted and not corked)

            except Exception:
                continue

        for pid, agg in aggregate.items():
            count = max(1, agg["count"])
            avg_volume = agg["vol_sum"] / count

            existing = self._sessions.get(pid)
            if existing is None:
                existing = AppAudioSession(
                    pid=pid,
                    process_name=agg["binary"],
                    display_name=agg["display"],
                    exe_path=agg["exe_path"],
                    is_system=False,
                )
                self._sessions[pid] = existing

            existing.volume = avg_volume
            existing.muted = agg["all_muted"]
            # Yaklaşık aktiflik göstergesi: en az bir akış sessize alınmamış
            # ve duraklatılmamışsa (corked=no), aksi halde 0.
            existing.peak = avg_volume if agg["any_active"] else 0.0

        self._indexes_by_pid = indexes_by_pid

        for pid in list(self._sessions.keys()):
            if pid not in seen_pids:
                del self._sessions[pid]

        return list(self._sessions.values())

    def _resolve_exe_path(self, pid_str: Optional[str]) -> Optional[str]:
        if not pid_str or not pid_str.isdigit() or psutil is None:
            return None
        try:
            return psutil.Process(int(pid_str)).exe()
        except Exception:
            return None

    # ------------------------------------------------------------------ #
    def update_peaks(self) -> None:
        # refresh_sessions() sırasında yaklaşık değer zaten hesaplanıyor;
        # pactl'ın senkron API'si daha sık bir sorgulamayı desteklemediği
        # için burada ek bir işlem yapılmaz (gereksiz süreç başlatmayı önler).
        pass

    # ------------------------------------------------------------------ #
    def set_volume(self, pid: int, level: float) -> bool:
        indexes = self._indexes_by_pid.get(pid)
        if not indexes:
            return False
        level = max(0.0, min(1.0, level))
        pct = int(round(level * 100))

        ok_any = False
        for sink_index in indexes:
            result = _run(["set-sink-input-volume", sink_index, f"{pct}%"])
            if result is not None:
                ok_any = True
            else:
                self._report_error(f"Ses ayarlanamadı (sink-input #{sink_index})")

        if not ok_any:
            return False

        sess = self._sessions.get(pid)
        if sess:
            sess.volume = level
            if level > 0 and sess.muted:
                self.set_mute(pid, False)
        return True

    def set_mute(self, pid: int, muted: bool) -> bool:
        indexes = self._indexes_by_pid.get(pid)
        if not indexes:
            return False

        ok_any = False
        for sink_index in indexes:
            result = _run(["set-sink-input-mute", sink_index, "1" if muted else "0"])
            if result is not None:
                ok_any = True
            else:
                self._report_error(f"Sessize alma başarısız (sink-input #{sink_index})")

        if not ok_any:
            return False

        sess = self._sessions.get(pid)
        if sess:
            sess.muted = muted
        return True
