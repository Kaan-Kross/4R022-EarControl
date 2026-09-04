"""
4R022 Ear Control - Özel Arayüz Bileşenleri
=============================================
- AnimatedVolumeSlider: Sürüklenebilir, animasyonlu, bordo dolgulu ses çubuğu.
- MeterBar: Anlık ses seviyesini (peak) gösteren küçük, akıcı ölçer.
- AppCard: Tek bir uygulamanın ikonu, adı, sessize alma düğmesi, ses çubuğu
  ve ölçeri ile birlikte "kart" olarak sunulduğu bileşen.
"""

from __future__ import annotations

from PyQt6.QtCore import (
    QEasingCurve,
    QPropertyAnimation,
    QRectF,
    Qt,
    pyqtProperty,
    pyqtSignal,
)
from PyQt6.QtGui import QAction, QColor, QFont, QFontMetrics, QIcon, QLinearGradient, QPainter, QPainterPath, QPen
from PyQt6.QtWidgets import (
    QFileIconProvider,
    QFrame,
    QGraphicsOpacityEffect,
    QHBoxLayout,
    QLabel,
    QMenu,
    QSizePolicy,
    QTabBar,
    QVBoxLayout,
    QWidget,
)

from . import theme

_ICON_PROVIDER = QFileIconProvider()


def icon_for_path(exe_path: str | None) -> QIcon:
    """Verilen exe yolundan sistem ikonunu döndürür; bulunamazsa varsayılan simge."""
    if exe_path:
        try:
            from PyQt6.QtCore import QFileInfo

            info = QFileInfo(exe_path)
            icon = _ICON_PROVIDER.icon(info)
            if icon and not icon.isNull():
                return icon
        except Exception:
            pass
    return QIcon()


_SYSTEM_ICON_CACHE: dict[int, QIcon] = {}


def system_sounds_icon(size: int = 36) -> QIcon:
    """
    Sistem Sesleri oturumu için exe yolu bulunmadığından, Windows'un
    kendi bilgisayar/hoparlör simgesine benzer, elle çizilmiş bir ikon
    üretir. Böylece kart, boş/simgesiz görünmez.
    """
    if size in _SYSTEM_ICON_CACHE:
        return _SYSTEM_ICON_CACHE[size]

    from PyQt6.QtCore import QRectF as _QRectF
    from PyQt6.QtGui import QPixmap

    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # Arka plan: yuvarlatılmış gri kare (Windows sistem simgesi hissi)
    bg_path = QPainterPath()
    bg_path.addRoundedRect(_QRectF(0, 0, size, size), size * 0.22, size * 0.22)
    painter.fillPath(bg_path, QColor(theme.SURFACE))
    painter.setPen(QPen(QColor(theme.BORDER), max(1.0, size * 0.03)))
    painter.drawPath(bg_path)

    # Monitör gövdesi
    body_color = QColor(theme.GRAY_TEXT)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(body_color)

    mon_w = size * 0.56
    mon_h = size * 0.38
    mon_x = (size - mon_w) / 2
    mon_y = size * 0.16
    monitor = QPainterPath()
    monitor.addRoundedRect(_QRectF(mon_x, mon_y, mon_w, mon_h), size * 0.04, size * 0.04)
    painter.fillPath(monitor, body_color)

    # Ekran (bordo vurgu)
    screen_pad = size * 0.045
    screen = QPainterPath()
    screen.addRoundedRect(
        _QRectF(
            mon_x + screen_pad,
            mon_y + screen_pad,
            mon_w - screen_pad * 2,
            mon_h - screen_pad * 2,
        ),
        size * 0.02,
        size * 0.02,
    )
    painter.fillPath(screen, QColor(theme.BORDO_LIGHT))

    # Stand (ayak)
    stand_w = size * 0.14
    stand_h = size * 0.10
    stand_x = (size - stand_w) / 2
    stand_y = mon_y + mon_h
    painter.fillPath(
        _rect_path(stand_x, stand_y, stand_w, stand_h), body_color
    )

    # Taban
    base_w = size * 0.34
    base_h = size * 0.055
    base_x = (size - base_w) / 2
    base_y = stand_y + stand_h
    painter.fillPath(
        _rect_path(base_x, base_y, base_w, base_h, radius=base_h / 2), body_color
    )

    # Ses dalgaları (sağ üstte küçük hoparlör vurgusu)
    painter.setPen(QPen(QColor(theme.BORDO_BRIGHT), max(1.2, size * 0.035)))
    cx, cy = size * 0.80, size * 0.28
    for i, r in enumerate((size * 0.06, size * 0.10)):
        rect = _QRectF(cx - r, cy - r, r * 2, r * 2)
        painter.drawArc(rect, -40 * 16, 80 * 16)

    painter.end()

    icon = QIcon(pixmap)
    _SYSTEM_ICON_CACHE[size] = icon
    return icon


def _rect_path(x: float, y: float, w: float, h: float, radius: float = 0.0) -> QPainterPath:
    from PyQt6.QtCore import QRectF as _QRectF

    path = QPainterPath()
    if radius > 0:
        path.addRoundedRect(_QRectF(x, y, w, h), radius, radius)
    else:
        path.addRect(_QRectF(x, y, w, h))
    return path


# ========================================================================
# Animasyonlu Ses Çubuğu
# ========================================================================
class AnimatedVolumeSlider(QWidget):
    """0.0 - 1.0 arası değer tutan, sürüklenebilir ve animasyonlu ses çubuğu."""

    valueChanged = pyqtSignal(float)      # kullanıcı sürüklediğinde / tıkladığında
    valueCommitted = pyqtSignal(float)    # bırakıldığında (kalıcı kayıt için)

    def __init__(self, parent: QWidget | None = None, height: int = 22) -> None:
        super().__init__(parent)
        self._value = 0.75
        self._display_value = 0.75  # animasyonla değişen görsel değer
        self._dragging = False
        self._muted = False
        self.setFixedHeight(height)
        self.setMinimumWidth(80)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMouseTracking(True)

        self._anim = QPropertyAnimation(self, b"displayValue")
        self._anim.setDuration(160)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)

    # -- animasyonlu özellik -------------------------------------------------
    def _get_display_value(self) -> float:
        return self._display_value

    def _set_display_value(self, v: float) -> None:
        self._display_value = v
        self.update()

    displayValue = pyqtProperty(float, _get_display_value, _set_display_value)

    # -- genel API -------------------------------------------------------
    def value(self) -> float:
        return self._value

    @property
    def is_dragging(self) -> bool:
        return self._dragging

    def set_value(self, value: float, animate: bool = True) -> None:
        value = max(0.0, min(1.0, value))
        self._value = value
        if animate and not self._dragging:
            self._anim.stop()
            self._anim.setStartValue(self._display_value)
            self._anim.setEndValue(value)
            self._anim.start()
        else:
            self._display_value = value
            self.update()

    def set_muted(self, muted: bool) -> None:
        self._muted = muted
        self.update()

    # -- fare olayları -----------------------------------------------------
    def _pos_to_value(self, x: int) -> float:
        track_pad = 2
        w = max(1, self.width() - track_pad * 2)
        v = (x - track_pad) / w
        return max(0.0, min(1.0, v))

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = True
            v = self._pos_to_value(event.position().x())
            self._value = v
            self._display_value = v
            self.update()
            self.valueChanged.emit(v)

    def mouseMoveEvent(self, event):
        if self._dragging:
            v = self._pos_to_value(event.position().x())
            self._value = v
            self._display_value = v
            self.update()
            self.valueChanged.emit(v)

    def mouseReleaseEvent(self, event):
        if self._dragging:
            self._dragging = False
            self.valueCommitted.emit(self._value)

    def wheelEvent(self, event):
        delta = 0.02 if event.angleDelta().y() > 0 else -0.02
        v = max(0.0, min(1.0, self._value + delta))
        self.set_value(v, animate=False)
        self.valueChanged.emit(v)
        self.valueCommitted.emit(v)

    # -- çizim -------------------------------------------------------------
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        h = self.height()
        w = self.width()
        track_h = max(6, int(h * 0.4))
        y = (h - track_h) / 2
        radius = track_h / 2

        # Arka plan track
        track_path = QPainterPath()
        track_path.addRoundedRect(QRectF(0, y, w, track_h), radius, radius)
        painter.fillPath(track_path, QColor(theme.SURFACE))

        # Dolgu
        fill_w = max(track_h, w * self._display_value)
        fill_color_start = QColor(theme.GRAY_TEXT_DIM) if self._muted else QColor(theme.BORDO)
        fill_color_end = QColor(theme.GRAY_TEXT_DIM) if self._muted else QColor(theme.BORDO_BRIGHT)

        gradient = QLinearGradient(0, 0, fill_w, 0)
        gradient.setColorAt(0.0, fill_color_start)
        gradient.setColorAt(1.0, fill_color_end)

        fill_path = QPainterPath()
        fill_path.addRoundedRect(QRectF(0, y, fill_w, track_h), radius, radius)
        painter.setClipPath(track_path)
        painter.fillPath(fill_path, gradient)
        painter.setClipping(False)

        # Topuz (thumb)
        thumb_r = h * 0.42
        thumb_x = max(thumb_r, min(w - thumb_r, fill_w))
        thumb_color = QColor(theme.GRAY_TEXT) if self._muted else QColor(theme.WHITE_TEXT)
        painter.setPen(QPen(QColor(theme.BORDO_LIGHT if not self._muted else theme.BORDER), 2))
        painter.setBrush(thumb_color)
        painter.drawEllipse(
            QRectF(thumb_x - thumb_r, h / 2 - thumb_r, thumb_r * 2, thumb_r * 2)
        )


# ========================================================================
# Küçük Ses Ölçer (Peak Meter)
# ========================================================================
class MeterBar(QWidget):
    """İnce, yatay, anlık ses seviyesini (0.0 - 1.0) gösteren akıcı ölçer."""

    def __init__(self, parent: QWidget | None = None, height: int = 4) -> None:
        super().__init__(parent)
        self._level = 0.0
        self._display_level = 0.0
        self.setFixedHeight(height)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        self._anim = QPropertyAnimation(self, b"displayLevel")
        self._anim.setDuration(90)
        self._anim.setEasingCurve(QEasingCurve.Type.OutQuad)

    def _get_display_level(self) -> float:
        return self._display_level

    def _set_display_level(self, v: float) -> None:
        self._display_level = v
        self.update()

    displayLevel = pyqtProperty(float, _get_display_level, _set_display_level)

    def set_level(self, level: float) -> None:
        level = max(0.0, min(1.0, level))
        # Yükselirken hızlı, düşerken biraz daha yumuşak tepki
        self._anim.stop()
        self._anim.setStartValue(self._display_level)
        self._anim.setEndValue(level)
        self._anim.setDuration(70 if level > self._display_level else 180)
        self._anim.start()
        self._level = level

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        radius = h / 2

        bg = QPainterPath()
        bg.addRoundedRect(QRectF(0, 0, w, h), radius, radius)
        painter.fillPath(bg, QColor(theme.BLACK_SOFT))

        fill_w = max(0.0, min(w, w * self._display_level))
        if fill_w <= 0:
            return

        gradient = QLinearGradient(0, 0, w, 0)
        gradient.setColorAt(0.0, QColor(theme.SUCCESS))
        gradient.setColorAt(0.7, QColor(theme.BORDO_LIGHT))
        gradient.setColorAt(1.0, QColor(theme.BORDO_GLOW))

        fill_path = QPainterPath()
        fill_path.addRoundedRect(QRectF(0, 0, fill_w, h), radius, radius)
        painter.setClipPath(bg)
        painter.fillPath(fill_path, gradient)


# ========================================================================
# Taşan Metni Kırpan Etiket (Eliding Label)
# ========================================================================
class ElidingLabel(QLabel):
    """
    QLabel türevi: metin, widget genişliğine sığmadığında sonunda "…" ile
    kırpılır (elide) — taşıp kartın diğer elemanlarını (yüzde etiketi,
    sessize alma düğmesi) bozması veya kartın kendisini gereksiz yere
    genişletmesi engellenir. Tam metin her zaman araç ipucu (tooltip)
    olarak saklanır, böylece kullanıcı üzerine gelince tam adı görebilir.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._full_text = ""
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

    def setFullText(self, text: str) -> None:
        self._full_text = text
        self.setToolTip(text)
        self._apply_elide()

    def fullText(self) -> str:
        """Kırpılmamış tam metni döndürür (ör. arama/filtreleme için —
        ekranda görünen, sonu '…' ile kesilmiş metin DEĞİL)."""
        return self._full_text

    def resizeEvent(self, event) -> None:  # noqa: D401 - Qt override
        super().resizeEvent(event)
        self._apply_elide()

    def _apply_elide(self) -> None:
        if not self._full_text:
            super().setText("")
            return
        metrics = QFontMetrics(self.font())
        elided = metrics.elidedText(
            self._full_text, Qt.TextElideMode.ElideRight, max(0, self.width())
        )
        super().setText(elided)


# ========================================================================
# Uygulama Kartı
# ========================================================================
class AppCard(QFrame):
    """Tek bir uygulamanın ses kontrolünü içeren kart bileşeni."""

    muteToggled = pyqtSignal(int, bool)      # pid, muted
    volumeChanged = pyqtSignal(int, float)   # pid, level (sürüklerken)
    volumeCommitted = pyqtSignal(int, float) # pid, level (bırakınca -> kaydet)
    hideRequested = pyqtSignal(int)          # pid — "Listeden Gizle" seçildiğinde

    def __init__(self, pid: int, compact: bool = False, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.pid = pid
        self.compact = compact
        self._hide_label = "Hide from list"
        self.setObjectName("AppCard")
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.DefaultContextMenu)
        self._build_ui()
        if not compact:
            self._apply_shadow()

    def set_hide_label(self, text: str) -> None:
        """Sağ tık menüsündeki 'Listeden Gizle' metnini, mevcut dile göre
        ayarlar (i18n metni AppCard'a dışarıdan enjekte edilir; bileşen
        Translator'a doğrudan bağımlı olmaz)."""
        self._hide_label = text

    def contextMenuEvent(self, event) -> None:
        menu = QMenu(self)
        hide_action = QAction(self._hide_label, self)
        hide_action.triggered.connect(lambda: self.hideRequested.emit(self.pid))
        menu.addAction(hide_action)
        menu.exec(event.globalPos())

    def _apply_shadow(self) -> None:
        """Karta hafif bir derinlik hissi vermek için ince bir gölge ekler.
        Kompakt (Hızlı Panel) kartlarda, performans ve görsel sadelik için
        bu efekt uygulanmaz."""
        from PyQt6.QtWidgets import QGraphicsDropShadowEffect

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(18)
        shadow.setXOffset(0)
        shadow.setYOffset(3)
        shadow.setColor(QColor(0, 0, 0, 110))
        self.setGraphicsEffect(shadow)

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        pad = 10 if self.compact else 14
        outer.setContentsMargins(pad, pad, pad, pad)
        outer.setSpacing(6 if self.compact else 8)

        top_row = QHBoxLayout()
        top_row.setSpacing(10)

        icon_size = 28 if self.compact else 36
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(icon_size, icon_size)
        self.icon_label.setScaledContents(True)
        top_row.addWidget(self.icon_label)

        name_col = QVBoxLayout()
        name_col.setSpacing(1)
        self.name_label = ElidingLabel()
        self.name_label.setObjectName("AppName")
        f = self.name_label.font()
        f.setPointSize(9 if self.compact else 10)
        self.name_label.setFont(f)
        self.name_label.setFullText("—")
        self.status_label = QLabel("")
        self.status_label.setObjectName("AppStatus")
        name_col.addWidget(self.name_label)
        name_col.addWidget(self.status_label)
        top_row.addLayout(name_col, 1)

        self.percent_label = QLabel("0%")
        self.percent_label.setObjectName("VolumePercent")
        self.percent_label.setFixedWidth(38)
        self.percent_label.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        top_row.addWidget(self.percent_label)

        self.mute_btn = _MuteButton(compact=self.compact)
        self.mute_btn.clicked.connect(self._on_mute_clicked)
        top_row.addWidget(self.mute_btn)

        outer.addLayout(top_row)

        self.slider = AnimatedVolumeSlider(height=18 if self.compact else 22)
        self.slider.valueChanged.connect(self._on_slider_changed)
        self.slider.valueCommitted.connect(self._on_slider_committed)
        outer.addWidget(self.slider)

        self.meter = MeterBar(height=3 if self.compact else 4)
        outer.addWidget(self.meter)

    # -- durum güncelleme --------------------------------------------------
    def set_icon(self, icon: QIcon) -> None:
        size = self.icon_label.width()
        if icon and not icon.isNull():
            self.icon_label.setPixmap(icon.pixmap(size, size))
        else:
            self.icon_label.setStyleSheet(
                f"background-color: {theme.SURFACE}; border-radius: {size // 2}px;"
            )

    def set_name(self, name: str) -> None:
        self.name_label.setFullText(name)

    def set_status(self, text: str) -> None:
        self.status_label.setText(text)

    def set_volume(self, level: float, animate: bool = True) -> None:
        self.slider.set_value(level, animate=animate)
        self.percent_label.setText(f"{int(round(level * 100))}%")

    def set_muted(self, muted: bool) -> None:
        self.mute_btn.set_muted(muted)
        self.slider.set_muted(muted)

    def set_peak(self, peak: float) -> None:
        self.meter.set_level(peak)

    # -- olaylar -------------------------------------------------------------
    def _on_mute_clicked(self) -> None:
        new_state = not self.mute_btn.muted
        self.mute_btn.set_muted(new_state)
        self.slider.set_muted(new_state)
        self.muteToggled.emit(self.pid, new_state)

    def _on_slider_changed(self, value: float) -> None:
        self.percent_label.setText(f"{int(round(value * 100))}%")
        self.volumeChanged.emit(self.pid, value)

    def _on_slider_committed(self, value: float) -> None:
        self.volumeCommitted.emit(self.pid, value)


class _MuteButton(QFrame):
    """Yuvarlak, hoparlör ikonlu sessize alma düğmesi."""

    clicked = pyqtSignal()

    def __init__(self, compact: bool = False, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        size = 26 if compact else 32
        self.setFixedSize(size, size)
        self.muted = False
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def set_muted(self, muted: bool) -> None:
        self.muted = muted
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()

        bg_color = QColor(theme.DANGER) if self.muted else QColor(theme.SURFACE)
        border_color = QColor(theme.DANGER) if self.muted else QColor(theme.BORDER)
        painter.setPen(QPen(border_color, 1))
        painter.setBrush(bg_color)
        painter.drawEllipse(1, 1, w - 2, h - 2)

        # Basit hoparlör simgesi
        icon_color = QColor(theme.WHITE_TEXT)
        painter.setPen(QPen(icon_color, 1.4))
        painter.setBrush(icon_color)
        cx, cy = w / 2, h / 2
        body = QPainterPath()
        body.moveTo(cx - 7, cy - 3)
        body.lineTo(cx - 3, cy - 3)
        body.lineTo(cx + 2, cy - 7)
        body.lineTo(cx + 2, cy + 7)
        body.lineTo(cx - 3, cy + 3)
        body.lineTo(cx - 7, cy + 3)
        body.closeSubpath()
        painter.drawPath(body)

        if self.muted:
            painter.setPen(QPen(icon_color, 1.6))
            painter.drawLine(int(cx + 3), int(cy - 5), int(cx + 8), int(cy + 5))
            painter.drawLine(int(cx + 8), int(cy - 5), int(cx + 3), int(cy + 5))
        else:
            painter.setPen(QPen(icon_color, 1.2))
            painter.drawArc(int(cx + 3), int(cy - 5), 8, 10, -60 * 16, 120 * 16)


# ========================================================================
# Animasyonlu Sekme Çubuğu (Tab Bar)
# ========================================================================
class AnimatedTabBar(QTabBar):
    """
    Standart QTabBar; tek fark, seçili sekmenin altındaki vurgu çizgisinin
    bir sekmeden diğerine anında "ışınlanması" yerine yumuşakça kayarak
    (QPropertyAnimation ile) geçiş yapmasıdır. Metin ve arka plan hâlâ QSS
    ile çizilir; yalnızca alt çizgi bu sınıf tarafından elle çizilir.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setDrawBase(False)
        self._indicator_x = 0.0
        self._indicator_w = 0.0
        self._initialized = False

        self._anim_x = QPropertyAnimation(self, b"indicatorX")
        self._anim_w = QPropertyAnimation(self, b"indicatorW")
        for anim in (self._anim_x, self._anim_w):
            anim.setDuration(240)
            anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        self.currentChanged.connect(self._animate_to_index)

    def _get_indicator_x(self) -> float:
        return self._indicator_x

    def _set_indicator_x(self, v: float) -> None:
        self._indicator_x = v
        self.update()

    indicatorX = pyqtProperty(float, _get_indicator_x, _set_indicator_x)

    def _get_indicator_w(self) -> float:
        return self._indicator_w

    def _set_indicator_w(self, v: float) -> None:
        self._indicator_w = v
        self.update()

    indicatorW = pyqtProperty(float, _get_indicator_w, _set_indicator_w)

    def showEvent(self, event) -> None:
        super().showEvent(event)
        if not self._initialized and self.count() > 0:
            rect = self.tabRect(max(0, self.currentIndex()))
            self._indicator_x = float(rect.x())
            self._indicator_w = float(rect.width())
            self._initialized = True
            self.update()

    def _animate_to_index(self, index: int) -> None:
        if index < 0 or index >= self.count():
            return
        rect = self.tabRect(index)
        if not self._initialized:
            # İlk kurulumda animasyon yapmadan doğrudan konumlan
            self._indicator_x = float(rect.x())
            self._indicator_w = float(rect.width())
            self._initialized = True
            self.update()
            return
        self._anim_x.stop()
        self._anim_w.stop()
        self._anim_x.setStartValue(self._indicator_x)
        self._anim_x.setEndValue(float(rect.x()))
        self._anim_w.setStartValue(self._indicator_w)
        self._anim_w.setEndValue(float(rect.width()))
        self._anim_x.start()
        self._anim_w.start()

    def paintEvent(self, event) -> None:
        super().paintEvent(event)
        if self._indicator_w <= 0:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        bar_h = 3.0
        y = self.height() - bar_h
        path = QPainterPath()
        path.addRoundedRect(QRectF(self._indicator_x, y, self._indicator_w, bar_h), 1.5, 1.5)
        painter.fillPath(path, QColor(theme.BORDO_BRIGHT))


def fade_in_widget(widget: QWidget, duration: int = 220) -> QPropertyAnimation:
    """
    Verilen widget'ı saydamdan tam görünür hale animasyonla getirir
    (sayfa/sekme geçişlerinde kullanılır). Döndürülen QPropertyAnimation
    referansı, çağıran taraf tarafından bir örnek değişkeninde tutulmalıdır
    (aksi halde Python çöp toplayıcısı animasyonu erken sonlandırabilir).
    """
    effect = QGraphicsOpacityEffect(widget)
    widget.setGraphicsEffect(effect)
    anim = QPropertyAnimation(effect, b"opacity", widget)
    anim.setDuration(duration)
    anim.setStartValue(0.0)
    anim.setEndValue(1.0)
    anim.setEasingCurve(QEasingCurve.Type.OutCubic)

    def _cleanup():
        # Animasyon bittikten sonra efekti kaldır: sürekli bir
        # QGraphicsOpacityEffect'in widget üzerinde kalması gereksiz
        # render maliyeti yaratır ve bazı alt widget'larda (ör. gölge
        # efektleri) görsel çakışmaya yol açabilir.
        widget.setGraphicsEffect(None)

    anim.finished.connect(_cleanup)
    anim.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
    return anim
