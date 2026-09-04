"""
4R022 Ear Control - Yapılandırma Yönetimi
==========================================
Kullanıcı ayarlarını (dil, otomatik başlatma, hatırlanan ses seviyeleri vb.)
platforma uygun kullanıcı veri klasöründe, atomik JSON yazımıyla saklar.
Bozulma ihtimaline karşı .bak yedeği tutulur ve okunamazsa varsayılana
otomatik olarak (self-healing) dönülür.
"""

from __future__ import annotations

import copy
import json
import os
import sys
import tempfile
import threading
from pathlib import Path
from typing import Any, Dict

APP_NAME = "4R022 Ear Control"
APP_FOLDER = "4R022EarControl"
VERSION = "1.8.0"

DEFAULT_CONFIG: Dict[str, Any] = {
    "language": "tr",                 # "tr" | "en"
    "start_with_windows": False,
    "start_minimized": True,
    "show_tray_notifications": True,
    "poll_interval_ms": 500,          # oturum listesi tarama sıklığı
    "meter_interval_ms": 60,          # ses ölçer (peak meter) güncelleme sıklığı
    "panel_position": "bottom_right",
    "remembered_volumes": {},         # {"process_name.exe": 0.0-1.0}
    "remembered_mutes": {},           # {"process_name.exe": true/false}
    "hidden_apps": [],                # kullanıcının listeden gizlediği process adları
    "window_geometry": None,
    "first_run": True,
}


def get_data_dir() -> Path:
    """İşletim sistemine uygun kullanıcı veri klasörünü döndürür."""
    if sys.platform == "win32":
        base = os.environ.get("APPDATA") or str(Path.home() / "AppData" / "Roaming")
    elif sys.platform == "darwin":
        base = str(Path.home() / "Library" / "Application Support")
    else:
        base = os.environ.get("XDG_CONFIG_HOME") or str(Path.home() / ".config")
    path = Path(base) / APP_FOLDER
    path.mkdir(parents=True, exist_ok=True)
    return path


class ConfigManager:
    """Thread-safe, atomik yazımlı ve kendi kendini onaran ayar yöneticisi."""

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._dir = get_data_dir()
        self._path = self._dir / "settings.json"
        self._backup_path = self._dir / "settings.json.bak"
        self._data: Dict[str, Any] = {}
        self._load()

    # ------------------------------------------------------------------ #
    def _load(self) -> None:
        with self._lock:
            data = self._try_read(self._path)
            if data is None:
                data = self._try_read(self._backup_path)
            if data is None:
                data = copy.deepcopy(DEFAULT_CONFIG)
            # Eksik anahtarları varsayılanlarla tamamla (sürüm güncellemeleri için)
            # ÖNEMLİ: deepcopy kullanılır — aksi halde "hidden_apps",
            # "remembered_volumes" gibi iç içe liste/sözlük değerleri,
            # DEFAULT_CONFIG ile referans paylaşır ve örn. hide_app()
            # çağrısı yanlışlıkla DEFAULT_CONFIG'in kendisini mutasyona
            # uğratıp tüm gelecekteki sıfırlamaları/örnekleri bozardı.
            merged = copy.deepcopy(DEFAULT_CONFIG)
            merged.update(data)
            self._data = merged
            self.save()

    @staticmethod
    def _try_read(path: Path):
        try:
            if path.exists():
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
        except (json.JSONDecodeError, OSError):
            return None
        return None

    def save(self) -> None:
        """Atomik yazım: önce geçici dosyaya yaz, sonra yerine taşı."""
        with self._lock:
            try:
                if self._path.exists():
                    self._path.replace(self._backup_path)
            except OSError:
                pass
            try:
                fd, tmp_name = tempfile.mkstemp(
                    dir=str(self._dir), prefix="settings_", suffix=".tmp"
                )
                with os.fdopen(fd, "w", encoding="utf-8") as f:
                    json.dump(self._data, f, ensure_ascii=False, indent=2)
                os.replace(tmp_name, self._path)
            except OSError:
                pass

    # ------------------------------------------------------------------ #
    def get(self, key: str, default: Any = None) -> Any:
        with self._lock:
            return self._data.get(key, default)

    def set(self, key: str, value: Any, autosave: bool = True) -> None:
        with self._lock:
            # Değişebilir (mutable) tipler için savunma amaçlı deepcopy:
            # çağıran taraf elindeki listeyi/sözlüğü daha sonra değiştirirse,
            # bu iç durumu (self._data) sessizce bozmasın.
            if isinstance(value, (list, dict)):
                value = copy.deepcopy(value)
            self._data[key] = value
            if autosave:
                self.save()

    def get_remembered_volume(self, process_name: str) -> float | None:
        with self._lock:
            return self._data.get("remembered_volumes", {}).get(process_name)

    def set_remembered_volume(self, process_name: str, level: float) -> None:
        with self._lock:
            self._data.setdefault("remembered_volumes", {})[process_name] = round(level, 3)
            self.save()

    def get_remembered_mute(self, process_name: str) -> bool | None:
        with self._lock:
            return self._data.get("remembered_mutes", {}).get(process_name)

    def set_remembered_mute(self, process_name: str, muted: bool) -> None:
        with self._lock:
            self._data.setdefault("remembered_mutes", {})[process_name] = bool(muted)
            self.save()

    # -- Gizlenen Uygulamalar (Hidden Apps) -------------------------------
    def is_app_hidden(self, process_name: str) -> bool:
        with self._lock:
            return process_name.lower() in {p.lower() for p in self._data.get("hidden_apps", [])}

    def hide_app(self, process_name: str) -> None:
        with self._lock:
            hidden = self._data.setdefault("hidden_apps", [])
            if process_name.lower() not in {p.lower() for p in hidden}:
                hidden.append(process_name)
                self.save()

    def unhide_all_apps(self) -> None:
        with self._lock:
            self._data["hidden_apps"] = []
            self.save()

    def hidden_app_count(self) -> int:
        with self._lock:
            return len(self._data.get("hidden_apps", []))


config = ConfigManager()
