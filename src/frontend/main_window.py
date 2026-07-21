# Free
from os import path
from time import time

# Download
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QIcon

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QSystemTrayIcon, QMenu, QAction, QPushButton
)

# Local
from src.config import load_config, VER, APP_FULL_NAME
from src.frontend.settings_dialog import SettingsDialog
from src.frontend.log_widget import LogWidget
from src.frontend.styles import load_stylesheet
from src.frontend.widgets.animated_button import AnimatedButton
from src.frontend.widgets.status_indicator import StatusIndicator
from src.frontend.widgets.custom_title_bar import CustomTitleBar
from src.utils import resource_path


class MainWindow(QMainWindow):
    append_text = pyqtSignal(str, str)

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.config = load_config()
        self.tray_icon = None
        self._closing = False
        self._toggle_lock = False
        self._last_toggle_time = 0
        self.settings_dialog = None
        self.settings_open = False

        self._resize_direction = None
        self._resize_start_pos = None
        self._resize_start_geo = None
        self._resize_margin = 12
        self._is_resizing = False

        flags = Qt.FramelessWindowHint | Qt.WindowMinimizeButtonHint
        if self.config.get("ALWAYS_ON_TOP", True):
            flags |= Qt.WindowStaysOnTopHint
        self.setWindowFlags(flags)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.setMinimumSize(500, 400)
        self.resize(500, 400)

        self.setStyleSheet(load_stylesheet("main_window.css"))

        central = QWidget()
        central.setObjectName("central_widget")
        self.setCentralWidget(central)

        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.title_bar = CustomTitleBar(self)
        self.title_bar.set_title(APP_FULL_NAME)
        main_layout.addWidget(self.title_bar)

        content = QWidget()
        content.setObjectName("content_widget")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(16, 12, 16, 16)
        content_layout.setSpacing(12)

        toolbar = QWidget()
        toolbar.setObjectName("toolbar")
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(8, 4, 8, 4)
        toolbar_layout.setSpacing(12)

        self.status_indicator = StatusIndicator()
        toolbar_layout.addWidget(self.status_indicator)

        self.status_label = QLabel("Остановлен")
        self.status_label.setObjectName("status_label")
        toolbar_layout.addWidget(self.status_label)

        toolbar_layout.addStretch()

        version_label = QLabel(f"v{VER}")
        version_label.setObjectName("version_label")
        toolbar_layout.addWidget(version_label)

        self.start_btn = AnimatedButton("СТАРТ")
        self.start_btn.setObjectName("start_btn")
        self.start_btn.clicked.connect(self._on_toggle)
        toolbar_layout.addWidget(self.start_btn)

        self.settings_btn = AnimatedButton()
        self.settings_btn.set_enable_scale(False)
        self.settings_btn.setObjectName("settings_btn")
        self.settings_btn.setFixedSize(40, 36)
        self.settings_btn.setText("⚙")
        self.settings_btn.clicked.connect(self._open_settings)
        toolbar_layout.addWidget(self.settings_btn)

        content_layout.addWidget(toolbar)

        log_container = QWidget()
        log_container.setObjectName("log_container")
        log_container_layout = QVBoxLayout(log_container)
        log_container_layout.setContentsMargins(0, 0, 0, 0)
        log_container_layout.setSpacing(0)

        self.log_widget = LogWidget()
        log_container_layout.addWidget(self.log_widget)

        bottom_bar = QWidget()
        bottom_bar.setObjectName("bottom_bar")
        bottom_bar_layout = QHBoxLayout(bottom_bar)
        bottom_bar_layout.setContentsMargins(8, 4, 8, 4)
        bottom_bar_layout.setSpacing(0)

        self.line_count_label = QLabel("0")
        self.line_count_label.setObjectName("line_count_label")
        bottom_bar_layout.addWidget(self.line_count_label)

        bottom_bar_layout.addStretch()

        self.clear_btn = QPushButton("Очистить")
        self.clear_btn.setObjectName("clear_btn")
        self.clear_btn.setFixedHeight(28)
        self.clear_btn.setCursor(Qt.PointingHandCursor)
        self.clear_btn.setToolTip("Очистить лог")
        self.clear_btn.clicked.connect(self._clear_log)
        bottom_bar_layout.addWidget(self.clear_btn)

        log_container_layout.addWidget(bottom_bar)
        content_layout.addWidget(log_container)

        main_layout.addWidget(content)

        icon_path = resource_path('icon.ico')
        if path.exists(icon_path):
            try:
                icon = QIcon(icon_path)
                self.setWindowIcon(icon)
                self._create_tray_icon(icon)
            except Exception:
                pass

        self.append_text.connect(self._append_text_slot)

        self.timer = QTimer()
        self.timer.timeout.connect(self._auto_save_settings)
        self.timer.start(2000)

        self.app.start_listener()
        self.app.gui = self

        self.update_status()
        self.setMouseTracking(True)

        self._update_line_count()

    def _update_line_count(self):
        if hasattr(self, 'line_count_label'):
            count = self.log_widget.line_count
            self.line_count_label.setText(f"{count}")

    def _clear_log(self):
        self.log_widget.clear_log()
        self._update_line_count()
        self.log("Лог очищен", 'info')

    def _open_settings(self):
        if self.app.enabled:
            self.log_warning("Настройки недоступны во время работы")
            return

        if self.settings_dialog and self.settings_dialog.isVisible():
            self.settings_dialog.raise_()
            self.settings_dialog.activateWindow()
            return

        self.settings_dialog = SettingsDialog(self)
        self.settings_dialog.setModal(False)
        self.settings_dialog.show()
        self.settings_open = True
        self.settings_btn.setEnabled(False)
        self.settings_btn.setToolTip("Настройки открыты")

    def _close_settings(self):
        if self.settings_dialog and self.settings_dialog.isVisible():
            self.settings_dialog.close()
        self.settings_open = False
        if not self.app.enabled:
            self.settings_btn.setEnabled(True)
            self.settings_btn.setToolTip("Настройки")
            self.settings_btn.set_color("#6c5ce7")
        else:
            self.settings_btn.setEnabled(False)
            self.settings_btn.setToolTip("Настройки недоступны во время работы")

    def _create_tray_icon(self, icon):
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(icon)

        menu = QMenu()

        show_action = QAction("Показать", self)
        show_action.triggered.connect(self.show)
        menu.addAction(show_action)

        menu.addSeparator()

        toggle_action = QAction("Старт/Стоп", self)
        toggle_action.triggered.connect(self._on_tray_toggle)
        menu.addAction(toggle_action)

        menu.addSeparator()

        quit_action = QAction("Выход", self)
        quit_action.triggered.connect(self._quit_application)
        menu.addAction(quit_action)

        self.tray_icon.setContextMenu(menu)
        self.tray_icon.activated.connect(self._tray_icon_activated)
        self.tray_icon.show()

    def _tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            if self.isVisible():
                self.hide()
            else:
                self.show()
                self.raise_()
                self.activateWindow()

    def _quit_application(self):
        if self._closing:
            return
        self._closing = True

        self._close_settings()
        self.app.cleanup()
        if self.tray_icon:
            self.tray_icon.hide()
        QApplication.quit()

    def _on_tray_toggle(self):
        self._on_toggle()

    def _on_toggle(self):
        current_time = time()
        if self._toggle_lock or (current_time - self._last_toggle_time) < 0.5:
            return

        self._toggle_lock = True
        self._last_toggle_time = current_time

        try:
            self.app.toggle()
            self.update_status()
        except Exception as e:
            self.log(f"Ошибка: {e}", 'error')
        finally:
            self._toggle_lock = False

    def _append_text_slot(self, text, tag):
        self.log_widget.append_colored(text, tag)
        self._update_line_count()

    def _auto_save_settings(self):
        pass

    def log(self, message, tag='default'):
        self.append_text.emit(message, tag)

    def log_info(self, message):
        self.log(message, 'info')

    def log_warning(self, message):
        self.log(message, 'warning')

    def log_error(self, message):
        self.log(message, 'error')

    def update_status(self):
        if self.app.enabled:
            self.start_btn.setText("СТОП")
            self.start_btn.set_running(True)
            self.status_label.setText("Работает")
            self.status_indicator.set_running(True)

            if self.settings_open:
                self._close_settings()

            self.settings_btn.setEnabled(False)
            self.settings_btn.setToolTip("Настройки недоступны во время работы")
            self.settings_btn.set_color("#ff6b6b")
        else:
            self.start_btn.setText("СТАРТ")
            self.start_btn.set_running(False)
            self.status_label.setText("Остановлен")
            self.status_indicator.set_running(False)

            if not self.settings_open:
                self.settings_btn.setEnabled(True)
                self.settings_btn.setToolTip("Настройки")
                self.settings_btn.set_color("#6c5ce7")
            else:
                self.settings_btn.setEnabled(False)
                self.settings_btn.setToolTip("Настройки открыты")

    def _get_resize_direction(self, pos):
        rect = self.rect()
        margin = self._resize_margin
        x = pos.x()
        y = pos.y()
        width = rect.width()
        height = rect.height()

        in_left = x <= margin
        in_right = x >= width - margin
        in_top = y <= margin
        in_bottom = y >= height - margin

        if in_left and in_top:
            return 'lefttop'
        if in_right and in_top:
            return 'righttop'
        if in_left and in_bottom:
            return 'leftbottom'
        if in_right and in_bottom:
            return 'rightbottom'
        if in_left:
            return 'left'
        if in_right:
            return 'right'
        if in_top:
            return 'top'
        if in_bottom:
            return 'bottom'

        return None

    def _get_cursor_for_direction(self, direction):
        if direction == 'left' or direction == 'right':
            return Qt.SizeHorCursor
        if direction == 'top' or direction == 'bottom':
            return Qt.SizeVerCursor
        if direction in ('lefttop', 'rightbottom'):
            return Qt.SizeFDiagCursor
        if direction in ('righttop', 'leftbottom'):
            return Qt.SizeBDiagCursor
        return Qt.ArrowCursor

    def _update_cursor(self, pos):
        if self._is_resizing:
            return

        direction = self._get_resize_direction(pos)
        cursor = self._get_cursor_for_direction(direction) if direction else Qt.ArrowCursor
        self.setCursor(cursor)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            pos = event.pos()

            if self.title_bar.geometry().contains(pos):
                super().mousePressEvent(event)
                return

            direction = self._get_resize_direction(pos)
            if direction:
                self._is_resizing = True
                self._resize_direction = direction
                self._resize_start_pos = event.globalPos()
                self._resize_start_geo = self.geometry()
                return

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        pos = event.pos()

        if self._is_resizing and self._resize_direction and self._resize_start_pos:
            delta = event.globalPos() - self._resize_start_pos
            geo = self._resize_start_geo

            new_x = geo.x()
            new_y = geo.y()
            new_w = geo.width()
            new_h = geo.height()

            direction = self._resize_direction

            if 'left' in direction:
                new_x = geo.x() + delta.x()
                new_w = geo.width() - delta.x()
            elif 'right' in direction:
                new_w = geo.width() + delta.x()

            if 'top' in direction:
                new_y = geo.y() + delta.y()
                new_h = geo.height() - delta.y()
            elif 'bottom' in direction:
                new_h = geo.height() + delta.y()

            if new_w < self.minimumWidth():
                if 'left' in direction:
                    new_x = geo.x() + geo.width() - self.minimumWidth()
                new_w = self.minimumWidth()

            if new_h < self.minimumHeight():
                if 'top' in direction:
                    new_y = geo.y() + geo.height() - self.minimumHeight()
                new_h = self.minimumHeight()

            self.setGeometry(new_x, new_y, new_w, new_h)
            return

        if not self._is_resizing:
            self._update_cursor(pos)

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._is_resizing = False
            self._resize_direction = None
            self._resize_start_pos = None
            self._resize_start_geo = None
            self._update_cursor(self.mapFromGlobal(self.cursor().pos()))
        super().mouseReleaseEvent(event)

    def leaveEvent(self, event):
        if not self._is_resizing:
            self.setCursor(Qt.ArrowCursor)
        super().leaveEvent(event)

    def closeEvent(self, event):
        if self._closing:
            event.accept()
            return

        self._close_settings()
        self.config = load_config()

        if self.config.get("MINIMIZE_TO_TRAY", False) and self.tray_icon:
            self.hide()
            if self.tray_icon:
                self.tray_icon.showMessage(
                    APP_FULL_NAME,
                    "Приложение свернуто в трей",
                    QSystemTrayIcon.Information,
                    2000
                )
            event.ignore()
            return

        self._closing = True
        try:
            self.app.cleanup()
            if self.tray_icon:
                self.tray_icon.hide()
        except Exception:
            pass
        event.accept()

    def showEvent(self, event):
        super().showEvent(event)
        self.update_status()

    def show(self):
        super().show()
        self.update_status()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'resize_indicator'):
            self.resize_indicator.move(self.width() - 30, self.height() - 30)
