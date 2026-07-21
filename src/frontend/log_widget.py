# Free
from datetime import datetime

# Download
from PyQt5.QtGui import QColor, QTextCharFormat, QTextCursor
from PyQt5.QtWidgets import QApplication, QTextEdit

# Local
from src.frontend.styles import load_stylesheet


class LogWidget(QTextEdit):
    MAX_LINES = 1000

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("log_area")
        self.setReadOnly(True)
        self.line_count = 0

        self.setStyleSheet(load_stylesheet("log_widget.css"))

        self.formats = {
            'info': self._create_format("#4ec9b0"),
            'warning': self._create_format('#dcdcaa'),
            'error': self._create_format('#f48771'),
            'default': self._create_format('#d4d4d4'),
            'settings': self._create_format("#569cd6"),
            'keyboard': self._create_format("#4ec9b0"),
            'nokey': self._create_format("#f48771"),
        }

    def _create_format(self, color):
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(color))
        return fmt

    def clear_log(self):
        self.clear()
        self.line_count = 0

        parent = self.parent()
        while parent:
            if hasattr(parent, '_update_line_count'):
                parent._update_line_count()
                break
            parent = parent.parent()

    def append_colored(self, text, tag='default'):
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.setTextCursor(cursor)

        ts = datetime.now().strftime("%H:%M:%S")
        self.textCursor().insertText(f"[{ts}] ", self.formats['default'])
        self.textCursor().insertText(
            f"{text}\n",
            self.formats.get(tag, self.formats['default'])
        )

        self.line_count += 1

        if self.line_count > self.MAX_LINES:
            cursor = self.textCursor()
            cursor.movePosition(QTextCursor.Start)
            cursor.movePosition(QTextCursor.Down, QTextCursor.KeepAnchor, 100)
            cursor.removeSelectedText()
            self.line_count -= 100

        self.ensureCursorVisible()
        QApplication.processEvents()
