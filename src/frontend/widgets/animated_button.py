# Download
from PyQt5.QtCore import QPropertyAnimation, QEasingCurve, pyqtProperty, Qt
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtGui import QColor, QPainter, QPainterPath

# Local
from src.frontend.styles import load_stylesheet


class AnimatedButton(QPushButton):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)

        self._opacity = 1.0
        self._scale = 1.0
        self._color = QColor(108, 92, 231)
        self._is_running = False
        self._enable_scale = True
        self._icon = None
        self._icon_size = 20

        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(36)
        self.setMinimumWidth(80)

        self.setStyleSheet(load_stylesheet("animated_button.css"))

        self.hover_anim = QPropertyAnimation(self, b"scale")
        self.hover_anim.setDuration(200)
        self.hover_anim.setEasingCurve(QEasingCurve.OutCubic)

        self.color_anim = QPropertyAnimation(self, b"color")
        self.color_anim.setDuration(200)
        self.color_anim.setEasingCurve(QEasingCurve.OutCubic)

    def set_icon(self, icon, icon_size=20):
        self._icon = icon
        self._icon_size = icon_size
        self.update()

    def set_enable_scale(self, enabled):
        self._enable_scale = enabled

    def set_running(self, running):
        self._is_running = running
        if running:
            self.setProperty("running", "true")
            self._color = QColor(255, 107, 107)
        else:
            self.setProperty("running", "false")
            self._color = QColor(108, 92, 231)
        self.style().polish(self)

    def set_color(self, color):
        self._color = QColor(color)
        self.update()

    def enterEvent(self, event):
        if self.isEnabled():
            if self._enable_scale:
                self.hover_anim.setStartValue(1.0)
                self.hover_anim.setEndValue(1.05)
                self.hover_anim.start()

            self.color_anim.setStartValue(self._color)
            if self._is_running:
                end_color = QColor(255, 122, 122)
            else:
                end_color = QColor(125, 111, 240)
            self.color_anim.setEndValue(end_color)
            self.color_anim.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        if self.isEnabled():
            if self._enable_scale:
                self.hover_anim.setStartValue(1.05)
                self.hover_anim.setEndValue(1.0)
                self.hover_anim.start()

            self.color_anim.setStartValue(self._color)
            self.color_anim.setEndValue(self._color)
            self.color_anim.start()
        super().leaveEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), 8, 8)

        painter.setOpacity(self._opacity)
        painter.fillPath(path, self._color)

        if self._icon and not self._icon.isNull():
            pixmap = self._icon.pixmap(self._icon_size, self._icon_size)
            if not pixmap.isNull():
                x = (self.width() - pixmap.width()) // 2
                y = (self.height() - pixmap.height()) // 2
                painter.drawPixmap(x, y, pixmap)
        else:
            painter.setPen(QColor(255, 255, 255))
            painter.setOpacity(self._opacity)
            painter.drawText(self.rect(), Qt.AlignCenter, self.text())

        painter.end()

    @pyqtProperty(float)
    def scale(self):
        return self._scale

    @scale.setter
    def scale(self, value):
        self._scale = value
        self.setFixedHeight(int(36 * value))
        self.setMinimumWidth(int(80 * value))

    @pyqtProperty(QColor)
    def color(self):
        return self._color

    @color.setter
    def color(self, value):
        self._color = value
        self.update()
