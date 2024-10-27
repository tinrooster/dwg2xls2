from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QComboBox, QTableWidget,
    QTableWidgetItem, QGroupBox, QCheckBox, QFileDialog,
    QMessageBox, QSpinBox, QDoubleSpinBox
)
from PyQt6.QtCore import Qt
import json
import logging
from pathlib import Path

logger = logging.getLogger('AutoCADExcelTool.DrawingDefaults')

class DrawingDefaultsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Drawing Defaults")
        self.setMinimumWidth(600)
        self.config_file = Path("config/drawing_defaults.json")
        self.setup_ui()
        self.load_config()

    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Default Drawing Settings
        drawing_group = QGroupBox("Default Drawing Settings")
        drawing_layout = QVBoxLayout()
        
        # Units
        units_layout = QHBoxLayout()
        units_layout.addWidget(QLabel("Default Units:"))
        self.units = QComboBox()
        self.units.addItems(["Millimeters", "Inches", "Meters"])
        units_layout.addWidget(self.units)
        drawing_layout.addLayout(units_layout)
        
        # Scale
        scale_layout = QHBoxLayout()
        scale_layout.addWidget(QLabel("Default Scale:"))
        self.scale = QDoubleSpinBox()
        self.scale.setRange(0.001, 1000.0)
        self.scale.setValue(1.0)
        self.scale.setDecimals(3)
        scale_layout.addWidget(self.scale)
        drawing_layout.addLayout(scale_layout)
        
        drawing_group.setLayout(drawing_layout)
        layout.addWidget(drawing_group)
        
        # Text Extraction Rules
        text_group = QGroupBox("Text Extraction Rules")
        text_layout = QVBoxLayout()
        
        self.text_table = QTableWidget(0, 3)
        self.text_table.setHorizontalHeaderLabels(["Pattern", "Field", "Priority"])
        self.text_table.horizontalHeader().setStretchLastSection(True)
        text_layout.addWidget(self.text_table)
        
        # Add/Remove text rule buttons
        text_btn_layout = QHBoxLayout()
        add_text_btn = QPushButton("Add Rule")
        add_text_btn.clicked.connect(self.add_text_rule)
        remove_text_btn = QPushButton("Remove Selected")
        remove_text_btn.clicked.connect(self.remove_text_rule)
        text_btn_layout.addWidget(add_text_btn)
        text_btn_layout.addWidget(remove_text_btn)
        text_layout.addLayout(text_btn_layout)
        
        text_group.setLayout(text_layout)
        layout.addWidget(text_group)
        
        # File Locations
        location_group = QGroupBox("File Locations")
        location_layout = QVBoxLayout()
        
        # Drawing Directory
        drawing_dir_layout = QHBoxLayout()
        drawing_dir_layout.addWidget(QLabel("Default Drawing Directory:"))
        self.drawing_dir = QLineEdit()
        drawing_dir_layout.addWidget(self.drawing_dir)
        drawing_dir_btn = QPushButton("Browse...")
        drawing_dir_btn.clicked.connect(lambda: self.browse_directory(self.drawing_dir))
        drawing_dir_layout.addWidget(drawing_dir_btn)
        location_layout.addLayout(drawing_dir_layout)
        
        # Backup Location
        backup_layout = QHBoxLayout()
        backup_layout.addWidget(QLabel("Backup Location:"))
        self.backup_dir = QLineEdit()
        backup_layout.addWidget(self.backup_dir)
        backup_btn = QPushButton("Browse...")
        backup_btn.clicked.connect(lambda: self.browse_directory(self.backup_dir))
        backup_layout.addWidget(backup_btn)
        location_layout.addLayout(backup_layout)
        
        location_group.setLayout(location_layout)
        layout.addWidget(location_group)
        
        # Processing Options
        processing_group = QGroupBox("Processing Options")
        processing_layout = QVBoxLayout()
        
        # Auto-detection settings
        self.auto_detect = QCheckBox("Auto-detect Text Fields")
        self.auto_detect.setChecked(True)
        processing_layout.addWidget(self.auto_detect)
        
        self.auto_layer = QCheckBox("Auto-create Layers")
        processing_layout.addWidget(self.auto_layer)
        
        # Text recognition
        text_recognition_layout = QHBoxLayout()
        text_recognition_layout.addWidget(QLabel("Text Recognition Mode:"))
        self.text_mode = QComboBox()
        self.text_mode.addItems(["Standard", "Enhanced", "Legacy"])
        text_recognition_layout.addWidget(self.text_mode)
        processing_layout.addLayout(text_recognition_layout)
        
        processing_group.setLayout(processing_layout)
        layout.addWidget(processing_group)
        
        # Buttons
        buttons = QHBoxLayout()
        save_btn = QPushButton("Save Settings")
        save_btn.clicked.connect(self.save_config)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        buttons.addWidget(save_btn)
        buttons.addWidget(cancel_btn)
        layout.addLayout(buttons)
        
        self.setLayout(layout)

    def add_text_rule(self):
        row = self.text_table.rowCount()
        self.text_table.insertRow(row)
        
        # Pattern field
        self.text_table.setItem(row, 0, QTableWidgetItem(""))
        
        # Field combo box
        field_combo = QComboBox()
        field_combo.addItems([
            "NUMBER", "ORIGIN", "DEST", "Wire Type", 
            "Length", "Project ID", "Note"
        ])
        self.text_table.setCellWidget(row, 1, field_combo)
        
        # Priority spinbox
        priority = QSpinBox()
        priority.setRange(1, 100)
        priority.setValue(row + 1)
        self.text_table.setCellWidget(row, 2, priority)

    def remove_text_rule(self):
        current_row = self.text_table.currentRow()
        if current_row >= 0:
            self.text_table.removeRow(current_row)

    def browse_directory(self, line_edit):
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Directory",
            line_edit.text()
        )
        if directory:
            line_edit.setText(directory)

    def load_config(self):
        try:
            if self.config_file.exists():
                with open(self.config_file) as f:
                    config = json.load(f)
                    
                    # Load drawing settings
                    self.units.setCurrentText(config.get('units', 'Millimeters'))
                    self.scale.setValue(config.get('scale', 1.0))
                    
                    # Load file locations
                    self.drawing_dir.setText(config.get('drawing_directory', ''))
                    self.backup_dir.setText(config.get('backup_directory', ''))
                    
                    # Load processing options
                    self.auto_detect.setChecked(config.get('auto_detect', True))
                    self.auto_layer.setChecked(config.get('auto_layer', False))
                    self.text_mode.setCurrentText(config.get('text_mode', 'Standard'))
                    
                    # Load text rules
                    rules = config.get('text_rules', [])
                    for rule in rules:
                        row = self.text_table.rowCount()
                        self.text_table.insertRow(row)
                        self.text_table.setItem(row, 0, QTableWidgetItem(rule['pattern']))
                        
                        field_combo = QComboBox()
                        field_combo.addItems([
                            "NUMBER", "ORIGIN", "DEST", "Wire Type", 
                            "Length", "Project ID", "Note"
                        ])
                        field_combo.setCurrentText(rule['field'])
                        self.text_table.setCellWidget(row, 1, field_combo)
                        
                        priority = QSpinBox()
                        priority.setRange(1, 100)
                        priority.setValue(rule['priority'])
                        self.text_table.setCellWidget(row, 2, priority)
        except Exception as e:
            logger.exception("Error loading drawing defaults:")

    def save_config(self):
        try:
            config = {
                'units': self.units.currentText(),
                'scale': self.scale.value(),
                'drawing_directory': self.drawing_dir.text(),
                'backup_directory': self.backup_dir.text(),
                'auto_detect': self.auto_detect.isChecked(),
                'auto_layer': self.auto_layer.isChecked(),
                'text_mode': self.text_mode.currentText(),
                'text_rules': []
            }
            
            # Save text rules
            for row in range(self.text_table.rowCount()):
                rule = {
                    'pattern': self.text_table.item(row, 0).text(),
                    'field': self.text_table.cellWidget(row, 1).currentText(),
                    'priority': self.text_table.cellWidget(row, 2).value()
                }
                config['text_rules'].append(rule)
            
            # Create config directory if it doesn't exist
            self.config_file.parent.mkdir(exist_ok=True)
            
            # Save configuration
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            self.accept()
        except Exception as e:
            logger.exception("Error saving drawing defaults:")
            QMessageBox.critical(self, "Error", f"Failed to save settings: {str(e)}")
