"""
4R022 Ear Control - Tema Modülü
================================
Marka renk paleti: Siyah / Bordo / Gri.
Tüm QSS burada merkezi olarak tanımlanır.
"""

# ---- Renk Paleti -----------------------------------------------------
BLACK          = "#0c0c0e"
BLACK_SOFT     = "#141417"
SURFACE        = "#1b1b1f"
SURFACE_HOVER  = "#232328"
CARD_BG        = "#1e1e22"
CARD_BG_HOVER  = "#26262c"
BORDER         = "#2c2c32"

GRAY_TEXT      = "#a8a8b0"
GRAY_TEXT_DIM  = "#7a7a82"
WHITE_TEXT     = "#f2f2f4"

BORDO          = "#7a1f2b"
BORDO_LIGHT    = "#8a2332"
BORDO_BRIGHT   = "#a5293a"
BORDO_GLOW     = "#c23348"

SUCCESS        = "#4caf6a"
DANGER         = "#c23348"
WARNING        = "#d9a441"

FONT_FAMILY = "'Segoe UI', 'Inter', 'Arial', sans-serif"

MAIN_STYLESHEET = f"""
* {{
    font-family: {FONT_FAMILY};
    outline: none;
}}

QWidget#RootWindow, QMainWindow {{
    background-color: {BLACK};
    color: {WHITE_TEXT};
}}

QWidget {{
    background-color: transparent;
    color: {WHITE_TEXT};
}}

/* ---------------- Scrollbar ---------------- */
QScrollArea {{
    border: none;
    background: transparent;
}}
QScrollBar:vertical {{
    background: {BLACK_SOFT};
    width: 10px;
    margin: 2px;
    border-radius: 5px;
}}
QScrollBar::handle:vertical {{
    background: {BORDO};
    border-radius: 5px;
    min-height: 30px;
}}
QScrollBar::handle:vertical:hover {{
    background: {BORDO_LIGHT};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

/* ---------------- Header ---------------- */
QLabel#BrandTitle {{
    color: {WHITE_TEXT};
    font-size: 20px;
    font-weight: 700;
    letter-spacing: 1px;
}}
QLabel#BrandBadge {{
    color: {WHITE_TEXT};
    background-color: {BORDO};
    border-radius: 9px;
    padding: 2px 10px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1px;
}}
QLabel#BrandSubtitle {{
    color: {GRAY_TEXT};
    font-size: 12px;
}}

/* ---------------- Buttons ---------------- */
QPushButton {{
    background-color: {SURFACE};
    color: {WHITE_TEXT};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 8px 16px;
    font-size: 13px;
    font-weight: 600;
}}
QPushButton:hover {{
    background-color: {SURFACE_HOVER};
    border-color: {BORDO_LIGHT};
}}
QPushButton:pressed {{
    background-color: {BLACK_SOFT};
}}

QPushButton#PrimaryButton {{
    background-color: {BORDO};
    border: 1px solid {BORDO_LIGHT};
    color: {WHITE_TEXT};
}}
QPushButton#PrimaryButton:hover {{
    background-color: {BORDO_LIGHT};
}}
QPushButton#PrimaryButton:pressed {{
    background-color: #611722;
}}

QPushButton#GhostButton {{
    background-color: transparent;
    border: 1px solid {BORDER};
}}
QPushButton#GhostButton:hover {{
    border-color: {BORDO_LIGHT};
    background-color: {SURFACE};
}}

QPushButton#MuteToggle {{
    background-color: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 16px;
    padding: 0px;
}}
QPushButton#MuteToggle:hover {{
    border-color: {BORDO_LIGHT};
}}
QPushButton#MuteToggle[muted="true"] {{
    background-color: {DANGER};
    border-color: {DANGER};
}}

/* ---------------- Tabs ---------------- */
QTabWidget::pane {{
    border: none;
    background: transparent;
    top: 6px;
}}
QTabBar::tab {{
    background: transparent;
    color: {GRAY_TEXT};
    padding: 10px 18px;
    margin-right: 4px;
    font-size: 13px;
    font-weight: 600;
}}
QTabBar::tab:selected {{
    color: {WHITE_TEXT};
}}
QTabBar::tab:hover {{
    color: {WHITE_TEXT};
}}
/* Not: seçili sekmenin altındaki vurgu çizgisi artık QSS ile değil,
   AnimatedTabBar (core/widgets.py) tarafından elle ve animasyonlu olarak
   çizilir — bu yüzden burada statik bir border-bottom TANIMLANMAZ. */

/* ---------------- Cards ---------------- */
QFrame#AppCard {{
    background-color: {CARD_BG};
    border: 1px solid {BORDER};
    border-radius: 14px;
}}
QFrame#AppCard:hover {{
    background-color: {CARD_BG_HOVER};
    border-color: {BORDO_LIGHT};
}}
QLabel#AppName {{
    color: {WHITE_TEXT};
    font-size: 13px;
    font-weight: 700;
}}
QLabel#AppStatus {{
    color: {GRAY_TEXT_DIM};
    font-size: 11px;
}}
QLabel#VolumePercent {{
    color: {GRAY_TEXT};
    font-size: 12px;
    font-weight: 600;
}}

/* ---------------- Inputs ---------------- */
QLineEdit {{
    background-color: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 8px 12px;
    color: {WHITE_TEXT};
    font-size: 13px;
}}
QLineEdit:focus {{
    border-color: {BORDO_LIGHT};
}}

QComboBox {{
    background-color: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 6px 12px;
    color: {WHITE_TEXT};
    min-width: 100px;
}}
QComboBox::drop-down {{ border: none; }}
QComboBox QAbstractItemView {{
    background-color: {SURFACE};
    color: {WHITE_TEXT};
    selection-background-color: {BORDO};
    border: 1px solid {BORDER};
    outline: none;
}}

QCheckBox {{
    color: {WHITE_TEXT};
    font-size: 13px;
    spacing: 10px;
}}
QCheckBox::indicator {{
    width: 18px;
    height: 18px;
    border-radius: 5px;
    border: 1px solid {BORDER};
    background: {SURFACE};
}}
QCheckBox::indicator:checked {{
    background-color: {BORDO};
    border-color: {BORDO_LIGHT};
}}

/* ---------------- Settings rows ---------------- */
QFrame#SettingsRow {{
    background-color: {CARD_BG};
    border: 1px solid {BORDER};
    border-radius: 12px;
}}
QLabel#SettingsRowTitle {{
    color: {WHITE_TEXT};
    font-size: 14px;
    font-weight: 700;
}}
QLabel#SettingsRowHint {{
    color: {GRAY_TEXT_DIM};
    font-size: 11px;
}}

/* ---------------- About ---------------- */
QLabel#AboutText {{
    color: {GRAY_TEXT};
    font-size: 13px;
    line-height: 20px;
}}
QLabel#AboutLogo {{
    color: {WHITE_TEXT};
    font-size: 26px;
    font-weight: 800;
}}

/* ---------------- Quick Panel (Tray Flyout) ---------------- */
QWidget#QuickPanel {{
    background-color: {BLACK_SOFT};
    border: 1px solid {BORDO_LIGHT};
    border-radius: 14px;
}}
QLabel#QuickPanelTitle {{
    color: {WHITE_TEXT};
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 1px;
}}

/* ---------------- Tooltip ---------------- */
QToolTip {{
    background-color: {SURFACE};
    color: {WHITE_TEXT};
    border: 1px solid {BORDO_LIGHT};
    padding: 4px 8px;
    border-radius: 6px;
}}

/* ---------------- Menu (tray context) ---------------- */
QMenu {{
    background-color: {SURFACE};
    color: {WHITE_TEXT};
    border: 1px solid {BORDER};
    border-radius: 10px;
    padding: 6px;
}}
QMenu::item {{
    padding: 8px 20px;
    border-radius: 6px;
}}
QMenu::item:selected {{
    background-color: {BORDO};
}}
QMenu::separator {{
    height: 1px;
    background: {BORDER};
    margin: 6px 4px;
}}
"""
