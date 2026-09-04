"""
4R022 Ear Control - Kontrol Paneli (Dashboard)
=================================================
Ana pencere: Uygulamalar (mixer), Ayarlar, Hakkında sekmeleri.
"""

from __future__ import annotations

from typing import Dict

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QCloseEvent, QIcon, QPixmap
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSpacerItem,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from . import theme
from .assets import asset_path
from .audio_engine import AppAudioSession
from .config import APP_NAME, VERSION, config
from .i18n import Translator
from .widgets import (
    AnimatedTabBar,
    AppCard,
    fade_in_widget,
    icon_for_path,
    system_sounds_icon,
)


class SettingsRow(QFrame):
    """Ayarlar sekmesindeki tek bir satır: başlık + açıklama + kontrol."""

    def __init__(self, title: str, hint: str, control: QWidget, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("SettingsRow")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)

        text_col = QVBoxLayout()
        text_col.setSpacing(2)
        title_lbl = QLabel(title)
        title_lbl.setObjectName("SettingsRowTitle")
        hint_lbl = QLabel(hint)
        hint_lbl.setObjectName("SettingsRowHint")
        hint_lbl.setWordWrap(True)
        text_col.addWidget(title_lbl)
        text_col.addWidget(hint_lbl)

        layout.addLayout(text_col, 1)
        layout.addWidget(control, 0, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        self.title_label = title_lbl
        self.hint_label = hint_lbl


class MixerTab(QWidget):
    """Uygulama ses kartlarının listelendiği ana sekme."""

    muteToggled = pyqtSignal(int, bool)
    volumeChanged = pyqtSignal(int, float)
    volumeCommitted = pyqtSignal(int, float)
    appHidden = pyqtSignal()  # bir uygulama gizlendiğinde (Ayarlar sekmesindeki sayaç için)

    def __init__(self, tr: Translator, parent=None) -> None:
        super().__init__(parent)
        self.tr = tr
        self.cards: Dict[int, AppCard] = {}
        self._pid_to_process: Dict[int, str] = {}
        self._per_app_supported = True
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)

        # ---- Platform sınırlama notu (yalnızca gerektiğinde görünür, ör. macOS) ----
        self.platform_note = QLabel()
        self.platform_note.setWordWrap(True)
        self.platform_note.setStyleSheet(
            f"color: {theme.WARNING}; background-color: {theme.CARD_BG}; "
            f"border: 1px solid {theme.BORDER}; border-radius: 10px; padding: 12px; font-size: 12px;"
        )
        layout.addWidget(self.platform_note)
        self.platform_note.hide()

        top_bar = QHBoxLayout()
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText(self.tr("search_placeholder"))
        self.search_box.textChanged.connect(self._filter_cards)
        top_bar.addWidget(self.search_box, 1)

        self.unmute_all_btn = QPushButton(self.tr("unmute_all"))
        self.unmute_all_btn.setObjectName("GhostButton")
        top_bar.addWidget(self.unmute_all_btn)

        self.mute_all_btn = QPushButton(self.tr("mute_all"))
        self.mute_all_btn.setObjectName("PrimaryButton")
        top_bar.addWidget(self.mute_all_btn)

        layout.addLayout(top_bar)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.container = QWidget()
        self.cards_layout = QVBoxLayout(self.container)
        self.cards_layout.setContentsMargins(0, 0, 4, 0)
        self.cards_layout.setSpacing(10)
        self.cards_layout.addStretch(1)
        self.scroll.setWidget(self.container)

        layout.addWidget(self.scroll, 1)

        self.empty_label = QLabel()
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setWordWrap(True)
        self.empty_label.setStyleSheet(f"color: {theme.GRAY_TEXT_DIM}; font-size: 13px; padding: 40px;")
        self._update_empty_text()
        layout.addWidget(self.empty_label)
        self.empty_label.hide()

    def _update_empty_text(self) -> None:
        self.empty_label.setText(f"{self.tr('no_sessions')}\n{self.tr('no_sessions_hint')}")

    def retranslate(self) -> None:
        self.search_box.setPlaceholderText(self.tr("search_placeholder"))
        self.unmute_all_btn.setText(self.tr("unmute_all"))
        self.mute_all_btn.setText(self.tr("mute_all"))
        self._update_empty_text()
        if not self._per_app_supported:
            self.platform_note.setText(
                f"{self.tr('platform_note_unsupported_title')}\n\n{self.tr('platform_note_unsupported_body')}"
            )
        for card in self.cards.values():
            card.set_hide_label(self.tr("hide_app"))

    def set_platform_capabilities(self, per_app_supported: bool) -> None:
        """Uygulama başına ses kontrolü desteklenmiyorsa (ör. macOS), listeyi
        gizleyip yerine açıklayıcı bir platform notu gösterir."""
        self._per_app_supported = per_app_supported
        self.search_box.setVisible(per_app_supported)
        self.unmute_all_btn.setVisible(per_app_supported)
        self.mute_all_btn.setVisible(per_app_supported)
        self.scroll.setVisible(per_app_supported and len(self.cards) > 0)
        self.empty_label.setVisible(per_app_supported and len(self.cards) == 0)
        self.platform_note.setVisible(not per_app_supported)
        if not per_app_supported:
            self.platform_note.setText(
                f"{self.tr('platform_note_unsupported_title')}\n\n{self.tr('platform_note_unsupported_body')}"
            )

    def _filter_cards(self, text: str) -> None:
        text = text.strip().lower()
        for card in self.cards.values():
            visible = text in card.name_label.fullText().lower()
            card.setVisible(visible)

    def sync_sessions(self, sessions: list[AppAudioSession]) -> None:
        """Oturum listesini kartlara yansıtır: yeni ekler, kapananı veya
        kullanıcının gizlediğini kaldırır."""
        visible_sessions = [s for s in sessions if not config.is_app_hidden(s.process_name)]
        visible_pids = {s.pid for s in visible_sessions}

        # Kapanan veya gizlenen kartları kaldır
        for pid in list(self.cards.keys()):
            if pid not in visible_pids:
                card = self.cards.pop(pid)
                self.cards_layout.removeWidget(card)
                card.deleteLater()
                self._pid_to_process.pop(pid, None)

        for sess in visible_sessions:
            self._pid_to_process[sess.pid] = sess.process_name
            card = self.cards.get(sess.pid)
            if card is None:
                card = AppCard(sess.pid)
                card.set_hide_label(self.tr("hide_app"))
                card.muteToggled.connect(self.muteToggled.emit)
                card.volumeChanged.connect(self.volumeChanged.emit)
                card.volumeCommitted.connect(self.volumeCommitted.emit)
                card.hideRequested.connect(self._on_hide_requested)
                self.cards[sess.pid] = card
                self.cards_layout.insertWidget(self.cards_layout.count() - 1, card)
                if sess.is_system:
                    card.set_icon(system_sounds_icon())
                else:
                    card.set_icon(icon_for_path(sess.exe_path))

            label = self.tr("system_sounds") if sess.is_system else sess.display_name
            card.set_name(label)
            card.set_volume(sess.volume)
            card.set_muted(sess.muted)
            status = self.tr("muted") if sess.muted else ""
            card.set_status(status)

        if self._per_app_supported:
            self.empty_label.setVisible(len(visible_sessions) == 0)
            self.scroll.setVisible(len(visible_sessions) > 0)

    def _on_hide_requested(self, pid: int) -> None:
        """Kullanıcı bir kartın sağ tık menüsünden 'Listeden Gizle'yi
        seçtiğinde çağrılır: uygulamayı kalıcı olarak (process adına göre)
        gizli listesine ekler ve kartı anında (bir sonraki taramayı
        beklemeden) arayüzden kaldırır."""
        process_name = self._pid_to_process.get(pid)
        if process_name:
            config.hide_app(process_name)
        card = self.cards.pop(pid, None)
        if card:
            self.cards_layout.removeWidget(card)
            card.deleteLater()
        self._pid_to_process.pop(pid, None)
        self.empty_label.setVisible(self._per_app_supported and len(self.cards) == 0)
        self.scroll.setVisible(self._per_app_supported and len(self.cards) > 0)
        self.appHidden.emit()

    def update_peaks(self, sessions: list[AppAudioSession]) -> None:
        for sess in sessions:
            card = self.cards.get(sess.pid)
            if card:
                card.set_peak(sess.peak)


class SettingsTab(QWidget):
    languageChanged = pyqtSignal(str)
    resetRequested = pyqtSignal()
    showHiddenRequested = pyqtSignal()

    def __init__(self, tr: Translator, parent=None) -> None:
        super().__init__(parent)
        self.tr = tr
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        self.lang_combo = QComboBox()
        self.lang_combo.addItem("Türkçe", "tr")
        self.lang_combo.addItem("English", "en")
        self.lang_combo.setCurrentIndex(0 if config.get("language", "tr") == "tr" else 1)
        self.lang_combo.currentIndexChanged.connect(
            lambda i: self.languageChanged.emit(self.lang_combo.itemData(i))
        )
        self.row_language = SettingsRow(self.tr("settings_language"), self.tr("settings_language_hint"), self.lang_combo)
        layout.addWidget(self.row_language)

        self.startup_check = QCheckBox()
        self.startup_check.setChecked(bool(config.get("start_with_windows", False)))
        self.row_startup = SettingsRow(self.tr("settings_startup"), self.tr("settings_startup_hint"), self.startup_check)
        layout.addWidget(self.row_startup)

        self.minimized_check = QCheckBox()
        self.minimized_check.setChecked(bool(config.get("start_minimized", True)))
        self.row_minimized = SettingsRow(
            self.tr("settings_start_minimized"), self.tr("settings_start_minimized_hint"), self.minimized_check
        )
        layout.addWidget(self.row_minimized)

        self.notif_check = QCheckBox()
        self.notif_check.setChecked(bool(config.get("show_tray_notifications", True)))
        self.row_notif = SettingsRow(
            self.tr("settings_notifications"), self.tr("settings_notifications_hint"), self.notif_check
        )
        layout.addWidget(self.row_notif)

        self.reset_btn = QPushButton(self.tr("settings_reset"))
        self.reset_btn.setObjectName("GhostButton")
        self.reset_btn.clicked.connect(self._on_reset_clicked)
        self.row_reset = SettingsRow(self.tr("settings_reset"), self.tr("settings_reset_hint"), self.reset_btn)
        layout.addWidget(self.row_reset)

        self.show_hidden_btn = QPushButton(self.tr("show_hidden"))
        self.show_hidden_btn.setObjectName("GhostButton")
        self.show_hidden_btn.clicked.connect(self._on_show_hidden_clicked)
        self.row_hidden = SettingsRow(
            self.tr("show_hidden"), self._hidden_hint_text(), self.show_hidden_btn
        )
        layout.addWidget(self.row_hidden)

        layout.addStretch(1)

        # Ayarları değiştikçe kaydet
        self.startup_check.toggled.connect(lambda v: config.set("start_with_windows", v))
        self.minimized_check.toggled.connect(lambda v: config.set("start_minimized", v))
        self.notif_check.toggled.connect(lambda v: config.set("show_tray_notifications", v))

    def _on_reset_clicked(self) -> None:
        box = QMessageBox(self)
        box.setWindowTitle(self.tr("settings_reset_confirm_title"))
        box.setText(self.tr("settings_reset_confirm_body"))
        box.setIcon(QMessageBox.Icon.Warning)
        box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if box.exec() == QMessageBox.StandardButton.Yes:
            self.resetRequested.emit()

    def _hidden_hint_text(self) -> str:
        n = config.hidden_app_count()
        return self.tr("hidden_apps_count").replace("{n}", str(n))

    def _on_show_hidden_clicked(self) -> None:
        config.unhide_all_apps()
        self.row_hidden.hint_label.setText(self._hidden_hint_text())
        self.showHiddenRequested.emit()

    def refresh_hidden_count(self) -> None:
        """Gizli uygulama sayısı Uygulamalar sekmesinde değiştiğinde
        (bir kart gizlendiğinde) bu sekmenin ipucu metnini günceller."""
        self.row_hidden.hint_label.setText(self._hidden_hint_text())

    def retranslate(self) -> None:
        self.row_language.title_label.setText(self.tr("settings_language"))
        self.row_language.hint_label.setText(self.tr("settings_language_hint"))
        self.row_startup.title_label.setText(self.tr("settings_startup"))
        self.row_startup.hint_label.setText(self.tr("settings_startup_hint"))
        self.row_minimized.title_label.setText(self.tr("settings_start_minimized"))
        self.row_minimized.hint_label.setText(self.tr("settings_start_minimized_hint"))
        self.row_notif.title_label.setText(self.tr("settings_notifications"))
        self.row_notif.hint_label.setText(self.tr("settings_notifications_hint"))
        self.row_reset.title_label.setText(self.tr("settings_reset"))
        self.row_reset.hint_label.setText(self.tr("settings_reset_hint"))
        self.reset_btn.setText(self.tr("settings_reset"))
        self.row_hidden.title_label.setText(self.tr("show_hidden"))
        self.row_hidden.hint_label.setText(self._hidden_hint_text())
        self.show_hidden_btn.setText(self.tr("show_hidden"))
        self.sync_language_selector()

    def sync_language_selector(self) -> None:
        """
        Dil, Ayarlar sekmesi dışından değiştirildiğinde (ör. sistem tepsisi
        sağ tık menüsünden) bu açılır kutunun seçili öğesini günceller.
        `blockSignals` ile, bu senkronizasyonun kendisinin gereksiz bir
        `languageChanged` sinyali tetiklemesi engellenir — aksi halde dil
        değişikliği sonsuz döngüye girmese de gereksiz yere tekrar işlenirdi.
        """
        target_index = 0 if self.tr.language == "tr" else 1
        if self.lang_combo.currentIndex() == target_index:
            return
        self.lang_combo.blockSignals(True)
        self.lang_combo.setCurrentIndex(target_index)
        self.lang_combo.blockSignals(False)


class AboutTab(QWidget):
    """
    Hakkında sekmesi: marka rozeti + başlık içeren bir üst kart, bir
    açıklama kartı ve geliştirici/sürüm/platform/lisans bilgilerini
    2x2 bir ızgarada gösteren küçük bilgi kartlarından oluşur.
    """

    def __init__(self, tr: Translator, parent=None) -> None:
        super().__init__(parent)
        self.tr = tr
        self._platform_name: str | None = None
        self.info_labels: Dict[str, tuple] = {}
        self._build_ui()

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("background: transparent; border: none;")
        outer.addWidget(scroll)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(20, 22, 20, 20)
        layout.setSpacing(14)
        scroll.setWidget(container)

        # ---- Üst kart: uygulama logosu, sürüm etiketi, tagline ----
        # Not: Önceden burada "4R" yazılı, elle çizilmiş bir rozet + ayrı bir
        # metin başlığı vardı. Artık bunun yerine assets/logo_full.png
        # içindeki gerçek uygulama logosu tam haliyle gösteriliyor.
        header_card = QFrame()
        header_card.setObjectName("AppCard")
        header_layout = QVBoxLayout(header_card)
        header_layout.setContentsMargins(20, 24, 20, 22)
        header_layout.setSpacing(6)
        header_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        self.logo_label = QLabel()
        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_pixmap = QPixmap(asset_path("logo_full.png"))
        if not logo_pixmap.isNull():
            from PyQt6.QtCore import Qt as _Qt

            scaled = logo_pixmap.scaledToWidth(
                168, _Qt.TransformationMode.SmoothTransformation
            )
            self.logo_label.setPixmap(scaled)
        else:
            # Logo dosyası bulunamazsa (ör. bozuk paket) sessizce boş kalır
            # yerine, uygulama adını yedek (fallback) olarak gösterir.
            self.logo_label.setText("4R022 Ear Control")
            self.logo_label.setStyleSheet(
                f"color: {theme.WHITE_TEXT}; font-size: 18px; font-weight: 800;"
            )
        header_layout.addWidget(self.logo_label, 0, Qt.AlignmentFlag.AlignHCenter)

        self.version_chip = QLabel(f"v{VERSION}")
        self.version_chip.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.version_chip.setStyleSheet(
            f"color: {theme.WHITE_TEXT}; background-color: {theme.SURFACE}; "
            f"border: 1px solid {theme.BORDER}; border-radius: 9px; "
            f"padding: 2px 12px; font-size: 11px; font-weight: 700;"
        )
        header_layout.addWidget(self.version_chip, 0, Qt.AlignmentFlag.AlignHCenter)

        self.tagline_label = QLabel(self.tr("app_subtitle"))
        self.tagline_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.tagline_label.setStyleSheet(
            f"color: {theme.GRAY_TEXT}; font-size: 12px; margin-top: 6px;"
        )
        header_layout.addWidget(self.tagline_label)

        layout.addWidget(header_card)

        # ---- Açıklama kartı ----
        desc_card = QFrame()
        desc_card.setObjectName("AppCard")
        desc_layout = QVBoxLayout(desc_card)
        desc_layout.setContentsMargins(18, 16, 18, 16)
        self.desc_label = QLabel(self.tr("about_desc"))
        self.desc_label.setObjectName("AboutText")
        self.desc_label.setWordWrap(True)
        desc_layout.addWidget(self.desc_label)
        layout.addWidget(desc_card)

        # ---- Bilgi ızgarası: Geliştirici / Sürüm / Platform / Lisans ----
        grid_frame = QFrame()
        grid_layout = QGridLayout(grid_frame)
        grid_layout.setSpacing(10)
        grid_layout.setContentsMargins(0, 0, 0, 0)

        info_items = [
            ("about_developer", "👤", "Kaan Kross — 4R022"),
            ("about_version", "🏷️", f"v{VERSION}"),
            ("platform_label", "🖥️", "—"),
            ("about_license", "📜", None),
        ]
        for i, (key, emoji, value) in enumerate(info_items):
            chip = QFrame()
            chip.setObjectName("AppCard")
            chip_layout = QVBoxLayout(chip)
            chip_layout.setContentsMargins(14, 12, 14, 12)
            chip_layout.setSpacing(4)

            top_row = QHBoxLayout()
            top_row.setSpacing(6)
            icon_lbl = QLabel(emoji)
            icon_lbl.setStyleSheet("font-size: 14px;")
            top_row.addWidget(icon_lbl)
            k_label = QLabel(self.tr(key))
            k_label.setStyleSheet(
                f"color: {theme.GRAY_TEXT_DIM}; font-size: 11px; font-weight: 600;"
            )
            top_row.addWidget(k_label)
            top_row.addStretch(1)
            chip_layout.addLayout(top_row)

            v_text = value if value else self.tr("about_license_text")
            v_label = QLabel(v_text)
            v_label.setWordWrap(True)
            v_label.setStyleSheet(
                f"color: {theme.WHITE_TEXT}; font-size: 12px; font-weight: 700;"
            )
            chip_layout.addWidget(v_label)

            grid_layout.addWidget(chip, i // 2, i % 2)
            self.info_labels[key] = (k_label, v_label)

        grid_layout.setColumnStretch(0, 1)
        grid_layout.setColumnStretch(1, 1)
        layout.addWidget(grid_frame)

        layout.addStretch(1)

        footer = QLabel("4R022 © 2026 — Kaan Kross")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer.setStyleSheet(f"color: {theme.GRAY_TEXT_DIM}; font-size: 10px; margin-top: 4px;")
        layout.addWidget(footer)

    def set_platform(self, platform_name: str) -> None:
        key_map = {"windows": "platform_windows", "linux": "platform_linux", "unsupported": "platform_unsupported"}
        _, v_label = self.info_labels.get("platform_label", (None, None))
        if v_label:
            v_label.setText(self.tr(key_map.get(platform_name, platform_name)))
        self._platform_name = platform_name

    def retranslate(self) -> None:
        self.tagline_label.setText(self.tr("app_subtitle"))
        self.desc_label.setText(self.tr("about_desc"))
        for key, (k_label, v_label) in self.info_labels.items():
            k_label.setText(self.tr(key))
            if key == "about_license":
                v_label.setText(self.tr("about_license_text"))
            elif key == "platform_label" and self._platform_name:
                self.set_platform(self._platform_name)


class DashboardWindow(QWidget):
    """Ana kontrol paneli penceresi."""

    languageChanged = pyqtSignal(str)
    muteToggled = pyqtSignal(int, bool)
    volumeChanged = pyqtSignal(int, float)
    volumeCommitted = pyqtSignal(int, float)
    muteAllRequested = pyqtSignal()
    unmuteAllRequested = pyqtSignal()
    resetRequested = pyqtSignal()
    showHiddenRequested = pyqtSignal()
    reallyClosing = pyqtSignal()  # Uygulamadan tamamen çıkış (tepsiye küçültme değil)

    def __init__(self, tr: Translator, parent=None) -> None:
        super().__init__(parent)
        self.tr = tr
        self.setObjectName("RootWindow")
        self.setWindowTitle(APP_NAME)
        self.resize(520, 700)
        self.setMinimumSize(440, 520)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = QFrame()
        header.setStyleSheet(f"background-color: {theme.BLACK_SOFT}; border-bottom: 1px solid {theme.BORDER};")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 16, 20, 16)

        title_col = QVBoxLayout()
        title_col.setSpacing(2)
        title_row = QHBoxLayout()
        title_row.setSpacing(8)
        self.title_label = QLabel(self.tr("app_title"))
        self.title_label.setObjectName("BrandTitle")
        badge = QLabel("4R022")
        badge.setObjectName("BrandBadge")
        title_row.addWidget(self.title_label)
        title_row.addWidget(badge)
        title_row.addStretch(1)
        self.subtitle_label = QLabel(self.tr("app_subtitle"))
        self.subtitle_label.setObjectName("BrandSubtitle")
        title_col.addLayout(title_row)
        title_col.addWidget(self.subtitle_label)

        header_layout.addLayout(title_col)
        layout.addWidget(header)

        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setTabBar(AnimatedTabBar())
        self._tab_fade_anim = None  # Referansı canlı tutmak için (bkz. fade_in_widget)

        self.mixer_tab = MixerTab(self.tr)
        self.mixer_tab.muteToggled.connect(self.muteToggled.emit)
        self.mixer_tab.volumeChanged.connect(self.volumeChanged.emit)
        self.mixer_tab.volumeCommitted.connect(self.volumeCommitted.emit)
        self.mixer_tab.mute_all_btn.clicked.connect(self.muteAllRequested.emit)
        self.mixer_tab.unmute_all_btn.clicked.connect(self.unmuteAllRequested.emit)
        self.mixer_tab.appHidden.connect(self.settings_tab_refresh_hidden_count)

        self.settings_tab = SettingsTab(self.tr)
        self.settings_tab.languageChanged.connect(self.languageChanged.emit)
        self.settings_tab.resetRequested.connect(self.resetRequested.emit)
        self.settings_tab.showHiddenRequested.connect(self.showHiddenRequested.emit)

        self.about_tab = AboutTab(self.tr)

        self.tabs.addTab(self.mixer_tab, self.tr("tab_mixer"))
        self.tabs.addTab(self.settings_tab, self.tr("tab_settings"))
        self.tabs.addTab(self.about_tab, self.tr("tab_about"))
        self.tabs.currentChanged.connect(self._on_tab_changed)

        layout.addWidget(self.tabs, 1)

    def settings_tab_refresh_hidden_count(self) -> None:
        self.settings_tab.refresh_hidden_count()

    def _on_tab_changed(self, index: int) -> None:
        """Uygulamalar → Ayarlar → Hakkında geçişlerinde, sayfa içeriğinin
        aniden değişmesi yerine yumuşak bir fade-in ile belirmesini sağlar
        (alt çizgi geçişi ise AnimatedTabBar tarafından ayrıca animasyonlanır)."""
        widget = self.tabs.widget(index)
        if widget is None:
            return
        if widget is self.settings_tab:
            self.settings_tab.refresh_hidden_count()
        self._tab_fade_anim = fade_in_widget(widget, duration=200)

    def retranslate(self) -> None:
        self.setWindowTitle(self.tr("app_title"))
        self.title_label.setText(self.tr("app_title"))
        self.subtitle_label.setText(self.tr("app_subtitle"))
        self.tabs.setTabText(0, self.tr("tab_mixer"))
        self.tabs.setTabText(1, self.tr("tab_settings"))
        self.tabs.setTabText(2, self.tr("tab_about"))
        self.mixer_tab.retranslate()
        self.settings_tab.retranslate()
        self.about_tab.retranslate()

    def sync_sessions(self, sessions) -> None:
        self.mixer_tab.sync_sessions(sessions)

    def update_peaks(self, sessions) -> None:
        self.mixer_tab.update_peaks(sessions)

    def set_platform_capabilities(self, per_app_supported: bool) -> None:
        self.mixer_tab.set_platform_capabilities(per_app_supported)
        if not per_app_supported:
            self.mixer_tab.retranslate()

    def set_platform_name(self, platform_name: str) -> None:
        self.about_tab.set_platform(platform_name)

    def closeEvent(self, event: QCloseEvent) -> None:
        """Pencere kapatma (X) tepsiye küçültür; gerçek çıkış tray menüsündendir."""
        event.ignore()
        self.hide()
