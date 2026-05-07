"""
ScheduleDialog - Diálogo para configurar auto-inicio
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QCheckBox, 
    QTimeEdit, QPushButton, QLabel, QGroupBox, QMessageBox, QSpacerItem, QSizePolicy
)
from PySide6.QtCore import Qt, QTime
import json
from pathlib import Path


DAY_NAMES = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]


class ScheduleDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Programación - Auto Inicio")
        self.setFixedSize(400, 380)
        self.config_file = Path("config.json")
        self.schedule = self._load_schedule()
        self._build_ui()
    
    def _load_schedule(self):
        """Carga configuración de horario"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                return config.get('schedule', {
                    'enabled': False,
                    'days': [],
                    'time': '08:00'
                })
        except Exception as e:
            print(f"Error cargando schedule: {e}")
        
        return {'enabled': False, 'days': [], 'time': '08:00'}
    
    def _save_schedule(self):
        """Guarda configuración de horario"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
            else:
                config = {}
            
            config['schedule'] = {
                'enabled': self.enabled_check.isChecked(),
                'days': [i for i, check in enumerate(self.day_checks) if check.isChecked()],
                'time': self.time_edit.time().toString("HH:mm")
            }
            
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            self.schedule = config['schedule']
            return True
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar: {e}")
            return False
    
    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Título
        title = QLabel("Configurar Auto-Inicio")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)
        
        # Checkbox habilitar
        self.enabled_check = QCheckBox("Habilitar auto-inicio (Cron)")
        self.enabled_check.setChecked(self.schedule['enabled'])
        layout.addWidget(self.enabled_check)
        
        # Días de la semana
        days_group = QGroupBox("Días de la semana")
        days_layout = QVBoxLayout(days_group)
        self.day_checks = []
        for i, day in enumerate(DAY_NAMES):
            check = QCheckBox(day)
            check.setChecked(i in self.schedule.get('days', []))
            self.day_checks.append(check)
            days_layout.addWidget(check)
        layout.addWidget(days_group)
        
        # Hora
        time_layout = QHBoxLayout()
        time_layout.addWidget(QLabel("Hora:"))
        self.time_edit = QTimeEdit()
        self.time_edit.setTime(QTime.fromString(self.schedule.get('time', '08:00'), "HH:mm"))
        self.time_edit.setDisplayFormat("HH:mm")
        time_layout.addWidget(self.time_edit)
        time_layout.addStretch()
        layout.addLayout(time_layout)
        
        # Spacer
        layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        # Botones
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Guardar")
        save_btn.setStyleSheet("background-color: #2b6de6; color: white; padding: 8px 20px; border-radius: 4px;")
        save_btn.clicked.connect(self._save_and_apply)
        
        cancel_btn = QPushButton("Cancelar")
        cancel_btn.setStyleSheet("padding: 8px 20px; border-radius: 4px;")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
    
    def _save_and_apply(self):
        """Guarda y aplica configuración"""
        if self._save_schedule():
            self._apply_cron()
            QMessageBox.information(self, "Éxito", "Configuración guardada correctamente")
            self.accept()
    
    def _apply_cron(self):
        """Aplica configuración a crontab"""
        if not self.schedule['enabled'] or not self.schedule['days']:
            # Deshabilitar: eliminar de crontab
            from utils.cron_helper import remove_from_crontab
            remove_from_crontab()
            print("[Schedule] Auto-inicio deshabilitado")
            return
        
        # Importar helper
        from utils.cron_helper import create_schedule_entry, add_to_crontab
        
        # Crear entrada
        cron_entry = create_schedule_entry(
            days=self.schedule['days'],
            time_str=self.schedule['time']
        )
        
        # Agregar a crontab
        if add_to_crontab(cron_entry):
            print(f"[Schedule] ✓ Configuración aplicada:")
            print(f"  Días: {', '.join(DAY_NAMES[d] for d in self.schedule['days'])}")
            print(f"  Hora: {self.schedule['time']}")
        else:
            print("[Schedule] ✗ Error aplicando configuración")
