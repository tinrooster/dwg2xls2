from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set
import networkx as nx
from datetime import datetime

@dataclass
class RouterPort:
    """Router port configuration"""
    index: int
    name: str
    port: int
    card: int
    is_source: bool = True
    status: str = "Active"
    last_updated: datetime = field(default_factory=datetime.now)

class RouterAnalyzer:
    """Analyzes EQX router configurations and signal flow"""

    def __init__(self, router_name: str = "RTR 512"):
        self.router_name = router_name
        self.sources: Dict[int, RouterPort] = {}
        self.destinations: Dict[int, RouterPort] = {}
        self.flow_graph = nx.DiGraph()
        
    def add_source(self, index: int, name: str, port: int, card: int):
        """Add source port to router"""
        self.sources[index] = RouterPort(
            index=index,
            name=name,
            port=port,
            card=card,
            is_source=True
        )
        # Add to flow graph
        self.flow_graph.add_node(
            f"SRC_{index}",
            type="source",
            name=name,
            port=port,
            card=card
        )

    def add_destination(self, index: int, name: str, port: int, card: int):
        """Add destination port to router"""
        self.destinations[index] = RouterPort(
            index=index,
            name=name,
            port=port,
            card=card,
            is_source=False
        )
        # Add to flow graph
        self.flow_graph.add_node(
            f"DST_{index}",
            type="destination",
            name=name,
            port=port,
            card=card
        )

    def add_crosspoint(self, source_index: int, dest_index: int):
        """Add router crosspoint"""
        if source_index in self.sources and dest_index in self.destinations:
            self.flow_graph.add_edge(
                f"SRC_{source_index}",
                f"DST_{dest_index}"
            )

# Example implementation with your router data
def setup_router():
    """Setup router with example data"""
    router = RouterAnalyzer("RTR 512")
    
    # Add sources from your data
    sources = [
        (1, "BLACK", 1, 1),
        (2, "BARS AND TONE", 2, 1),
        (3, "OPEN_03", 3, 1),
        (4, "KABC-DirectTV", 4, 1),
        (5, "CAM-Chroma", 5, 1),
        (6, "ABC1", 6, 1),
        (7, "ABC2", 7, 1),
        (8, "MAC-Shared_WEB", 8, 1),
        (9, "CAM-Flash_ST", 9, 1),
        (10, "OPEN_10", 10, 1),
        # ... add more sources as needed
    ]

    for index, name, port, card in sources:
        router.add_source(index, name, port, card)

    return router

def analyze_camera_chain():
    """Analyze camera signal chain"""
    router = setup_router()
    
    # Find all camera sources
    camera_sources = [
        port for port in router.sources.values()
        if "CAM" in port.name
    ]
    
    print(f"Found {len(camera_sources)} camera sources:")
    for cam in camera_sources:
        print(f"Camera: {cam.name} on port {cam.port}, card {cam.card}")
        
    return camera_sources

def analyze_card_usage():
    """Analyze router card usage"""
    router = setup_router()
    
    # Group ports by card
    card_usage = {}
    for port in router.sources.values():
        if port.card not in card_usage:
            card_usage[port.card] = {
                'total': 0,
                'ports': [],
                'types': set()
            }
        card_usage[port.card]['total'] += 1
        card_usage[port.card]['ports'].append(port)
        
        # Determine signal type from name
        if "CAM" in port.name:
            card_usage[port.card]['types'].add("Camera")
        elif "PLAYBACK" in port.name:
            card_usage[port.card]['types'].add("Playback")
        elif "WEB" in port.name:
            card_usage[port.card]['types'].add("Web")
            
    return card_usage

# Example usage
if __name__ == "__main__":
    # Analyze camera chain
    print("Analyzing Camera Chain:")
    camera_sources = analyze_camera_chain()
    
    print("\nAnalyzing Card Usage:")
    card_usage = analyze_card_usage()
    for card_num, usage in card_usage.items():
        print(f"\nCard {card_num}:")
        print(f"Total ports used: {usage['total']}")
        print(f"Signal types: {', '.join(usage['types'])}")
