import logging
import json
from pathlib import Path
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QComboBox, QTableWidget,
    QTableWidgetItem, QFileDialog, QGroupBox
)
from PyQt6.QtCore import Qt

# Get module-specific logger
logger = logging.getLogger('AutoCADExcelTool.ConfigDialog')

class FieldMappingDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Field Mapping Configuration")
        self.setMinimumWidth(600)
        self.config_file = Path("config/field_mapping.json")
        self.setup_ui()
        self.load_config()

    def setup_ui(self):
        layout = QVBoxLayout()
        
        # File type selection
        file_group = QGroupBox("File Type Settings")
        file_layout = QVBoxLayout()
        self.file_type = QComboBox()
        self.file_type.addItems(["DXF", "DWG"])
        file_layout.addWidget(QLabel("Primary File Type:"))
        file_layout.addWidget(self.file_type)
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)
        
        # Field mapping table
        mapping_group = QGroupBox("Field Mappings")
        mapping_layout = QVBoxLayout()
        self.mapping_table = QTableWidget(0, 3)
        self.mapping_table.setHorizontalHeaderLabels(["Target Field", "Layer Name", "Field Pattern"])
        self.mapping_table.horizontalHeader().setStretchLastSection(True)
        mapping_layout.addWidget(self.mapping_table)
        
        # Add/Remove mapping buttons
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("Add Mapping")
        add_btn.clicked.connect(self.add_mapping_row)
        remove_btn = QPushButton("Remove Selected")
        remove_btn.clicked.connect(self.remove_mapping_row)
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(remove_btn)
        mapping_layout.addLayout(btn_layout)
        mapping_group.setLayout(mapping_layout)
        layout.addWidget(mapping_group)
        
        # Analysis settings
        analysis_group = QGroupBox("Analysis Settings")
        analysis_layout = QVBoxLayout()
        self.sample_file = QLineEdit()
        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self.browse_sample)
        analyze_btn = QPushButton("Analyze Sample File")
        analyze_btn.clicked.connect(self.analyze_sample)
        analysis_layout.addWidget(QLabel("Sample Drawing File:"))
        file_browse = QHBoxLayout()
        file_browse.addWidget(self.sample_file)
        file_browse.addWidget(browse_btn)
        analysis_layout.addLayout(file_browse)
        analysis_layout.addWidget(analyze_btn)
        analysis_group.setLayout(analysis_layout)
        layout.addWidget(analysis_group)
        
        # Buttons
        buttons = QHBoxLayout()
        save_btn = QPushButton("Save Configuration")
        save_btn.clicked.connect(self.save_config)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        buttons.addWidget(save_btn)
        buttons.addWidget(cancel_btn)
        layout.addLayout(buttons)
        
        self.setLayout(layout)

    def add_mapping_row(self):
        row = self.mapping_table.rowCount()
        self.mapping_table.insertRow(row)
        
        # Add combobox for target field
        field_combo = QComboBox()
        field_combo.addItems([
            "NUMBER", "ORIGIN", "DEST", "Wire Type", 
            "Length", "Project ID", "Note"
        ])
        self.mapping_table.setCellWidget(row, 0, field_combo)

    def remove_mapping_row(self):
        current_row = self.mapping_table.currentRow()
        if current_row >= 0:
            self.mapping_table.removeRow(current_row)

    def browse_sample(self):
        """Open file dialog for sample drawing selection"""
        try:
            logger.debug("Opening sample file dialog")
            dialog = QFileDialog(self)
            dialog.setWindowTitle("Select Sample Drawing")
            dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
            dialog.setNameFilter("Drawing Files (*.dwg *.dxf);;All Files (*.*)")
            
            if dialog.exec() == QFileDialog.DialogCode.Accepted:
                files = dialog.selectedFiles()
                if files:
                    self.sample_file.setText(files[0])
                    logger.debug(f"Selected sample file: {files[0]}")
                    
        except Exception as e:
            logger.exception("Error in browse_sample:")
            raise

    def analyze_sample(self):
        # Add sample file analysis code here
        pass

    def load_config(self):
        try:
            if self.config_file.exists():
                with open(self.config_file) as f:
                    config = json.load(f)
                    # Load configuration into UI
                    self.file_type.setCurrentText(config.get('file_type', 'DXF'))
                    mappings = config.get('mappings', [])
                    for mapping in mappings:
                        self.add_mapping_row()
                        row = self.mapping_table.rowCount() - 1
                        self.mapping_table.cellWidget(row, 0).setCurrentText(
                            mapping.get('target_field', '')
                        )
                        self.mapping_table.setItem(
                            row, 1, 
                            QTableWidgetItem(mapping.get('layer_name', ''))
                        )
                        self.mapping_table.setItem(
                            row, 2, 
                            QTableWidgetItem(mapping.get('pattern', ''))
                        )
                    logger.debug("Configuration loaded successfully")
        except Exception as e:
            logger.exception("Error loading configuration:")

    def save_config(self):
        try:
            config = {
                'file_type': self.file_type.currentText(),
                'mappings': []
            }
            
            for row in range(self.mapping_table.rowCount()):
                mapping = {
                    'target_field': self.mapping_table.cellWidget(row, 0).currentText(),
                    'layer_name': self.mapping_table.item(row, 1).text(),
                    'pattern': self.mapping_table.item(row, 2).text()
                }
                config['mappings'].append(mapping)
            
            self.config_file.parent.mkdir(exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            logger.debug("Configuration saved successfully")
            self.accept()
            
        except Exception as e:
            logger.exception("Error saving configuration:")