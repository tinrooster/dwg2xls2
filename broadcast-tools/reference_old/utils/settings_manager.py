from pathlib import Path
import json
import logging

logger = logging.getLogger('AutoCADExcelTool.Settings')

class SettingsManager:
    def __init__(self):
        self.settings_file = Path("config/app_settings.json")
        self.settings = self.load_settings()

    def load_settings(self):
        try:
            if self.settings_file.exists():
                with open(self.settings_file) as f:
                    return json.load(f)
            return self.get_default_settings()
        except Exception as e:
            logger.exception("Error loading settings:")
            return self.get_default_settings()

    def get_default_settings(self):
        return {
            'last_drawing_dir': str(Path.home() / "Documents"),
            'last_excel_dir': str(Path.home() / "Documents"),
            'last_config_dir': str(Path.home() / "Documents"),
            'recent_files': [],
            'recent_configs': []
        }

    def save_settings(self):
        try:
            self.settings_file.parent.mkdir(exist_ok=True)
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            logger.exception("Error saving settings:")

    def update_last_dir(self, dir_type, path):
        """Update the last used directory for a specific type"""
        if path:
            self.settings[f'last_{dir_type}_dir'] = str(Path(path).parent)
            self.save_settings()

    def get_last_dir(self, dir_type):
        """Get the last used directory for a specific type"""
        return self.settings.get(f'last_{dir_type}_dir', str(Path.home() / "Documents"))
