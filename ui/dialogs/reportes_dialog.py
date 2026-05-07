"""
ReportesDialog - Muestra reportes generados
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QListWidget, QListWidgetItem,
    QPushButton, QLabel, QGroupBox, QMessageBox
)
from PySide6.QtCore import Qt
from pathlib import Path
import os


class ReportesDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Reportes Generados")
        self.setFixedSize(450, 400)
        self._build_ui()
    
    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Título
        title = QLabel("Reportes Generados")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)
        
        # ========== SECCIÓN: LISTA DE REPORTES ==========
        report_group = QGroupBox("Archivos CSV")
        report_layout = QVBoxLayout(report_group)
        
        self.report_list = QListWidget()
        self._load_reports()
        report_layout.addWidget(self.report_list)
        
        layout.addWidget(report_group)
        
        # Spacer
        layout.addStretch()
        
        # ========== BOTÓN SALIR ==========
        close_btn = QPushButton("Salir")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #e05c5c;
                color: white;
                padding: 10px 20px;
                border-radius: 6px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c04c4c;
            }
        """)
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)
    
    def _load_reports(self):
        """Carga lista de reportes CSV"""
        reports_dir = Path("reports")
        if not reports_dir.exists():
            item = QListWidgetItem("No hay reportes generados")
            item.setFlags(item.flags() & ~Qt.ItemIsEnabled)
            self.report_list.addItem(item)
            return
        
        csv_files = sorted(
            reports_dir.glob("*.csv"),
            key=os.path.getmtime,
            reverse=True
        )
        
        if not csv_files:
            item = QListWidgetItem("No hay reportes generados")
            item.setFlags(item.flags() & ~Qt.ItemIsEnabled)
            self.report_list.addItem(item)
            return
        
        for csv_file in csv_files:
            item = QListWidgetItem(csv_file.name)
            item.setData(Qt.UserRole, str(csv_file))
            self.report_list.addItem(item)
