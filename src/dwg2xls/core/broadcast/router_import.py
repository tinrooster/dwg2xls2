import pandas as pd
from typing import Optional

class RouterConfigImporter:
    """Imports router configurations from various formats"""

    @staticmethod
    def from_excel(file_path: str, sheet_name: Optional[str] = None) -> EQXRouter:
        """Import router configuration from Excel"""
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        
        # Extract router ID from first column header
        router_id = df.columns[0].split()[0]
        router = EQXRouter(router_id)
        
        current_card = 1
        
        for _, row in df.iterrows():
            # Extract values
            index = row.iloc[0]
            name = row.iloc[1]
            port = row.iloc[2]
            card = row.iloc[4] if not pd.isna(row.iloc[4]) else current_card
            
            # Update current card if we hit a card boundary
            if not pd.isna(card):
                current_card = card
                
            # Add port to router
            router.add_port(
                card_number=int(current_card),
                port_index=int(index),
                name=str(name),
                port_number=int(port)
            )
            
        return router
