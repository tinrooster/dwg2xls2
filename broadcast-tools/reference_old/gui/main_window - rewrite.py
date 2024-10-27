"""
Main Window for AutoCAD Excel Tool
Handles the primary user interface and coordinates all functionality
"""

#------------------------------------------------------------------------------
# Imports
#------------------------------------------------------------------------------
import logging
import os
from pathlib import Path
from typing import Optional

from PyQt6.QtWidgets import (
    QMainWindow, QFileDialog, QMessageBox, QProgressDialog,
    QTextEdit, QDockWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QInputDialog, QWidget, QMenu
)
from PyQt6.QtCore import Qt, QSettings
from PyQt6.QtGui import QAction, QActionGroup

# Local imports
from ..utils.logger import setup_logger
from ..utils.drawing_processor import DrawingProcessor
from ..utils.excel_exporter import ExcelExporter
from ..widgets.preview_panel import PreviewPanel
from ..widgets.file_browser import FileBrowser
from ..widgets.field_mapping_dialog import FieldMappingDialog
from ..core import ConnectorFactory, ConnectorType

# Module logger
logger = logging.getLogger('AutoCADExcelTool.MainWindow')

#------------------------------------------------------------------------------
# Main Window Class
#------------------------------------------------------------------------------
class MainWindow(QMainWindow):
    """Main application window for AutoCAD Excel Tool"""
    
    def __init__(self):
        super().__init__()
        self.logger = setup_logger()
        self.drawing_data = []
        self.connector = ConnectorFactory.create_connector(ConnectorType.DXF)
        
        # Apply dark theme
        self._apply_dark_theme()
        
        # Initialize UI
        self.init_ui()
        self.create_menu_bar()
        
        self.logger.info("Main window initialized")

    def _apply_dark_theme(self):
        """Apply dark theme to the application"""
        self.setStyleSheet("""
            QMainWindow, QWidget {
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
            QMenuBar {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QMenuBar::item:selected {
                background-color: #3b3b3b;
            }
            QMenu {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QMenu::item:selected {
                background-color: #3b3b3b;
            }
        """)

    #--------------------------------------------------------------------------
    # UI Setup Methods
    #--------------------------------------------------------------------------
    def init_ui(self):
        """Initialize the user interface"""
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
        """Create the application menu bar"""
        menu_bar = self.menuBar()
        menu_bar.setNativeMenuBar(False)

        # File Menu
        file_menu = menu_bar.addMenu("&File")
        self._create_file_menu(file_menu)

        # Configuration Menu
        config_menu = menu_bar.addMenu("&Configuration")
        self._create_config_menu(config_menu)

        # Help Menu
        help_menu = menu_bar.addMenu("&Help")
        self._create_help_menu(help_menu)

    def _create_file_menu(self, menu: QMenu):
        """Create the File menu items"""
        # Open action
        open_action = menu.addAction("Open Drawing")
        open_action.triggered.connect(self.open_drawing)

        menu.addSeparator()

        # Export submenu
        export_menu = menu.addMenu("Export")
        export_new_action = export_menu.addAction("Export to New Excel")
        export_new_action.triggered.connect(self.export_to_new_excel)

        merge_action = export_menu.addAction("Merge to Existing Excel")
        merge_action.triggered.connect(self.merge_to_excel)

        menu.addSeparator()
        exit_action = menu.addAction("Exit")
        exit_action.triggered.connect(self.close)

    def _create_config_menu(self, menu: QMenu):
        """Create the Configuration menu items"""
        # Add configuration actions
        field_mapping_action = menu.addAction("Field Mapping")
        field_mapping_action.triggered.connect(self.show_field_mapping)

        layer_settings_action = menu.addAction("Layer Settings")
        layer_settings_action.triggered.connect(self.show_layer_settings)

        export_settings_action = menu.addAction("Export Settings")
        export_settings_action.triggered.connect(self.show_export_settings)

        drawing_defaults_action = menu.addAction("Drawing Defaults")
        drawing_defaults_action.triggered.connect(self.show_drawing_defaults)

        field_requirements_action = menu.addAction("Field Requirements")
        field_requirements_action.triggered.connect(self.show_field_requirements)

        # Connector selection submenu
        connector_menu = menu.addMenu("Connector Type")
        self._create_connector_menu(connector_menu)

        # Backup/Restore
        menu.addSeparator()
        backup_restore_action = menu.addAction("Backup/Restore")
        backup_restore_action.triggered.connect(self.show_backup_restore)

    def _create_connector_menu(self, menu: QMenu):
        """Create the connector selection menu"""
        # Create actions
        dxf_action = QAction("DXF Reader", self)
        dxf_action.setCheckable(True)
        dxf_action.setChecked(True)
        
        com_action = QAction("AutoCAD COM", self)
        com_action.setCheckable(True)
        
        # Create action group
        action_group = QActionGroup(self)
        action_group.addAction(dxf_action)
        action_group.addAction(com_action)
        action_group.setExclusive(True)
        
        # Add to menu
        menu.addAction(dxf_action)
        menu.addAction(com_action)
        
        # Connect actions
        dxf_action.triggered.connect(lambda: self.change_connector(ConnectorType.DXF))
        com_action.triggered.connect(lambda: self.change_connector(ConnectorType.COM))

    def _create_help_menu(self, menu: QMenu):
        """Create the Help menu items"""
        help_contents_action = menu.addAction("Help Contents")
        help_contents_action.triggered.connect(self.show_help)
        help_contents_action.setShortcut("F1")

        menu.addSeparator()

        about_action = menu.addAction("About")
        about_action.triggered.connect(self.show_about)

        credits_action = menu.addAction("Credits")
        credits_action.triggered.connect(self.show_credits)

    #--------------------------------------------------------------------------
    # File Handling Methods
    #--------------------------------------------------------------------------
    def on_file_selected(self, file_path):
        """Handle file selection"""
        self.logger.info(f"Selected file: {file_path}")
        try:
            if not Path(file_path).exists():
                raise Exception("File not found")
                
            drawing_info = self.connector.get_drawing_info(file_path)
            
            if drawing_info:
                data = [
                    [
                        drawing_info['filename'],
                        cable_num,
                        drawing_info['project_id'],
                        drawing_info['last_modified']
                    ]
                    for cable_num in drawing_info['cable_numbers']
                ]
                
                self.drawing_data = data
                self.preview_widget.update_preview(data)
                self.statusBar().showMessage(f"Processed: {file_path}")
            else:
                raise Exception("No data could be extracted from the drawing")
                
        except Exception as e:
            self.logger.error(f"Error processing file: {str(e)}")
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to process drawing.\n\n"
                f"Error: {str(e)}\n\n"
                "Please check:\n"
                "1. The file is a valid DWG/DXF file\n"
                "2. The file contains text entities\n"
                "3. You have necessary permissions"
            )
            self.statusBar().showMessage("Error processing drawing")

    def open_drawing(self):
        """Open and process multiple drawing files"""
        try:
            file_paths, _ = QFileDialog.getOpenFileNames(
                self,
                "Select Drawing Files",
                "",
                "AutoCAD Files (*.dwg *.dxf);;All Files (*.*)"
            )

            if not file_paths:
                return

            progress = QProgressDialog("Processing drawings...", "Cancel", 0, len(file_paths), self)
            progress.setWindowModality(Qt.WindowModality.WindowModal)

            all_drawing_data = []
            for index, file_path in enumerate(file_paths):
                try:
                    progress.setValue(index)
                    if progress.wasCanceled():
                        break

                    drawing_info = self.connector.get_drawing_info(file_path)
                    if drawing_info:
                        data = [
                            [
                                drawing_info['filename'],
                                cable_num,
                                drawing_info['project_id'],
                                drawing_info['last_modified']
                            ]
                            for cable_num in drawing_info['cable_numbers']
                        ]
                        all_drawing_data.extend(data)

                except Exception as e:
                    QMessageBox.warning(
                        self, 
                        "Processing Error",
                        f"Error processing {os.path.basename(file_path)}: {str(e)}"
                    )
                    continue

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
                    QMessageBox.warning(
                        self, 
                        "Warning",
                        "Please choose a different filename or use 'Merge to Existing Excel'"
                    )
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
                sheets = ExcelExporter.get_available_sheets(file_path)

                sheet_name = None
                if len(sheets) > 1:
                    sheet, ok = QInputDialog.getItem(
                        self,
                        "Select Worksheet",
                        "Choose worksheet to merge with:",
                        sheets,
                        0,
                        False
                    )
                    if ok:
                        sheet_name = sheet
                    else:
                        return

                ExcelExporter.merge_to_excel(self.drawing_data, file_path, sheet_name)
                QMessageBox.information(self, "Success", "Data merged successfully!")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to merge: {str(e)}")

    #--------------------------------------------------------------------------
    # Configuration Methods
    #--------------------------------------------------------------------------
    def change_connector(self, connector_type: ConnectorType):
        """Change the AutoCAD connector type"""
        self.connector = ConnectorFactory.create_connector(connector_type)
        self.statusBar().showMessage(f"Changed to {connector_type.value} connector")

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
