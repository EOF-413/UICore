from time import sleep
from threading import Thread

from pynput.keyboard import Listener, Key
from src.config import load_config
from src.frontend import LogWidget


class App:
    def __init__(self):
        self.enabled = False
        self.running = True
        self.loop_thread = None
        self.gui = None
        self.listener = None
        self.gui = LogWidget

    def loop(self):
        while self.running:
            config = load_config()
            if not self.enabled:
                sleep(0.05)
                continue

            self.gui.log(f"Sleep {config['HOLD']}", 'warning')
            sleep(config['COOLDOWN'])

    def on_press(self, key):
        try:
            if key == Key.f9:
                if self.gui:
                    self.gui._on_toggle()
        except Exception:
            pass

    def start_listener(self):
        if self.listener is None or not self.listener.running:
            self.listener = Listener(on_press=self.on_press)
            self.listener.daemon = True
            self.listener.start()

    def start(self):
        if not self.enabled:
            self.enabled = True
            if self.gui:
                self.gui.log_info("Запущено")
                self.gui.update_status()
            if not self.loop_thread or not self.loop_thread.is_alive():
                self.loop_thread = Thread(target=self.loop, daemon=True)
                self.loop_thread.start()

    def stop(self):
        self.enabled = False
        if self.gui:
            self.gui.log_info("Остановлено")
            self.gui.update_status()

    def toggle(self):
        if self.enabled:
            self.stop()
        else:
            self.start()

    def cleanup(self):
        self.running = False
        self.enabled = False
        if self.listener and self.listener.running:
            self.listener.stop()
