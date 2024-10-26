from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Any

@dataclass
class ProductionControlConfig:
    """Production Control Room Configuration"""
    room_id: str  # e.g., "PCR2"
    switcher: AcuityConfig
    multiviewers: List[MultiviewerConfig]
    router_integration: Dict[str, str]  # Router connections
    automation: Optional[str] = None
    
    # Monitoring configurations
    preview_monitors: List[str] = field(default_factory=list)
    program_monitors: List[str] = field(default_factory=list)
    aux_monitors: List[str] = field(default_factory=list)
    
    # Source assignments
    me1_sources: Dict[int, str] = field(default_factory=dict)
    me2_sources: Dict[int, str] = field(default_factory=dict)
    aux_bus_assigns: Dict[int, str] = field(default_factory=dict)

class ProductionSystemManager:
    """Manages Production System Configuration"""
    
    def __init__(self):
        self.control_rooms: Dict[str, ProductionControlConfig] = {}
        self.multiviewers: Dict[str, MultiviewerConfig] = {}
        self.source_names: Dict[str, str] = {}  # Maps router sources to friendly names

    def configure_control_room(self, 
                             room_id: str,
                             switcher_config: AcuityConfig,
                             multiviewer_configs: List[MultiviewerConfig]) -> ProductionControlConfig:
        """Configure a production control room"""
        config = ProductionControlConfig(
            room_id=room_id,
            switcher=switcher_config,
            multiviewers=multiviewer_configs,
            router_integration={}
        )
        self.control_rooms[room_id] = config
        return config

    def add_source_mapping(self, 
                          router_source: str, 
                          friendly_name: str,
                          attributes: Dict[str, Any] = None):
        """Add source name mapping"""
        self.source_names[router_source] = {
            'name': friendly_name,
            'attributes': attributes or {}
        }

    def configure_multiviewer_layout(self,
                                   mv_id: str,
                                   layout: str,
                                   source_assignments: Dict[int, str]):
        """Configure multiviewer layout and sources"""
        if mv_id in self.multiviewers:
            mv = self.multiviewers[mv_id]
            if layout in mv.supported_layouts:
                # Configure layout and assignments
                pass
