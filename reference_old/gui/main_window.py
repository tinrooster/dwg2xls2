import logging
import os
from pathlib import Path
from typing import Optional

from PyQt6.QtWidgets import (
    QMainWindow, QFileDialog, QMessageBox, QProgressDialog,
    QTextEdit, QDockWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QInputDialog, QWidget, QMenuBar, QMenu, QStatusBar, QApplication
)
from PyQt6.QtCore import Qt, QSettings

# Local imports
from ..utils.logger import setup_logger
from ..utils.drawing_processor import DrawingProcessor
from ..utils.excel_exporter import ExcelExporter
from ..widgets.preview_panel import PreviewPanel
from ..widgets.file_browser import FileBrowser
from ..widgets.field_mapping_dialog import FieldMappingDialog
from ..core.autocad_manager import BaseAutoCADConnector  # instead of AutoCADConnector
from .drawing_preview import DrawingPreview

# Get module-specific logger
logger = logging.getLogger('AutoCADExcelTool.MainWindow')

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.logger = setup_logger()
        self.drawing_data = []
        
        # Initialize UI
        self.init_ui()
        self.create_menu_bar()
        
        # Create status bar
        self.statusBar().showMessage("Ready")
        
        # Set window properties
        self.setWindowTitle("DWG to Excel Converter")
        self.setMinimumSize(800, 600)
        
        self.logger.info("Main window initialized")

    def init_ui(self):
        try:
            logger.debug("Setting up UI")
            
            # Create central widget and layout
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            
            # Create layout for central widget
            self.main_layout = QVBoxLayout(central_widget)
            
            # Create and add preview widget
            self.preview_widget = DrawingPreview()
            self.main_layout.addWidget(self.preview_widget)
            
            logger.debug("UI setup complete")
        except Exception as e:
            logger.exception("Error setting up UI:")
            raise

    def create_menu_bar(self):
        """Create the main menu bar with File and Help menus"""
        menubar = self.menuBar()
        
        # File Menu
        file_menu = menubar.addMenu('&File')
        
        # Add Open action
        open_action = file_menu.addAction('&Open')
        open_action.setShortcut('Ctrl+O')
        open_action.setStatusTip('Open DWG file')
        open_action.triggered.connect(self.open_file)
        
        # Add Export action
        export_action = file_menu.addAction('&Export')
        export_action.setShortcut('Ctrl+E')
        export_action.setStatusTip('Export to Excel')
        export_action.triggered.connect(self.export_to_excel)
        
        # Add Exit action
        exit_action = file_menu.addAction('&Exit')
        exit_action.setShortcut('Ctrl+Q')
        exit_action.setStatusTip('Exit application')
        exit_action.triggered.connect(self.close)
        
        # Help Menu
        help_menu = menubar.addMenu('&Help')
        
        # Add About action
        about_action = help_menu.addAction('&About')
        about_action.setStatusTip('About this application')
        about_action.triggered.connect(self.show_about)

    def open_file(self):
        """Open a DWG file dialog and handle the selected file"""
        try:
            file_name, _ = QFileDialog.getOpenFileName(
                self,
                "Open DWG File",
                "",
                "DWG Files (*.dwg);;All Files (*.*)"
            )
            
            if file_name:
                self.logger.info(f"Opening file: {file_name}")
                # TODO: Add your DWG file processing logic here
                self.preview_widget.load_drawing(file_name)  # You'll need to implement this in DrawingPreview
                self.statusBar().showMessage(f"Opened: {file_name}")
        except Exception as e:
            self.logger.error(f"Error opening file: {str(e)}")
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to open file: {str(e)}"
            )

    def export_to_excel(self):
        """Export the current drawing data to Excel"""
        try:
            if not hasattr(self, 'drawing_data') or not self.drawing_data:
                QMessageBox.warning(
                    self,
                    "Warning",
                    "No drawing data to export. Please open a DWG file first."
                )
                return

            file_name, _ = QFileDialog.getSaveFileName(
                self,
                "Export to Excel",
                "",
                "Excel Files (*.xlsx);;All Files (*.*)"
            )
            
            if file_name:
                if not file_name.endswith('.xlsx'):
                    file_name += '.xlsx'
                    
                # Create progress dialog
                progress = QProgressDialog("Exporting to Excel...", "Cancel", 0, 100, self)
                progress.setWindowModality(Qt.WindowModality.WindowModal)
                progress.show()
                
                # TODO: Add your Excel export logic here
                exporter = ExcelExporter()
                exporter.export_to_excel(self.drawing_data, file_name)
                
                progress.setValue(100)
                self.statusBar().showMessage(f"Exported to: {file_name}")
                
                QMessageBox.information(
                    self,
                    "Success",
                    "Export completed successfully!"
                )
        except Exception as e:
            self.logger.error(f"Error exporting to Excel: {str(e)}")
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to export: {str(e)}"
            )

    def show_about(self):
        """Show the about dialog"""
        about_text = """
        <h2>DWG to Excel Converter</h2>
        <p>Version 1.0</p>
        <p>A tool for extracting data from AutoCAD DWG files and exporting to Excel.</p>
        <p>© 2024 Your Name/Company</p>
        """
        
        QMessageBox.about(
            self,
            "About DWG to Excel Converter",
            about_text
        )

    # ... rest of the methods remain the same ...
