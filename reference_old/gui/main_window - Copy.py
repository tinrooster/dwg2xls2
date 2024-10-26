import logging
import os
from pathlib import Path
from typing import Optional

from PyQt6.QtWidgets import (
    QMainWindow, QFileDialog, QMessageBox, QProgressDialog,
    QTextEdit, QDockWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QInputDialog, QWidget
)
from PyQt6.QtCore import Qt, QSettings
from PyQt6.QtGui import QActionGroup  # Add this import

# Local imports
from ..utils.logger import setup_logger
from ..utils.drawing_processor import DrawingProcessor
from ..utils.excel_exporter import ExcelExporter
from ..widgets.preview_panel import PreviewPanel
from ..widgets.file_browser import FileBrowser
from ..widgets.field_mapping_dialog import FieldMappingDialog
from ..core.connector_factory import ConnectorFactory, ConnectorType

# Get module-specific logger
logger = logging.getLogger('AutoCADExcelTool.MainWindow')

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.logger = setup_logger()
        self.drawing_data = []
        self.connector = ConnectorFactory.create_connector(ConnectorType.DXF)  # Default to DXF
        
        # Set dark theme
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QWidget {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QPushButton {
                background-color: #3b3b3b;
                border: 1px solid #555555;
                padding: 5px;
                border-radius: 3px;
                color: #ffffff;
            }
            QPushButton:hover {
                background-color: #454545;
            }
            QTableWidget {
                background-color: #2b2b2b;
                color: #ffffff;
                gridline-color: #3b3b3b;
            }
            QTableWidget::item {
                border-color: #3b3b3b;
            }
            QHeaderView::section {
                background-color: #3b3b3b;
                color: #ffffff;
                border: 1px solid #555555;
            }
            QLabel {
                color: #ffffff;
            }
            QMessageBox {
                background-color: #2b2b2b;
                color: #ffffff;
            }
        """)
        
        # Initialize UI
        self.init_ui()
        self.create_menu_bar()
        
        self.logger.info("Main window initialized")

    def init_ui(self):
        # Set window properties
        self.setWindowTitle('AutoCAD Excel Tool')
        self.setMinimumSize(800, 600)

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Create and add widgets
        self.preview_widget = PreviewPanel()
        self.file_browser = FileBrowser()

        layout.addWidget(self.file_browser)
        layout.addWidget(self.preview_widget)

        # Connect signals
        self.file_browser.file_selected.connect(self.on_file_selected)

        # Create status bar
        self.status_bar = self.statusBar()
        self.status_bar.showMessage('Ready')

    def create_menu_bar(self):
        menu_bar = self.menuBar()
        menu_bar.setNativeMenuBar(False)
        menu_bar.clear()

        # File Menu
        file_menu = menu_bar.addMenu("&File")
        open_action = file_menu.addAction("Open Drawing")
        open_action.triggered.connect(self.open_drawing)

        file_menu.addSeparator()

        # Export options
        export_menu = file_menu.addMenu("Export")
        export_new_action = export_menu.addAction("Export to New Excel")
        export_new_action.triggered.connect(self.export_to_new_excel)

        merge_action = export_menu.addAction("Merge to Existing Excel")
        merge_action.triggered.connect(self.merge_to_excel)

        file_menu.addSeparator()
        exit_action = file_menu.addAction("Exit")
        exit_action.triggered.connect(self.close)

        # Configuration Menu
        config_menu = menu_bar.addMenu("&Configuration")

        field_mapping_action = config_menu.addAction("Field Mapping")
        field_mapping_action.triggered.connect(self.show_field_mapping)

        layer_settings_action = config_menu.addAction("Layer Settings")
        layer_settings_action.triggered.connect(self.show_layer_settings)

        export_settings_action = config_menu.addAction("Export Settings")
        export_settings_action.triggered.connect(self.show_export_settings)

        drawing_defaults_action = config_menu.addAction("Drawing Defaults")
        drawing_defaults_action.triggered.connect(self.show_drawing_defaults)

        field_requirements_action = config_menu.addAction("Field Requirements")
        field_requirements_action.triggered.connect(self.show_field_requirements)

        # Add connector selection to Configuration menu
        connector_menu = config_menu.addMenu("Connector Type")
        
        dxf_action = connector_menu.addAction("DXF Reader")
        dxf_action.setCheckable(True)
        dxf_action.setChecked(True)
        
        com_action = connector_menu.addAction("AutoCAD COM")
        com_action.setCheckable(True)
        
        # Make actions exclusive
        action_group = QActionGroup(self)
        action_group.addAction(dxf_action)
        action_group.addAction(com_action)
        action_group.setExclusive(True)
        
        # Connect actions
        dxf_action.triggered.connect(lambda: self.change_connector(ConnectorType.DXF))
        com_action.triggered.connect(lambda: self.change_connector(ConnectorType.COM))

        # Help Menu
        help_menu = menu_bar.addMenu("&Help")

        help_contents_action = help_menu.addAction("Help Contents")
        help_contents_action.triggered.connect(self.show_help)
        help_contents_action.setShortcut("F1")

        help_menu.addSeparator()

        about_action = help_menu.addAction("About")
        about_action.triggered.connect(self.show_about)

        credits_action = help_menu.addAction("Credits")
        credits_action.triggered.connect(self.show_credits)

        # Backup/Restore Menu
        config_menu.addSeparator()
        backup_restore_action = config_menu.addAction("Backup/Restore")
        backup_restore_action.triggered.connect(self.show_backup_restore)

    def change_connector(self, connector_type: ConnectorType):
        """Change the AutoCAD connector type"""
        self.connector = ConnectorFactory.create_connector(connector_type)
        self.statusBar().showMessage(f"Changed to {connector_type.value} connector")

    def on_file_selected(self, file_path):
        """Handle file selection"""
        self.logger.info(f"Selected file: {file_path}")
        try:
            # Use AutoCADConnector to get drawing info
            connector = AutoCADConnector()
            drawing_info = connector.get_drawing_info(file_path)
            
            if drawing_info:
                # Convert drawing info to table format
                data = [
                    [
                        drawing_info['filename'],
                        cable_num,  # Each cable number gets its own row
                        drawing_info['project_id'],
                        drawing_info['last_modified']
                    ]
                    for cable_num in drawing_info['cable_numbers']
                ]
                
                # Update the preview panel with the extracted data
                self.preview_widget.update_preview(data)
                self.statusBar().showMessage(f"Processed: {file_path}")
            else:
                self.logger.error("No data could be extracted from the drawing")
                QMessageBox.critical(
                    self,
                    "Error",
                    "No data could be extracted from the drawing.\n\n"
                    "Please check:\n"
                    "1. AutoCAD is installed and running\n"
                    "2. The file is a valid DWG/DXF file\n"
                    "3. The file contains text entities"
                )
                
        except Exception as e:
            self.logger.exception(f"Error processing file: {str(e)}")
            QMessageBox.critical(
                self,
                "Error",
                f"Error processing file:\n{str(e)}\n\n"
                "Please check the application log for details."
            )

    def open_drawing(self):
        """Open and process multiple drawing files"""
        try:
            file_paths, _ = QFileDialog.getOpenFileNames(
                self,
                "Select Drawing Files",
                "",
                "All Files (*.*)"
            )

            if not file_paths:
                return

            # Create progress dialog for batch processing
            progress = QProgressDialog("Processing drawings...", "Cancel", 0, len(file_paths), self)
            progress.setWindowModality(Qt.WindowModality.WindowModal)

            all_drawing_data = []
            processor = DrawingProcessor()

            for index, file_path in enumerate(file_paths):
                try:
                    # Update progress
                    progress.setValue(index)
                    if progress.wasCanceled():
                        break

                    # Process drawing
                    drawing_data = processor.extract_drawing_data(file_path)
                    all_drawing_data.extend(drawing_data)

                except Exception as e:
                    QMessageBox.warning(self, "Processing Error",
                        f"Error processing {os.path.basename(file_path)}: {str(e)}")
                    continue

            # Update the preview with all processed data
            if all_drawing_data:
                self.drawing_data = all_drawing_data
                self.preview_widget.update_preview(all_drawing_data)
                self.status_bar.showMessage(f"Processed {len(file_paths)} drawing(s)")

            progress.setValue(len(file_paths))

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to process drawings: {str(e)}")

    def export_to_new_excel(self):
        """Export to a new Excel file"""
        if not self.drawing_data:
            QMessageBox.warning(self, "Warning", "No drawing data to export!")
            return

        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Create New Excel File",
                "",
                "Excel Files (*.xlsx);;All Files (*.*)"
            )

            if file_path:
                if not file_path.endswith('.xlsx'):
                    file_path += '.xlsx'

                if os.path.exists(file_path):
                    QMessageBox.warning(self, "Warning",
                        "Please choose a different filename or use 'Merge to Existing Excel'")
                    return

                ExcelExporter.export_to_new_excel(self.drawing_data, file_path)
                QMessageBox.information(self, "Success", "Data exported to new file successfully!")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export: {str(e)}")

    def merge_to_excel(self):
        """Merge with existing Excel file"""
        if not self.drawing_data:
            QMessageBox.warning(self, "Warning", "No drawing data to merge!")
            return

        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Select Excel File to Merge With",
                "",
                "Excel Files (*.xlsx);;All Files (*.*)"
            )

            if file_path:
                # Get available sheets
                sheets = ExcelExporter.get_available_sheets(file_path)

                # If multiple sheets, let user choose
                sheet_name = None
                if len(sheets) > 1:
                    sheet, ok = QInputDialog.getItem(
                        self,
                        "Select Worksheet",
                        "Choose worksheet to merge with:",
                        sheets,
                        0,  # Default to first sheet
                        False  # Non-editable
                    )
                    if ok:
                        sheet_name = sheet
                    else:
                        return

                ExcelExporter.merge_to_excel(self.drawing_data, file_path, sheet_name)
                QMessageBox.information(self, "Success", "Data merged successfully!")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to merge: {str(e)}")

    def show_field_mapping(self):
        """Show the field mapping configuration dialog"""
        try:
            dialog = FieldMappingDialog(self)
            dialog.exec()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open configuration: {str(e)}")

    def show_layer_settings(self):
        """Show the layer settings configuration dialog"""
        try:
            from ..widgets.layer_settings_dialog import LayerSettingsDialog
            dialog = LayerSettingsDialog(self)
            dialog.exec()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open layer settings: {str(e)}")

    def show_export_settings(self):
        """Show the export settings configuration dialog"""
        try:
            from ..widgets.export_settings_dialog import ExportSettingsDialog
            dialog = ExportSettingsDialog(self)
            dialog.exec()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open export settings: {str(e)}")

    def show_drawing_defaults(self):
        """Show the drawing defaults configuration dialog"""
        try:
            from ..widgets.drawing_defaults_dialog import DrawingDefaultsDialog
            dialog = DrawingDefaultsDialog(self)
            dialog.exec()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open drawing defaults: {str(e)}")

    def show_field_requirements(self):
        """Show the field requirements configuration dialog"""
        try:
            from ..widgets.field_requirements_dialog import FieldRequirementsDialog
            dialog = FieldRequirementsDialog(self)
            dialog.exec()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open field requirements: {str(e)}")

    def show_backup_restore(self):
        """Show the backup/restore dialog"""
        try:
            from ..widgets.backup_restore_dialog import BackupRestoreDialog
            dialog = BackupRestoreDialog(self)
            dialog.exec()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open backup/restore dialog: {str(e)}")

    def show_help(self):
        """Show the help dialog"""
        try:
            from ..widgets.help_dialog import HelpDialog
            dialog = HelpDialog(self)
            dialog.exec()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open help: {str(e)}")

    def show_about(self):
        """Show the About dialog"""
        QMessageBox.about(
            self,
            "About AutoCAD Excel Tool",
            """<h3>AutoCAD Excel Tool</h3>
            <p>Version 1.0</p>
            <p>A tool for extracting and managing cable data from AutoCAD drawings.</p>
            <p>Features:</p>
            <ul>
                <li>Extract cable information from DXF/DWG files</li>
                <li>Export data to Excel spreadsheets</li>
                <li>Configurable field mapping</li>
                <li>Layer management</li>
                <li>Automated text recognition</li>
            </ul>
            <p>© 2024 All rights reserved.</p>"""
        )

    def show_credits(self):
        """Show the Credits dialog"""
        QMessageBox.about(
            self,
            "Credits",
            """<h3>Credits</h3>
            <p><b>Development Team:</b></p>
            <ul>
                <li>AC Hay - Project Lead & Development</li>
                <li>Claude - AI Assistant & Development Support</li>
            </ul>
            <p><b>Special Thanks:</b></p>
            <ul>
                <li>PyQt6 Team</li>
                <li>ezdxf Project</li>
                <li>OpenAI</li>
            </ul>
            <p>Thank you to all contributors and users!</p>"""
        )

