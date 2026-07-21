# Free
import sys
from os import path


def resource_path(relative_path):
    if getattr(sys, 'frozen', False):
        base_path = path.dirname(sys.executable)
    else:
        base_path = path.abspath(".")
    return path.join(base_path, relative_path)
