import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from abc import ABC, abstractmethod
import ezdxf
from ezdxf.document import Drawing
from enum import Enum

logger = logging.getLogger('AutoCADExcelTool.AutoCADManager')

class BaseAutoCADConnector(ABC):
    """Base class for AutoCAD file handling"""
    
    @abstractmethod
    def get_drawing_info(self, file_path: str) -> Optional[Dict[str, Any]]:
        pass

class AutoCADConnector(BaseAutoCADConnector):
    """Concrete implementation of AutoCAD connector"""
    
    def get_drawing_info(self, file_path: str) -> Optional[Dict[str, Any]]:
        from ..utils.drawing_processor import DrawingProcessor
        processor = DrawingProcessor()
        return processor.extract_drawing_data(file_path)

class DXFConnector(BaseAutoCADConnector):
    """Handles reading DXF files using ezdxf"""
    
    def __init__(self):
        self.doc: Optional[Drawing] = None
        
    def get_drawing_info(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Extract information from a DXF file"""
        try:
            logger.debug(f"Opening drawing: {file_path}")
            
            # Load the DXF drawing
            self.doc = ezdxf.readfile(file_path)
            
            # Get modelspace
            msp = self.doc.modelspace()
            
            # Extract basic information
            drawing_info = {
                'filename': Path(file_path).name,
                'project_id': self._get_project_id(),
                'cable_numbers': self._get_cable_numbers(msp),
                'last_modified': datetime.fromtimestamp(
                    Path(file_path).stat().st_mtime
                ).strftime('%Y-%m-%d %H:%M:%S')
            }
            
            return drawing_info
            
        except Exception as e:
            logger.exception(f"Error getting drawing info from {file_path}")
            raise
            
    def _get_project_id(self) -> str:
        """Extract project ID from drawing"""
        try:
            return self.doc.header.get('$PROJECTNAME', 'UNKNOWN')
        except:
            return 'UNKNOWN'
        
    def _get_cable_numbers(self, msp) -> List[str]:
        """Extract cable numbers from drawing modelspace"""
        cable_numbers = []
        
        logger.debug("Starting cable number extraction")
        
        try:
            # Get all text entities
            text_entities = msp.query('TEXT MTEXT')
            
            for entity in text_entities:
                try:
                    # Get text content based on entity type
                    if entity.dxftype() == 'TEXT':
                        text = entity.dxf.text
                    elif entity.dxftype() == 'MTEXT':
                        text = entity.text
                    else:
                        continue
                        
                    logger.debug(f"Found text: {text}")
                    
                    # Check for cable number pattern
                    if text and any(text.upper().startswith(prefix) for prefix in ['CABLE-', 'CBL-']):
                        cable_numbers.append(text)
                        logger.debug(f"Found cable number: {text}")
                        
                except Exception as e:
                    logger.debug(f"Error reading text entity: {e}")
                    continue
            
            return cable_numbers or ["NO-CABLES-FOUND"]
            
        except Exception as e:
            logger.error(f"Error during cable number extraction: {e}")
            return ["ERROR-EXTRACTING-CABLES"]

class DWGConnector(DXFConnector):
    """Handles reading DWG files using ezdxf"""
    # Inherits all functionality from DXFConnector since ezdxf can handle both
    pass

class ConnectorType(Enum):
    """Enum for different types of AutoCAD connectors"""
    DXF = "dxf"
    DWG = "dwg"

class ConnectorFactory:
    """Factory class for creating AutoCAD connectors"""
    
    @staticmethod
    def create_connector(connector_type: ConnectorType, file_path: Optional[str] = None) -> Optional[BaseAutoCADConnector]:
        """Create and return appropriate connector based on type and file extension"""
        if file_path:
            ext = Path(file_path).suffix.lower()
            if ext == '.dwg':
                logger.debug("DWG file detected - using DWG connector")
                return DWGConnector()
            elif ext == '.dxf':
                logger.debug("DXF file detected - using DXF connector")
                return DXFConnector()
        
        # Default to DXF connector
        return DXFConnector()
