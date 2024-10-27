from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QTabWidget, QWidget, 
    QGroupBox, QLabel, QLineEdit, QPushButton, 
    QListWidget, QListWidgetItem, QCheckBox, 
    QGraphicsView, QGraphicsScene, QTableWidget,
    QTableWidgetItem, QHBoxLayout
)
from PyQt6.QtGui import QPen, QBrush, QColor
from PyQt6.QtCore import Qt
import re
import logging

logger = logging.getLogger('AutoCADExcelTool.InteractiveExamples')

class InteractiveExamplesDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Interactive Examples")
        self.setMinimumSize(800, 600)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Example categories
        tabs = QTabWidget()
        
        # Field Mapping Examples
        field_mapping_tab = QWidget()
        fm_layout = QVBoxLayout()
        
        # Pattern matching example
        pattern_group = QGroupBox("Pattern Matching")
        pattern_layout = QVBoxLayout()
        
        pattern_layout.addWidget(QLabel("Try these patterns with sample text:"))
        
        self.pattern_input = QLineEdit()
        pattern_layout.addWidget(self.pattern_input)
        
        self.sample_text = QLineEdit()
        self.sample_text.setPlaceholderText("Enter sample text to test")
        pattern_layout.addWidget(self.sample_text)
        
        test_btn = QPushButton("Test Pattern")
        test_btn.clicked.connect(self.test_pattern)
        pattern_layout.addWidget(test_btn)
        
        self.pattern_result = QLabel()
        pattern_layout.addWidget(self.pattern_result)
        
        pattern_group.setLayout(pattern_layout)
        fm_layout.addWidget(pattern_group)
        
        # Common patterns
        patterns_list = QListWidget()
        patterns = [
            "CBL-*", "*mm²", "FROM:*", "TO:*", "L=*m",
            "CABLE_*", "#*", "* AWG", "*-*-*"
        ]
        for pattern in patterns:
            item = QListWidgetItem(pattern)
            item.setToolTip(f"Click to try pattern: {pattern}")
            patterns_list.addItem(item)
        patterns_list.itemClicked.connect(
            lambda item: self.pattern_input.setText(item.text())
        )
        fm_layout.addWidget(QLabel("Common Patterns (click to try):"))
        fm_layout.addWidget(patterns_list)
        
        field_mapping_tab.setLayout(fm_layout)
        tabs.addTab(field_mapping_tab, "Field Mapping")
        
        # Layer Management Examples
        layer_tab = QWidget()
        layer_layout = QVBoxLayout()
        
        # Layer visibility demo
        layer_demo = QGraphicsView()
        scene = QGraphicsScene()
        
        # Add sample layers
        layers = {
            "CABLE_TEXT": Qt.GlobalColor.blue,
            "CABLE_LINE": Qt.GlobalColor.red,
            "DIMENSIONS": Qt.GlobalColor.green
        }
        
        y_pos = 0
        self.layer_items = {}
        for layer_name, color in layers.items():
            # Layer name
            text = scene.addText(layer_name)
            text.setPos(10, y_pos)
            
            # Visibility checkbox
            checkbox = QCheckBox()
            checkbox.setChecked(True)
            proxy = scene.addWidget(checkbox)
            proxy.setPos(150, y_pos)
            
            # Sample content
            item = scene.addRect(200, y_pos, 100, 20, 
                               QPen(color), QBrush(color))
            
            self.layer_items[layer_name] = item
            checkbox.toggled.connect(
                lambda checked, item=item: item.setVisible(checked)
            )
            
            y_pos += 40
        
        layer_demo.setScene(scene)
        layer_layout.addWidget(QLabel("Layer Visibility Demo:"))
        layer_layout.addWidget(layer_demo)
        
        layer_tab.setLayout(layer_layout)
        tabs.addTab(layer_tab, "Layer Management")
        
        # Excel Export Examples
        excel_tab = QWidget()
        excel_layout = QVBoxLayout()
        
        # Sample data preview
        preview = QTableWidget(5, 4)
        preview.setHorizontalHeaderLabels(
            ["Cable Number", "From", "To", "Type"]
        )
        
        # Add sample data
        sample_data = [
            ["CBL-001", "Panel A", "Panel B", "4x4mm²"],
            ["CBL-002", "MCC-1", "Drive-1", "3x2.5mm²"],
            ["CBL-003", "UPS", "Server", "2x1.5mm²"]
        ]
        
        for row, data in enumerate(sample_data):
            for col, value in enumerate(data):
                preview.setItem(row, col, QTableWidgetItem(value))
        
        excel_layout.addWidget(QLabel("Export Preview:"))
        excel_layout.addWidget(preview)
        
        excel_tab.setLayout(excel_layout)
        tabs.addTab(excel_tab, "Excel Export")
        
        layout.addWidget(tabs)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)

    def test_pattern(self):
        """Test pattern matching"""
        import re
        pattern = self.pattern_input.text()
        text = self.sample_text.text()
        
        try:
            # Convert AutoCAD-style pattern to regex
            regex = pattern.replace("*", ".*")
            regex = f"^{regex}$"
            
            if re.match(regex, text):
                self.pattern_result.setText(
                    "✅ Pattern matches!"
                )
                self.pattern_result.setStyleSheet(
                    "color: green;"
                )
            else:
                self.pattern_result.setText(
                    "❌ No match"
                )
                self.pattern_result.setStyleSheet(
                    "color: red;"
                )
                
        except Exception as e:
            self.pattern_result.setText(
                f"Error: {str(e)}"
            )
            self.pattern_result.setStyleSheet(
                "color: red;"
            )
