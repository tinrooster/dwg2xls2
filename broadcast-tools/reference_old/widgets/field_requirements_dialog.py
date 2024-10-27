from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QTableWidget, QTableWidgetItem,
    QCheckBox, QMessageBox
)
from pathlib import Path
import json
import logging

logger = logging.getLogger('AutoCADExcelTool.FieldRequirements')

class FieldRequirementsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Field Requirements")
        self.setMinimumWidth(400)
        self.config_file = Path("config/field_requirements.json")
        self.setup_ui()
        self.load_config()

    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Instructions
        layout.addWidget(QLabel("Select which fields are required for valid configuration:"))
        
        # Fields table
        self.fields_table = QTableWidget(0, 2)
        self.fields_table.setHorizontalHeaderLabels(["Field Name", "Required"])
        self.fields_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.fields_table)
        
        # Default fields
        default_fields = ["NUMBER", "ORIGIN", "DEST", "Wire Type", "Length", 
                         "Project ID", "Note", "Layer Name", "Field Pattern"]
        
        for field in default_fields:
            self.add_field_row(field)
        
        # Buttons
        button_layout = QHBoxLayout()
        save_btn = QPushButton("Save Requirements")
        save_btn.clicked.connect(self.save_config)
        reset_btn = QPushButton("Reset to Defaults")
        reset_btn.clicked.connect(self.reset_to_defaults)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(reset_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)

    def add_field_row(self, field_name, required=False):
        row = self.fields_table.rowCount()
        self.fields_table.insertRow(row)
        
        # Field name
        self.fields_table.setItem(row, 0, QTableWidgetItem(field_name))
        
        # Required checkbox
        checkbox = QCheckBox()
        checkbox.setChecked(required)
        self.fields_table.setCellWidget(row, 1, checkbox)

    def reset_to_defaults(self):
        # Default required fields
        defaults = {
            "NUMBER": True,
            "ORIGIN": True,
            "DEST": True,
            "Wire Type": False,
            "Length": False,
            "Project ID": False,
            "Note": False,
            "Layer Name": True,
            "Field Pattern": False
        }
        
        self.fields_table.setRowCount(0)
        for field, required in defaults.items():
            self.add_field_row(field, required)

    def load_config(self):
        try:
            if self.config_file.exists():
                with open(self.config_file) as f:
                    config = json.load(f)
                    self.fields_table.setRowCount(0)
                    for field, required in config.items():
                        self.add_field_row(field, required)
        except Exception as e:
            logger.exception("Error loading field requirements:")
            self.reset_to_defaults()

    def save_config(self):
        try:
            config = {}
            for row in range(self.fields_table.rowCount()):
                field_name = self.fields_table.item(row, 0).text()
                required = self.fields_table.cellWidget(row, 1).isChecked()
                config[field_name] = required
            
            self.config_file.parent.mkdir(exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            self.accept()
            
        except Exception as e:
            logger.exception("Error saving field requirements:")
            QMessageBox.critical(self, "Error", f"Failed to save requirements: {str(e)}")
