# Download
from PyQt5.QtCore import Qt, QTimer

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton, QGroupBox,
    QCheckBox, QSlider, QFrame,
    QSizeGrip, QWidget, QMessageBox
)

# Local
from src.config import load_config, save_config, DEFAULT_CONFIG
from src.frontend.styles import load_stylesheet
from src.frontend.widgets.custom_title_bar import CustomTitleBar


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.config = load_config()
        self.setWindowTitle("Настройки")
        self._is_closing = False
        self._save_timer = QTimer()
        self._save_timer.timeout.connect(self._auto_save)
        self._save_timer.start(500)

        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.Dialog |
            Qt.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.setMinimumSize(450, 500)
        self.resize(460, 500)

        self.setStyleSheet(load_stylesheet("settings_dialog.css"))

        container = QFrame()
        container.setObjectName("settings_container")
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(container)

        layout = QVBoxLayout(container)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        title_bar = CustomTitleBar(self)
        title_bar.set_title("Настройки")
        layout.addWidget(title_bar)

        content = QWidget()
        content.setObjectName("settings_content")
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(12)
        content_layout.setContentsMargins(20, 16, 20, 12)

        capture_group = QGroupBox("Захват")
        capture_layout = QGridLayout()
        capture_layout.setVerticalSpacing(10)
        capture_layout.setHorizontalSpacing(15)

        label_hold = QLabel("Время удержания:")
        label_hold.setMinimumWidth(120)
        capture_layout.addWidget(label_hold, 0, 0)

        hold_container = QHBoxLayout()
        hold_container.setSpacing(8)
        self.hold_edit = QLineEdit(str(self.config["HOLD"]))
        self.hold_edit.setFixedWidth(70)
        hold_container.addWidget(self.hold_edit)
        hold_container.addWidget(QLabel("сек"))
        hold_container.addStretch()
        capture_layout.addLayout(hold_container, 0, 1)

        label_cooldown = QLabel("Задержка:")
        label_cooldown.setMinimumWidth(120)
        capture_layout.addWidget(label_cooldown, 1, 0)

        cooldown_container = QHBoxLayout()
        cooldown_container.setSpacing(8)
        self.cooldown_edit = QLineEdit(str(self.config["COOLDOWN"]))
        self.cooldown_edit.setFixedWidth(70)
        cooldown_container.addWidget(self.cooldown_edit)
        cooldown_container.addWidget(QLabel("сек"))
        cooldown_container.addStretch()
        capture_layout.addLayout(cooldown_container, 1, 1)

        capture_group.setLayout(capture_layout)
        content_layout.addWidget(capture_group)

        match_group = QGroupBox("Совпадение")
        match_layout = QVBoxLayout()
        match_layout.setSpacing(8)

        match_row = QHBoxLayout()
        match_row.setSpacing(12)
        threshold_label = QLabel("Порог совпадения:")
        threshold_label.setMinimumWidth(120)
        match_row.addWidget(threshold_label)

        self.match_slider = QSlider(Qt.Horizontal)
        self.match_slider.setRange(10, 100)
        self.match_slider.setValue(int(self.config["MIN_MATCH"] * 100))
        self.match_slider.setFixedWidth(150)
        self.match_slider.valueChanged.connect(self._on_match_changed)
        match_row.addWidget(self.match_slider)

        self.match_label = QLabel(f"{self.config['MIN_MATCH'] * 100:.0f}%")
        self.match_label.setObjectName("match_value")
        self.match_label.setFixedWidth(40)
        match_row.addWidget(self.match_label)
        match_row.addStretch()

        match_layout.addLayout(match_row)
        match_group.setLayout(match_layout)
        content_layout.addWidget(match_group)

        window_group = QGroupBox("Окно")
        window_layout = QVBoxLayout()
        window_layout.setSpacing(8)

        self.top_checkbox = QCheckBox("Поверх всех окон")
        self.top_checkbox.setChecked(self.config.get("ALWAYS_ON_TOP", True))
        self.top_checkbox.stateChanged.connect(self._on_setting_changed)
        window_layout.addWidget(self.top_checkbox)

        self.tray_checkbox = QCheckBox("Сворачивать в трей")
        self.tray_checkbox.setChecked(self.config.get("MINIMIZE_TO_TRAY", False))
        self.tray_checkbox.stateChanged.connect(self._on_setting_changed)
        window_layout.addWidget(self.tray_checkbox)

        window_group.setLayout(window_layout)
        content_layout.addWidget(window_group)

        reset_btn = QPushButton("Сбросить настройки")
        reset_btn.setObjectName("reset_btn")
        reset_btn.setFixedWidth(150)
        reset_btn.clicked.connect(self._reset_settings)
        reset_btn.setToolTip("Вернуть настройки по умолчанию")

        reset_layout = QHBoxLayout()
        reset_layout.addStretch()
        reset_layout.addWidget(reset_btn)
        reset_layout.addStretch()
        content_layout.addLayout(reset_layout)

        bottom_bar = QWidget()
        bottom_bar.setObjectName("settings_bottom_bar")
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

        content_layout.addWidget(bottom_bar)
        layout.addWidget(content)

        self.hold_edit.textChanged.connect(self._on_setting_changed)
        self.cooldown_edit.textChanged.connect(self._on_setting_changed)

    def _on_match_changed(self, value):
        self.match_label.setText(f"{value}%")
        self._save_config()

    def _on_setting_changed(self):
        self._save_timer.start(500)

    def _save_config(self):
        try:
            hold_text = self.hold_edit.text()
            cooldown_text = self.cooldown_edit.text()

            if hold_text and cooldown_text:
                hold = float(hold_text)
                cooldown = float(cooldown_text)

                if 0.1 <= hold <= 3.0:
                    self.config["HOLD"] = hold
                if 0.01 <= cooldown <= 2.0:
                    self.config["COOLDOWN"] = cooldown

                self.config["MIN_MATCH"] = self.match_slider.value() / 100.0
                self.config["ALWAYS_ON_TOP"] = self.top_checkbox.isChecked()
                self.config["MINIMIZE_TO_TRAY"] = self.tray_checkbox.isChecked()

                save_config(self.config)

                if self.parent_window:
                    self.parent_window.config = load_config()
                    if self.config["ALWAYS_ON_TOP"]:
                        self.parent_window.setWindowFlags(
                            self.parent_window.windowFlags() | Qt.WindowStaysOnTopHint
                        )
                    else:
                        self.parent_window.setWindowFlags(
                            self.parent_window.windowFlags() & ~Qt.WindowStaysOnTopHint
                        )
                    self.parent_window.show()

        except ValueError:
            pass

    def _auto_save(self):
        if self._is_closing:
            return
        self._save_config()
        self._save_timer.stop()

    def _reset_settings(self):
        reply = QMessageBox.question(
            self,
            "Сброс настроек",
            "Вы уверены, что хотите сбросить все настройки к значениям по умолчанию?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.config.update(DEFAULT_CONFIG)
            self.hold_edit.setText(str(self.config["HOLD"]))
            self.cooldown_edit.setText(str(self.config["COOLDOWN"]))
            self.match_slider.setValue(int(self.config["MIN_MATCH"] * 100))
            self.match_label.setText(f"{self.config['MIN_MATCH'] * 100:.0f}%")
            self.top_checkbox.setChecked(self.config["ALWAYS_ON_TOP"])
            self.tray_checkbox.setChecked(self.config["MINIMIZE_TO_TRAY"])
            self._save_config()

    def closeEvent(self, event):
        if not self._is_closing:
            self._is_closing = True
            self._save_timer.stop()
            self._save_config()

        if self.parent_window:
            self.parent_window.settings_open = False
            if not self.parent_window.app.enabled:
                self.parent_window.settings_btn.setEnabled(True)
                self.parent_window.settings_btn.setToolTip("Настройки")
                self.parent_window.settings_btn.set_color("#6c5ce7")
            else:
                self.parent_window.settings_btn.setEnabled(False)
                self.parent_window.settings_btn.setToolTip("Настройки недоступны во время работы")

        event.accept()
