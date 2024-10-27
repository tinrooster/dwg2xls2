from typing import Dict, Any, Optional
import json
import yaml
import csv
import xml.etree.ElementTree as ET
from pathlib import Path
import pandas as pd
from datetime import datetime

class ConfigurationIO:
    """Handles import and export of facility configurations"""

    def __init__(self, validator: Optional[ConfigValidator] = None):
        self.validator = validator or ConfigValidator()
        self.supported_formats = {
            '.json': self._handle_json,
            '.yaml': self._handle_yaml,
            '.csv': self._handle_csv,
            '.xml': self._handle_xml,
            '.xlsx': self._handle_excel
        }

    def export_configuration(self, 
                           config_data: Dict[str, Any], 
                           output_path: Path,
                           format_type: Optional[str] = None) -> bool:
        """Export configuration to specified format"""
        if format_type:
            extension = format_type
        else:
            extension = output_path.suffix.lower()

        if extension not in self.supported_formats:
            raise ValueError(f"Unsupported format: {extension}")

        try:
            self.supported_formats[extension](config_data, output_path, mode='export')
            return True
        except Exception as e:
            raise Exception(f"Export failed: {str(e)}")

    def import_configuration(self, 
                           input_path: Path,
                           format_type: Optional[str] = None) -> Dict[str, Any]:
        """Import configuration from file"""
        if format_type:
            extension = format_type
        else:
            extension = input_path.suffix.lower()

        if extension not in self.supported_formats:
            raise ValueError(f"Unsupported format: {extension}")

        try:
            config_data = self.supported_formats[extension](input_path, None, mode='import')
            
            # Validate imported data
            errors = self._validate_imported_data(config_data)
            if errors:
                raise ValueError(f"Validation errors: {', '.join(errors)}")
                
            return config_data
        except Exception as e:
            raise Exception(f"Import failed: {str(e)}")

    def _handle_json(self, 
                    data: Any, 
                    file_path: Path, 
                    mode: str = 'export') -> Optional[Dict[str, Any]]:
        """Handle JSON format"""
        if mode == 'export':
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
        else:
            with open(file_path, 'r') as f:
                return json.load(f)

    def _handle_yaml(self, 
                    data: Any, 
                    file_path: Path, 
                    mode: str = 'export') -> Optional[Dict[str, Any]]:
        """Handle YAML format"""
        if mode == 'export':
            with open(file_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False)
        else:
            with open(file_path, 'r') as f:
                return yaml.safe_load(f)

    def _handle_csv(self, 
                   data: Any, 
                   file_path: Path, 
                   mode: str = 'export') -> Optional[Dict[str, Any]]:
        """Handle CSV format"""
        if mode == 'export':
            # Flatten nested structure for CSV
            flattened_data = self._flatten_data(data)
            df = pd.DataFrame(flattened_data)
            df.to_csv(file_path, index=False)
        else:
            df = pd.read_csv(file_path)
            return self._unflatten_data(df.to_dict('records'))

    def _handle_xml(self, 
                   data: Any, 
                   file_path: Path, 
                   mode: str = 'export') -> Optional[Dict[str, Any]]:
        """Handle XML format"""
        if mode == 'export':
            root = ET.Element('facility_configuration')
            self._dict_to_xml(data, root)
            tree = ET.ElementTree(root)
            tree.write(file_path, encoding='utf-8', xml_declaration=True)
        else:
            tree = ET.parse(file_path)
            return self._xml_to_dict(tree.getroot())

    def _handle_excel(self, 
                     data: Any, 
                     file_path: Path, 
                     mode: str = 'export') -> Optional[Dict[str, Any]]:
        """Handle Excel format"""
        if mode == 'export':
            with pd.ExcelWriter(file_path) as writer:
                # Create separate sheets for each main category
                for category, items in data.items():
                    if isinstance(items, dict):
                        df = pd.DataFrame.from_dict(items, orient='index')
                        df.to_excel(writer, sheet_name=category)
        else:
            # Read all sheets into a dictionary
            excel_data = pd.read_excel(file_path, sheet_name=None)
            return {
                sheet_name: df.to_dict('index')
                for sheet_name, df in excel_data.items()
            }

    def _flatten_data(self, data: Dict[str, Any], 
                     parent_key: str = '', 
                     sep: str = '.') -> List[Dict[str, Any]]:
        """Flatten nested dictionary structure"""
        items = []
        for key, value in data.items():
            new_key = f"{parent_key}{sep}{key}" if parent_key else key
            if isinstance(value, dict):
                items.extend(self._flatten_data(value, new_key, sep=sep))
            else:
                items.append({new_key: value})
        return items

    def _unflatten_data(self, 
                       flattened: List[Dict[str, Any]], 
                       sep: str = '.') -> Dict[str, Any]:
        """Reconstruct nested dictionary structure"""
        result = {}
        for item in flattened:
            for key, value in item.items():
                parts = key.split(sep)
                d = result
                for part in parts[:-1]:
                    if part not in d:
                        d[part] = {}
                    d = d[part]
                d[parts[-1]] = value
        return result

    def _dict_to_xml(self, data: Dict[str, Any], parent_element: ET.Element):
        """Convert dictionary to XML structure"""
        for key, value in data.items():
            if isinstance(value, dict):
                child = ET.SubElement(parent_element, key)
                self._dict_to_xml(value, child)
            else:
                child = ET.SubElement(parent_element, key)
                child.text = str(value)

    def _xml_to_dict(self, element: ET.Element) -> Dict[str, Any]:
        """Convert XML to dictionary structure"""
        result = {}
        for child in element:
            if len(child) > 0:
                result[child.tag] = self._xml_to_dict(child)
            else:
                result[child.tag] = child.text
        return result

    def _validate_imported_data(self, data: Dict[str, Any]) -> List[str]:
        """Validate imported configuration data"""
        errors = []
        
        # Validate rooms
        for room_id, room_data in data.get('rooms', {}).items():
            room_errors = self.validator.validate_room(room_data)
            errors.extend(room_errors)
            
        # Validate rack types
        for type_id, type_data in data.get('rack_types', {}).items():
            type_errors = self.validator.validate_rack_type(type_data)
            errors.extend(type_errors)
            
        return errors
