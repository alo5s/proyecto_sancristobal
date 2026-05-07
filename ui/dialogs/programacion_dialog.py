"""
ProgramacionDialog - Configuración de notificaciones y vencimientos
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QCheckBox, 
    QPushButton, QLabel, QGroupBox, QSpacerItem, QSizePolicy
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
import json
from pathlib import Path


class ProgramacionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Programación")
        self.setFixedSize(450, 400)
        self.config_file = Path("config.json")
        self.config = self._load_config()
        self._build_ui()
    
    def _load_config(self):
        """Carga configuración"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error cargando config: {e}")
        return {}
    
    def _save_config(self):
        """Guarda configuración"""
        try:
            # Asegurar que todas las claves existan
            defaults = {
                'notif_correo': True,
                'notif_whapp': True,
                'venc_7dias': True,
                'venc_8dias': False
            }
            for key, value in defaults.items():
                if key not in self.config:
                    self.config[key] = value
            
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    existing = json.load(f)
                existing.update(self.config)
                self.config = existing
            
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            return True
        except Exception as e:
            print(f"Error guardando config: {e}")
            return False
    
    def _build_ui(self):
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
        self.correo_check.setChecked(self.config.get('notif_correo', True))
        notif_layout.addWidget(self.correo_check)
        
        self.whapp_check = QCheckBox("Enviar WhatsApp")
        self.whapp_check.setChecked(self.config.get('notif_whapp', True))
        notif_layout.addWidget(self.whapp_check)
        
        layout.addWidget(notif_group)
        
        # ========== SECCIÓN 2: VENCIMIENTOS ==========
        venc_group = QGroupBox("Vencimientos (etapa_2)")
        venc_layout = QVBoxLayout(venc_group)
        
        self.dias_7_check = QCheckBox("Procesar 7 días")
        self.dias_7_check.setChecked(self.config.get('venc_7dias', True))
        venc_layout.addWidget(self.dias_7_check)
        
        self.dias_8_check = QCheckBox("Procesar 8 a 15 días")
        self.dias_8_check.setChecked(self.config.get('venc_8dias', False))
        venc_layout.addWidget(self.dias_8_check)
        
        layout.addWidget(venc_group)
        
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
        """Guarda configuración y cierra"""
        self.config['notif_correo'] = self.correo_check.isChecked()
        self.config['notif_whapp'] = self.whapp_check.isChecked()
        self.config['venc_7dias'] = self.dias_7_check.isChecked()
        self.config['venc_8dias'] = self.dias_8_check.isChecked()
        
        if self._save_config():
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.information(self, "Éxito", "Configuración guardada correctamente")
            self.accept()
