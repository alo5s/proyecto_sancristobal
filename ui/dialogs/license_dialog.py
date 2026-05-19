"""
LicenseDialog - Muestra estado de licencia y permite renovar
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QGroupBox, QLineEdit, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from utils.license_manager import get_license_info, validate_and_store_key

GREEN = "#4ecb8d"
RED = "#e05c5c"
MUTED = "#555555"
ACCENT = "#2b6de6"


class LicenseDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Licencias")
        self.setFixedSize(420, 340)
        self._build_ui()
        self._load_status()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        title = QLabel("Licencia de Uso")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)

        # Estado
        self.status_group = QGroupBox("Estado")
        status_layout = QVBoxLayout(self.status_group)
        self.lbl_machine = QLabel()
        self.lbl_expire = QLabel()
        self.lbl_days = QLabel()
        for lbl in (self.lbl_machine, self.lbl_expire, self.lbl_days):
            lbl.setStyleSheet(f"font-size: 13px; color: {MUTED};")
            status_layout.addWidget(lbl)
        layout.addWidget(self.status_group)

        # Renovar
        renew_group = QGroupBox("Renovar Licencia")
        renew_layout = QVBoxLayout(renew_group)

        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText("Pegue la nueva clave de licencia aquí")
        self.key_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #555555;
                border-radius: 6px;
                font-size: 13px;
            }
        """)
        renew_layout.addWidget(self.key_input)

        btn_renew = QPushButton("Renovar")
        btn_renew.setStyleSheet(f"""
            QPushButton {{
                background-color: {ACCENT};
                color: white;
                padding: 10px 20px;
                border-radius: 6px;
                font-size: 13px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #1f55c0;
            }}
        """)
        btn_renew.clicked.connect(self._renew)
        renew_layout.addWidget(btn_renew)

        layout.addWidget(renew_group)

        # Cerrar
        close_btn = QPushButton("Cerrar")
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {RED};
                color: white;
                padding: 10px 20px;
                border-radius: 6px;
                font-size: 13px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #c04c4c;
            }}
        """)
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)

    def _load_status(self):
        info = get_license_info()
        self.lbl_machine.setText(f"🔑 Machine ID: {info['machine_id']}")
        self.lbl_expire.setText(f"📅 Vence: {info['expire_date']}")
        color = GREEN if info["is_valid"] else RED
        status_text = "Vigente" if info["is_valid"] else "VENCIDA"
        self.lbl_days.setText(
            f"{'✅' if info['is_valid'] else '❌'} Estado: {status_text} "
            f"({info['days_left']} días restantes)"
        )
        self.lbl_days.setStyleSheet(
            f"font-size: 13px; font-weight: bold; color: {color};"
        )

    def _renew(self):
        key = self.key_input.text().strip()
        if not key:
            QMessageBox.warning(self, "Renovar", "Ingrese una clave de licencia")
            return
        ok, msg = validate_and_store_key(key)
        if ok:
            QMessageBox.information(self, "Renovar", msg)
            self._load_status()
            self.key_input.clear()
            parent = self.parent()
            if parent and hasattr(parent, "check_license_status"):
                parent.check_license_status()
        else:
            QMessageBox.critical(self, "Error", msg)
