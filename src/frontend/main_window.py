# Free
from os import path
from time import time

# Download
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QIcon

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QSystemTrayIcon, QMenu, QAction, QSizeGrip
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

        # Устанавливаем флаги окна с учетом "поверх всех окон"
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
        self.start_btn.setFixedSize(100, 40)
        self.start_btn.clicked.connect(self._on_toggle)
        toolbar_layout.addWidget(self.start_btn)

        self.settings_btn = AnimatedButton()
        self.settings_btn.set_enable_scale(False)
        self.settings_btn.setObjectName("settings_btn")
        self.settings_btn.setFixedSize(40, 40)
        self.settings_btn.setToolTip("Настройки")

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
        bottom_bar_layout.setContentsMargins(6, 2, 4, 2)
        bottom_bar_layout.setSpacing(4)

        hint_label = QLabel("Измените размер окна здесь")
        hint_label.setStyleSheet("color: #4a4a6a; font-size: 11px;")
        bottom_bar_layout.addWidget(hint_label)

        bottom_bar_layout.addStretch()

        resize_icon = QLabel("↘")
        resize_icon.setStyleSheet("color: #4a4a6a; font-size: 16px;")
        bottom_bar_layout.addWidget(resize_icon)

        resize_handle = QSizeGrip(self)
        resize_handle.setObjectName("resize_handle")
        resize_handle.setFixedSize(16, 16)
        resize_handle.setToolTip("Потяни меня!")
        bottom_bar_layout.addWidget(resize_handle)

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

            # Блокируем и красим в красный
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
