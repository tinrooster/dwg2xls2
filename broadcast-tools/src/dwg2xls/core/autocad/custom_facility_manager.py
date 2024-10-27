from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Any
import json
import yaml
from pathlib import Path
import logging
from datetime import datetime

@dataclass
class CustomRoom:
    """User-defined room configuration"""
    id: str
    name: str
    description: str
    attributes: Dict[str, Any] = field(default_factory=dict)
    parent_room: Optional[str] = None

@dataclass
class CustomRackType:
    """User-defined rack type"""
    id: str
    name: str
    description: str
    default_height: int = 45
    attributes: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CustomRackSeries:
    """User-defined rack series"""
    prefix: str
    start_number: int
    end_number: int
    rack_type: str
    room: str
    description: str
    attributes: Dict[str, Any] = field(default_factory=dict)

class FacilityManager:
    """Manages user-defined facility configurations"""

    def __init__(self, config_path: Optional[Path] = None):
        self.logger = logging.getLogger(__name__)
        self.config_path = config_path or Path("facility_config.yaml")
        
        self.rooms: Dict[str, CustomRoom] = {}
        self.rack_types: Dict[str, CustomRackType] = {}
        self.rack_series: Dict[str, CustomRackSeries] = {}
        
        self.load_configuration()

    def add_room(self, 
                room_id: str, 
                name: str, 
                description: str,
                attributes: Dict[str, Any] = None,
                parent_room: Optional[str] = None) -> CustomRoom:
        """Add a new room configuration"""
        if room_id in self.rooms:
            raise ValueError(f"Room ID {room_id} already exists")
            
        room = CustomRoom(
            id=room_id,
            name=name,
            description=description,
            attributes=attributes or {},
            parent_room=parent_room
        )
        self.rooms[room_id] = room
        self.save_configuration()
        return room

    def add_rack_type(self, 
                     type_id: str, 
                     name: str,
                     description: str,
                     default_height: int = 45,
                     attributes: Dict[str, Any] = None) -> CustomRackType:
        """Add a new rack type"""
        if type_id in self.rack_types:
            raise ValueError(f"Rack type {type_id} already exists")
            
        rack_type = CustomRackType(
            id=type_id,
            name=name,
            description=description,
            default_height=default_height,
            attributes=attributes or {}
        )
        self.rack_types[type_id] = rack_type
        self.save_configuration()
        return rack_type

    def add_rack_series(self,
                       prefix: str,
                       start_number: int,
                       end_number: int,
                       rack_type: str,
                       room: str,
                       description: str,
                       attributes: Dict[str, Any] = None) -> CustomRackSeries:
        """Add a new rack series"""
        # Validate references
        if rack_type not in self.rack_types:
            raise ValueError(f"Rack type {rack_type} does not exist")
        if room not in self.rooms:
            raise ValueError(f"Room {room} does not exist")
            
        series_id = f"{prefix}_{start_number}_{end_number}"
        if series_id in self.rack_series:
            raise ValueError(f"Rack series {series_id} already exists")
            
        series = CustomRackSeries(
            prefix=prefix,
            start_number=start_number,
            end_number=end_number,
            rack_type=rack_type,
            room=room,
            description=description,
            attributes=attributes or {}
        )
        self.rack_series[series_id] = series
        self.save_configuration()
        return series

    def save_configuration(self):
        """Save current configuration to file"""
        config = {
            'metadata': {
                'last_updated': datetime.now().isoformat(),
                'version': '1.0'
            },
            'rooms': {
                room_id: {
                    'name': room.name,
                    'description': room.description,
                    'attributes': room.attributes,
                    'parent_room': room.parent_room
                }
                for room_id, room in self.rooms.items()
            },
            'rack_types': {
                type_id: {
                    'name': rack_type.name,
                    'description': rack_type.description,
                    'default_height': rack_type.default_height,
                    'attributes': rack_type.attributes
                }
                for type_id, rack_type in self.rack_types.items()
            },
            'rack_series': {
                series_id: {
                    'prefix': series.prefix,
                    'start_number': series.start_number,
                    'end_number': series.end_number,
                    'rack_type': series.rack_type,
                    'room': series.room,
                    'description': series.description,
                    'attributes': series.attributes
                }
                for series_id, series in self.rack_series.items()
            }
        }
        
        with open(self.config_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
        
        self.logger.info(f"Configuration saved to {self.config_path}")

    def load_configuration(self):
        """Load configuration from file"""
        if not self.config_path.exists():
            self.logger.info("No configuration file found. Starting with empty configuration.")
            return
            
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
                
            # Load rooms
            for room_id, room_data in config.get('rooms', {}).items():
                self.rooms[room_id] = CustomRoom(
                    id=room_id,
                    **room_data
                )
                
            # Load rack types
            for type_id, type_data in config.get('rack_types', {}).items():
                self.rack_types[type_id] = CustomRackType(
                    id=type_id,
                    **type_data
                )
                
            # Load rack series
            for series_id, series_data in config.get('rack_series', {}).items():
                self.rack_series[series_id] = CustomRackSeries(**series_data)
                
            self.logger.info(f"Configuration loaded from {self.config_path}")
            
        except Exception as e:
            self.logger.error(f"Error loading configuration: {str(e)}")
            raise
