"""
config_manager.py — Gestión de configuración (config.json)
"""

import json
import os

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

DEFAULT_CONFIG = {
    "username": "",
    "password": "",
    "login_url": "https://productores.sancristobal.com.ar",
    "headless": False,
    "schedule": {
        "enabled": False,
        "days": [],  # [0,1,2,3,4,5,6] where 0=Monday
        "time": "08:00"
    }
}


def load_config():
    """Carga la configuración desde config.json. Si no existe, crea uno por defecto."""
    if not os.path.exists(CONFIG_FILE):
        save_config(DEFAULT_CONFIG)

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            config = json.load(f)

        # Asegurar que todas las claves existan
        for key, value in DEFAULT_CONFIG.items():
            if key not in config:
                config[key] = value

        return config

    except Exception as e:
        print(f"Error leyendo config.json: {e}")
        return DEFAULT_CONFIG.copy()


def save_config(data: dict):
    """Guarda la configuración en config.json"""
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Error guardando config.json: {e}")


def reset_config():
    """Elimina el archivo de configuración"""
    if os.path.exists(CONFIG_FILE):
        os.remove(CONFIG_FILE)
