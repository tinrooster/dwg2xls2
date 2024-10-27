from typing import List, Dict, Any
from dataclasses import dataclass
from .it_patterns import ITDevice, ITDeviceAnalyzer, ITPatterns
import logging

@dataclass
class RackMount:
    """Represents a rack-mounted device"""
    device: ITDevice
    u_position: int
    u_height: int
    rack_name: str

class RackLayoutAnalyzer:
    """Analyzes rack layouts in drawings"""

    def __init__(self):
        self.device_analyzer = ITDeviceAnalyzer()
        self.logger = logging.getLogger(__name__)

    async def analyze_rack_layout(self, 
                                entities: List[Dict[str, Any]], 
                                rack_bounds: tuple[float, float, float, float]) -> Dict[str, Any]:
        """Analyze rack layout within specified bounds"""
        rack_info = {
            'rack_name': self._find_rack_name(entities),
            'devices': [],
            'total_u': 42,  # Default, can be adjusted
            'used_u': 0
        }

        # Sort entities by vertical position (Y coordinate)
        sorted_entities = sorted(
            entities, 
            key=lambda e: e.get('position', (0, 0))[1], 
            reverse=True
        )

        current_u = 1
        for entity in sorted_entities:
            device = self.device_analyzer.analyze_device(
                entity.get('text', ''),
                entity.get('position', (0, 0))
            )
            if device:
                mount = RackMount(
                    device=device,
                    u_position=current_u,
                    u_height=device.rack_units,
                    rack_name=rack_info['rack_name']
                )
                rack_info['devices'].append(mount)
                current_u += device.rack_units
                rack_info['used_u'] += device.rack_units

        return rack_info

    def _find_rack_name(self, entities: List[Dict[str, Any]]) -> str:
        """Find rack name from entities"""
        rack_pattern = ITPatterns.LOCATION_PATTERNS['rack']
        for entity in entities:
            text = entity.get('text', '')
            match = re.search(rack_pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)
        return "UNKNOWN_RACK"
