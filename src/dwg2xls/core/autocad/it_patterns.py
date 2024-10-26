from typing import Dict, List, Any, Optional, Pattern, Tuple
import re
from dataclasses import dataclass
from enum import Enum, auto
import logging

class DeviceCategory(Enum):
    """Categories of IT and Broadcast devices"""
    NETWORK = auto()
    SERVER = auto()
    STORAGE = auto()
    WORKSTATION = auto()
    DISPLAY = auto()
    CAMERA = auto()
    AUDIO = auto()
    KVM = auto()
    SECURITY = auto()
    BROADCAST = auto()
    CONTROL = auto()
    PERIPHERAL = auto()

@dataclass
class ITDevice:
    """Represents an IT or Broadcast device"""
    id: str
    category: DeviceCategory
    make: Optional[str] = None
    model: Optional[str] = None
    rack_units: int = 1
    position: Tuple[float, float] = (0, 0)
    connections: List[str] = None
    ip_address: Optional[str] = None
    subnet: Optional[str] = None
    vlan: Optional[int] = None

class ITPatterns:
    """Comprehensive patterns for IT and Broadcast equipment"""
    
    # Network Equipment
    NETWORK_PATTERNS = {
        'switch': r'(?:SW|SWITCH)[0-9]{2,3}(?:-[A-Z])?',  # SW01, SWITCH102-A
        'router': r'(?:RTR|ROUTER)[0-9]{2,3}',  # RTR01, ROUTER102
        'firewall': r'(?:FW|FIREWALL)[0-9]{2,3}',  # FW01, FIREWALL02
        'wireless_ap': r'(?:WAP|AP)[0-9]{2,3}',  # WAP01, AP102
        'patch_panel': r'(?:PP|PATCH)[0-9]{2,3}[A-Z]?',  # PP01A, PATCH102
    }

    # Server and Storage
    SERVER_PATTERNS = {
        'rack_server': r'(?:SRV|SERVER)[0-9]{2,3}',  # SRV01, SERVER102
        'blade': r'BLADE[0-9]{2,3}',  # BLADE01
        'storage': r'(?:STG|SAN|NAS)[0-9]{2,3}',  # STG01, SAN102
        'backup': r'(?:BKP|BACKUP)[0-9]{2,3}',  # BKP01, BACKUP102
    }

    # Broadcast Equipment
    BROADCAST_PATTERNS = {
        'camera': r'(?:CAM|CAMERA)[0-9]{2,3}(?:-[A-Z])?',  # CAM01, CAMERA102-A
        'video_switcher': r'(?:VS|VSWITCH)[0-9]{2,3}',  # VS01, VSWITCH102
        'encoder': r'(?:ENC|ENCODER)[0-9]{2,3}',  # ENC01, ENCODER102
        'decoder': r'(?:DEC|DECODER)[0-9]{2,3}',  # DEC01, DECODER102
        'matrix': r'(?:MTX|MATRIX)[0-9]{2,3}',  # MTX01, MATRIX102
    }

    # Display and Monitor
    DISPLAY_PATTERNS = {
        'monitor': r'(?:MON|MONITOR)[0-9]{2,3}',  # MON01, MONITOR102
        'display': r'(?:DISP|DISPLAY)[0-9]{2,3}',  # DISP01, DISPLAY102
        'video_wall': r'(?:VW|VWALL)[0-9]{2,3}',  # VW01, VWALL102
        'projector': r'(?:PROJ|PROJECTOR)[0-9]{2,3}',  # PROJ01, PROJECTOR102
    }

    # Control Systems
    CONTROL_PATTERNS = {
        'controller': r'(?:CTRL|CONTROLLER)[0-9]{2,3}',  # CTRL01, CONTROLLER102
        'processor': r'(?:PROC|PROCESSOR)[0-9]{2,3}',  # PROC01, PROCESSOR102
        'kvm': r'KVM[0-9]{2,3}(?:-[A-Z])?',  # KVM01, KVM102-A
        'touchpanel': r'(?:TP|TOUCH)[0-9]{2,3}',  # TP01, TOUCH102
    }

    # Network Addressing
    NETWORK_ADDRESSING = {
        'ip_address': r'(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)',
        'subnet_mask': r'(?:\/[0-9]{1,2})|(?:255\.(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){2}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?))',
        'vlan': r'VLAN\s*[0-9]{1,4}',
        'mac_address': r'(?:[0-9A-Fa-f]{2}[:-]){5}(?:[0-9A-Fa-f]{2})',
    }

    # Rack and Location
    LOCATION_PATTERNS = {
        'rack': r'(?:RACK|R)[0-9]{2,3}(?:-[A-Z])?',  # RACK01, R102-A
        'rack_position': r'U[0-9]{1,2}',  # U1, U42
        'room': r'(?:RM|ROOM)[0-9]{2,3}[A-Z]?',  # RM101, ROOM102A
        'data_center': r'DC[0-9]{1,2}',  # DC1, DC02
    }

class ITDeviceAnalyzer:
    """Analyzes IT and broadcast device information"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._compile_patterns()

    def _compile_patterns(self):
        """Compile all regex patterns"""
        self.compiled_patterns = {}
        for category, patterns in vars(ITPatterns).items():
            if isinstance(patterns, dict):
                self.compiled_patterns[category] = {
                    name: re.compile(pattern, re.IGNORECASE)
                    for name, pattern in patterns.items()
                }

    def analyze_device(self, text: str, position: Tuple[float, float]) -> Optional[ITDevice]:
        """Analyze text to identify IT device information"""
        try:
            device_info = self._identify_device_type(text)
            if device_info:
                return ITDevice(
                    id=text,
                    category=device_info['category'],
                    position=position,
                    connections=self._extract_connections(text),
                    ip_address=self._extract_ip_address(text),
                    vlan=self._extract_vlan(text)
                )
        except Exception as e:
            self.logger.error(f"Error analyzing device {text}: {str(e)}")
        return None

    def _identify_device_type(self, text: str) -> Optional[Dict[str, Any]]:
        """Identify device type from text"""
        for category, patterns in self.compiled_patterns.items():
            for device_type, pattern in patterns.items():
                if pattern.search(text):
                    return {
                        'category': self._map_to_device_category(category),
                        'type': device_type
                    }
        return None

    @staticmethod
    def _map_to_device_category(pattern_category: str) -> DeviceCategory:
        """Map pattern category to DeviceCategory enum"""
        category_mapping = {
            'NETWORK_PATTERNS': DeviceCategory.NETWORK,
            'SERVER_PATTERNS': DeviceCategory.SERVER,
            'BROADCAST_PATTERNS': DeviceCategory.BROADCAST,
            'DISPLAY_PATTERNS': DeviceCategory.DISPLAY,
            'CONTROL_PATTERNS': DeviceCategory.CONTROL
        }
        return category_mapping.get(pattern_category, DeviceCategory.PERIPHERAL)

    def _extract_connections(self, text: str) -> List[str]:
        """Extract connection information from text"""
        connections = []
        # Look for connection indicators like "TO", "FROM", "-->"
        connection_pattern = r'(?:TO|FROM|-->)\s*([A-Z0-9-]+)'
        matches = re.finditer(connection_pattern, text, re.IGNORECASE)
        return [match.group(1) for match in matches]

    def _extract_ip_address(self, text: str) -> Optional[str]:
        """Extract IP address from text"""
        ip_pattern = self.compiled_patterns['NETWORK_ADDRESSING']['ip_address']
        match = ip_pattern.search(text)
        return match.group(0) if match else None

    def _extract_vlan(self, text: str) -> Optional[int]:
        """Extract VLAN information from text"""
        vlan_pattern = self.compiled_patterns['NETWORK_ADDRESSING']['vlan']
        match = vlan_pattern.search(text)
        if match:
            vlan_text = match.group(0)
            return int(re.search(r'[0-9]+', vlan_text).group(0))
        return None
