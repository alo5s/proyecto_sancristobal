"""
ScheduleDialog - Diálogo para configurar auto-inicio
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QCheckBox,
    QTimeEdit, QPushButton, QLabel, QGroupBox, QMessageBox, QSpacerItem, QSizePolicy
)
from PySide6.QtCore import Qt, QTime
from config_manager import get_settings


DAY_NAMES = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]


class ScheduleDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Programación - Auto Inicio")
        self.setFixedSize(400, 380)
        self._build_ui()

    def _build_ui(self):
        s = get_settings()
        s.beginGroup("schedule")
        enabled = s.value("enabled", False, type=bool)
        days = s.value("days", [], type=list)
        time_str = s.value("time", "08:00")
        s.endGroup()

        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        title = QLabel("Configurar Auto-Inicio")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)

        self.enabled_check = QCheckBox("Habilitar auto-inicio (Cron)")
        self.enabled_check.setChecked(enabled)
        layout.addWidget(self.enabled_check)

        days_group = QGroupBox("Días de la semana")
        days_layout = QVBoxLayout(days_group)
        self.day_checks = []
        for i, day in enumerate(DAY_NAMES):
            check = QCheckBox(day)
            check.setChecked(i in days)
            self.day_checks.append(check)
            days_layout.addWidget(check)
        layout.addWidget(days_group)

        time_layout = QHBoxLayout()
        time_layout.addWidget(QLabel("Hora:"))
        self.time_edit = QTimeEdit()
        self.time_edit.setTime(QTime.fromString(time_str, "HH:mm"))
        self.time_edit.setDisplayFormat("HH:mm")
        time_layout.addWidget(self.time_edit)
        time_layout.addStretch()
        layout.addLayout(time_layout)

        layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))

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
        s = get_settings()
        s.beginGroup("schedule")
        s.setValue("enabled", self.enabled_check.isChecked())
        s.setValue("days", [i for i, check in enumerate(self.day_checks) if check.isChecked()])
        s.setValue("time", self.time_edit.time().toString("HH:mm"))
        s.endGroup()
        s.sync()

        self._apply_cron()
        QMessageBox.information(self, "Éxito", "Configuración guardada correctamente")
        self.accept()

    def _apply_cron(self):
        s = get_settings()
        s.beginGroup("schedule")
        enabled = s.value("enabled", False, type=bool)
        days = s.value("days", [], type=list)
        time_str = s.value("time", "08:00")
        s.endGroup()

        if not enabled or not days:
            from utils.cron_helper import remove_from_crontab
            remove_from_crontab()
            print("[Schedule] Auto-inicio deshabilitado")
            return

        from utils.cron_helper import create_schedule_entry, add_to_crontab
        cron_entry = create_schedule_entry(days=days, time_str=time_str)

        if add_to_crontab(cron_entry):
            print(f"[Schedule] ✓ Configuración aplicada:")
            print(f"  Días: {', '.join(DAY_NAMES[d] for d in days)}")
            print(f"  Hora: {time_str}")
        else:
            print("[Schedule] ✗ Error aplicando configuración")
