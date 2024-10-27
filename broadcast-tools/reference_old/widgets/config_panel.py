# gui/widgets/config_panel.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, QLineEdit,
                            QComboBox, QPushButton, QSpinBox, QCheckBox)
from PyQt6.QtCore import pyqtSignal

class ConfigPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        # AutoCAD settings
        self.acad_version = QComboBox()
        self.acad_version.addItems(["AutoCAD LT 2020", "AutoCAD LT 2021", "AutoCAD LT 2022"])
        
        # Excel settings
        self.excel_template = QLineEdit()
        self.sheet_name = QLineEdit()
        
        # Add to form
        form_layout.addRow("AutoCAD Version:", self.acad_version)
        form_layout.addRow("Excel Template:", self.excel_template)
        form_layout.addRow("Sheet Name:", self.sheet_name)

        # Buttons
        self.save_btn = QPushButton("Save Configuration")
        self.reset_btn = QPushButton("Reset to Defaults")

        layout.addLayout(form_layout)
        layout.addWidget(self.save_btn)
        layout.addWidget(self.reset_btn)

