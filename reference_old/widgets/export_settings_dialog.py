from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QComboBox, QTableWidget,
    QTableWidgetItem, QGroupBox, QCheckBox, QFileDialog,
    QMessageBox, QSpinBox
)
from PyQt6.QtCore import Qt
import json
import logging
from pathlib import Path

logger = logging.getLogger('AutoCADExcelTool.ExportSettings')

class ExportSettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Export Settings")
        self.setMinimumWidth(600)
        self.config_file = Path("config/export_settings.json")
        self.setup_ui()
        self.load_config()

    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Excel Format Settings
        format_group = QGroupBox("Excel Format Settings")
        format_layout = QVBoxLayout()
        
        # Excel Version
        excel_version_layout = QHBoxLayout()
        excel_version_layout.addWidget(QLabel("Excel Version:"))
        self.excel_version = QComboBox()
        self.excel_version.addItems(["Excel 2007+ (.xlsx)", "Excel 97-2003 (.xls)"])
        excel_version_layout.addWidget(self.excel_version)
        format_layout.addLayout(excel_version_layout)
        
        # Sheet Settings
        sheet_layout = QHBoxLayout()
        sheet_layout.addWidget(QLabel("Default Sheet Name:"))
        self.default_sheet = QLineEdit()
        self.default_sheet.setPlaceholderText("e.g., Cable List")
        sheet_layout.addWidget(self.default_sheet)
        format_layout.addLayout(sheet_layout)
        
        format_group.setLayout(format_layout)
        layout.addWidget(format_group)
        
        # Column Order
        column_group = QGroupBox("Column Order")
        column_layout = QVBoxLayout()
        
        self.column_table = QTableWidget(0, 3)
        self.column_table.setHorizontalHeaderLabels(["Field Name", "Include", "Order"])
        self.column_table.horizontalHeader().setStretchLastSection(True)
        column_layout.addWidget(self.column_table)
        
        # Add default columns
        default_columns = ["NUMBER", "DWG", "ORIGIN", "DEST", "Wire Type", "Length", "Note", "Project ID"]
        for i, col in enumerate(default_columns):
            self.add_column_row(col, True, i + 1)
        
        column_group.setLayout(column_layout)
        layout.addWidget(column_group)
        
        # Export Location
        location_group = QGroupBox("Default Export Location")
        location_layout = QHBoxLayout()
        
        self.export_location = QLineEdit()
        location_layout.addWidget(self.export_location)
        
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_location)
        location_layout.addWidget(browse_btn)
        
        location_group.setLayout(location_layout)
        layout.addWidget(location_group)
        
        # Data Formatting
        format_group = QGroupBox("Data Formatting")
        format_layout = QVBoxLayout()
        
        # Date format
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("Date Format:"))
        self.date_format = QComboBox()
        self.date_format.addItems(["YYYY-MM-DD", "DD/MM/YYYY", "MM/DD/YYYY"])
        date_layout.addWidget(self.date_format)
        format_layout.addLayout(date_layout)
        
        # Number formatting
        self.use_thousand_separator = QCheckBox("Use Thousand Separator")
        format_layout.addWidget(self.use_thousand_separator)
        
        decimal_layout = QHBoxLayout()
        decimal_layout.addWidget(QLabel("Decimal Places:"))
        self.decimal_places = QSpinBox()
        self.decimal_places.setRange(0, 6)
        self.decimal_places.setValue(2)
        decimal_layout.addWidget(self.decimal_places)
        format_layout.addLayout(decimal_layout)
        
        format_group.setLayout(format_layout)
        layout.addWidget(format_group)
        
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

    def add_column_row(self, name, included=True, order=0):
        row = self.column_table.rowCount()
        self.column_table.insertRow(row)
        
        # Column name
        self.column_table.setItem(row, 0, QTableWidgetItem(name))
        
        # Include checkbox
        checkbox = QCheckBox()
        checkbox.setChecked(included)
        self.column_table.setCellWidget(row, 1, checkbox)
        
        # Order spinbox
        order_spin = QSpinBox()
        order_spin.setRange(0, 100)
        order_spin.setValue(order)
        self.column_table.setCellWidget(row, 2, order_spin)

    def browse_location(self):
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Default Export Directory",
            self.export_location.text()
        )
        if directory:
            self.export_location.setText(directory)

    def load_config(self):
        try:
            if self.config_file.exists():
                with open(self.config_file) as f:
                    config = json.load(f)
                    
                    # Load Excel format settings
                    self.excel_version.setCurrentText(config.get('excel_version', 'Excel 2007+ (.xlsx)'))
                    self.default_sheet.setText(config.get('default_sheet', 'Cable List'))
                    
                    # Load export location
                    self.export_location.setText(config.get('export_location', ''))
                    
                    # Load formatting settings
                    self.date_format.setCurrentText(config.get('date_format', 'YYYY-MM-DD'))
                    self.use_thousand_separator.setChecked(config.get('use_thousand_separator', True))
                    self.decimal_places.setValue(config.get('decimal_places', 2))
                    
        except Exception as e:
            logger.exception("Error loading export settings:")

    def save_config(self):
        try:
            config = {
                'excel_version': self.excel_version.currentText(),
                'default_sheet': self.default_sheet.text(),
                'export_location': self.export_location.text(),
                'date_format': self.date_format.currentText(),
                'use_thousand_separator': self.use_thousand_separator.isChecked(),
                'decimal_places': self.decimal_places.value(),
                'columns': []
            }
            
            # Save column settings
            for row in range(self.column_table.rowCount()):
                column = {
                    'name': self.column_table.item(row, 0).text(),
                    'included': self.column_table.cellWidget(row, 1).isChecked(),
                    'order': self.column_table.cellWidget(row, 2).value()
                }
                config['columns'].append(column)
            
            # Create config directory if it doesn't exist
            self.config_file.parent.mkdir(exist_ok=True)
            
            # Save configuration
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            self.accept()
            
        except Exception as e:
            logger.exception("Error saving export settings:")
            QMessageBox.critical(self, "Error", f"Failed to save settings: {str(e)}")
