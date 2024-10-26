from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QMessageBox
from pathlib import Path
import json
import logging
from ..utils.settings_manager import SettingsManager

class BaseConfigDialog(QDialog):
    def __init__(self, parent=None, config_name=""):
        super().__init__(parent)
        self.config_name = config_name
        self.settings = SettingsManager()
        self.config_dir = Path("config")
        
    def save_configuration(self, config_data):
        """Generic configuration save with naming"""
        try:
            # Show save dialog
            save_dialog = QDialog(self)
            save_dialog.setWindowTitle(f"Save {self.config_name} Configuration")
            layout = QVBoxLayout()
            
            # ... similar save dialog layout as field_mapping ...
            
            if save_dialog.exec() == QDialog.DialogCode.Accepted:
                config_name = name_input.text().strip()
                if not config_name:
                    QMessageBox.warning(self, "Warning", "Please enter a configuration name.")
                    return
                
                config_file = self.config_dir / f"{self.config_name.lower()}_{config_name}.json"
                
                # Handle overwrite warning
                if config_file.exists() and not overwrite_check.isChecked():
                    reply = QMessageBox.question(self, "Configuration Exists",
                                               f"Configuration '{config_name}' already exists. Overwrite?")
                    if reply == QMessageBox.StandardButton.No:
                        return
                
                # Save configuration
                self.config_dir.mkdir(exist_ok=True)
                with open(config_file, 'w') as f:
                    json.dump(config_data, f, indent=2)
                
                QMessageBox.information(self, "Configuration Saved",
                                      f"Configuration '{config_name}' saved successfully!")
                
                return True
                
        except Exception as e:
            logger.exception(f"Error saving {self.config_name} configuration:")
            QMessageBox.critical(self, "Error", f"Failed to save configuration: {str(e)}")
            return False
