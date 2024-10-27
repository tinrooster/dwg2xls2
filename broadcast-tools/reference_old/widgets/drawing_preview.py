import logging
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QLabel
)
from PyQt6.QtCore import Qt
import pandas as pd
from PyQt6.QtGui import QColor

# Get module-specific logger
logger = logging.getLogger('AutoCADExcelTool.DrawingPreview')

class DrawingPreview(QWidget):
    def __init__(self):
        super().__init__()
        logger.debug("Initializing DrawingPreview")
        self.init_ui()
    
    def init_ui(self):
        try:
            logger.debug("Setting up DrawingPreview UI")
            # Main layout
            layout = QVBoxLayout()
            layout.setContentsMargins(0, 0, 0, 0)  # Remove margins
            self.setLayout(layout)
            
            # Create table
            self.table = QTableWidget()
            self.table.setColumnCount(11)  # Adjust based on your columns
            headers = ['NUMBER', 'DWG', 'ORIGIN', 'DEST', 'Alternate Dwg', 
                      'Wire Type', 'Length', 'Note', 'Project ID', 'flag',
                      'File Name']
            self.table.setHorizontalHeaderLabels(headers)
            
            # Set minimal initial size
            self.table.setRowCount(0)  # Start with no rows
            header_height = self.table.horizontalHeader().height()
            self.table.setMinimumHeight(header_height + 2)  # Just enough for header
            
            # Style the table
            self.table.setStyleSheet("""
                QTableWidget {
                    background-color: #2b2b2b;
                    gridline-color: #3d3d3d;
                    color: #ffffff;
                }
                QHeaderView::section {
                    background-color: #3d3d3d;
                    color: #ffffff;
                    padding: 5px;
                    border: 1px solid #505050;
                }
                QTableWidget::item {
                    padding: 5px;
                }
            """)
            
            # Add table to layout
            layout.addWidget(self.table)
            
            logger.debug("Drawing preview UI initialized")
        except Exception as e:
            logger.exception("Error initializing drawing preview UI:")
            raise
    
    def show_empty_state(self):
        """Reset to empty state"""
        self.table.clearContents()
        self.table.setRowCount(0)  # No rows when empty
    
    def update_preview(self, data):
        try:
            logger.debug(f"Updating preview with {len(data)} rows of data")
            
            # Clear existing content
            self.table.clearContents()
            
            if not data:
                # Reset to placeholder rows if no data
                self.table.setRowCount(10)
                return
            
            # Update with actual data
            self.table.setRowCount(len(data))
            
            # Get headers directly
            headers = ['NUMBER', 'DWG', 'ORIGIN', 'DEST', 'Alternate Dwg', 
                      'Wire Type', 'Length', 'Note', 'Project ID', 'flag',
                      'File Name']
            
            for row, item in enumerate(data):
                for col, header in enumerate(headers):  # Use headers list directly
                    value = str(item.get(header, ''))
                    table_item = QTableWidgetItem(value)
                    table_item.setForeground(QColor('#ffffff'))
                    self.table.setItem(row, col, table_item)
            
            # Adjust column widths
            self.table.resizeColumnsToContents()
            
            logger.debug("Preview updated successfully")
        except Exception as e:
            logger.exception("Error updating preview:")
            raise
