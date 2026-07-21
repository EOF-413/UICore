# Download
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
from PyQt5.QtGui import QPainter, QColor, QLinearGradient, QPainterPath

# Local
from src.frontend.styles import load_stylesheet


class CustomTitleBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.drag_position = None
        self._radius = 16

        self.setFixedHeight(44)
        self.setObjectName("title_bar")

        self.setStyleSheet(load_stylesheet("custom_title_bar.css"))

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 10, 0)
        layout.setSpacing(4)

        self.title_label = QLabel("Приложение")
        self.title_label.setObjectName("title_label")
        layout.addWidget(self.title_label)

        layout.addStretch()

        self.min_btn = QPushButton("─")
        self.min_btn.setObjectName("min_btn")
        self.min_btn.setFixedSize(32, 32)
        self.min_btn.clicked.connect(self._minimize)
        layout.addWidget(self.min_btn)

        self.close_btn = QPushButton("✕")
        self.close_btn.setObjectName("close_btn")
        self.close_btn.setFixedSize(32, 32)
        self.close_btn.clicked.connect(self._close)
        layout.addWidget(self.close_btn)

    def set_title(self, title):
        self.title_label.setText(title)

    def _minimize(self):
        if self.parent:
            self.parent.showMinimized()

    def _close(self):
        if self.parent:
            self.parent.close()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = (
                event.globalPos() - self.parent.frameGeometry().topLeft()
            )
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.drag_position:
            self.parent.move(event.globalPos() - self.drag_position)
            event.accept()

    def mouseDoubleClickEvent(self, event):
        pass

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        path = QPainterPath()
        rect = self.rect()

        path.moveTo(0, self._radius)
        path.quadTo(0, 0, self._radius, 0)
        path.lineTo(rect.width() - self._radius, 0)
        path.quadTo(rect.width(), 0, rect.width(), self._radius)
        path.lineTo(rect.width(), rect.height())
        path.lineTo(0, rect.height())
        path.closeSubpath()

        gradient = QLinearGradient(0, 0, rect.width(), 0)
        gradient.setColorAt(0, QColor(26, 26, 46))
        gradient.setColorAt(0.5, QColor(31, 31, 55))
        gradient.setColorAt(1, QColor(37, 37, 64))

        painter.fillPath(path, gradient)

        glow = QColor(108, 92, 231, 15)
        painter.fillRect(0, rect.height() - 2, rect.width(), 2, glow)

        painter.end()
