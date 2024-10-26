from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import logging

class AutoCADConnectorException(Exception):
    """Base exception for AutoCAD connection errors"""
    pass

class BaseAutoCADConnector(ABC):
    """Abstract base class for AutoCAD connectors"""
    
    def __init__(self, drawing_path: Path):
        self.drawing_path = drawing_path
        self.app = None
        self.doc = None
        self._logger = logging.getLogger(__name__)

    @abstractmethod
    async def connect(self) -> None:
        """Establish connection to AutoCAD application"""
        pass

    @abstractmethod
    async def open_drawing(self) -> None:
        """Open the specified drawing file"""
        pass

    @abstractmethod
    async def close_drawing(self) -> None:
        """Close the current drawing"""
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """Disconnect from AutoCAD application"""
        pass

    @abstractmethod
    async def get_all_text(self) -> List[Dict[str, Any]]:
        """Extract all text entities from drawing"""
        pass

    @abstractmethod
    async def get_block_attributes(self) -> List[Dict[str, Any]]:
        """Extract all block attributes from drawing"""
        pass

    async def __aenter__(self):
        """Context manager entry"""
        await self.connect()
        await self.open_drawing()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        await self.close_drawing()
        await self.disconnect()

