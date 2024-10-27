from typing import Dict, List, Any, Optional
import win32com.client
import pythoncom
from pathlib import Path
import logging

from .base_connector import BaseAutoCADConnector, AutoCADConnectorException

class DCOMAutoCADConnector(BaseAutoCADConnector):
    """AutoCAD connector using DCOM automation"""

    async def connect(self) -> None:
        """Establish DCOM connection to AutoCAD"""
        try:
            pythoncom.CoInitialize()
            self.app = win32com.client.Dispatch("AutoCAD.Application")
            self._logger.info("Successfully connected to AutoCAD")
        except Exception as e:
            self._logger.error(f"Failed to connect to AutoCAD: {str(e)}")
            raise AutoCADConnectorException(f"AutoCAD connection failed: {str(e)}")

    async def open_drawing(self) -> None:
        """Open drawing file in AutoCAD"""
        try:
            self.doc = self.app.Documents.Open(str(self.drawing_path))
            self._logger.info(f"Opened drawing: {self.drawing_path}")
        except Exception as e:
            self._logger.error(f"Failed to open drawing: {str(e)}")
            raise AutoCADConnectorException(f"Failed to open drawing: {str(e)}")

    async def get_all_text(self) -> List[Dict[str, Any]]:
        """Extract all text entities from current drawing"""
        text_entities = []
        try:
            model_space = self.doc.ModelSpace
            for i in range(model_space.Count):
                entity = model_space.Item(i)
                if entity.ObjectName == "AcDbText":
                    text_entities.append({
                        "text": entity.TextString,
                        "position": (entity.InsertionPoint[0], entity.InsertionPoint[1]),
                        "height": entity.Height,
                        "layer": entity.Layer
                    })
            return text_entities
        except Exception as e:
            self._logger.error(f"Error extracting text: {str(e)}")
            raise AutoCADConnectorException(f"Text extraction failed: {str(e)}")

    async def get_block_attributes(self) -> List[Dict[str, Any]]:
        """Extract block attributes from current drawing"""
        attributes = []
        try:
            model_space = self.doc.ModelSpace
            for i in range(model_space.Count):
                entity = model_space.Item(i)
                if entity.ObjectName == "AcDbBlockReference":
                    if entity.HasAttributes:
                        block_attrs = {}
                        for j in range(entity.GetAttributes().Count):
                            attr = entity.GetAttributes().Item(j)
                            block_attrs[attr.TagString] = attr.TextString
                        attributes.append({
                            "block_name": entity.EffectiveName,
                            "position": (entity.InsertionPoint[0], entity.InsertionPoint[1]),
                            "attributes": block_attrs,
                            "layer": entity.Layer
                        })
            return attributes
        except Exception as e:
            self._logger.error(f"Error extracting block attributes: {str(e)}")
            raise AutoCADConnectorException(f"Block attribute extraction failed: {str(e)}")

    async def close_drawing(self) -> None:
        """Close current drawing"""
        try:
            if self.doc:
                self.doc.Close()
                self._logger.info("Drawing closed successfully")
        except Exception as e:
            self._logger.error(f"Error closing drawing: {str(e)}")
            raise AutoCADConnectorException(f"Failed to close drawing: {str(e)}")

    async def disconnect(self) -> None:
        """Disconnect from AutoCAD"""
        try:
            if self.app:
                self.app.Quit()
                pythoncom.CoUninitialize()
                self._logger.info("Disconnected from AutoCAD")
        except Exception as e:
            self._logger.error(f"Error disconnecting from AutoCAD: {str(e)}")
            raise AutoCADConnectorException(f"Failed to disconnect: {str(e)}")

