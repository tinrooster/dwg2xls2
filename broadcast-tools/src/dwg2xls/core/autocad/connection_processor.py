from typing import List, Dict
import pandas as pd
import re

class ConnectionProcessor:
    """Processes broadcast connection data"""

    def __init__(self):
        self.signal_analyzer = SignalFlowAnalyzer()

    def process_connection_data(self, data: pd.DataFrame) -> Dict[str, List[SignalConnection]]:
        """Process connection data from DataFrame"""
        connections_by_device = {}
        
        for _, row in data.iterrows():
            connection = self.signal_analyzer.parse_connection(row.to_dict())
            
            # Group by origin device
            if connection.origin_device:
                if connection.origin_device not in connections_by_device:
                    connections_by_device[connection.origin_device] = []
                connections_by_device[connection.origin_device].append(connection)
                
            # Group by destination device
            if connection.dest_device:
                if connection.dest_device not in connections_by_device:
                    connections_by_device[connection.dest_device] = []
                connections_by_device[connection.dest_device].append(connection)

        return connections_by_device

    def analyze_signal_chain(self, 
                           connections: List[SignalConnection]) -> Dict[str, Any]:
        """Analyze complete signal chain"""
        return {
            'total_connections': len(connections),
            'unique_devices': self._get_unique_devices(connections),
            'signal_types': self._get_signal_types(connections),
            'wire_types': self._get_wire_types(connections),
            'card_assignments': self._get_card_assignments(connections)
        }

    @staticmethod
    def _get_unique_devices(connections: List[SignalConnection]) -> List[str]:
        """Get list of unique devices in signal chain"""
        devices = set()
        for conn in connections:
            if conn.origin_device:
                devices.add(conn.origin_device)
            if conn.dest_device:
                devices.add(conn.dest_device)
        return sorted(list(devices))

    @staticmethod
    def _get_signal_types(connections: List[SignalConnection]) -> Dict[str, int]:
        """Count signal types in connections"""
        signal_types = {}
        for conn in connections:
            if 'ACUITY' in conn.origin:
                signal_types['ACUITY'] = signal_types.get('ACUITY', 0) + 1
            if 'MDA' in conn.destination:
                signal_types['MDA'] = signal_types.get('MDA', 0) + 1
            if 'MDB' in conn.destination:
                signal_types['MDB'] = signal_types.get('MDB', 0) + 1
            if 'MDC' in conn.destination:
                signal_types['MDC'] = signal_types.get('MDC', 0) + 1
        return signal_types

    @staticmethod
    def _get_wire_types(connections: List[SignalConnection]) -> Dict[str, int]:
        """Count wire types used"""
        wire_types = {}
        for conn in connections:
            if conn.wire_type:
                wire_types[conn.wire_type] = wire_types.get(conn.wire_type, 0) + 1
        return wire_types

    @staticmethod
    def _get_card_assignments(connections: List[SignalConnection]) -> Dict[str, List[str]]:
        """Get EQX card assignments"""
        card_assignments = {}
        for conn in connections:
            if 'EQX' in conn.notes:
                card_match = re.search(r'CARD\s*#(\d+)', conn.notes)
                if card_match:
                    card_num = card_match.group(1)
                    if card_num not in card_assignments:
                        card_assignments[card_num] = []
                    card_assignments[card_num].append(conn.number)
        return card_assignments
