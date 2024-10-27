from enum import Enum
from typing import Dict, List, Optional, Pattern
import re

class DeviceCategory(Enum):
    ROUTER = "Router"
    CAMERA = "Camera"
    PRODUCTION = "Production"
    PLAYBACK = "Playback"
    MULTIVIEWER = "Multiviewer"
    GRAPHICS = "Graphics"
    PROMPTER = "Prompter"
    WEB = "Web"
    TEST = "Test"

class DevicePatterns:
    """Device naming patterns"""
    
    PATTERNS = {
        # Router patterns
        "EQX": r"(?P<device>EQX)[-_](?P<type>IN|OUT)[-_](?P<number>\d+)",
        "RTR": r"RTR\s*(?P<size>\d+)\s*(?P<type>SRC|DST)",
        
        # Camera patterns
        "CAM": r"CAM[-_](?P<number>\d+)[-_](?P<type>ST|Flash|Chroma)?",
        "CCU": r"(?P<cam>CAM\d+)[-_]CCU",
        
        # Playback patterns
        "PLAYBACK": r"PLAYBACK[-_](?P<number>\d+)[-_]B(?P<bank>\d+)[-_](?P<slot>\d+)",
        
        # Web/PC patterns
        "PC": r"PC[-_](?P<letter>[A-Z])[-_]WEB",
        "MAC": r"MAC[-_]Shared[-_]WEB",
        
        # Test signals
        "BLACK": r"^BLACK$",
        "BARS": r"^BARS AND TONE$",
        "OPEN": r"^OPEN[-_](?P<number>\d+)$",
        
        # Prompter
        "PROMPT": r"PROMPT[-_](?P<channel>[AB])",
        
        # Delay/Processing
        "DELAY": r"DelayQuad[-_]MV",
        
        # Generic patterns
        "ABC": r"ABC(?P<number>\d+)",
        "DIRECTV": r"(?P<station>[A-Z]+)[-_]DirectTV"
    }

class RackPatterns:
    """Rack naming patterns"""
    
    PATTERNS = {
        # Technical Equipment Room patterns
        "TE_MDF": r"T[XK](?P<number>\d{2})",      # TX01-TK17
        "TE_CAMERA": r"TC(?P<number>\d{2})",      # TC03-TC13
        "TE_INTERCOM": r"TD(?P<number>\d{2})",    # TD01-TD13
        "TE_EQUIPMENT": r"TE(?P<number>\d{2})",   # TE01-TE13
        "TE_FRAME": r"TF(?P<number>\d{2})",       # TF01-TF12
        "TE_GRID": r"TG(?P<number>\d{2})",        # TG01-TG12
        "TE_AUDIO": r"TH(?P<number>\d{2})",       # TH01-TH11
        "TE_VIDEO": r"TJ(?P<number>\d{2})",       # TJ01-TJ10
        
        # Master Control patterns
        "MCR_A": r"CA(?P<number>\d{2})",          # CA01-CA04
        "MCR_B": r"CB(?P<number>\d{2})",          # CB01-CB04
    }

class PatternMatcher:
    """Matches device and rack patterns"""
    
    def __init__(self):
        self.device_patterns = {
            name: re.compile(pattern) 
            for name, pattern in DevicePatterns.PATTERNS.items()
        }
        self.rack_patterns = {
            name: re.compile(pattern)
            for name, pattern in RackPatterns.PATTERNS.items()
        }

    def match_device(self, device_name: str) -> Dict[str, any]:
        """Match device name against known patterns"""
        for pattern_name, pattern in self.device_patterns.items():
            match = pattern.match(device_name)
            if match:
                return {
                    "pattern": pattern_name,
                    "category": self._get_device_category(pattern_name),
                    "matches": match.groupdict()
                }
        return None

    def match_rack(self, rack_name: str) -> Dict[str, any]:
        """Match rack name against known patterns"""
        for pattern_name, pattern in self.rack_patterns.items():
            match = pattern.match(rack_name)
            if match:
                return {
                    "pattern": pattern_name,
                    "area": pattern_name.split('_')[0],
                    "matches": match.groupdict()
                }
        return None

    def _get_device_category(self, pattern_name: str) -> DeviceCategory:
        """Determine device category from pattern name"""
        category_map = {
            "EQX": DeviceCategory.ROUTER,
            "RTR": DeviceCategory.ROUTER,
            "CAM": DeviceCategory.CAMERA,
            "CCU": DeviceCategory.CAMERA,
            "PLAYBACK": DeviceCategory.PLAYBACK,
            "PC": DeviceCategory.WEB,
            "MAC": DeviceCategory.WEB,
            "BLACK": DeviceCategory.TEST,
            "BARS": DeviceCategory.TEST,
            "OPEN": DeviceCategory.TEST,
            "PROMPT": DeviceCategory.PROMPTER,
            "DELAY": DeviceCategory.PRODUCTION
        }
        return category_map.get(pattern_name, None)
