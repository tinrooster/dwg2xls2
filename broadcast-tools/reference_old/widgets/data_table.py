import logging
from typing import Dict, Any, List

from PyQt6.QtWidgets import (
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QAbstractItemView
)
from PyQt6.QtCore import Qt

class DataTable(QTableWidget):
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        
        # Configure table properties
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setEditTriggers(QAbstractItemView.EditTrigger.DoubleClicked)
        
        # Configure headers
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.horizontalHeader().setStretchLastSection(True)
        self.verticalHeader().setVisible(False)
        
        # Set default columns
        self.setColumnCount(4)
        self.setHorizontalHeaderLabels([
            "Item Number",
            "Description",
            "Length",
            "Notes"
        ])
        
    def load_data(self, data: Dict[str, Any]):
        """Load drawing data into the table"""
        try:
            self.clear()
            if not data:
                return
                
            # Extract headers from data
            headers = self._get_headers(data)
            self.setColumnCount(len(headers))
            self.setHorizontalHeaderLabels(headers)
            
            # Populate table with data
            self._populate_table(data)
            
            # Adjust column widths
            self.resizeColumnsToContents()
            
        except Exception as e:
            self.logger.error(f"Error loading data: {str(e)}", exc_info=True)
            
    def _get_headers(self, data: Dict[str, Any]) -> List[str]:
        """Extract column headers from data"""
        if isinstance(data, dict) and data:
            # If data is a dictionary of rows
            first_row = next(iter(data.values()))
            return list(first_row.keys())
        return []
        
    def _populate_table(self, data: Dict[str, Any]):
        """Populate table with drawing data"""
        try:
            # Set row count
            self.setRowCount(len(data))
            
            # Add data to table
            for row, (_, row_data) in enumerate(data.items()):
                for col, (header, value) in enumerate(row_data.items()):
                    item = QTableWidgetItem(str(value))
                    self.setItem(row, col, item)
                    
        except Exception as e:
            self.logger.error(f"Error populating table: {str(e)}", exc_info=True)
            
    def get_data(self) -> Dict[str, Any]:
        """Get current table data as dictionary"""
        data = {}
        try:
            headers = [self.horizontalHeaderItem(col).text() 
                      for col in range(self.columnCount())]
            
            for row in range(self.rowCount()):
                row_data = {}
                for col, header in enumerate(headers):
                    item = self.item(row, col)
                    row_data[header] = item.text() if item else ""
                data[row] = row_data
                
        except Exception as e:
            self.logger.error(f"Error getting table data: {str(e)}", exc_info=True)
            
        return data
