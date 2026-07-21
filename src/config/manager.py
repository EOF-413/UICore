# Free
from os import path, getenv, makedirs
from json import load, dump, JSONDecodeError

# Local
from .constants import APP_NAME, DEFAULT_CONFIG


def get_config_path():
    app_data = getenv('APPDATA')
    config_dir = path.join(app_data, 'EOF-413', APP_NAME)
    if not path.exists(config_dir):
        makedirs(config_dir)
    return path.join(config_dir, 'config.json')


def load_config():
    config_path = get_config_path()
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = load(f)
            for key, val in DEFAULT_CONFIG.items():
                if key not in config:
                    config[key] = val
            return config
    except (FileNotFoundError, JSONDecodeError):
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()


def save_config(data):
    config_path = get_config_path()
    with open(config_path, 'w', encoding='utf-8') as f:
        dump(data, f, indent=4, ensure_ascii=False)
