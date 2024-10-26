from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum, auto
import re
import logging

class BroadcastDeviceType(Enum):
    """Broadcast equipment types"""
    ROUTER = auto()          # Signal routers
    FRAME = auto()           # Frame/chassis systems
    PATCH_PANEL = auto()     # Patch panels
    RTR = auto()             # RTR blocks from diagram
    FSK = auto()             # FSK processing
    GPIO = auto()            # GPIO interfaces
    RELAY = auto()           # Relay systems
    TALLY = auto()           # Tally systems
    ENCODER = auto()         # Encoding systems
    MULTIVIEWER = auto()     # Multiviewer systems
    CONNECT_SERVER = auto()  # Connection servers

@dataclass
class PatchPoint:
    """Represents a patch panel connection point"""
    frame: str          # e.g., "TJ07"
    frame_number: str   # e.g., "FR1"
    slot: str          # e.g., "SL1"
    row: int
    position: int
    connected_to: Optional[str] = None

@dataclass
class SignalPath:
    """Represents a signal flow path"""
    source: str
    destination: str
    signal_type: str
    intermediate_devices: List[str] = None
    gpio_triggers: List[str] = None

class BroadcastPatterns:
    """Patterns for broadcast equipment and connections"""
    
    # Frame and Slot Patterns
    FRAME_PATTERNS = {
        'frame_slot': r'([A-Z]+[0-9]+)\s*FR([0-9]+)\s*SL([0-9]+)',  # TJ07 FR1 SL1
        'frame_id': r'[A-Z]+[0-9]+',  # TJ07, TH03
        'slot_id': r'(?:SL|SLOT)[0-9]+',  # SL1, SLOT12
    }

    # Signal Flow Patterns
    SIGNAL_PATTERNS = {
        'rtr_block': r'RTR\s*(?:Src|Dst)?\s*[0-9]+',  # RTR Src 384
        'fsk_block': r'(?:TK04|TX04)\s*FSK',  # TK04 FSK
        'stereo_path': r'[0-9]+\.[0-9]+\s*STEREO',  # 7.1 STEREO
        'connect_server': r'Connect\s*server\s*[0-9]+',  # Connect server 1
    }

    # Control and Trigger Patterns
    CONTROL_PATTERNS = {
        'gpio': r'GPIO\s*[0-9]+',  # GPIO 14
        'relay': r'(?:TX04|TK04)\s*RELAY\s*[0-9]+',  # TX04 RELAY 2
        'tally': r'(?:TG11|TALLY)\s*[0-9]+',  # TG11, TALLY 1
        'pcr': r'PCR[0-9]+',  # PCR2
    }

    # Device Connection Patterns
    CONNECTION_PATTERNS = {
        'patch_connection': r'([A-Z][0-9]+)\s*->\s*([A-Z][0-9]+)',  # TJ03 -> TJ09
        'signal_flow': r'([A-Z0-9]+)\s*→\s*([A-Z0-9]+)',  # Using arrow symbol
        'dwg_reference': r'DWG\'?S?\s*[0-9]+',  # DWG's 22749
    }

class BroadcastAnalyzer:
    """Analyzes broadcast equipment and connections"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._compile_patterns()

    def _compile_patterns(self):
        """Compile all regex patterns"""
        self.compiled_patterns = {}
        for category, patterns in vars(BroadcastPatterns).items():
            if isinstance(patterns, dict):
                self.compiled_patterns[category] = {
                    name: re.compile(pattern, re.IGNORECASE)
                    for name, pattern in patterns.items()
                }

    def parse_patch_point(self, text: str) -> Optional[PatchPoint]:
        """Parse patch panel point information"""
        try:
            match = self.compiled_patterns['FRAME_PATTERNS']['frame_slot'].match(text)
            if match:
                frame, fr_num, slot = match.groups()
                return PatchPoint(
                    frame=frame,
                    frame_number=f"FR{fr_num}",
                    slot=f"SL{slot}",
                    row=0,  # Set from additional data
                    position=0  # Set from additional data
                )
        except Exception as e:
            self.logger.error(f"Error parsing patch point {text}: {str(e)}")
        return None

    def analyze_signal_flow(self, entities: List[Dict[str, Any]]) -> List[SignalPath]:
        """Analyze signal flow from drawing entities"""
        signal_paths = []
        current_path = None

        for entity in entities:
            text = entity.get('text', '')
            
            # Look for signal source/destination
            if 'RTR' in text or 'FSK' in text:
                if current_path is None:
                    current_path = SignalPath(
                        source=text,
                        destination="",
                        signal_type="",
                        intermediate_devices=[],
                        gpio_triggers=[]
                    )
                else:
                    current_path.destination = text
                    signal_paths.append(current_path)
                    current_path = None

            # Check for GPIO triggers
            gpio_match = self.compiled_patterns['CONTROL_PATTERNS']['gpio'].search(text)
            if gpio_match and current_path:
                current_path.gpio_triggers.append(gpio_match.group(0))

        return signal_paths

    def parse_patch_connections(self, text: str) -> Tuple[str, str]:
        """Parse patch panel connections"""
        match = self.compiled_patterns['CONNECTION_PATTERNS']['patch_connection'].search(text)
        if match:
            return match.group(1), match.group(2)
        return None, None

    def identify_device_type(self, text: str) -> Optional[BroadcastDeviceType]:
        """Identify broadcast device type from text"""
        type_indicators = {
            'RTR': BroadcastDeviceType.RTR,
            'FSK': BroadcastDeviceType.FSK,
            'GPIO': BroadcastDeviceType.GPIO,
            'RELAY': BroadcastDeviceType.RELAY,
            'TALLY': BroadcastDeviceType.TALLY,
            'CONNECT SERVER': BroadcastDeviceType.CONNECT_SERVER,
            'MULTIVIEWER': BroadcastDeviceType.MULTIVIEWER
        }

        for indicator, device_type in type_indicators.items():
            if indicator in text.upper():
                return device_type
        return None
