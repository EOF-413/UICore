# Free
from sys import argv, exit

# Download
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

# Local
from src.core import App
from src.frontend import MainWindow


if __name__ == '__main__':
    QApplication.setAttribute(Qt.AA_DisableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, False)

    app = QApplication(argv)

    auto_app = App()
    window = MainWindow(auto_app)
    auto_app.gui = window
    window.log_info("Нажмите F9 для старта/остановки")
    window.show()

    exit_code = app.exec_()
    auto_app.cleanup()
    exit(exit_code)
