from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QComboBox, QTableWidget,
    QTableWidgetItem, QFileDialog, QGroupBox, QTextEdit,
    QMessageBox, QListWidget, QCheckBox
)
from PyQt6.QtCore import Qt
import json
import logging
from pathlib import Path
from ..utils.settings_manager import SettingsManager

logger = logging.getLogger('AutoCADExcelTool.FieldMapping')

__all__ = ['FieldMappingDialog']

class FieldMappingDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Field Mapping")
        self.setMinimumWidth(800)
        self.config_file = Path("config/field_mapping.json")
        self.detected_patterns = []  # Initialize empty patterns list
        self.settings = SettingsManager()  # Add settings manager
        self.setup_ui()
        self.load_config()

    def setup_ui(self):
        """Initialize the UI components"""
        layout = QVBoxLayout()
        
        # File Type Settings
        file_type_group = QGroupBox("File Type Settings")
        file_type_layout = QVBoxLayout()
        
        # Primary File Type
        file_type_layout.addWidget(QLabel("Primary File Type:"))
        self.file_type = QComboBox()
        self.file_type.addItems(["DXF", "DWG"])
        file_type_layout.addWidget(self.file_type)
        
        file_type_group.setLayout(file_type_layout)
        layout.addWidget(file_type_group)
        
        # Field Mappings
        mapping_group = QGroupBox("Field Mappings")
        mapping_layout = QVBoxLayout()
        
        self.mapping_table = QTableWidget(0, 3)
        self.mapping_table.setHorizontalHeaderLabels(["Target Field", "Layer Name", "Field Pattern"])
        self.mapping_table.horizontalHeader().setStretchLastSection(True)
        mapping_layout.addWidget(self.mapping_table)
        
        # Add/Remove mapping buttons
        button_layout = QHBoxLayout()
        add_btn = QPushButton("Add Mapping")
        add_btn.clicked.connect(self.add_mapping_row)
        remove_btn = QPushButton("Remove Selected")
        remove_btn.clicked.connect(self.remove_mapping_row)
        pattern_help_btn = QPushButton("Pattern Help")
        pattern_help_btn.clicked.connect(self.show_pattern_help)
        
        button_layout.addWidget(add_btn)
        button_layout.addWidget(remove_btn)
        button_layout.addWidget(pattern_help_btn)
        mapping_layout.addLayout(button_layout)
        
        mapping_group.setLayout(mapping_layout)
        layout.addWidget(mapping_group)
        
        # Analysis Settings
        analysis_group = QGroupBox("Analysis Settings")
        analysis_layout = QVBoxLayout()
        
        analysis_layout.addWidget(QLabel("Note: DWG files are required for layer analysis."))
        
        # Sample Drawing File
        sample_layout = QHBoxLayout()
        sample_layout.addWidget(QLabel("Sample Drawing File:"))
        self.sample_file = QLineEdit()
        sample_layout.addWidget(self.sample_file)
        browse_btn = QPushButton("Browse DWG")
        browse_btn.clicked.connect(self.browse_sample)
        sample_layout.addWidget(browse_btn)
        analysis_layout.addLayout(sample_layout)
        
        # Analyze button
        analyze_btn = QPushButton("Analyze Sample File")
        analyze_btn.clicked.connect(self.analyze_sample)
        analysis_layout.addWidget(analyze_btn)
        
        # Results display
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        analysis_layout.addWidget(self.results_text)
        
        analysis_group.setLayout(analysis_layout)
        layout.addWidget(analysis_group)
        
        # Save/Cancel buttons
        self.button_layout = QHBoxLayout()  # Store as instance variable
        save_btn = QPushButton("Save Configuration")
        save_btn.clicked.connect(self.save_config)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        self.button_layout.addWidget(save_btn)
        self.button_layout.addWidget(cancel_btn)
        layout.addLayout(self.button_layout)
        
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
        
        # Add combobox for layer name
        layer_combo = QComboBox()
        layer_combo.addItems(sorted(self.available_layers))
        layer_combo.setEditable(True)  # Allow manual entry for new layers
        
        self.mapping_table.setCellWidget(row, 0, field_combo)
        self.mapping_table.setCellWidget(row, 1, layer_combo)
        self.mapping_table.setItem(row, 2, QTableWidgetItem(""))

    def remove_mapping_row(self):
        current_row = self.mapping_table.currentRow()
        if current_row >= 0:
            self.mapping_table.removeRow(current_row)

    def browse_sample(self):
        """Browse for a sample drawing file"""
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Select Sample Drawing",
                self.settings.get_last_dir('drawing'),  # Use last directory
                "Drawing Files (*.dwg *.dxf);;All Files (*.*)"
            )
            if file_path:
                self.sample_file.setText(file_path)
                self.settings.update_last_dir('drawing', file_path)  # Update last directory
        except Exception as e:
            logger.exception("Error browsing for sample:")
            QMessageBox.critical(self, "Error", f"Failed to open file browser: {str(e)}")

    def analyze_sample(self):
        """Analyze the sample file and display results"""
        file_path = self.sample_file.text()
        if not file_path:
            QMessageBox.warning(self, "Warning", "Please select a sample file first.")
            return
        
        try:
            from ..utils.drawing_processor import DrawingProcessor
            processor = DrawingProcessor()
            analysis = processor.analyze_drawing_structure(file_path)
            
            # Update available layers
            self.available_layers = set(analysis['layers'])
            
            # Store detected patterns
            self.detected_patterns = analysis.get('text_patterns', [])
            
            # Update existing layer combos
            for row in range(self.mapping_table.rowCount()):
                layer_combo = self.mapping_table.cellWidget(row, 1)
                if isinstance(layer_combo, QComboBox):
                    current_text = layer_combo.currentText()
                    layer_combo.clear()
                    layer_combo.addItems(sorted(self.available_layers))
                    if current_text in self.available_layers:
                        layer_combo.setCurrentText(current_text)
            
            # Display results
            self.results_text.clear()
            self.results_text.append("Available Layers:")
            for layer in sorted(analysis['layers']):
                self.results_text.append(f"- {layer}")
            
            # Show text samples by layer
            self.results_text.append("\nText Content by Layer:")
            for layer, texts in analysis['text_by_layer'].items():
                if texts:  # Only show layers with text
                    self.results_text.append(f"\n{layer}:")
                    for text in texts[:3]:  # Show first 3 examples
                        self.results_text.append(f"  • {text}")
            
            # Show text patterns if any
            if self.detected_patterns:
                self.results_text.append("\nDetected Text Patterns:")
                for pattern in sorted(self.detected_patterns)[:5]:  # Show first 5 patterns
                    self.results_text.append(f"- {pattern}")
            
        except Exception as e:
            logger.exception("Error analyzing sample file:")
            QMessageBox.critical(self, "Error", f"Failed to analyze file: {str(e)}")

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
        except Exception as e:
            logger.exception("Error loading configuration:")

    def validate_configuration(self):
        """Validate the configuration against required fields"""
        try:
            # Load required fields
            req_file = Path("config/field_requirements.json")
            if not req_file.exists():
                return True, []  # If no requirements file, assume all valid
            
            with open(req_file) as f:
                required_fields = json.load(f)
            
            # Check each required field
            missing_fields = []
            for row in range(self.mapping_table.rowCount()):
                target_field = self.mapping_table.cellWidget(row, 0)
                layer_name = self.mapping_table.cellWidget(row, 1)
                pattern = self.mapping_table.item(row, 2)
                
                if target_field and target_field.currentText() in required_fields:
                    if required_fields[target_field.currentText()]:
                        if not layer_name or not layer_name.currentText():
                            missing_fields.append(f"Layer Name for {target_field.currentText()}")
                        if not pattern or not pattern.text():
                            missing_fields.append(f"Field Pattern for {target_field.currentText()}")
            
            return len(missing_fields) == 0, missing_fields
            
        except Exception as e:
            logger.exception("Error validating configuration:")
            return False, ["Error validating configuration"]

    def save_config(self):
        try:
            # First validate
            is_valid, missing_fields = self.validate_configuration()
            if not is_valid:
                error_msg = "The following required fields are missing:\n\n"
                error_msg += "\n".join(f"• {field}" for field in missing_fields)
                error_msg += "\n\nWould you like to configure required fields?"
                
                reply = QMessageBox.warning(
                    self, 
                    "Validation Error",
                    error_msg,
                    QMessageBox.StandardButton.Yes | 
                    QMessageBox.StandardButton.No
                )
                
                if reply == QMessageBox.StandardButton.Yes:
                    from .field_requirements_dialog import FieldRequirementsDialog
                    dialog = FieldRequirementsDialog(self)
                    dialog.exec()
                    return
                return
            
            # Get existing configurations
            config_dir = Path("config")
            config_dir.mkdir(exist_ok=True)
            existing_configs = list(config_dir.glob("field_mapping_*.json"))
            
            # Show save dialog with options
            save_dialog = QDialog(self)
            save_dialog.setWindowTitle("Save Configuration")
            layout = QVBoxLayout()
            
            # Configuration name
            name_layout = QHBoxLayout()
            name_layout.addWidget(QLabel("Configuration Name:"))
            name_input = QLineEdit()
            name_layout.addWidget(name_input)
            layout.addLayout(name_layout)
            
            # Show existing configurations
            if existing_configs:
                layout.addWidget(QLabel("\nExisting Configurations:"))
                config_list = QListWidget()
                for config in existing_configs:
                    config_list.addItem(config.stem.replace('field_mapping_', ''))
                layout.addWidget(config_list)
                
                # Option to overwrite
                overwrite_check = QCheckBox("Overwrite if exists")
                layout.addWidget(overwrite_check)
            
            # Preview of what will be saved
            layout.addWidget(QLabel("\nConfiguration Summary:"))
            summary = QTextEdit()
            summary.setReadOnly(True)
            summary_text = f"File Type: {self.file_type.currentText()}\n\nMappings:\n"
            for row in range(self.mapping_table.rowCount()):
                target_field = self.mapping_table.cellWidget(row, 0)
                layer_name = self.mapping_table.cellWidget(row, 1)
                pattern = self.mapping_table.item(row, 2)
                if target_field and layer_name:
                    summary_text += f"• {target_field.currentText()} <- {layer_name.currentText()}"
                    if pattern and pattern.text():
                        summary_text += f" (Pattern: {pattern.text()})"
                    summary_text += "\n"
            summary.setText(summary_text)
            layout.addWidget(summary)
            
            # Buttons
            buttons = QHBoxLayout()
            save_btn = QPushButton("Save")
            cancel_btn = QPushButton("Cancel")
            buttons.addWidget(save_btn)
            buttons.addWidget(cancel_btn)
            layout.addLayout(buttons)
            
            save_dialog.setLayout(layout)
            
            # Connect buttons
            cancel_btn.clicked.connect(save_dialog.reject)
            save_btn.clicked.connect(save_dialog.accept)
            
            if save_dialog.exec() == QDialog.DialogCode.Accepted:
                config_name = name_input.text().strip()
                if not config_name:
                    QMessageBox.warning(self, "Warning", "Please enter a configuration name.")
                    return
                
                # Build the config file path
                config_file = config_dir / f"field_mapping_{config_name}.json"
                
                # Check for existing config
                if config_file.exists() and not (hasattr(overwrite_check, 'isChecked') and overwrite_check.isChecked()):
                    reply = QMessageBox.question(
                        self,
                        "Configuration Exists",
                        f"Configuration '{config_name}' already exists. Overwrite?",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                    )
                    if reply == QMessageBox.StandardButton.No:
                        return
                
                # Save the configuration
                config = {
                    'name': config_name,
                    'file_type': self.file_type.currentText(),
                    'mappings': []
                }
                
                for row in range(self.mapping_table.rowCount()):
                    target_field = self.mapping_table.cellWidget(row, 0)
                    layer_name = self.mapping_table.cellWidget(row, 1)
                    pattern = self.mapping_table.item(row, 2)
                    
                    if target_field and layer_name:
                        mapping = {
                            'target_field': target_field.currentText() or '',
                            'layer_name': layer_name.currentText() or '',
                            'pattern': pattern.text() if pattern else ''
                        }
                        config['mappings'].append(mapping)
                
                # Save to file
                with open(config_file, 'w') as f:
                    json.dump(config, f, indent=2)
                
                QMessageBox.information(
                    self,
                    "Configuration Saved",
                    f"""Configuration '{config_name}' saved successfully!

Location: {config_file}

You can load this configuration from the File menu.
All configurations are stored in: {config_dir}"""
                )
                
                self.accept()
                
        except Exception as e:
            logger.exception("Error saving configuration:")
            QMessageBox.critical(
                self, 
                "Error", 
                f"Failed to save configuration: {str(e)}"
            )

    def show_pattern_help(self):
        """Show help for field patterns"""
        help_text = """Field patterns help identify text in your drawings.

Examples:
• CBL-* - Matches any text starting with 'CBL-'
• *mm² - Matches any text ending with 'mm²'
• FROM:* - Matches any text starting with 'FROM:'
• L=* - Matches any text starting with 'L='
"""

        if self.detected_patterns:
            help_text += "\nDetected patterns in your sample:\n"
            help_text += "\n".join(f"• {pattern}" for pattern in self.detected_patterns)
        else:
            help_text += "\nNo patterns detected yet. Try analyzing a sample file first."

        QMessageBox.information(
            self,
            "Field Pattern Help",
            help_text
        )

