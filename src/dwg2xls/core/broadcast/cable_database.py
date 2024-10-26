from dataclasses import dataclass, field
from typing import Dict, List, Optional, Union
from enum import Enum
import datetime

class CableType(Enum):
    VIDEO_SDI = "Video SDI"
    AUDIO_AES = "Audio AES"
    AUDIO_ANALOG = "Audio Analog"
    FIBER = "Fiber"
    CAT6 = "CAT6"
    CONTROL = "Control"
    INTERCOM = "Intercom"
    TIMECODE = "Timecode"
    REFERENCE = "Reference"
    GPIO = "GPIO"
    MADI = "MADI"
    DANTE = "Dante"

@dataclass
class CableSpecification:
    """Cable specification details"""
    type: CableType
    manufacturer: str
    model: str
    impedance: Optional[float] = None
    awg: Optional[str] = None
    shield_type: Optional[str] = None
    jacket_color: Optional[str] = None
    max_length: Optional[float] = None
    notes: Optional[str] = None

@dataclass
class CableConnection:
    """Represents a cable connection between two points"""
    cable_id: str
    source_room: str
    source_rack: str
    source_device: str
    source_connector: str
    dest_room: str
    dest_rack: str
    dest_device: str
    dest_connector: str
    cable_type: CableType
    cable_spec: CableSpecification
    length: float
    label_scheme: str
    installation_date: Optional[datetime.date] = None
    last_tested: Optional[datetime.date] = None
    status: str = "Active"

class CableDatabaseManager:
    """Manages broadcast facility cable database"""
    
    def __init__(self):
        self.connections: Dict[str, CableConnection] = {}
        self.cable_specs: Dict[str, CableSpecification] = {}
        self.rooms: Set[str] = set()
        self.racks: Dict[str, Set[str]] = {}  # room -> racks mapping
        
    def add_cable_spec(self, 
                      spec_id: str, 
                      specification: CableSpecification):
        """Add a cable specification to the database"""
        self.cable_specs[spec_id] = specification

    def add_connection(self, connection: CableConnection):
        """Add a cable connection to the database"""
        # Add rooms and racks to tracking
        self.rooms.add(connection.source_room)
        self.rooms.add(connection.dest_room)
        
        if connection.source_room not in self.racks:
            self.racks[connection.source_room] = set()
        if connection.dest_room not in self.racks:
            self.racks[connection.dest_room] = set()
            
        self.racks[connection.source_room].add(connection.source_rack)
        self.racks[connection.dest_room].add(connection.dest_rack)
        
        # Add connection
        self.connections[connection.cable_id] = connection

    def get_connections_by_device(self, device: str) -> List[CableConnection]:
        """Get all connections for a specific device"""
        return [
            conn for conn in self.connections.values()
            if conn.source_device == device or conn.dest_device == device
        ]

    def get_connections_by_rack(self, room: str, rack: str) -> List[CableConnection]:
        """Get all connections for a specific rack"""
        return [
            conn for conn in self.connections.values()
            if (conn.source_room == room and conn.source_rack == rack) or
               (conn.dest_room == room and conn.dest_rack == rack)
        ]

    def generate_labels(self, connection: CableConnection) -> Dict[str, str]:
        """Generate cable labels for both ends"""
        return {
            'source': f"{connection.cable_id}-A {connection.source_room}/{connection.source_rack}",
            'dest': f"{connection.cable_id}-B {connection.dest_room}/{connection.dest_rack}"
        }

    def export_database(self, format: str = 'csv') -> Union[str, bytes]:
        """Export cable database in specified format"""
        # Implementation for exporting to various formats
        pass

    def validate_connection(self, connection: CableConnection) -> List[str]:
        """Validate a cable connection"""
        errors = []
        
        # Validate rooms and racks exist
        if connection.source_room not in self.rooms:
            errors.append(f"Invalid source room: {connection.source_room}")
        if connection.dest_room not in self.rooms:
            errors.append(f"Invalid destination room: {connection.dest_room}")
            
        # Validate cable specifications
        spec = self.cable_specs.get(connection.cable_spec)
        if spec and connection.length > spec.max_length:
            errors.append(f"Cable length exceeds maximum for specification")
            
        return errors
