# gui/widgets/preview_panel.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
                            QHeaderView, QPushButton, QLabel)
from PyQt6.QtCore import pyqtSignal
import pandas as pd

class PreviewPanel(QWidget):  # Make sure this class name matches exactly
    """Widget for previewing drawing data"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        """Initialize the UI components"""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Add preview label
        self.label = QLabel("Drawing Data Preview")
        layout.addWidget(self.label)
        
        # Create table widget
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels([
            "Filename", "Cable Number", "Project ID", "Last Modified"
        ])
        layout.addWidget(self.table)
        
    def setup_connections(self):
        self.apply_btn.clicked.connect(self.apply_changes)
        self.export_btn.clicked.connect(self.export_data)

    def apply_changes(self):
        print("Applying changes...")

    def export_data(self):
        print("Exporting data...")

    def update_preview(self, data):
        """Update the preview with new data"""
        self.table.setRowCount(len(data))
        
        for row, row_data in enumerate(data):
            for col, value in enumerate(row_data):
                item = QTableWidgetItem(str(value))
                self.table.setItem(row, col, item)
                
        self.table.resizeColumnsToContents()
