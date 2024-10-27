from pathlib import Path
import json
import shutil
import datetime
import zipfile
import logging

logger = logging.getLogger('AutoCADExcelTool.ConfigManager')

class ConfigManager:
    def __init__(self):
        self.config_dir = Path("config")
        self.backup_dir = self.config_dir / "backups"
        self.config_types = {
            'field_mapping': 'Field Mappings',
            'layer_settings': 'Layer Settings',
            'export_settings': 'Export Settings',
            'drawing_defaults': 'Drawing Defaults'
        }

    def create_backup(self):
        """Create a backup of all configurations"""
        try:
            # Create backup directory
            self.backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Create timestamp for backup name
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = self.backup_dir / f"config_backup_{timestamp}.zip"
            
            # Create zip file containing all configs
            with zipfile.ZipFile(backup_file, 'w') as zipf:
                for config_file in self.config_dir.glob("*.json"):
                    if config_file.is_file():
                        zipf.write(config_file, config_file.name)
            
            return backup_file
            
        except Exception as e:
            logger.exception("Error creating backup:")
            raise

    def restore_backup(self, backup_file):
        """Restore configuration from a backup"""
        try:
            # Create timestamp for current config backup
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            current_backup = self.create_backup()
            
            # Extract backup files
            with zipfile.ZipFile(backup_file, 'r') as zipf:
                zipf.extractall(self.config_dir)
            
            return current_backup
            
        except Exception as e:
            logger.exception("Error restoring backup:")
            raise

    def list_backups(self):
        """List available backup files"""
        try:
            if not self.backup_dir.exists():
                return []
            return sorted(self.backup_dir.glob("config_backup_*.zip"), reverse=True)
        except Exception as e:
            logger.exception("Error listing backups:")
            return []

    def get_backup_info(self, backup_file):
        """Get information about a backup file"""
        try:
            info = {
                'date': datetime.datetime.strptime(
                    backup_file.stem.replace('config_backup_', ''),
                    "%Y%m%d_%H%M%S"
                ),
                'size': backup_file.stat().st_size,
                'configs': []
            }
            
            with zipfile.ZipFile(backup_file, 'r') as zipf:
                info['configs'] = zipf.namelist()
            
            return info
            
        except Exception as e:
            logger.exception("Error getting backup info:")
            return None
