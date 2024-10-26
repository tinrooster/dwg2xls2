from typing import List, Dict, Any
import logging

class DrawingContentAnalyzer:
    """Analyzes drawing content using pattern matchers"""

    def __init__(self):
        self.pattern_analyzer = PatternAnalyzer()
        self.circuit_identifier = CircuitIdentifier()
        self.device_identifier = DeviceIdentifier()
        self.logger = logging.getLogger(__name__)

    async def analyze_entity(self, entity: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a single drawing entity"""
        analysis = {
            'entity_type': entity.get('type', 'unknown'),
            'matches': [],
            'identified_elements': {}
        }

        # Analyze text content
        text_content = entity.get('text', '') or entity.get('block_name', '')
        if text_content:
            # Get pattern matches
            matches = self.pattern_analyzer.analyze_text(text_content)
            analysis['matches'] = [
                {
                    'type': match.pattern_type,
                    'value': match.value,
                    'confidence': match.confidence
                }
                for match in matches
            ]

            # Identify circuits
            if any(m.pattern_type.startswith('CIRCUIT_PATTERNS') for m in matches):
                analysis['identified_elements']['circuit'] = \
                    self.circuit_identifier.identify_circuit_type(text_content)

            # Identify devices
            if any(m.pattern_type.startswith('DEVICE_PATTERNS') for m in matches):
                analysis['identified_elements']['device'] = \
                    self.device_identifier.identify_device(text_content)

        return analysis

    async def analyze_drawing_section(self, 
                                    entities: List[Dict[str, Any]], 
                                    area: tuple[float, float, float, float]) -> Dict[str, Any]:
        """Analyze a specific section of the drawing"""
        section_analysis = {
            'bounds': area,
            'entities': [],
            'identified_elements': {
                'circuits': [],
                'devices': [],
                'annotations': []
            }
        }

        for entity in entities:
            if self._is_entity_in_bounds(entity, area):
                analysis = await self.analyze_entity(entity)
                section_analysis['entities'].append(analysis)

                # Categorize identified elements
                if 'circuit' in analysis['identified_elements']:
                    section_analysis['identified_elements']['circuits'].append(
                        analysis['identified_elements']['circuit']
                    )
                if 'device' in analysis['identified_elements']:
                    section_analysis['identified_elements']['devices'].append(
                        analysis['identified_elements']['device']
                    )

        return section_analysis

    @staticmethod
    def _is_entity_in_bounds(entity: Dict[str, Any], 
                            bounds: tuple[float, float, float, float]) -> bool:
        """Check if entity is within specified bounds"""
        if 'position' not in entity:
            return False
        
        x, y = entity['position']
        x1, y1, x2, y2 = bounds
        return x1 <= x <= x2 and y1 <= y <= y2
