from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from enum import Enum, auto
import re

class SignalType(Enum):
    """Broadcast signal types"""
    ACUITY = auto()      # Acuity production switcher
    MDA = auto()         # Multi-definition amplifier
    MDB = auto()         # Distribution amplifier
    MDC = auto()         # Distribution control
    RSW = auto()         # Router switch
    CAM = auto()         # Camera
    GVG = auto()         # Grass Valley Group
    HEAD_FIBER = auto()  # Fiber optic head
    ROUTER = auto()      # Router
    EQX = auto()         # Equipment matrix

@dataclass
class SignalConnection:
    """Represents a broadcast signal connection"""
    number: str              # e.g., "109241"
    drawing: str            # e.g., "22738"
    origin: str             # e.g., "TH03 PC2 ACUITY OUT-K1"
    destination: str        # e.g., "TK01 - MDA-1-16(PC2-MV1)RSW-82"
    alternate_drawing: str   # e.g., "22070"
    wire_type: str          # e.g., "1694 Yellow"
    notes: str              # e.g., "EQX INPUT CARD #5"
    
    # Parsed components
    origin_device: str      # e.g., "TH03"
    origin_port: str        # e.g., "PC2"
    dest_device: str        # e.g., "TK01"
    dest_port: str          # e.g., "MDA-1-16"
    rsw_number: str         # e.g., "RSW-82"

@dataclass
class CameraChain:
    """Represents a camera signal chain"""
    camera_id: str          # e.g., "CAMERA-4"
    net_id: str            # e.g., "NET1"
    sd_out: str            # e.g., "SD OUT"
    gvg_id: str            # e.g., "GVG (VTC)"
    fiber_id: str          # e.g., "HEAD-FIBER"
    signal_paths: List[str] # Connected signal paths

class BroadcastSignalPatterns:
    """Enhanced patterns for broadcast signals"""
    
    # Device and Port Patterns
    DEVICE_PATTERNS = {
        'acuity': r'(?P<device>T[HK][0-9]+)\s*(?P<port>PC[23])\s*ACUITY\s*OUT-(?P<output>[A-Z][0-9])',
        'mda': r'(?P<device>T[HK][0-9]+)\s*-\s*MDA-(?P<unit>[0-9]-[0-9]+)',
        'mdb': r'(?P<device>T[HK][0-9]+)\s*-\s*MDB-(?P<unit>[0-9]-[0-9]+)',
        'mdc': r'(?P<device>T[HK][0-9]+)\s*-\s*MDC-(?P<unit>[0-9]-[0-9]+)',
        'rsw': r'RSW-(?P<number>[0-9]+)',
        'camera': r'CAMERA-(?P<number>[0-9]+)',
        'router': r'(?P<type>TEST|ROUTER)\s*(?P<port>INPUT|OUTPUT)',
    }

    # Signal Flow Patterns
    SIGNAL_PATTERNS = {
        'mv_signal': r'(?P<port>PC[23]-MV[0-9])',
        'net': r'NET[0-9]',
        'sd_out': r'SD\s*OUT',
        'gvg': r'GVG\s*\(VTC\)',
        'fiber': r'HEAD-FIBER',
    }

    # Connection Reference Patterns
    CONNECTION_PATTERNS = {
        'wire': r'(?P<type>1694)\s*(?P<color>Yellow)',
        'eqx_card': r'EQX\s*INPUT\s*CARD\s*#(?P<number>[0-9]+)',
        'drawing': r'DWG\s*(?P<number>[0-9]+)',
    }

class SignalFlowAnalyzer:
    """Analyzes broadcast signal flow"""

    def parse_connection(self, row_data: Dict[str, str]) -> SignalConnection:
        """Parse connection data from spreadsheet row"""
        connection = SignalConnection(
            number=row_data.get('NUMBER', ''),
            drawing=row_data.get('DWG', ''),
            origin=row_data.get('ORIGIN', ''),
            destination=row_data.get('DEST', ''),
            alternate_drawing=row_data.get('Alternate Dwg', ''),
            wire_type=row_data.get('Wire Type', ''),
            notes=row_data.get('Notes', ''),
            origin_device='',
            origin_port='',
            dest_device='',
            dest_port='',
            rsw_number=''
        )

        # Parse origin components
        origin_match = re.match(
            BroadcastSignalPatterns.DEVICE_PATTERNS['acuity'],
            connection.origin
        )
        if origin_match:
            connection.origin_device = origin_match.group('device')
            connection.origin_port = origin_match.group('port')

        # Parse destination components
        dest_parts = connection.destination.split('-', 1)
        if len(dest_parts) > 1:
            connection.dest_device = dest_parts[0].strip()
            
            # Extract RSW number
            rsw_match = re.search(
                BroadcastSignalPatterns.DEVICE_PATTERNS['rsw'],
                connection.destination
            )
            if rsw_match:
                connection.rsw_number = rsw_match.group(0)

            # Extract destination port
            for pattern_name in ['mda', 'mdb', 'mdc']:
                port_match = re.search(
                    BroadcastSignalPatterns.DEVICE_PATTERNS[pattern_name],
                    connection.destination
                )
                if port_match:
                    connection.dest_port = f"{pattern_name.upper()}-{port_match.group('unit')}"
                    break

        return connection

    def analyze_camera_chain(self, entities: List[Dict[str, Any]]) -> CameraChain:
        """Analyze camera chain from drawing entities"""
        camera_chain = CameraChain(
            camera_id="",
            net_id="",
            sd_out="",
            gvg_id="",
            fiber_id="",
            signal_paths=[]
        )

        for entity in entities:
            text = entity.get('text', '')
            
            # Match camera components
            for pattern_name, pattern in BroadcastSignalPatterns.SIGNAL_PATTERNS.items():
                match = re.search(pattern, text)
                if match:
                    if pattern_name == 'net':
                        camera_chain.net_id = match.group(0)
                    elif pattern_name == 'sd_out':
                        camera_chain.sd_out = match.group(0)
                    elif pattern_name == 'gvg':
                        camera_chain.gvg_id = match.group(0)
                    elif pattern_name == 'fiber':
                        camera_chain.fiber_id = match.group(0)

            # Collect signal paths
            if '-->' in text or '→' in text:
                camera_chain.signal_paths.append(text)

        return camera_chain
