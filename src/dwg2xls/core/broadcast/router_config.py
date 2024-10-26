from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Any
from enum import Enum
import re

class SignalType(Enum):
    """EQX Router Signal Types"""
    BLACK = "BLACK"
    BARS = "BARS_AND_TONE"
    CAMERA = "CAM"
    PLAYBACK = "PLAYBACK"
    WEB = "WEB"
    DIRECTV = "DIRECTV"
    PROMPT = "PROMPT"
    DELAY = "DELAY"
    OPEN = "OPEN"

class RouterPortType(Enum):
    """Router Port Types"""
    INPUT = "INPUT"
    OUTPUT = "OUTPUT"

@dataclass
class RouterPort:
    """Represents a router input/output port"""
    index: int
    name: str
    port_number: int
    card_number: int
    signal_type: SignalType
    attributes: Dict[str, str] = field(default_factory=dict)

@dataclass
class RouterCard:
    """Represents an EQX router card"""
    card_number: int
    port_count: int = 18
    ports: Dict[int, RouterPort] = field(default_factory=dict)
    port_type: RouterPortType  # INPUT or OUTPUT
    card_model: str = ""  # Specific EQX card model number if needed

class EQXRouter:
    """Manages Evertz EQX Router Configuration"""

    def __init__(self, router_id: str):
        self.router_id = router_id
        self.input_cards: Dict[int, RouterCard] = {}
        self.output_cards: Dict[int, RouterCard] = {}
        self.signal_patterns = {
            SignalType.CAMERA: r'CAM-\d+_ST$|CAM-.*Flash.*|CAM-Chroma',
            SignalType.PLAYBACK: r'PLAYBACK-\d+_B\d-\d+',
            SignalType.WEB: r'PC-[A-Z]_WEB|MAC-Shared_WEB',
            SignalType.PROMPT: r'PROMPT-[AB]',
            SignalType.DELAY: r'DelayQuad_MV',
            SignalType.BLACK: r'^BLACK$',
            SignalType.BARS: r'^BARS AND TONE$',
            SignalType.OPEN: r'^OPEN_\d+$'
        }

    def add_input_port(self, 
                        card_number: int, 
                        port_index: int, 
                        name: str, 
                        port_number: int) -> RouterPort:
        """Add a new input port to the router configuration"""
        # Ensure card exists
        if card_number not in self.input_cards:
            self.input_cards[card_number] = RouterCard(
                card_number=card_number,
                port_type=RouterPortType.INPUT
            )

        # Determine signal type
        signal_type = self._determine_signal_type(name)

        # Create port
        port = RouterPort(
            index=port_index,
            name=name,
            port_number=port_number,
            card_number=card_number,
            signal_type=signal_type
        )

        # Add port to card
        self.input_cards[card_number].ports[port_number] = port
        return port

    def add_output_port(self, 
                        card_number: int, 
                        port_index: int, 
                        name: str, 
                        port_number: int) -> RouterPort:
        """Add a new output port to the router configuration"""
        # Ensure card exists
        if card_number not in self.output_cards:
            self.output_cards[card_number] = RouterCard(
                card_number=card_number,
                port_type=RouterPortType.OUTPUT
            )

        # Determine signal type
        signal_type = self._determine_signal_type(name)

        # Create port
        port = RouterPort(
            index=port_index,
            name=name,
            port_number=port_number,
            card_number=card_number,
            signal_type=signal_type
        )

        # Add port to card
        self.output_cards[card_number].ports[port_number] = port
        return port

    def _determine_signal_type(self, name: str) -> SignalType:
        """Determine signal type from port name"""
        for signal_type, pattern in self.signal_patterns.items():
            if re.search(pattern, name):
                return signal_type
        return SignalType.OPEN

    def get_ports_by_type(self, signal_type: SignalType) -> List[RouterPort]:
        """Get all ports of a specific signal type"""
        ports = []
        for card in self.input_cards.values():
            for port in card.ports.values():
                if port.signal_type == signal_type:
                    ports.append(port)
        return sorted(ports, key=lambda x: x.index)

    def get_card_utilization(self, card_number: int) -> Dict[str, int]:
        """Get utilization statistics for a card"""
        if card_number not in self.input_cards:
            raise ValueError(f"Card {card_number} not found")

        card = self.input_cards[card_number]
        utilization = {
            'total_ports': card.port_count,
            'used_ports': len(card.ports),
            'available_ports': card.port_count - len(card.ports)
        }
        
        # Count by signal type
        signal_counts = {}
        for port in card.ports.values():
            signal_type = port.signal_type.value
            signal_counts[signal_type] = signal_counts.get(signal_type, 0) + 1
            
        utilization['signal_counts'] = signal_counts
        return utilization

    def export_configuration(self) -> Dict[str, Any]:
        """Export router configuration"""
        return {
            'router_id': self.router_id,
            'cards': {
                card_num: {
                    'card_number': card.card_number,
                    'port_count': card.port_count,
                    'ports': {
                        port_num: {
                            'index': port.index,
                            'name': port.name,
                            'port_number': port.port_number,
                            'signal_type': port.signal_type.value,
                            'attributes': port.attributes
                        }
                        for port_num, port in card.ports.items()
                    }
                }
                for card_num, card in self.input_cards.items()
            }
        }
