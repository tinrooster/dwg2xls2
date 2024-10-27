from typing import Dict, List, Any, Optional, Pattern, Tuple
import re
from dataclasses import dataclass
from enum import Enum
import logging

@dataclass
class MatchResult:
    """Stores the result of a pattern match"""
    matched: bool
    value: Optional[str] = None
    confidence: float = 0.0
    pattern_type: str = ""
    additional_info: Dict[str, Any] = None

class ElectricalPatterns:
    """Comprehensive patterns for electrical drawing elements"""
    
    # Circuit Identifiers
    CIRCUIT_PATTERNS = {
        'mcr_circuit': r'MCR\s*[0-9]{3,4}',  # MCR1038, MCR 1039
        'panel_circuit': r'[A-Z]{1,2}[0-9]{1,2}-[0-9]{1,3}',  # A1-103, LP2-24
        'circuit_reference': r'C[A-Z][0-9]{2,3}',  # CA02, CB103
        'circuit_number': r'(?:CKT|CCT|CIRCUIT)\s*#?\s*[0-9]{1,3}',  # Circuit #12, CKT 24
    }

    # Device Identifiers
    DEVICE_PATTERNS = {
        'device_count': r'(?:DEVICE|DEV)\.?\s*(?:COUNT|QTY|QUANTITY)?\s*[:=]?\s*(\d+)',
        'fixture_type': r'(?:FXT|FIXTURE)\s*TYPE\s*[:=]?\s*([A-Z][0-9]{1,2})',
        'device_id': r'(?:DEV|DEVICE)\s*ID\s*[:=]?\s*([A-Z0-9\-]+)',
        'switch_id': r'SW\s*[0-9]{1,3}[A-Z]?',  # SW12, SW12A
        'receptacle': r'RECEP(?:TACLE)?\s*[0-9]{1,3}',  # RECEP12, RECEPTACLE 24
    }

    # Room and Location
    LOCATION_PATTERNS = {
        'room_number': r'(?:RM|ROOM)\s*[A-Z]?-?[0-9]{3,4}[A-Z]?',  # RM-123, ROOM A-101
        'floor_level': r'(?:FLOOR|LVL|LEVEL)\s*[0-9]{1,2}',
        'area_name': r'(?:AREA|ZONE)\s*[A-Z][0-9]?',
        'grid_reference': r'[A-Z][0-9]+/[0-9]+',  # A1/23, B12/45
    }

    # Electrical Properties
    ELECTRICAL_PATTERNS = {
        'voltage': r'(?:120|277|480|208|240)\s*V(?:AC)?',
        'phase': r'(?:1|3)(?:\s*-|\s+)(?:PH|PHASE|Φ)',
        'amperage': r'[0-9]+\s*A(?:MP)?',
        'wire_size': r'#\s*[0-9]{1,2}\s*(?:AWG)?',
        'conduit_size': r'[0-9]/[0-9]"[C]?',  # 3/4"C, 1/2"
    }

    # Drawing Annotations
    ANNOTATION_PATTERNS = {
        'revision': r'REV(?:ISION)?\s*[0-9]+',
        'detail': r'DETAIL\s*[A-Z0-9]/[A-Z0-9]',
        'scale': r'SCALE\s*(?:1|3|6)"\s*=\s*(?:1|2|4)\'(?:-|_)0"',
        'sheet_number': r'(?:SHT|SHEET)\s*[A-Z][0-9]{1,2}',
    }

class PatternAnalyzer:
    """Analyzes text content using electrical patterns"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._compile_patterns()

    def _compile_patterns(self):
        """Compile all regex patterns for efficiency"""
        self.compiled_patterns = {}
        for category, patterns in vars(ElectricalPatterns).items():
            if isinstance(patterns, dict):
                self.compiled_patterns[category] = {
                    name: re.compile(pattern, re.IGNORECASE)
                    for name, pattern in patterns.items()
                }

    def analyze_text(self, text: str) -> List[MatchResult]:
        """Analyze text content against all patterns"""
        results = []
        for category, patterns in self.compiled_patterns.items():
            for pattern_name, compiled_pattern in patterns.items():
                match = compiled_pattern.search(text)
                if match:
                    results.append(MatchResult(
                        matched=True,
                        value=match.group(0),
                        confidence=1.0,
                        pattern_type=f"{category}.{pattern_name}",
                        additional_info={'groups': match.groups()}
                    ))
        return results

class CircuitIdentifier:
    """Specialized identifier for circuit-related information"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def identify_circuit_type(self, circuit_id: str) -> Dict[str, Any]:
        """Identify circuit type and properties from ID"""
        patterns = {
            'mcr': (r'MCR\s*(?P<number>[0-9]{3,4})', 'Motor Control Relay'),
            'panel': (r'(?P<panel>[A-Z]{1,2})(?P<circuit>[0-9]{1,3})', 'Panel Circuit'),
            'emergency': (r'E(?P<panel>[A-Z])(?P<number>[0-9]{2,3})', 'Emergency Circuit'),
            'control': (r'C(?P<type>[A-Z])(?P<number>[0-9]{2,3})', 'Control Circuit')
        }

        for circuit_type, (pattern, description) in patterns.items():
            match = re.match(pattern, circuit_id, re.IGNORECASE)
            if match:
                return {
                    'type': circuit_type,
                    'description': description,
                    'components': match.groupdict(),
                    'original': circuit_id
                }
        
        return {'type': 'unknown', 'original': circuit_id}

class DeviceIdentifier:
    """Specialized identifier for electrical devices"""

    DEVICE_TYPES = {
        'L': 'Lighting',
        'R': 'Receptacle',
        'S': 'Switch',
        'M': 'Motor',
        'P': 'Panel',
        'T': 'Transformer',
        'D': 'Distribution'
    }

    def identify_device(self, text: str) -> Dict[str, Any]:
        """Identify device type and properties"""
        device_info = {
            'type': 'unknown',
            'properties': {},
            'original_text': text
        }

        # Check for device count
        count_match = re.search(r'(?:COUNT|QTY)\s*[:=]?\s*(\d+)', text, re.IGNORECASE)
        if count_match:
            device_info['properties']['count'] = int(count_match.group(1))

        # Check for device type prefix
        type_match = re.match(r'([A-Z])[0-9-]', text)
        if type_match and type_match.group(1) in self.DEVICE_TYPES:
            device_info['type'] = self.DEVICE_TYPES[type_match.group(1)]

        return device_info
