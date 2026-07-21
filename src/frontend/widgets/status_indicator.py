# Download
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QColor, QBrush, QRadialGradient


class StatusIndicator(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(16, 16)
        self._color = QColor(108, 92, 231)
        self._is_running = False
        self._pulse = 0
        self._timer = QTimer()
        self._timer.timeout.connect(self._pulse_animation)
        self._timer.start(50)

    def set_running(self, running):
        self._is_running = running
        if running:
            self._color = QColor(0, 200, 83)
        else:
            self._color = QColor(255, 82, 82)
        self.update()

    def _pulse_animation(self):
        if self._is_running:
            self._pulse = (self._pulse + 0.05) % 1.0
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        if self._is_running:
            alpha = int(20 + 30 * (0.5 + 0.5 * (self._pulse * 2 - 1)))
            glow_color = QColor(self._color)
            glow_color.setAlpha(alpha)

            gradient = QRadialGradient(8, 8, 12, 8, 8)
            gradient.setColorAt(0, glow_color)
            gradient.setColorAt(1, QColor(0, 0, 0, 0))
            painter.setBrush(gradient)
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(-2, -2, 20, 20)

        painter.setBrush(QBrush(self._color))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(2, 2, 12, 12)

        if self._is_running:
            highlight = QColor(255, 255, 255, 60)
            painter.setBrush(highlight)
            painter.drawEllipse(4, 4, 6, 4)

        painter.end()
