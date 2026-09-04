"""
4R022 Ear Control
===================
Uygulama bazlı ses yönetimi — EarTrumpet tarzı, Windows Ses Karıştırıcısı
ile aynı sistem API'lerini kullanan profesyonel bir masaüstü ses paneli.

Geliştirici: Kaan Kross — 4R022
"""

from __future__ import annotations

import os
import sys

from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QIcon
from PyQt6.QtNetwork import QLocalServer, QLocalSocket
from PyQt6.QtWidgets import QApplication, QMessageBox, QSystemTrayIcon

BASE_DIR = os.path.dirname(os.path.abspath(__file__))          # .../Main
PROJECT_ROOT = os.path.dirname(BASE_DIR)                        # proje kökü (core/, assets/ burada)

# main.py, Main/ alt klasöründe yaşadığından, "core" paketinin bulunabilmesi
# için proje kökünü sys.path'e ekliyoruz. Bu, hem `python Main/main.py`
# ile doğrudan çalıştırmada hem de PyInstaller ile derlenmiş halinde
# (spec dosyası zaten pathex ile kökü eklese de) çalışmayı garanti eder.
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


def resource_path(*parts: str) -> str:
    """PyInstaller ile paketlendiğinde de doğru yolu bulur (sys._MEIPASS)."""
    base = getattr(sys, "_MEIPASS", PROJECT_ROOT)
    return os.path.join(base, *parts)


ASSETS_DIR = resource_path("assets")
APP_ICON_PATH = os.path.join(ASSETS_DIR, "app.ico")     # tam logo: pencere/exe ikonu
TRAY_ICON_PATH = os.path.join(ASSETS_DIR, "tray_icon.ico")  # kırpılmış amblem: küçük tepsi ikonu

SINGLE_INSTANCE_KEY = "4R022-EarControl-SingleInstance"


# --------------------------------------------------------------------------
# Windows ile Otomatik Başlatma (Registry Run Key) — stdlib winreg kullanır
# --------------------------------------------------------------------------
def set_autostart(enabled: bool) -> None:
    if sys.platform != "win32":
        return
    try:
        import winreg

        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE) as key:
            if enabled:
                exe = sys.executable
                if getattr(sys, "frozen", False):
                    cmd = f'"{exe}"'
                else:
                    script = os.path.abspath(__file__)
                    cmd = f'"{exe}" "{script}"'
                winreg.SetValueEx(key, "4R022EarControl", 0, winreg.REG_SZ, cmd)
            else:
                try:
                    winreg.DeleteValue(key, "4R022EarControl")
                except FileNotFoundError:
                    pass
    except OSError:
        pass


# --------------------------------------------------------------------------
# Uygulama
# --------------------------------------------------------------------------
class EarControlApp:
    def __init__(self) -> None:
        from core.audio_engine import AudioEngine, is_eartrumpet_running
        from core.config import config
        from core.dashboard import DashboardWindow
        from core.i18n import Translator
        from core.tray import QuickPanel, TrayController
        from core import theme

        self.config = config
        self.tr = Translator(config.get("language", "tr"))

        self.app = QApplication.instance() or QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)
        self.app.setStyleSheet(theme.MAIN_STYLESHEET)
        self.app.setApplicationName("4R022 Ear Control")

        self.app_icon = QIcon(APP_ICON_PATH) if os.path.exists(APP_ICON_PATH) else QIcon()
        self.tray_icon_img = QIcon(TRAY_ICON_PATH) if os.path.exists(TRAY_ICON_PATH) else self.app_icon
        self.app.setWindowIcon(self.app_icon)

        self.engine = AudioEngine()
        self.engine.set_error_handler(self._on_engine_error)

        self.dashboard = DashboardWindow(self.tr)
        self.dashboard.setWindowIcon(self.app_icon)
        self.dashboard.set_platform_capabilities(self.engine.capabilities.per_app_volume)
        self.dashboard.set_platform_name(self.engine.platform_name)

        self.quick_panel = QuickPanel(self.tr)
        self.quick_panel.set_platform_capabilities(self.engine.capabilities.per_app_volume)

        self.tray = TrayController(self.tr, self.tray_icon_img, self.quick_panel)

        self._wire_signals()
        self._apply_autostart_from_config()

        if not self.engine.available:
            self._show_platform_warning()

        if is_eartrumpet_running() and config.get("show_tray_notifications", True):
            QTimer.singleShot(
                1500,
                lambda: self.tray.notify("4R022 Ear Control", self.tr("eartrumpet_detected")),
            )

        # Zamanlayıcılar: oturum taraması ve ses ölçer güncellemesi.
        # Performans notu: pencere (dashboard/hızlı panel) görünür değilken
        # hem oturum taraması hem de ses ölçer güncellemesi gereksiz CPU
        # kullanır (özellikle Windows'ta her tık COM çağrısına dönüşür).
        # Bu yüzden görünürlüğe göre iki farklı hızda çalışır:
        # - Görünürken: config'teki hızlı aralık (varsayılan 500ms / 60ms)
        # - Gizliyken: oturum taraması çok daha seyrek (arka planda hâlâ
        #   hafif bir şekilde güncel kalması için), ses ölçer tamamen durur
        #   (gizliyken zaten kimse peak animasyonunu görmüyor).
        self._fast_poll_ms = int(config.get("poll_interval_ms", 500))
        self._slow_poll_ms = max(self._fast_poll_ms * 4, 2000)

        self.session_timer = QTimer()
        self.session_timer.timeout.connect(self._refresh_sessions)
        self.session_timer.start(self._fast_poll_ms)

        self.meter_timer = QTimer()
        self.meter_timer.timeout.connect(self._update_meters)
        self.meter_timer.start(int(config.get("meter_interval_ms", 60)))

        self._refresh_sessions()

        self.tray.set_active_language(self.tr.language)
        self.tray.show()

        if config.get("first_run", True):
            config.set("first_run", False)

    # ------------------------------------------------------------------ #
    def _wire_signals(self) -> None:
        # Tray -> uygulama
        self.tray.openDashboardRequested.connect(self._show_dashboard)
        self.tray.muteAllRequested.connect(self._mute_all)
        self.tray.unmuteAllRequested.connect(self._unmute_all)
        self.tray.languageSelected.connect(self._change_language)
        self.tray.exitRequested.connect(self._quit)

        # Quick panel -> motor
        self.quick_panel.muteToggled.connect(self._on_mute_toggled)
        self.quick_panel.volumeChanged.connect(self._on_volume_changed)
        self.quick_panel.volumeCommitted.connect(self._on_volume_committed)
        self.quick_panel.muteAllRequested.connect(self._mute_all)
        self.quick_panel.unmuteAllRequested.connect(self._unmute_all)
        self.quick_panel.openDashboardRequested.connect(self._show_dashboard)

        # Dashboard -> motor
        self.dashboard.muteToggled.connect(self._on_mute_toggled)
        self.dashboard.volumeChanged.connect(self._on_volume_changed)
        self.dashboard.volumeCommitted.connect(self._on_volume_committed)
        self.dashboard.muteAllRequested.connect(self._mute_all)
        self.dashboard.unmuteAllRequested.connect(self._unmute_all)
        self.dashboard.languageChanged.connect(self._change_language)
        self.dashboard.resetRequested.connect(self._reset_settings)
        self.dashboard.showHiddenRequested.connect(self._refresh_sessions)

    # ------------------------------------------------------------------ #
    def _is_ui_visible(self) -> bool:
        return self.dashboard.isVisible() or self.quick_panel.isVisible()

    def _refresh_sessions(self) -> None:
        # Bir sonraki tık için doğru hızı seç (görünürlük her an değişebilir)
        self.session_timer.setInterval(
            self._fast_poll_ms if self._is_ui_visible() else self._slow_poll_ms
        )
        sessions = self.engine.refresh_sessions()
        self.dashboard.sync_sessions(sessions)
        self.quick_panel.sync_sessions(sessions)

    def _update_meters(self) -> None:
        if not self._is_ui_visible():
            # Hiçbir pencere görünmüyorsa peak ölçümü kimseye gösterilmiyor
            # demektir; gereksiz sistem çağrısı (özellikle Windows COM)
            # yapmaktan kaçınarak arka plan CPU kullanımını azaltır.
            return
        self.engine.update_peaks()
        sessions = self.engine.get_sessions()
        self.dashboard.update_peaks(sessions)
        self.quick_panel.update_peaks(sessions)

    def _on_mute_toggled(self, pid: int, muted: bool) -> None:
        self.engine.set_mute(pid, muted)
        sess = next((s for s in self.engine.get_sessions() if s.pid == pid), None)
        if sess and not sess.is_system:
            self.config.set_remembered_mute(sess.process_name, muted)

    def _on_volume_changed(self, pid: int, level: float) -> None:
        self.engine.set_volume(pid, level)

    def _on_volume_committed(self, pid: int, level: float) -> None:
        self.engine.set_volume(pid, level)
        sess = next((s for s in self.engine.get_sessions() if s.pid == pid), None)
        if sess and not sess.is_system:
            self.config.set_remembered_volume(sess.process_name, level)

    def _mute_all(self) -> None:
        self.engine.mute_all()
        self._refresh_sessions()
        if self.config.get("show_tray_notifications", True):
            self.tray.notify(self.tr("notif_muted_all_title"), self.tr("notif_muted_all_body"))

    def _unmute_all(self) -> None:
        self.engine.unmute_all()
        self._refresh_sessions()
        if self.config.get("show_tray_notifications", True):
            self.tray.notify(self.tr("notif_unmuted_all_title"), self.tr("notif_unmuted_all_body"))

    def _show_dashboard(self) -> None:
        self.quick_panel.hide()
        self.dashboard.show()
        self.dashboard.raise_()
        self.dashboard.activateWindow()

    def _change_language(self, language: str) -> None:
        self.tr.set_language(language)
        self.config.set("language", language)
        self.dashboard.retranslate()
        self.quick_panel.retranslate()
        self.tray.retranslate()
        self.tray.set_active_language(language)

    def _reset_settings(self) -> None:
        import copy

        from core.config import DEFAULT_CONFIG

        for key, value in DEFAULT_CONFIG.items():
            # deepcopy şart: aksi halde "hidden_apps" gibi liste/sözlük
            # değerleri DEFAULT_CONFIG ile referans paylaşır ve sonraki bir
            # hide_app()/set_remembered_*() çağrısı yanlışlıkla
            # DEFAULT_CONFIG'in kendisini kalıcı olarak bozar.
            self.config.set(key, copy.deepcopy(value), autosave=False)
        self.config.save()
        set_autostart(False)
        QMessageBox.information(self.dashboard, self.tr("app_title"), self.tr("settings_saved"))

    def _apply_autostart_from_config(self) -> None:
        set_autostart(bool(self.config.get("start_with_windows", False)))
        # Ayarlar sekmesinden değiştirildiğinde de senkron tut
        self.dashboard.settings_tab.startup_check.toggled.connect(set_autostart)

    def _on_engine_error(self, message: str) -> None:
        # Sessizce günlüğe düşür; kullanıcıyı her hata için rahatsız etme
        sys.stderr.write(f"[4R022 Ear Control] {message}\n")

    def _show_platform_warning(self) -> None:
        hints = {
            "windows": "pycaw / comtypes kurulu değil. Lütfen: pip install pycaw comtypes",
            "linux": "'pactl' komutu bulunamadı. PulseAudio veya PipeWire-Pulse kurulu olmalı.",
            "unsupported": "Bu işletim sistemi desteklenmiyor. 4R022 Ear Control yalnızca Windows ve Linux'ta çalışır.",
        }
        hint_en = {
            "windows": "pycaw / comtypes not installed. Please run: pip install pycaw comtypes",
            "linux": "'pactl' command not found. PulseAudio or PipeWire-Pulse must be installed.",
            "unsupported": "This operating system is not supported. 4R022 Ear Control only runs on Windows and Linux.",
        }
        name = self.engine.platform_name
        QMessageBox.warning(
            None,
            "4R022 Ear Control",
            f"Ses motoru başlatılamadı ({name}).\n{hints.get(name, '')}\n\n"
            f"Audio engine could not start ({name}).\n{hint_en.get(name, '')}",
        )

    def _quit(self) -> None:
        self.tray.hide()
        self.app.quit()

    def run(self) -> int:
        return self.app.exec()


def _already_running() -> bool:
    """Tek örnek (single instance) kontrolü: QLocalSocket ile."""
    socket = QLocalSocket()
    socket.connectToServer(SINGLE_INSTANCE_KEY)
    is_running = socket.waitForConnected(200)
    socket.close()
    return is_running


def _start_instance_server() -> QLocalServer:
    server = QLocalServer()
    QLocalServer.removeServer(SINGLE_INSTANCE_KEY)
    server.listen(SINGLE_INSTANCE_KEY)
    return server


def main() -> int:
    # QApplication'dan önce tek örnek kontrolü yapılamaz (QLocalSocket QCoreApplication ister)
    app_probe = QApplication.instance() or QApplication(sys.argv)

    if _already_running():
        QMessageBox.information(
            None,
            "4R022 Ear Control",
            "4R022 Ear Control zaten çalışıyor (sistem tepsisine bakın).\n"
            "4R022 Ear Control is already running (check the system tray).",
        )
        return 0

    _instance_server = app_probe.property("_instance_server")
    server = _start_instance_server()
    app_probe.setProperty("_instance_server", server)

    if not QSystemTrayIcon.isSystemTrayAvailable():
        QMessageBox.critical(
            None,
            "4R022 Ear Control",
            "Sistem tepsisi bu ortamda kullanılamıyor.\n"
            "System tray is not available in this environment.",
        )
        return 1

    controller = EarControlApp()
    return controller.run()


if __name__ == "__main__":
    sys.exit(main())
