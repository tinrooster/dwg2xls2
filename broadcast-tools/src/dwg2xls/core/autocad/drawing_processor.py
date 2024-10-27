from typing import Dict, List, Any
from pathlib import Path
import logging

from .lt_connector import LTAutoCADConnector
from .data_extractors import (
    DrawingAnalyzer, 
    DeviceExtractor, 
    CircuitExtractor, 
    DrawingType
)

class DrawingProcessor:
    """Processes AutoCAD drawings to extract relevant information"""

    def __init__(self, drawing_path: Path):
        self.drawing_path = drawing_path
        self.logger = logging.getLogger(__name__)
        self.analyzer = DrawingAnalyzer()
        self.device_extractor = DeviceExtractor()
        self.circuit_extractor = CircuitExtractor()

    async def process_drawing(self) -> Dict[str, Any]:
        """Process drawing and extract all relevant information"""
        try:
            async with LTAutoCADConnector(self.drawing_path) as connector:
                # Get all entities
                text_entities = await connector.get_all_text()
                block_entities = await connector.get_block_attributes()
                all_entities = text_entities + block_entities

                # Determine drawing type
                drawing_type = self.analyzer.determine_drawing_type(all_entities)

                result = {
                    'drawing_type': drawing_type.value,
                    'file_path': str(self.drawing_path),
                    'devices': [],
                    'circuits': {},
                }

                # Extract information based on drawing type
                if drawing_type == DrawingType.FLOOR_PLAN:
                    result['devices'] = await self.device_extractor.extract_devices_from_floorplan(
                        block_entities
                    )
                elif drawing_type == DrawingType.CIRCUIT_DIAGRAM:
                    result['circuits'] = await self.circuit_extractor.extract_circuits(
                        all_entities
                    )

                return result

        except Exception as e:
            self.logger.error(f"Error processing drawing {self.drawing_path}: {str(e)}")
            raise
