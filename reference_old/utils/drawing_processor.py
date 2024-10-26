import logging
import os
from typing import List, Dict, Any, Optional
import ezdxf
import re
from pathlib import Path

# Get module-specific logger
logger = logging.getLogger('AutoCADExcelTool.DrawingProcessor')

class DrawingProcessor:
    def __init__(self):
        logger.debug("Initializing DrawingProcessor")

    def analyze_drawing_structure(self, filepath: str) -> Dict[str, Any]:
        """Analyze drawing structure to identify layers and patterns"""
        try:
            logger.debug(f"Analyzing drawing structure: {filepath}")
            
            # Initialize analysis results
            analysis = {
                'layers': set(),
                'text_patterns': set(),
                'entity_types': set(),
                'text_by_layer': {}
            }
            
            # Check file extension
            ext = Path(filepath).suffix.lower()
            
            # Only analyze DXF files for now
            if ext == '.dxf':
                doc = ezdxf.readfile(filepath)
                msp = doc.modelspace()
                
                # Collect layer names
                for layer in doc.layers:
                    layer_name = layer.dxf.name
                    analysis['layers'].add(layer_name)
                    analysis['text_by_layer'][layer_name] = []
                
                # Analyze entities
                for entity in msp:
                    # Track entity types
                    entity_type = entity.dxftype()
                    analysis['entity_types'].add(entity_type)
                    
                    # For text entities, collect by layer
                    if entity_type == 'TEXT':
                        layer_name = entity.dxf.layer
                        text = str(entity.dxf.text)  # Ensure it's a string
                        
                        # Initialize layer if not exists
                        if layer_name not in analysis['text_by_layer']:
                            analysis['text_by_layer'][layer_name] = []
                        
                        # Add text to layer collection
                        if text:
                            analysis['text_by_layer'][layer_name].append(text)
                            analysis['text_patterns'].add(text)
            
            # Convert sets to lists for JSON serialization
            return {
                'layers': sorted(list(analysis['layers'])),
                'text_patterns': sorted(list(analysis['text_patterns'])),
                'entity_types': sorted(list(analysis['entity_types'])),
                'text_by_layer': {
                    k: sorted(v) for k, v in analysis['text_by_layer'].items()
                }
            }
            
        except Exception as e:
            logger.exception(f"Error analyzing drawing {filepath}:")
            raise

    def extract_drawing_data(self, filepath: str) -> List[Dict[str, Any]]:
        """Extract data from a drawing file"""
        try:
            logger.debug(f"Processing drawing: {filepath}")
            
            # Check file extension
            ext = Path(filepath).suffix.lower()
            filename = Path(filepath).name
            filename_no_ext = Path(filepath).stem
            
            # Initialize basic drawing data
            drawing_data = [{
                'NUMBER': '',
                'DWG': filename_no_ext,  # Filename without extension
                'ORIGIN': '',
                'DEST': '',
                'Alternate Dwg': '',
                'Wire Type': '',
                'Length': '',
                'Note': '',
                'Project ID': '',
                'flag': 'dwgimport',
                'File Name': filename  # Full filename
            }]
            
            # Only try to read DXF files with ezdxf
            if ext == '.dxf':
                doc = ezdxf.readfile(filepath)
                msp = doc.modelspace()
                
                # Process entities
                for entity in msp:
                    if entity.dxftype() == 'TEXT':
                        # Process text entities
                        pass
            
            return drawing_data
            
        except Exception as e:
            logger.exception(f"Error processing drawing {filepath}:")
            raise

    def _extract_cable_number(self, filepath: str) -> str:
        """Extract cable number from filename or drawing content"""
        try:
            # Extract from filename first (e.g., CABLE_CBL-001_20241024.dwg)
            filename = Path(filepath).stem
            if 'CBL-' in filename.upper():
                parts = filename.split('_')
                for part in parts:
                    if 'CBL-' in part.upper():
                        return part
            return 'CBL-UNKNOWN'
        except Exception as e:
            logger.warning(f"Could not extract cable number: {e}")
            return 'CBL-ERROR'
            
    def _extract_project_id(self, filepath: str) -> str:
        """Extract project ID from drawing path or content"""
        try:
            # Extract from parent folder name
            project_folder = Path(filepath).parent.name
            if project_folder.startswith('PRJ-'):
                return project_folder
            return 'PRJ-UNKNOWN'
        except Exception as e:
            logger.warning(f"Could not extract project ID: {e}")
            return 'PRJ-ERROR'
            
    def _extract_origin(self, filepath: str) -> str:
        """Extract origin information"""
        # For now, return placeholder
        return 'ORIGIN-TBD'
        
    def _extract_destination(self, filepath: str) -> str:
        """Extract destination information"""
        # For now, return placeholder
        return 'DEST-TBD'
        
    def _extract_wire_type(self, filepath: str) -> str:
        """Extract wire type information"""
        # For now, return placeholder
        return 'TYPE-TBD'
        
    def _extract_length(self, filepath: str) -> str:
        """Extract cable length information"""
        # For now, return placeholder
        return 'LENGTH-TBD'
