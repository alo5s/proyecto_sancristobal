"""
license_manager.py — Gestión de licencias
"""

import hmac
import hashlib
import base64
import uuid
from datetime import date, timedelta
from config_manager import get_settings

SECRET = b"SanCristobalLic2026"

def get_machine_id() -> str:
    mac = uuid.getnode()
    return hashlib.sha256(str(mac).encode()).hexdigest()[:12].upper()

def get_license_info() -> dict:
    s = get_settings()
    first_run = s.value("license_first_run", True, type=bool)
    if first_run:
        expire = date.today() + timedelta(days=1)
        s.setValue("license_first_run", False)
        s.setValue("license_expire", expire.isoformat())
        s.sync()

    expire_str = s.value("license_expire", "")
    try:
        expire = date.fromisoformat(expire_str) if expire_str else date.today()
    except ValueError:
        expire = date.today()

    return {
        "expire_date": expire.isoformat(),
        "days_left": (expire - date.today()).days,
        "is_valid": expire >= date.today(),
        "machine_id": get_machine_id(),
        "has_license": bool(s.value("license_key", "")),
    }

def validate_and_store_key(key: str) -> tuple[bool, str]:
    try:
        decoded = base64.b64decode(key.encode()).decode()
        parts = decoded.rsplit(":", 2)
        if len(parts) != 3:
            return False, "Formato de clave inválido"
        expire_date_str, machine_id, sig = parts
        # Verificar firma
        msg = f"{expire_date_str}:{machine_id}"
        expected = hmac.new(SECRET, msg.encode(), hashlib.sha256).hexdigest()[:16]
        if not hmac.compare_digest(sig, expected):
            return False, "Clave inválida"
        # Verificar vigencia
        expire = date.fromisoformat(expire_date_str)
        if expire < date.today():
            return False, "Clave vencida"
        # Guardar
        s = get_settings()
        s.setValue("license_expire", expire_date_str)
        s.setValue("license_key", key)
        s.sync()
        return True, f"Licencia renovada hasta {expire_date_str}"
    except Exception as e:
        return False, f"Error: {e}"
