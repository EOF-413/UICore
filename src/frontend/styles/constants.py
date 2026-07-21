# Free
from os import path


def load_stylesheet(filename):
    styles_dir = path.dirname(path.abspath(__file__))
    lpath = path.join(styles_dir, filename)
    try:
        with open(lpath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return ""
