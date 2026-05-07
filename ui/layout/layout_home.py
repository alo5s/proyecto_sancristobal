"""
layout_home.py — Vista principal (QWidget)
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont

from config_manager import load_config, save_config
from bot.browser_manager import BrowserManager

# ── Paleta de colores (fondo claro) ──────────────────────────────
BG        = "#f0f0f0"
PANEL     = "#f0f0f0"
BORDER    = "#555555"
ACCENT    = "#2b6de6"  # Azul más oscuro para fondo blanco
ACCENT2   = "#1a5bc4"
TEXT      = "#1a1a1a"
MUTED     = "#555555"
ERROR     = "#e05c5c"
SUCCESS   = "#4ecb8d"

# ── Fuentes ────────────────────────────────────────
FONT_TITLE  = QFont("Courier New", 16, QFont.Bold)
FONT_BIGBTN = QFont("Courier New", 18, QFont.Bold)
FONT_BTN    = QFont("Courier New", 12)
FONT_TINY   = QFont("Courier New", 10)


class HomeView(QWidget):
    logout_requested = Signal()
    start_requested = Signal(dict)
    pause_requested = Signal()
    resume_requested = Signal()
    stop_requested = Signal()

    def __init__(self, user):
        super().__init__()
        self.user = user
        self.is_compact = False
        self.config_data = load_config()
        self.logs = []
        self._build_ui()

    def _build_ui(self):
        # QSS estilos
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {BG};
                color: {TEXT};
                font-family: "Courier New";
            }}
            QPushButton#primary {{
                background-color: {ACCENT};
                border: none;
                border-radius: 12px;
                padding: 24px 80px;
                color: {BG};
                font-family: "Courier New";
                font-size: 18px;
                font-weight: bold;
            }}
            QPushButton#primary:hover {{
                background-color: {ACCENT2};
            }}
            QPushButton#primary:pressed {{
                background-color: #3a6fd8;
            }}
            QPushButton#secondary {{
                background-color: {PANEL};
                border: 1px solid {BORDER};
                border-radius: 8px;
                padding: 10px 20px;
                color: {TEXT};
                font-size: 12px;
            }}
            QPushButton#secondary:hover {{
                background-color: {BORDER};
            }}
            QLabel#title {{
                color: {TEXT};
                font-size: 16px;
                font-weight: bold;
            }}
            QLabel#status {{
                color: {MUTED};
                font-size: 10px;
            }}
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 30, 40, 20)
        main_layout.setSpacing(20)

        # Header
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)

        title = QLabel("AUTOBOT — Cobranza")
        title.setObjectName("title")
        title.setFont(FONT_TITLE)
        header_layout.addWidget(title)

        header_layout.addStretch()

        self.status_label = QLabel("● Navegador activo")
        self.status_label.setObjectName("status")
        self.status_label.setFont(FONT_TINY)
        header_layout.addWidget(self.status_label)

        main_layout.addWidget(header)

        main_layout.addStretch()

        # Botón principal
        btn_layout = QHBoxLayout()
        btn_layout.setAlignment(Qt.AlignCenter)

        self.btn_ejecutar = QPushButton("▶  EJECUTAR COBRANZA")
        self.btn_ejecutar.setObjectName("primary")
        self.btn_ejecutar.setFont(FONT_BIGBTN)
        self.btn_ejecutar.clicked.connect(self._ejecutar_cobranza)
        btn_layout.addWidget(self.btn_ejecutar)

        main_layout.addLayout(btn_layout)
        main_layout.addStretch()

        # Botones de acceso rápido
        quick_layout = QHBoxLayout()
        quick_layout.setAlignment(Qt.AlignCenter)
        quick_layout.setSpacing(12)

        btn_exit = QPushButton("Salir")
        btn_exit.setObjectName("secondary")
        btn_exit.setFont(FONT_BTN)
        btn_exit.clicked.connect(self._exit_app)
        quick_layout.addWidget(btn_exit)

        btn_reportes = QPushButton("📊  Reportes")
        btn_reportes.setObjectName("secondary")
        btn_reportes.setFont(FONT_BTN)
        btn_reportes.clicked.connect(self.show_reportes)
        quick_layout.addWidget(btn_reportes)

        btn_prog = QPushButton("🕐  Programación")
        btn_prog.setObjectName("secondary")
        btn_prog.setFont(FONT_BTN)
        btn_prog.clicked.connect(self.show_programacion)
        quick_layout.addWidget(btn_prog)

        main_layout.addLayout(quick_layout)

        # Logs area
        self.log_label = QLabel("Listo")
        self.log_label.setObjectName("status")
        self.log_label.setFont(FONT_TINY)
        main_layout.addWidget(self.log_label)

    def _ejecutar_cobranza(self):
        self.btn_ejecutar.setEnabled(False)
        self.btn_ejecutar.setText("EJECUTANDO...")
        self.log("Ejecutando proceso de cobranza...")

        # Emitir señal para que el controller inicie la automatización
        data = {
            "ubicaciones": [],
            "aseguradoras": [],
            "polizas_ubicacion": "",
            "pago_ubicacion": "",
            "excel_ubicacion": "",
            "guardado_ubicacion": ""
        }
        self.start_requested.emit(data)

    def log(self, msg):
        self.logs.append(msg)
        self.log_label.setText(msg)

    def show_bot_error(self, msg):
        self.log(f"ERROR: {msg}")

    def reset_bot_ui(self):
        self.btn_ejecutar.setEnabled(True)
        self.btn_ejecutar.setText("▶  EJECUTAR COBRANZA")

    def show_poliza_alert(self, msg):
        self.log(msg)

    def show_persona_no_encontrada(self, dni, poliza, asegurado):
        self.log(f"Persona no encontrada: DNI {dni}, Póliza {poliza}")
    
    def _exit_app(self):
        """Cierra toda la aplicación"""
        from PySide6.QtWidgets import QMessageBox
        reply = QMessageBox.question(
            self, "Salir",
            "¿Estás seguro de salir del programa?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            from PySide6.QtWidgets import QApplication
            QApplication.quit()

    def reload_custom_data(self):
        pass  # Implementar si es necesario

    def show_reportes(self):
        from ui.dialogs.reportes_dialog import ReportesDialog
        dialog = ReportesDialog(self)
        dialog.exec()
    
    def show_programacion(self):
        from ui.dialogs.programacion_dialog import ProgramacionDialog
        dialog = ProgramacionDialog(self)
        dialog.exec()
