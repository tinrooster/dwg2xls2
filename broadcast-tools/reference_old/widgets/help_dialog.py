from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QTreeWidget, QTreeWidgetItem,
    QTextBrowser, QSplitter, QLineEdit, QFrame,
    QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtPrintSupport import QPrinter
from PyQt6.QtGui import QTextDocument
from ..resources.help.content import HELP_CONTENT, SEARCH_INDEX
import tempfile
import webbrowser
from pathlib import Path
import logging
from .interactive_examples_dialog import InteractiveExamplesDialog  # Add this import

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HelpDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("AutoCAD Excel Tool Help")
        self.resize(800, 600)
        
        logger.debug("Initializing HelpDialog")
        self.setup_ui()
        self.load_help_content()

    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Search bar
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Search:"))
        self.search_input = QLineEdit()
        self.search_input.textChanged.connect(self.search_help)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)
        
        # Main splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel with tree and search results
        left_panel = QFrame()
        left_layout = QVBoxLayout()
        
        self.topics_tree = QTreeWidget()
        self.topics_tree.setHeaderLabel("Topics")
        self.topics_tree.setMinimumWidth(250)
        self.topics_tree.itemClicked.connect(self.on_topic_selected)
        
        self.search_results = QTreeWidget()
        self.search_results.setHeaderLabel("Search Results")
        self.search_results.setMinimumWidth(250)
        self.search_results.itemClicked.connect(self.show_search_result)
        self.search_results.hide()
        
        left_layout.addWidget(self.topics_tree)
        left_layout.addWidget(self.search_results)
        left_panel.setLayout(left_layout)
        
        # Content viewer with navigation
        right_panel = QFrame()
        right_layout = QVBoxLayout()
        
        nav_layout = QHBoxLayout()
        self.back_btn = QPushButton("← Back")
        self.back_btn.clicked.connect(self.navigate_back)
        self.forward_btn = QPushButton("Forward →")
        self.forward_btn.clicked.connect(self.navigate_forward)
        nav_layout.addWidget(self.back_btn)
        nav_layout.addWidget(self.forward_btn)
        nav_layout.addStretch()
        
        # Add export button to navigation bar
        self.export_btn = QPushButton("Export as PDF")
        self.export_btn.clicked.connect(self.export_pdf)
        nav_layout.addWidget(self.export_btn)
        
        # Add interactive examples button
        self.examples_btn = QPushButton("Try Examples")
        self.examples_btn.clicked.connect(self.show_interactive_examples)
        nav_layout.addWidget(self.examples_btn)
        
        self.content_view = QTextBrowser()
        self.content_view.setOpenExternalLinks(True)
        self.content_view.setStyleSheet("""
            QTextBrowser {
                background-color: white;
                padding: 10px;
            }
        """)
        
        right_layout.addLayout(nav_layout)
        right_layout.addWidget(self.content_view)
        right_panel.setLayout(right_layout)
        
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        layout.addWidget(splitter)
        
        # Navigation history
        self.history = []
        self.current_index = -1
        self.update_nav_buttons()
        
        self.setLayout(layout)

    def search_help(self, text):
        """Search help content"""
        if not text:
            self.search_results.hide()
            self.topics_tree.show()
            return
            
        self.search_results.clear()
        self.search_results.show()
        self.topics_tree.hide()
        
        # Search in index
        results = set()
        for term, topics in SEARCH_INDEX.items():
            if text.lower() in term.lower():
                results.update(topics)
        
        # Search in content
        for topic_id, content in HELP_CONTENT.items():
            if (text.lower() in content['title'].lower() or 
                text.lower() in content['content'].lower()):
                results.add(topic_id)
        
        # Show results
        for topic_id in sorted(results):
            item = QTreeWidgetItem([HELP_CONTENT[topic_id]['title']])
            item.setData(0, Qt.ItemDataRole.UserRole, topic_id)
            self.search_results.addTopLevelItem(item)  # Changed from addItem to addTopLevelItem

    def show_search_result(self, item):
        """Show content for search result"""
        topic_id = item.data(0, Qt.ItemDataRole.UserRole)
        self.show_content(topic_id)

    def navigate_back(self):
        """Navigate to previous topic"""
        if self.current_index > 0:
            self.current_index -= 1
            self.show_content(self.history[self.current_index], False)
        self.update_nav_buttons()

    def navigate_forward(self):
        """Navigate to next topic"""
        if self.current_index < len(self.history) - 1:
            self.current_index += 1
            self.show_content(self.history[self.current_index], False)
        self.update_nav_buttons()

    def update_nav_buttons(self):
        """Update navigation button states"""
        self.back_btn.setEnabled(self.current_index > 0)
        self.forward_btn.setEnabled(self.current_index < len(self.history) - 1)

    def show_content(self, topic_id, add_to_history=True):
        """Show help content for topic"""
        if topic_id in HELP_CONTENT:
            content = HELP_CONTENT[topic_id]
            
            # Add CSS styling
            styled_content = f"""
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
                    h2 {{ color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
                    h3 {{ color: #34495e; margin-top: 20px; }}
                    .section {{ margin: 20px 0; }}
                    img {{ max-width: 100%; border: 1px solid #ddd; border-radius: 4px; }}
                    code {{ background: #f8f9fa; padding: 2px 4px; border-radius: 3px; }}
                    pre {{ background: #f8f9fa; padding: 15px; border-radius: 4px; overflow-x: auto; }}
                    ul, ol {{ padding-left: 20px; }}
                    li {{ margin: 5px 0; }}
                </style>
                {content['content']}
            """
            
            self.content_view.setHtml(styled_content)
            
            if add_to_history:
                # Add to navigation history
                self.history = self.history[:self.current_index + 1]
                self.history.append(topic_id)
                self.current_index = len(self.history) - 1
                self.update_nav_buttons()

    def on_topic_selected(self, current, previous):
        """Handle topic selection"""
        if not current:
            return
        
        topic_id = current.data(0, Qt.ItemDataRole.UserRole)
        
        # If it's a category (parent item), show category overview instead of debug info
        if current.parent() is None:  # This is a main category
            category_name = current.text(0)
            category_content = f"""
                <h2>{category_name}</h2>
                <div class="section">
                    <h3>In This Section</h3>
                    <ul>
            """
            # Add links to all child topics
            for i in range(current.childCount()):
                child = current.child(i)
                child_title = child.text(0)
                category_content += f"<li><a href='#{child.data(0, Qt.ItemDataRole.UserRole)}'>{child_title}</a></li>"
            
            category_content += "</ul></div>"
            self.content_view.setHtml(category_content)
            return

        # Regular topic content display
        if topic_id and topic_id in HELP_CONTENT:
            content = HELP_CONTENT[topic_id]["content"]
            self.content_view.setHtml(content)
        else:
            logger.warning(f"No content found for topic: {topic_id}")

    def load_help_content(self):
        """Load help content into tree"""
        logger.debug("Loading help content into tree")
        
        # Getting Started
        getting_started = self.add_category("Getting Started")
        for topic_id in ["Overview", "Quick Start Guide", "System Requirements"]:
            self.add_topic(getting_started, topic_id)

        # Field Mapping
        field_mapping = self.add_category("Field Mapping")
        for topic_id in ["Understanding Field Mapping", "Creating Field Maps", "Pattern Matching"]:
            self.add_topic(field_mapping, topic_id)

        # Layer Settings
        layer_settings = self.add_category("Layer Settings")
        for topic_id in ["Layer Management", "Layer Visibility", "Layer Colors"]:
            self.add_topic(layer_settings, topic_id)

        # Export Settings
        export_settings = self.add_category("Export Settings")
        for topic_id in ["Excel Export Options", "Column Configuration", "Data Formatting"]:
            self.add_topic(export_settings, topic_id)

        # Drawing Settings
        drawing_settings = self.add_category("Drawing Settings")
        for topic_id in ["Default Settings", "Text Extraction", "Processing Options"]:
            self.add_topic(drawing_settings, topic_id)

        # Configuration Management
        config_management = self.add_category("Configuration Management")
        self.add_topic(config_management, "Configuration Management")

        # Add Troubleshooting category
        troubleshooting = self.add_category("Troubleshooting")
        self.add_topic(troubleshooting, "Troubleshooting")  # Main troubleshooting guide

    def add_category(self, name):
        """Add a category to the tree"""
        item = QTreeWidgetItem([name])
        self.topics_tree.addTopLevelItem(item)
        logger.debug(f"Added category item: {name}")
        return item

    def add_topic(self, parent, topic_id):
        """Add a topic under a category"""
        if topic_id in HELP_CONTENT:
            item = QTreeWidgetItem([HELP_CONTENT[topic_id]["title"]])
            item.setData(0, Qt.ItemDataRole.UserRole, topic_id)  # Store the topic_id
            parent.addChild(item)
            logger.debug(f"Successfully added topic: {topic_id}")
            return item
        logger.warning(f"Failed to add topic {topic_id} - not found in HELP_CONTENT")
        return None

    def export_pdf(self):
        """Export current help content as PDF"""
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Export Documentation",
                str(Path.home() / "AutoCAD-Excel-Tool-Documentation.pdf"),
                "PDF Files (*.pdf)"
            )
            
            if file_path:
                printer = QPrinter()
                printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
                printer.setOutputFileName(file_path)
                
                # Create complete documentation
                doc = QTextDocument()
                
                # Add table of contents
                content = "<h1>AutoCAD Excel Tool Documentation</h1>\n<h2>Table of Contents</h2>\n<ul>"
                for topic_id, topic_data in HELP_CONTENT.items():
                    content += f'<li><a href="#{topic_id}">{topic_data["title"]}</a></li>'
                content += "</ul>\n\n"
                
                # Add all topics
                for topic_id, topic_data in HELP_CONTENT.items():
                    content += f'<div id="{topic_id}">\n{topic_data["content"]}\n</div>\n\n'
                
                doc.setHtml(content)
                doc.print(printer)  # Changed from print_ to print
                
                QMessageBox.information(
                    self,
                    "Export Complete",
                    f"Documentation exported to:\n{file_path}"
                )
                
        except Exception as e:
            logger.exception("Error exporting PDF:")
            QMessageBox.critical(self, "Error", f"Failed to export PDF: {str(e)}")

    def show_interactive_examples(self):
        """Show interactive examples dialog"""
        try:
            dialog = InteractiveExamplesDialog(self)
            dialog.exec()
        except Exception as e:
            logger.exception("Error showing examples:")
            QMessageBox.critical(self, "Error", f"Failed to show examples: {str(e)}")
