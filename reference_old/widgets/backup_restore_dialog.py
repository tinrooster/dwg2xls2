from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QListWidget, QListWidgetItem,
    QMessageBox, QFileDialog
)
from PyQt6.QtCore import Qt
import humanize
from ..utils.config_manager import ConfigManager

class BackupRestoreDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Backup and Restore")
        self.setMinimumWidth(600)
        self.config_manager = ConfigManager()
        self.setup_ui()
        self.load_backups()

    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Backup list
        layout.addWidget(QLabel("Available Backups:"))
        self.backup_list = QListWidget()
        self.backup_list.itemSelectionChanged.connect(self.update_backup_info)
        layout.addWidget(self.backup_list)
        
        # Backup info
        self.info_label = QLabel()
        layout.addWidget(self.info_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        create_backup_btn = QPushButton("Create Backup")
        create_backup_btn.clicked.connect(self.create_backup)
        
        restore_backup_btn = QPushButton("Restore Selected")
        restore_backup_btn.clicked.connect(self.restore_backup)
        
        import_backup_btn = QPushButton("Import Backup")
        import_backup_btn.clicked.connect(self.import_backup)
        
        export_backup_btn = QPushButton("Export Selected")
        export_backup_btn.clicked.connect(self.export_backup)
        
        button_layout.addWidget(create_backup_btn)
        button_layout.addWidget(restore_backup_btn)
        button_layout.addWidget(import_backup_btn)
        button_layout.addWidget(export_backup_btn)
        
        layout.addLayout(button_layout)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)

    def load_backups(self):
        """Load available backups into the list"""
        self.backup_list.clear()
        for backup_file in self.config_manager.list_backups():
            info = self.config_manager.get_backup_info(backup_file)
            if info:
                item = QListWidgetItem(
                    f"Backup from {info['date'].strftime('%Y-%m-%d %H:%M:%S')}"
                )
                item.setData(Qt.ItemDataRole.UserRole, backup_file)
                self.backup_list.addItem(item)

    def update_backup_info(self):
        """Update the backup information display"""
        items = self.backup_list.selectedItems()
        if not items:
            self.info_label.setText("")
            return
            
        backup_file = items[0].data(Qt.ItemDataRole.UserRole)
        info = self.config_manager.get_backup_info(backup_file)
        if info:
            self.info_label.setText(
                f"Size: {humanize.naturalsize(info['size'])}\n"
                f"Contains {len(info['configs'])} configurations:\n"
                f"• " + "\n• ".join(info['configs'])
            )

    def create_backup(self):
        """Create a new backup"""
        try:
            backup_file = self.config_manager.create_backup()
            self.load_backups()
            QMessageBox.information(
                self,
                "Backup Created",
                f"Backup created successfully!\nLocation: {backup_file}"
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to create backup: {str(e)}"
            )

    def restore_backup(self):
        """Restore selected backup"""
        items = self.backup_list.selectedItems()
        if not items:
            QMessageBox.warning(self, "Warning", "Please select a backup to restore.")
            return
            
        backup_file = items[0].data(Qt.ItemDataRole.UserRole)
        
        reply = QMessageBox.question(
            self,
            "Confirm Restore",
            "This will replace your current configuration with the backup.\n"
            "A backup of your current configuration will be created first.\n"
            "Do you want to continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                current_backup = self.config_manager.restore_backup(backup_file)
                QMessageBox.information(
                    self,
                    "Backup Restored",
                    f"Backup restored successfully!\n"
                    f"Your previous configuration was backed up to:\n{current_backup}"
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to restore backup: {str(e)}"
                )

    def import_backup(self):
        """Import a backup file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Import Backup",
            str(Path.home()),
            "Backup Files (*.zip);;All Files (*.*)"
        )
        
        if file_path:
            try:
                shutil.copy(file_path, self.config_manager.backup_dir)
                self.load_backups()
                QMessageBox.information(
                    self,
                    "Backup Imported",
                    "Backup imported successfully!"
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to import backup: {str(e)}"
                )

    def export_backup(self):
        """Export selected backup"""
        items = self.backup_list.selectedItems()
        if not items:
            QMessageBox.warning(self, "Warning", "Please select a backup to export.")
            return
            
        backup_file = items[0].data(Qt.ItemDataRole.UserRole)
        
        save_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Backup",
            str(Path.home() / backup_file.name),
            "Backup Files (*.zip);;All Files (*.*)"
        )
        
        if save_path:
            try:
                shutil.copy(backup_file, save_path)
                QMessageBox.information(
                    self,
                    "Backup Exported",
                    f"Backup exported successfully to:\n{save_path}"
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to export backup: {str(e)}"
                )
