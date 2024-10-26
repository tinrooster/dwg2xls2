from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set
import re

class BroadcastRoom(Enum):
    """Broadcast facility rooms"""
    TE_ROOM = "TE"          # Technical Equipment Room
    MCR = "MCR"             # Master Control Room
    PCR2 = "PCR2"          # Production Control Room 2
    PCR3 = "PCR3"          # Production Control Room 3
    STUDIO = "STUDIO"       # Studio
    CUSTOM = "CUSTOM"       # For custom room additions

class RackType(Enum):
    """Types of equipment racks"""
    MDF = "MDF"                    # Main Distribution Frame
    CAMERA = "CAMERA"              # Camera Systems
    INTERCOM = "INTERCOM"          # Intercom/ClearCom Systems
    AUDIO = "AUDIO"                # Audio Systems
    VIDEO_JACKFIELD = "JACKFIELD"  # Video Jack Fields
    VIDEO_ROUTER = "ROUTER"        # Video Routing
    DA = "DA"                      # Distribution Amplifiers
    MASTER_CONTROL = "MC"          # Master Control
    CUSTOM = "CUSTOM"              # Custom rack type

@dataclass
class RackSeries:
    """Represents a series of racks"""
    prefix: str              # e.g., "TX", "TC", "CA"
    start_number: int        # Starting number
    end_number: int         # Ending number
    rack_type: RackType
    room: BroadcastRoom
    description: str = ""
    custom_attributes: Dict[str, str] = field(default_factory=dict)

@dataclass
class RackConfiguration:
    """Configuration for a specific rack"""
    rack_id: str            # e.g., "TX01", "CA03"
    room: BroadcastRoom
    rack_type: RackType
    ru_height: int = 45     # Rack units height
    occupied_ru: Set[int] = field(default_factory=set)
    equipment: Dict[str, Dict] = field(default_factory=dict)

class BroadcastRackManager:
    """Manages broadcast rack configurations and layouts"""

    def __init__(self):
        self.rack_series = self._initialize_rack_series()
        self.rack_configs: Dict[str, RackConfiguration] = {}
        self.custom_series: List[RackSeries] = []

    def _initialize_rack_series(self) -> List[RackSeries]:
        """Initialize standard rack series configurations"""
        return [
            # TE Room MDF and Interconnections
            RackSeries("TX", 1, 17, RackType.MDF, BroadcastRoom.TE_ROOM, 
                      "MDF and Interconnections"),
            
            # Camera Systems
            RackSeries("TC", 3, 13, RackType.CAMERA, BroadcastRoom.TE_ROOM, 
                      "Camera Systems"),
            
            # Intercom/ClearCom
            RackSeries("TD", 1, 13, RackType.INTERCOM, BroadcastRoom.TE_ROOM, 
                      "Intercom and ClearCom Systems"),
            
            # TE Series
            RackSeries("TE", 1, 13, RackType.CUSTOM, BroadcastRoom.TE_ROOM, 
                      "TE Equipment Series"),
            
            # TF Series
            RackSeries("TF", 1, 12, RackType.CUSTOM, BroadcastRoom.TE_ROOM, 
                      "TF Equipment Series"),
            
            # TG Series
            RackSeries("TG", 1, 12, RackType.CUSTOM, BroadcastRoom.TE_ROOM, 
                      "TG Equipment Series"),
            
            # Audio and Acuity
            RackSeries("TH", 1, 11, RackType.AUDIO, BroadcastRoom.TE_ROOM, 
                      "Audio and Acuity Systems"),
            
            # Video Jack Fields and DAs
            RackSeries("TJ", 1, 10, RackType.VIDEO_JACKFIELD, BroadcastRoom.TE_ROOM, 
                      "Video Jack Fields and DAs"),
            
            # TK Series
            RackSeries("TK", 1, 10, RackType.CUSTOM, BroadcastRoom.TE_ROOM, 
                      "TK Equipment Series"),
            
            # Master Control Room Series A
            RackSeries("CA", 1, 4, RackType.MASTER_CONTROL, BroadcastRoom.MCR, 
                      "Master Control Series A"),
            
            # Master Control Room Series B
            RackSeries("CB", 1, 4, RackType.MASTER_CONTROL, BroadcastRoom.MCR, 
                      "Master Control Series B"),
        ]

    def add_custom_rack_series(self, 
                              prefix: str, 
                              start_num: int, 
                              end_num: int,
                              rack_type: RackType,
                              room: BroadcastRoom,
                              description: str = "",
                              attributes: Dict[str, str] = None) -> RackSeries:
        """Add a custom rack series"""
        new_series = RackSeries(
            prefix=prefix,
            start_number=start_num,
            end_number=end_num,
            rack_type=rack_type,
            room=room,
            description=description,
            custom_attributes=attributes or {}
        )
        self.custom_series.append(new_series)
        return new_series

    def get_rack_info(self, rack_id: str) -> Optional[Dict[str, any]]:
        """Get information about a specific rack"""
        prefix = re.match(r'([A-Z]+)', rack_id).group(1)
        number = int(re.search(r'(\d+)', rack_id).group(1))
        
        # Search all rack series (standard and custom)
        for series in self.rack_series + self.custom_series:
            if (series.prefix == prefix and 
                series.start_number <= number <= series.end_number):
                return {
                    'rack_id': rack_id,
                    'series': series.prefix,
                    'number': number,
                    'type': series.rack_type.value,
                    'room': series.room.value,
                    'description': series.description,
                    'custom_attributes': series.custom_attributes
                }
        return None

    def configure_rack(self, 
                      rack_id: str, 
                      ru_height: int = 45) -> RackConfiguration:
        """Configure a specific rack"""
        rack_info = self.get_rack_info(rack_id)
        if not rack_info:
            raise ValueError(f"Invalid rack ID: {rack_id}")
            
        config = RackConfiguration(
            rack_id=rack_id,
            room=BroadcastRoom(rack_info['room']),
            rack_type=RackType(rack_info['type']),
            ru_height=ru_height
        )
        self.rack_configs[rack_id] = config
        return config

    def add_equipment_to_rack(self,
                            rack_id: str,
                            equipment_name: str,
                            ru_start: int,
                            ru_size: int,
                            equipment_type: str,
                            attributes: Dict[str, any] = None) -> bool:
        """Add equipment to a rack configuration"""
        if rack_id not in self.rack_configs:
            self.configure_rack(rack_id)
            
        config = self.rack_configs[rack_id]
        
        # Check if RU space is available
        requested_rus = set(range(ru_start, ru_start + ru_size))
        if any(ru in config.occupied_ru for ru in requested_rus):
            return False
            
        # Add equipment
        config.equipment[equipment_name] = {
            'ru_start': ru_start,
            'ru_size': ru_size,
            'type': equipment_type,
            'attributes': attributes or {}
        }
        
        # Mark RUs as occupied
        config.occupied_ru.update(requested_rus)
        return True

    def get_room_racks(self, room: BroadcastRoom) -> List[str]:
        """Get all rack IDs in a specific room"""
        room_racks = []
        for series in self.rack_series + self.custom_series:
            if series.room == room:
                room_racks.extend([
                    f"{series.prefix}{str(num).zfill(2)}"
                    for num in range(series.start_number, series.end_number + 1)
                ])
        return sorted(room_racks)

    def get_rack_type_equipment(self, rack_type: RackType) -> Dict[str, List[str]]:
        """Get all equipment of a specific rack type"""
        equipment_by_rack = {}
        for rack_id, config in self.rack_configs.items():
            if config.rack_type == rack_type:
                equipment_by_rack[rack_id] = list(config.equipment.keys())
        return equipment_by_rack
