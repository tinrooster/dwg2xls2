# gui/widgets/file_browser.py
from PyQt6.QtWidgets import (
    QWidget, QPushButton, QVBoxLayout, 
    QFileDialog, QLabel
)
from PyQt6.QtCore import pyqtSignal

class FileBrowser(QWidget):
    """Widget for browsing and selecting files"""
    
    # Signal emitted when a file is selected
    file_selected = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        """Initialize the UI components"""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Add instructions label
        self.label = QLabel("Select AutoCAD drawing files (DWG/DXF)")
        layout.addWidget(self.label)
        
        # Add browse button
        self.browse_button = QPushButton("Browse Files...")
        self.browse_button.clicked.connect(self.browse_files)
        layout.addWidget(self.browse_button)
        
        # Add some stretch to keep widgets at the top
        layout.addStretch()
        
    def browse_files(self):
        """Open file dialog and emit selected file path"""
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Drawing Files",
            "",
            "AutoCAD Files (*.dwg *.dxf);;All Files (*.*)"
        )
        
        # Emit the first selected file path
        if file_paths:
            self.file_selected.emit(file_paths[0])
