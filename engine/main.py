import os
import sys


def get_application_root() -> str:
    if hasattr(sys, 'frozen'):
        app_root = os.path.dirname(sys.executable)
    else:
        app_root = os.path.dirname(os.path.abspath(__file__))
    return app_root


application_root = get_application_root()