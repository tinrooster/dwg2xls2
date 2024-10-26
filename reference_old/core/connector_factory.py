from enum import Enum
from typing import Optional
from .autocad_manager import BaseAutoCADConnector, DXFConnector, COMAutoCADConnector

class ConnectorType(Enum):
    DXF = "dxf"
    COM = "com"

class ConnectorFactory:
    @staticmethod
    def create_connector(connector_type: ConnectorType) -> Optional[BaseAutoCADConnector]:
        if connector_type == ConnectorType.DXF:
            return DXFConnector()
        elif connector_type == ConnectorType.COM:
            return COMAutoCADConnector()
        return None
