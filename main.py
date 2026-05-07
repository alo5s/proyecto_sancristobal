"""
main.py — Punto de entrada de la aplicación
"""

import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QMenuBar, QMenu, QMessageBox, QWidget
from PySide6.QtGui import QFont, QAction

# Importar el controller
from controller.app_controller import AppController

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

# ── Fuentes ────────────────────────────────────
FONT_MENU   = QFont("Courier New", 11)


class AppMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AUTOBOT")
        self.setFixedSize(360, 420)

        # Configurar QSS global
        self.setStyleSheet(self._get_global_qss())

        # Crear menú único
        self._create_menu()

        # Controller
        self.controller = AppController(self)

    def _create_menu(self):
        menubar = self.menuBar()
        menu = QMenu("Menú", self)
        menu.setFont(FONT_MENU)

        # Grupo 1: Configuración
        config_action = QAction("Configuración", self)
        config_action.triggered.connect(self.show_config)
        menu.addAction(config_action)

        menu.addSeparator()

        # Grupo 2: Visualización
        self.toggle_browser_action = QAction("Mostrar navegador", self)
        self.toggle_browser_action.triggered.connect(self.toggle_browser)
        menu.addAction(self.toggle_browser_action)

        toggle_logs_action = QAction("Mostrar/Ocultar logs", self)
        toggle_logs_action.triggered.connect(self.toggle_logs)
        menu.addAction(toggle_logs_action)

        toggle_compact_action = QAction("Modo compacto", self)
        toggle_compact_action.triggered.connect(self.toggle_compact_mode)
        menu.addAction(toggle_compact_action)

        menu.addSeparator()

        # Grupo 3: Información
        docs_action = QAction("Documentación", self)
        docs_action.triggered.connect(self.show_documentation)
        menu.addAction(docs_action)

        about_action = QAction("Acerca de", self)
        about_action.triggered.connect(self.show_about)
        menu.addAction(about_action)

        menubar.addMenu(menu)

    def _get_global_qss(self):
        return f"""
            QMainWindow {{
                background-color: {BG};
            }}

            QMenuBar {{
                background-color: {BG};
                border-bottom: 1px solid {BORDER};
                padding: 2px;
            }}

            QMenuBar::item {{
                padding: 4px 10px;
                border-radius: 4px;
                color: {MUTED};
                font-size: 11px;
            }}

            QMenuBar::item:selected {{
                background-color: {PANEL};
                color: {TEXT};
            }}

            QMenu {{
                background-color: {PANEL};
                border: 1px solid {BORDER};
                padding: 4px;
            }}

            QMenu::item {{
                padding: 6px 20px;
                color: {TEXT};
                font-size: 11px;
            }}

            QMenu::item:selected {{
                background-color: {BORDER};
            }}

            QMenu::separator {{
                height: 1px;
                background-color: {BORDER};
                margin: 4px 0;
            }}
        """

    def _get_browser_text(self):
        from config_manager import load_config
        config_data = load_config()
        return "Mostrar navegador" if config_data.get("headless", True) else "Ocultar navegador"

    def toggle_browser(self):
        from config_manager import load_config, save_config
        config_data = load_config()
        config_data["headless"] = not config_data.get("headless", True)
        save_config(config_data)
        self.toggle_browser_action.setText(self._get_browser_text())
        QMessageBox.information(self, "Información", "Reiniciá la app para aplicar cambios")

    def toggle_logs(self):
        QMessageBox.information(self, "Logs", "Función de logs en desarrollo")

    def toggle_compact_mode(self):
        QMessageBox.information(self, "Modo compacto", "Función en desarrollo")

    def show_config(self):
        from ui.dialogs.schedule_dialog import ScheduleDialog
        dialog = ScheduleDialog(self)
        dialog.exec()

    def show_documentation(self):
        QMessageBox.information(self, "Documentación", "Documentación disponible en: https://github.com/usuario/autobot")

    def show_about(self):
        QMessageBox.about(self, "Acerca de AUTOBOT",
            "AUTOBOT v1.0\n\n"
            "Automatización de procesos\n"
            "Powered by Playwright + Python"
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AppMainWindow()
    window.show()
    sys.exit(app.exec())
