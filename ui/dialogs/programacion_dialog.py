"""
ProgramacionDialog - Configuración de notificaciones y vencimientos
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QCheckBox, 
    QPushButton, QLabel, QGroupBox, QSpacerItem, QSizePolicy
)
from PySide6.QtCore import Qt
from config_manager import get_settings


class ProgramacionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Programación")
        self.setFixedSize(450, 480)
        self._build_ui()

    def _build_ui(self):
        s = get_settings()

        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        title = QLabel("Configuración de Ejecución")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)

        # ========== SECCIÓN 1: NOTIFICACIONES ==========
        notif_group = QGroupBox("Notificaciones (_compartir)")
        notif_layout = QVBoxLayout(notif_group)

        self.correo_check = QCheckBox("Enviar Correo")
        self.correo_check.setChecked(s.value("notif_correo", True, type=bool))
        notif_layout.addWidget(self.correo_check)

        self.whapp_check = QCheckBox("Enviar WhatsApp")
        self.whapp_check.setChecked(s.value("notif_whapp", True, type=bool))
        notif_layout.addWidget(self.whapp_check)

        layout.addWidget(notif_group)

        # ========== SECCIÓN 2: VENCIMIENTOS ==========
        venc_group = QGroupBox("Vencimientos (etapa_2)")
        venc_layout = QVBoxLayout(venc_group)

        self.dias_7_check = QCheckBox("Procesar 7 días")
        self.dias_7_check.setChecked(s.value("venc_7dias", True, type=bool))
        venc_layout.addWidget(self.dias_7_check)

        self.dias_8_check = QCheckBox("Procesar 8 a 15 días")
        self.dias_8_check.setChecked(s.value("venc_8dias", False, type=bool))
        venc_layout.addWidget(self.dias_8_check)

        layout.addWidget(venc_group)

        # ========== SECCIÓN 3: MODALIDADES DE PAGO ==========
        mod_group = QGroupBox("Modalidades de pago (etapa_1)")
        mod_layout = QVBoxLayout(mod_group)

        MODALIDADES = ["EFECTIVO", "DÉBITO DIRECTO", "TARJETA DE CRÉDITO"]
        self.modalidad_checks = []
        selected = s.value("modalidades_pago", [], type=list)
        for mod in MODALIDADES:
            check = QCheckBox(mod)
            check.setChecked(mod in selected)
            self.modalidad_checks.append(check)
            mod_layout.addWidget(check)

        layout.addWidget(mod_group)

        # Spacer
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # ========== BOTÓN GUARDAR ==========
        save_btn = QPushButton("Guardar Configuración")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #2b6de6;
                color: white;
                padding: 10px 20px;
                border-radius: 6px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1a5bc4;
            }
        """)
        save_btn.clicked.connect(self._save_and_close)
        layout.addWidget(save_btn)

    def _save_and_close(self):
        s = get_settings()
        s.setValue("notif_correo", self.correo_check.isChecked())
        s.setValue("notif_whapp", self.whapp_check.isChecked())
        s.setValue("venc_7dias", self.dias_7_check.isChecked())
        s.setValue("venc_8dias", self.dias_8_check.isChecked())
        s.setValue("modalidades_pago", [
            check.text() for check in self.modalidad_checks if check.isChecked()
        ])
        s.sync()

        from PySide6.QtWidgets import QMessageBox
        QMessageBox.information(self, "Éxito", "Configuración guardada correctamente")
        self.accept()
