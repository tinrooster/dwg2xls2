from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QComboBox, QTableWidget,
    QTableWidgetItem, QGroupBox, QCheckBox,
    QMessageBox
)
from PyQt6.QtCore import Qt
import json
import logging
from pathlib import Path

logger = logging.getLogger('AutoCADExcelTool.LayerSettings')

class LayerSettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Layer Settings")
        self.setMinimumWidth(500)
        self.config_file = Path("config/layer_settings.json")
        self.setup_ui()
        self.load_config()

    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Layer Visibility
        visibility_group = QGroupBox("Layer Visibility")
        visibility_layout = QVBoxLayout()
        
        # Layer table
        self.layer_table = QTableWidget(0, 2)
        self.layer_table.setHorizontalHeaderLabels(["Layer Name", "Visible"])
        self.layer_table.horizontalHeader().setStretchLastSection(True)
        visibility_layout.addWidget(self.layer_table)
        
        # Add/Remove layer buttons
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("Add Layer")
        add_btn.clicked.connect(self.add_layer_row)
        remove_btn = QPushButton("Remove Selected")
        remove_btn.clicked.connect(self.remove_layer_row)
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(remove_btn)
        visibility_layout.addLayout(btn_layout)
        
        visibility_group.setLayout(visibility_layout)
        layout.addWidget(visibility_group)
        
        # Layer Colors
        colors_group = QGroupBox("Layer Colors")
        colors_layout = QVBoxLayout()
        self.color_table = QTableWidget(0, 2)
        self.color_table.setHorizontalHeaderLabels(["Layer Name", "Color"])
        self.color_table.horizontalHeader().setStretchLastSection(True)
        colors_layout.addWidget(self.color_table)
        colors_group.setLayout(colors_layout)
        layout.addWidget(colors_group)
        
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

    def add_layer_row(self):
        row = self.layer_table.rowCount()
        self.layer_table.insertRow(row)
        
        # Add layer name field
        self.layer_table.setItem(row, 0, QTableWidgetItem(""))
        
        # Add visibility checkbox
        checkbox = QCheckBox()
        checkbox.setChecked(True)
        self.layer_table.setCellWidget(row, 1, checkbox)

    def remove_layer_row(self):
        current_row = self.layer_table.currentRow()
        if current_row >= 0:
            self.layer_table.removeRow(current_row)

    def load_config(self):
        try:
            if self.config_file.exists():
                with open(self.config_file) as f:
                    config = json.load(f)
                    
                    # Load layer visibility settings
                    for layer_name, visible in config.get('layer_visibility', {}).items():
                        row = self.layer_table.rowCount()
                        self.layer_table.insertRow(row)
                        self.layer_table.setItem(row, 0, QTableWidgetItem(layer_name))
                        checkbox = QCheckBox()
                        checkbox.setChecked(visible)
                        self.layer_table.setCellWidget(row, 1, checkbox)
                        
        except Exception as e:
            logger.exception("Error loading layer settings:")

    def save_config(self):
        try:
            config = {
                'layer_visibility': {},
                'layer_colors': {}
            }
            
            # Save layer visibility settings
            for row in range(self.layer_table.rowCount()):
                layer_name = self.layer_table.item(row, 0).text()
                checkbox = self.layer_table.cellWidget(row, 1)
                if isinstance(checkbox, QCheckBox):
                    config['layer_visibility'][layer_name] = checkbox.isChecked()
            
            # Create config directory if it doesn't exist
            self.config_file.parent.mkdir(exist_ok=True)
            
            # Save configuration
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            self.accept()
            
        except Exception as e:
            logger.exception("Error saving layer settings:")
            QMessageBox.critical(self, "Error", f"Failed to save settings: {str(e)}")
