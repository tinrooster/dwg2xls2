from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt

class DrawingPreview(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        # Add a label to show status
        self.status_label = QLabel("No drawing loaded")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.status_label)
        
        # Set a minimum size for the preview area
        self.setMinimumSize(400, 300)
        self.setStyleSheet("background-color: #f0f0f0;")
    
    def load_drawing(self, file_path):
        """Load and display a DWG file"""
        # TODO: Implement actual DWG file loading and preview
        self.status_label.setText(f"Loading: {file_path}")
        # This is where you'd implement the actual drawing preview
        # You might need to use a CAD library or convert to image first
