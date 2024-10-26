from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional
from enum import Enum
import networkx as nx
import matplotlib.pyplot as plt

class SignalFormat(Enum):
    SDI_SD = "SD-SDI"
    SDI_HD = "HD-SDI"
    SDI_3G = "3G-SDI"
    SDI_12G = "12G-SDI"
    FIBER = "Fiber"
    IP_2110 = "SMPTE 2110"
    ANALOG = "Analog"
    AES = "AES"
    MADI = "MADI"
    DANTE = "Dante"

@dataclass
class SignalNode:
    """Represents a point in the signal chain"""
    device_id: str
    device_type: str
    room: str
    rack: str
    connector: str
    signal_format: SignalFormat
    attributes: Dict[str, any] = field(default_factory=dict)

@dataclass
class SignalPath:
    """Represents a signal path between nodes"""
    source: SignalNode
    destination: SignalNode
    cable_id: Optional[str] = None
    router_path: Optional[List[str]] = None
    active: bool = True

class SignalFlowAnalyzer:
    """Analyzes broadcast signal flow"""

    def __init__(self):
        self.graph = nx.DiGraph()  # Directed graph for signal flow
        self.nodes: Dict[str, SignalNode] = {}
        self.paths: Dict[str, SignalPath] = {}
        self.critical_paths: Set[str] = set()

    def add_node(self, node: SignalNode):
        """Add a signal node to the flow graph"""
        node_id = f"{node.room}_{node.rack}_{node.device_id}"
        self.nodes[node_id] = node
        self.graph.add_node(node_id, **node.__dict__)

    def add_path(self, path: SignalPath):
        """Add a signal path to the flow graph"""
        source_id = f"{path.source.room}_{path.source.rack}_{path.source.device_id}"
        dest_id = f"{path.destination.room}_{path.destination.rack}_{path.destination.device_id}"
        
        # Add path to graph
        self.graph.add_edge(
            source_id, 
            dest_id, 
            cable_id=path.cable_id,
            router_path=path.router_path,
            active=path.active
        )
        
        # Store path reference
        path_id = f"{source_id}_to_{dest_id}"
        self.paths[path_id] = path

    def analyze_signal_chain(self, start_node: str, end_node: str) -> Dict[str, any]:
        """Analyze a complete signal chain between two points"""
        try:
            # Find all paths between nodes
            all_paths = list(nx.all_simple_paths(self.graph, start_node, end_node))
            
            # Analyze each path
            path_analysis = []
            for path in all_paths:
                analysis = {
                    'path': path,
                    'length': len(path) - 1,
                    'router_hops': self._count_router_hops(path),
                    'format_conversions': self._analyze_format_conversions(path),
                    'critical_points': self._identify_critical_points(path)
                }
                path_analysis.append(analysis)
            
            return {
                'paths_found': len(all_paths),
                'path_details': path_analysis,
                'redundant_paths': len(all_paths) > 1,
                'shortest_path': min(path_analysis, key=lambda x: x['length'])
            }
            
        except nx.NetworkXNoPath:
            return {'error': 'No path found between specified nodes'}

    def find_bottlenecks(self) -> List[str]:
        """Identify potential signal flow bottlenecks"""
        bottlenecks = []
        
        # Check node connectivity
        for node in self.graph.nodes():
            in_degree = self.graph.in_degree(node)
            out_degree = self.graph.out_degree(node)
            
            # High in/out degree might indicate a bottleneck
            if in_degree > 5 or out_degree > 5:
                bottlenecks.append({
                    'node': node,
                    'in_connections': in_degree,
                    'out_connections': out_degree
                })
        
        return bottlenecks

    def visualize_flow(self, 
                      highlight_path: Optional[List[str]] = None,
                      save_path: Optional[str] = None):
        """Visualize signal flow graph"""
        pos = nx.spring_layout(self.graph)
        
        # Draw basic graph
        nx.draw(self.graph, pos, with_labels=True, node_color='lightblue', 
                node_size=1500, font_size=8)
        
        # Highlight specific path if provided
        if highlight_path:
            path_edges = list(zip(highlight_path[:-1], highlight_path[1:]))
            nx.draw_networkx_edges(self.graph, pos, edgelist=path_edges, 
                                 edge_color='r', width=2)
        
        if save_path:
            plt.savefig(save_path)
        else:
            plt.show()

    def _count_router_hops(self, path: List[str]) -> int:
        """Count number of router crosspoints in path"""
        router_hops = 0
        for node in path:
            if 'EQX' in node or 'RTR' in node:
                router_hops += 1
        return router_hops

    def _analyze_format_conversions(self, path: List[str]) -> List[Dict[str, str]]:
        """Analyze signal format conversions along path"""
        conversions = []
        for i in range(len(path) - 1):
            source_format = self.nodes[path[i]].signal_format
            dest_format = self.nodes[path[i + 1]].signal_format
            
            if source_format != dest_format:
                conversions.append({
                    'point': path[i],
                    'from': source_format.value,
                    'to': dest_format.value
                })
        return conversions

    def _identify_critical_points(self, path: List[str]) -> List[str]:
        """Identify critical points in signal path"""
        critical_points = []
        for node in path:
            # Check if node is in critical paths set
            if node in self.critical_paths:
                critical_points.append(node)
            
            # Check if node is a single point of failure
            if self.graph.degree(node) == 1:
                critical_points.append(node)
                
        return critical_points
