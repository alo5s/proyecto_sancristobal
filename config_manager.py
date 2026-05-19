"""
config_manager.py — Configuración via QSettings (PySide6 cross-platform)
"""

from PySide6.QtCore import QSettings

ORG_NAME = "SanCristobal"
APP_NAME = "AUTOBOT"


def get_settings():
    return QSettings(ORG_NAME, APP_NAME)


def reset_config():
    settings = get_settings()
    settings.clear()
