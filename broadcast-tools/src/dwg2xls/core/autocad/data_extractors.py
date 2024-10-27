from typing import Dict, List, Any, Optional, Pattern
import re
from dataclasses import dataclass
from enum import Enum
import difflib
import logging
from pathlib import Path

@dataclass
class ExtractedDevice:
    """Represents an extracted device with its properties"""
    id: str
    type: str
    count: int
    circuit: str
    location: tuple[float, float]
    attributes: Dict[str, Any]

class DrawingType(Enum):
    FLOOR_PLAN = "floor_plan"
    CIRCUIT_DIAGRAM = "circuit_diagram"
    RISER_DIAGRAM = "riser_diagram"
    UNKNOWN = "unknown"

class PatternMatcher:
    """Handles pattern matching for various drawing elements"""
    
    # Common patterns in electrical drawings
    PATTERNS = {
        'circuit_id': r'(?:MCR|CR|C)[0-9]{3,4}',
        'device_count': r'(?:DEVICE\s+COUNT|COUNT):\s*(\d+)',
        'room_number': r'(?:RM|ROOM)\s*(\d{3,4})',
        'panel_name': r'PANEL\s*([A-Z0-9\-]+)',
        'device_id': r'[A-Z]{1,2}-\d{2,3}',
    }

    @staticmethod
    def get_best_match(text: str, possible_matches: List[str], threshold: float = 0.85) -> Optional[str]:
        """Find the best matching string using fuzzy matching"""
        matches = difflib.get_close_matches(text, possible_matches, n=1, cutoff=threshold)
        return matches[0] if matches else None

    @staticmethod
    def extract_with_pattern(text: str, pattern: str) -> Optional[str]:
        """Extract text matching a specific pattern"""
        match = re.search(pattern, text, re.IGNORECASE)
        return match.group(0) if match else None

class DrawingAnalyzer:
    """Analyzes drawing content to determine type and extract relevant data"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def determine_drawing_type(self, entities: List[Dict[str, Any]]) -> DrawingType:
        """Determine drawing type based on content analysis"""
        circuit_indicators = ['MCR', 'CIRCUIT', 'PANEL']
        floor_indicators = ['ROOM', 'DEVICE COUNT', 'FLOOR']
        
        text_content = ' '.join(str(e.get('text', '')) for e in entities)
        
        if any(ind in text_content.upper() for ind in circuit_indicators):
            return DrawingType.CIRCUIT_DIAGRAM
        elif any(ind in text_content.upper() for ind in floor_indicators):
            return DrawingType.FLOOR_PLAN
        return DrawingType.UNKNOWN

class DeviceExtractor:
    """Extracts device information from drawings"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.pattern_matcher = PatternMatcher()

    async def extract_devices_from_floorplan(self, 
                                           entities: List[Dict[str, Any]]) -> List[ExtractedDevice]:
        """Extract device information from floor plan drawings"""
        devices = []
        device_blocks = self._filter_device_blocks(entities)
        
        for block in device_blocks:
            try:
                device = self._parse_device_block(block)
                if device:
                    devices.append(device)
            except Exception as e:
                self.logger.warning(f"Failed to parse device block: {str(e)}")
                continue
                
        return devices

    def _filter_device_blocks(self, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter entities to find device blocks"""
        return [
            entity for entity in entities
            if isinstance(entity.get('block_name', ''), str) and
            ('DEVICE' in entity['block_name'].upper() or
             'FIXTURE' in entity['block_name'].upper())
        ]

    def _parse_device_block(self, block: Dict[str, Any]) -> Optional[ExtractedDevice]:
        """Parse a device block into structured data"""
        try:
            attrs = block.get('attributes', {})
            
            # Extract device count
            count_text = next((v for k, v in attrs.items() 
                             if 'COUNT' in k.upper()), '0')
            count = int(re.search(r'\d+', count_text).group(0))
            
            # Extract circuit ID
            circuit = next((v for k, v in attrs.items() 
                          if 'CIRCUIT' in k.upper()), '')
            
            return ExtractedDevice(
                id=block.get('block_name', ''),
                type=self._determine_device_type(block),
                count=count,
                circuit=circuit,
                location=block.get('position', (0, 0)),
                attributes=attrs
            )
        except Exception as e:
            self.logger.error(f"Error parsing device block: {str(e)}")
            return None

    def _determine_device_type(self, block: Dict[str, Any]) -> str:
        """Determine device type from block attributes"""
        block_name = block.get('block_name', '').upper()
        if 'LIGHT' in block_name:
            return 'LIGHTING'
        elif 'RECEPT' in block_name:
            return 'RECEPTACLE'
        elif 'SWITCH' in block_name:
            return 'SWITCH'
        return 'UNKNOWN'

class CircuitExtractor:
    """Extracts circuit information from drawings"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.pattern_matcher = PatternMatcher()

    async def extract_circuits(self, entities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract circuit information from circuit diagrams"""
        circuits = {}
        
        # Find circuit IDs
        circuit_texts = [
            entity for entity in entities
            if isinstance(entity.get('text', ''), str) and
            re.search(PatternMatcher.PATTERNS['circuit_id'], entity.get('text', ''))
        ]
        
        for circuit_text in circuit_texts:
            try:
                circuit_id = self.pattern_matcher.extract_with_pattern(
                    circuit_text['text'],
                    PatternMatcher.PATTERNS['circuit_id']
                )
                if circuit_id:
                    circuits[circuit_id] = self._analyze_circuit_connections(
                        circuit_id, entities, circuit_text['position']
                    )
            except Exception as e:
                self.logger.warning(f"Failed to analyze circuit {circuit_id}: {str(e)}")
                continue
                
        return circuits

    def _analyze_circuit_connections(self, 
                                   circuit_id: str, 
                                   entities: List[Dict[str, Any]], 
                                   position: tuple) -> Dict[str, Any]:
        """Analyze connections and properties of a circuit"""
        nearby_entities = self._find_nearby_entities(position, entities)
        return {
            'id': circuit_id,
            'connected_devices': self._find_connected_devices(nearby_entities),
            'panel': self._find_associated_panel(nearby_entities),
            'properties': self._extract_circuit_properties(nearby_entities)
        }

    def _find_nearby_entities(self, 
                            position: tuple, 
                            entities: List[Dict[str, Any]], 
                            radius: float = 50.0) -> List[Dict[str, Any]]:
        """Find entities within a radius of a position"""
        return [
            entity for entity in entities
            if entity.get('position') and
            self._calculate_distance(position, entity['position']) <= radius
        ]

    @staticmethod
    def _calculate_distance(p1: tuple, p2: tuple) -> float:
        """Calculate distance between two points"""
        return ((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2) ** 0.5
