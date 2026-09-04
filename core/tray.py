"""
4R022 Ear Control - Sistem Tepsisi ve Hızlı Panel
====================================================
Sağ alttaki sistem tepsisi simgesi ve üzerine tıklandığında açılan,
EarTrumpet tarzı küçük hızlı kontrol panelini içerir.
"""

from __future__ import annotations

from typing import Dict, List

from PyQt6.QtCore import QPoint, Qt, pyqtSignal
from PyQt6.QtGui import QAction, QActionGroup, QGuiApplication, QIcon
from PyQt6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMenu,
    QPushButton,
    QScrollArea,
    QSystemTrayIcon,
    QVBoxLayout,
    QWidget,
)

from . import theme
from .audio_engine import AppAudioSession
from .config import config
from .i18n import Translator
from .widgets import AppCard, icon_for_path, system_sounds_icon

QUICK_PANEL_MAX_HEIGHT = 420
QUICK_PANEL_WIDTH = 320


class QuickPanel(QWidget):
    """Sistem tepsisi üzerine tıklandığında açılan küçük, kalıcı olmayan panel."""

    muteToggled = pyqtSignal(int, bool)
    volumeChanged = pyqtSignal(int, float)
    volumeCommitted = pyqtSignal(int, float)
    muteAllRequested = pyqtSignal()
    unmuteAllRequested = pyqtSignal()
    openDashboardRequested = pyqtSignal()

    def __init__(self, tr: Translator, parent=None) -> None:
        super().__init__(
            parent,
            Qt.WindowType.Popup
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.NoDropShadowWindowHint,
        )
        self.tr = tr
        self.cards: Dict[int, AppCard] = {}
        self._per_app_supported = True
        self.setObjectName("QuickPanel")
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
        self.setFixedWidth(QUICK_PANEL_WIDTH)
        self._build_ui()

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        header = QFrame()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(16, 12, 12, 10)

        self.title_label = QLabel(self.tr("quick_panel_title"))
        self.title_label.setObjectName("QuickPanelTitle")
        header_layout.addWidget(self.title_label)
        header_layout.addStretch(1)

        self.open_btn = QPushButton("⋯")
        self.open_btn.setObjectName("GhostButton")
        self.open_btn.setFixedSize(28, 26)
        self.open_btn.setToolTip(self.tr("tray_open_dashboard"))
        self.open_btn.clicked.connect(self.openDashboardRequested.emit)
        header_layout.addWidget(self.open_btn)

        outer.addWidget(header)

        divider = QFrame()
        divider.setFixedHeight(1)
        divider.setStyleSheet(f"background-color: {theme.BORDER};")
        outer.addWidget(divider)

        action_row = QFrame()
        action_layout = QHBoxLayout(action_row)
        action_layout.setContentsMargins(14, 0, 14, 8)
        action_layout.setSpacing(8)

        self.unmute_all_btn = QPushButton(self.tr("unmute_all"))
        self.unmute_all_btn.setObjectName("GhostButton")
        self.unmute_all_btn.clicked.connect(self.unmuteAllRequested.emit)
        action_layout.addWidget(self.unmute_all_btn)

        self.mute_all_btn = QPushButton(self.tr("mute_all"))
        self.mute_all_btn.setObjectName("PrimaryButton")
        self.mute_all_btn.clicked.connect(self.muteAllRequested.emit)
        action_layout.addWidget(self.mute_all_btn)

        outer.addWidget(action_row)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setMaximumHeight(QUICK_PANEL_MAX_HEIGHT)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.setStyleSheet("background: transparent; border: none;")

        self.container = QWidget()
        self.container.setStyleSheet("background: transparent;")
        self.cards_layout = QVBoxLayout(self.container)
        self.cards_layout.setContentsMargins(10, 0, 10, 10)
        self.cards_layout.setSpacing(8)
        self.cards_layout.addStretch(1)
        self.scroll.setWidget(self.container)

        outer.addWidget(self.scroll)

        self.empty_label = QLabel(self.tr("no_sessions"))
        self.empty_label.setWordWrap(True)
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setStyleSheet(f"color: {theme.GRAY_TEXT_DIM}; font-size: 12px; padding: 24px;")
        outer.addWidget(self.empty_label)
        self.empty_label.hide()

    def retranslate(self) -> None:
        self.title_label.setText(self.tr("quick_panel_title"))
        self.open_btn.setToolTip(self.tr("tray_open_dashboard"))
        self.unmute_all_btn.setText(self.tr("unmute_all"))
        self.mute_all_btn.setText(self.tr("mute_all"))
        self.empty_label.setText(
            self.tr("platform_note_unsupported_body") if not self._per_app_supported else self.tr("no_sessions")
        )

    def set_platform_capabilities(self, per_app_supported: bool) -> None:
        self._per_app_supported = per_app_supported
        self.unmute_all_btn.setVisible(per_app_supported)
        self.mute_all_btn.setVisible(per_app_supported)
        self.scroll.setVisible(per_app_supported and len(self.cards) > 0)
        self.empty_label.setVisible(not per_app_supported or len(self.cards) == 0)
        self.retranslate()

    def sync_sessions(self, sessions: List[AppAudioSession]) -> None:
        visible_sessions = [s for s in sessions if not config.is_app_hidden(s.process_name)]
        visible_pids = {s.pid for s in visible_sessions}
        for pid in list(self.cards.keys()):
            if pid not in visible_pids:
                card = self.cards.pop(pid)
                self.cards_layout.removeWidget(card)
                card.deleteLater()

        for sess in visible_sessions:
            card = self.cards.get(sess.pid)
            if card is None:
                card = AppCard(sess.pid, compact=True)
                card.muteToggled.connect(self.muteToggled.emit)
                card.volumeChanged.connect(self.volumeChanged.emit)
                card.volumeCommitted.connect(self.volumeCommitted.emit)
                self.cards[sess.pid] = card
                self.cards_layout.insertWidget(self.cards_layout.count() - 1, card)
                if sess.is_system:
                    card.set_icon(system_sounds_icon(28))
                else:
                    card.set_icon(icon_for_path(sess.exe_path))

            label = self.tr("system_sounds") if sess.is_system else sess.display_name
            card.set_name(label)
            card.set_volume(sess.volume)
            card.set_muted(sess.muted)

        if self._per_app_supported:
            self.empty_label.setVisible(len(visible_sessions) == 0)
            self.scroll.setVisible(len(visible_sessions) > 0)

        # İçerik yüksekliğine göre panel boyutunu ayarla
        content_height = self.container.sizeHint().height()
        self.scroll.setFixedHeight(min(QUICK_PANEL_MAX_HEIGHT, max(60, content_height)))
        self.adjustSize()

    def update_peaks(self, sessions: List[AppAudioSession]) -> None:
        for sess in sessions:
            card = self.cards.get(sess.pid)
            if card:
                card.set_peak(sess.peak)

    def show_near_tray(self, tray_icon_geometry) -> None:
        """Paneli, tepsi simgesinin hemen üzerinde (görev çubuğu konumuna göre) gösterir."""
        screen = QGuiApplication.primaryScreen()
        available = screen.availableGeometry() if screen else None

        self.adjustSize()
        panel_w = self.width()
        panel_h = self.height()

        if tray_icon_geometry is not None and not tray_icon_geometry.isNull():
            anchor_x = tray_icon_geometry.center().x()
            anchor_y = tray_icon_geometry.top()
        elif available is not None:
            anchor_x = available.right() - 40
            anchor_y = available.bottom()
        else:
            anchor_x, anchor_y = 100, 100

        x = anchor_x - panel_w // 2
        y = anchor_y - panel_h - 8

        if available is not None:
            x = max(available.left() + 8, min(x, available.right() - panel_w - 8))
            y = max(available.top() + 8, min(y, available.bottom() - panel_h - 8))

        self.move(QPoint(int(x), int(y)))
        self.show()
        self.raise_()
        self.activateWindow()


class TrayController(QSystemTrayIcon):
    """Sistem tepsisi simgesini ve sağ tık menüsünü yönetir."""

    openDashboardRequested = pyqtSignal()
    muteAllRequested = pyqtSignal()
    unmuteAllRequested = pyqtSignal()
    languageSelected = pyqtSignal(str)
    exitRequested = pyqtSignal()

    def __init__(self, tr: Translator, icon: QIcon, quick_panel: QuickPanel, parent=None) -> None:
        super().__init__(icon, parent)
        self.tr = tr
        self.quick_panel = quick_panel
        self.setToolTip(self.tr("tray_tooltip"))
        self._build_menu()
        self.activated.connect(self._on_activated)

    def _build_menu(self) -> None:
        self.menu = QMenu()

        self.open_action = QAction(self.tr("tray_open_dashboard"), self)
        self.open_action.triggered.connect(self.openDashboardRequested.emit)
        self.menu.addAction(self.open_action)

        self.menu.addSeparator()

        self.mute_all_action = QAction(self.tr("tray_mute_all"), self)
        self.mute_all_action.triggered.connect(self.muteAllRequested.emit)
        self.menu.addAction(self.mute_all_action)

        self.unmute_all_action = QAction(self.tr("tray_unmute_all"), self)
        self.unmute_all_action.triggered.connect(self.unmuteAllRequested.emit)
        self.menu.addAction(self.unmute_all_action)

        self.menu.addSeparator()

        self.lang_menu = QMenu(self.tr("tray_language"))
        lang_group = QActionGroup(self)
        lang_group.setExclusive(True)

        self.tr_action = QAction("Türkçe", self, checkable=True)
        self.tr_action.triggered.connect(lambda: self.languageSelected.emit("tr"))
        self.en_action = QAction("English", self, checkable=True)
        self.en_action.triggered.connect(lambda: self.languageSelected.emit("en"))
        for a in (self.tr_action, self.en_action):
            lang_group.addAction(a)
            self.lang_menu.addAction(a)
        self.menu.addMenu(self.lang_menu)

        self.menu.addSeparator()

        self.exit_action = QAction(self.tr("tray_exit"), self)
        self.exit_action.triggered.connect(self.exitRequested.emit)
        self.menu.addAction(self.exit_action)

        self.setContextMenu(self.menu)

    def set_active_language(self, language: str) -> None:
        self.tr_action.setChecked(language == "tr")
        self.en_action.setChecked(language == "en")

    def retranslate(self) -> None:
        self.setToolTip(self.tr("tray_tooltip"))
        self.open_action.setText(self.tr("tray_open_dashboard"))
        self.mute_all_action.setText(self.tr("tray_mute_all"))
        self.unmute_all_action.setText(self.tr("tray_unmute_all"))
        self.lang_menu.setTitle(self.tr("tray_language"))
        self.exit_action.setText(self.tr("tray_exit"))

    def _on_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        if reason in (
            QSystemTrayIcon.ActivationReason.Trigger,
            QSystemTrayIcon.ActivationReason.DoubleClick,
        ):
            if self.quick_panel.isVisible():
                self.quick_panel.hide()
            else:
                self.quick_panel.show_near_tray(self.geometry())

    def notify(self, title: str, body: str) -> None:
        self.showMessage(title, body, QSystemTrayIcon.MessageIcon.Information, 2500)
