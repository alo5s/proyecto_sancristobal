"""
layout_login.py — Vista de login (QWidget) - Misma apariencia que login.py original
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit,
    QPushButton
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from config_manager import load_config, save_config

# ── Paleta de colores (fondo claro) ──────────────────────────
BG        = "#f0f0f0"
PANEL     = "#f0f0f0"
BORDER    = "#555555"
ACCENT    = "#2b6de6"  # Azul más oscuro para fondo blanco
ACCENT2   = "#1a5bc4"
TEXT      = "#1a1a1a"
MUTED     = "#555555"
ERROR     = "#e05c5c"
SUCCESS   = "#4ecb8d"

# ── Fuentes ────────────────────────────────────────────
FONT_LOGO   = QFont("Arial", 30)
FONT_TITLE  = QFont("Arial", 20, QFont.Bold)
FONT_INPUT  = QFont("Arial", 14)
FONT_BTN    = QFont("Arial", 14, QFont.Bold)
FONT_TINY   = QFont("Arial", 11)
FONT_MENU   = QFont("Arial", 12)

# ── QSS Estilos ────────────────────────────────────────────
QSS = f"""
QWidget {{
    background-color: {BG};
    color: {TEXT};
    font-family: "Arial";
}}

QLineEdit {{
    background-color: {PANEL};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 10px 12px;
    color: {TEXT};
    font-size: 14px;
}}

QLineEdit:focus {{
    border: 1px solid {ACCENT};
}}

QLineEdit::placeholder {{
    color: {MUTED};
}}

QPushButton#primary {{
    background-color: {ACCENT};
    border: none;
    border-radius: 8px;
    padding: 12px 24px;
    color: {BG};
    font-family: "Arial";
    font-size: 14px;
    font-weight: bold;
}}

QPushButton#primary:hover {{
    background-color: {ACCENT2};
}}

QPushButton#primary:pressed {{
    background-color: #3a6fd8;
}}

QPushButton#primary:disabled {{
    background-color: {MUTED};
    color: #333333;
}}

QLabel#logo {{
    color: {ACCENT};
    font-size: 30px;
}}

QLabel#title {{
    color: {TEXT};
    font-size: 20px;
    font-weight: bold;
}}

QLabel#subtitle {{
    color: {MUTED};
    font-size: 11px;
}}

QLabel#status {{
    color: {MUTED};
    font-size: 11px;
}}

QPushButton#togglePass {{
    background-color: transparent;
    border: none;
    color: {ACCENT};
    font-family: "Arial";
    font-size: 11px;
    text-align: center;
    padding: 4px 0px;
}}

QPushButton#togglePass:hover {{
    text-decoration: underline;
}}
"""


class LoginView(QWidget):
    login_requested = Signal(str, str)

    def __init__(self):
        super().__init__()
        self.config_data = load_config()
        self._build_ui()

    def _build_ui(self):
        self.setStyleSheet(QSS)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 20, 40, 20)
        layout.setSpacing(12)
        layout.setAlignment(Qt.AlignCenter)

        # Logo
        logo = QLabel("◈")
        logo.setObjectName("logo")
        logo.setFont(FONT_LOGO)
        logo.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo)

        # Título
        title = QLabel("AUTOBOT")
        title.setObjectName("title")
        title.setFont(FONT_TITLE)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        layout.addSpacing(24)

        # Usuario
        self.entry_user = QLineEdit()
        self.entry_user.setPlaceholderText("usuario")
        self.entry_user.setFont(FONT_INPUT)
        self.entry_user.setText(self.config_data.get("username", ""))
        layout.addWidget(self.entry_user)

        # Contraseña
        self.entry_pass = QLineEdit()
        self.entry_pass.setPlaceholderText("contraseña")
        self.entry_pass.setEchoMode(QLineEdit.Password)
        self.entry_pass.setFont(FONT_INPUT)
        self.entry_pass.setText(self.config_data.get("password", ""))
        layout.addWidget(self.entry_pass)

        # Texto para mostrar/ocultar contraseña
        self.btn_toggle_pass = QPushButton("Ver contraseña")
        self.btn_toggle_pass.setObjectName("togglePass")
        self.btn_toggle_pass.setFlat(True)
        self.btn_toggle_pass.setCursor(Qt.PointingHandCursor)
        self.btn_toggle_pass.clicked.connect(self._toggle_password_visibility)
        layout.addWidget(self.btn_toggle_pass, 0, Qt.AlignCenter)

        layout.addSpacing(20)

        # Botón Entrar
        self.btn_login = QPushButton("ENTRAR  →")
        self.btn_login.setObjectName("primary")
        self.btn_login.setFont(FONT_BTN)
        self.btn_login.clicked.connect(self._handle_login)
        layout.addWidget(self.btn_login)

        # Status
        self.lbl_status = QLabel("")
        self.lbl_status.setObjectName("status")
        self.lbl_status.setFont(FONT_TINY)
        self.lbl_status.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.lbl_status)

        layout.addStretch()

        # Footer
        footer = QLabel("v1.0 · playwright")
        footer.setObjectName("subtitle")
        footer.setFont(FONT_TINY)
        footer.setAlignment(Qt.AlignCenter)
        layout.addWidget(footer)

        # Conectar Enter
        self.entry_user.returnPressed.connect(self._handle_login)
        self.entry_pass.returnPressed.connect(self._handle_login)
        self.entry_user.setFocus()

    def _handle_login(self):
        user = self.entry_user.text().strip()
        pwd = self.entry_pass.text().strip()

        if not user or not pwd:
            self._set_status("completá los campos", ERROR)
            return

        # Guardar credenciales en config
        self.config_data["username"] = user
        self.config_data["password"] = pwd
        save_config(self.config_data)

        self.btn_login.setEnabled(False)
        self.btn_login.setText("conectando...")
        self._set_status("iniciando navegador...", MUTED)
        self.login_requested.emit(user, pwd)

    def _set_status(self, msg, color):
        self.lbl_status.setText(msg)
        # Solo cambiar color temporalmente, sin romper QSS
        if color == ERROR:
            self.lbl_status.setStyleSheet(f"color: {ERROR}; font-family: Arial; font-size: 11px;")
        elif color == SUCCESS:
            self.lbl_status.setStyleSheet(f"color: {SUCCESS}; font-family: Arial; font-size: 11px;")
        else:
            # MUTED - usar QSS por defecto
            self.lbl_status.setStyleSheet("")

    def reset(self):
        self.btn_login.setEnabled(True)
        self.btn_login.setText("ENTRAR  →")
        self.lbl_status.setText("")
        # Restaurar estilo QSS
        self.lbl_status.setStyleSheet("")

    def _toggle_password_visibility(self):
        """Alterna entre mostrar y ocultar la contraseña"""
        if self.entry_pass.echoMode() == QLineEdit.Password:
            self.entry_pass.setEchoMode(QLineEdit.Normal)
            self.btn_toggle_pass.setText("Ocultar contraseña")
        else:
            self.entry_pass.setEchoMode(QLineEdit.Password)
            self.btn_toggle_pass.setText("Ver contraseña")
