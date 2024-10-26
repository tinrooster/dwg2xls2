from typing import Dict, List, Any, Optional, Tuple
import win32com.client
import pythoncom
from pathlib import Path
import logging
import time

from .base_connector import BaseAutoCADConnector, AutoCADConnectorException

class LTAutoCADConnector(BaseAutoCADConnector):
    """
    AutoCAD LT connector implementation.
    Handles the limitations of LT version while providing core functionality.
    """

    async def connect(self) -> None:
        """Establish connection to AutoCAD LT"""
        try:
            pythoncom.CoInitialize()
            # Try AutoCAD LT first, fall back to regular AutoCAD if needed
            try:
                self.app = win32com.client.Dispatch("AutoCAD.Application.LT")
            except:
                self.app = win32com.client.Dispatch("AutoCAD.Application")
            
            self.app.Visible = True  # LT often needs visible window
            self._logger.info("Successfully connected to AutoCAD LT")
        except Exception as e:
            self._logger.error(f"Failed to connect to AutoCAD LT: {str(e)}")
            raise AutoCADConnectorException(f"AutoCAD LT connection failed: {str(e)}")

    async def open_drawing(self) -> None:
        """Open drawing file in AutoCAD LT with retry logic"""
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                self.doc = self.app.Documents.Open(str(self.drawing_path))
                self._logger.info(f"Opened drawing: {self.drawing_path}")
                # Ensure drawing is fully loaded
                time.sleep(1)
                return
            except Exception as e:
                retry_count += 1
                if retry_count == max_retries:
                    self._logger.error(f"Failed to open drawing after {max_retries} attempts: {str(e)}")
                    raise AutoCADConnectorException(f"Failed to open drawing: {str(e)}")
                time.sleep(2)  # Wait before retry

    async def get_all_text(self) -> List[Dict[str, Any]]:
        """
        Extract all text entities from current drawing.
        Includes special handling for LT limitations.
        """
        text_entities = []
        try:
            model_space = self.doc.ModelSpace
            for i in range(model_space.Count):
                try:
                    entity = model_space.Item(i)
                    # Handle both regular text and MText
                    if entity.ObjectName in ["AcDbText", "AcDbMText"]:
                        text_data = {
                            "text": entity.TextString,
                            "position": (
                                entity.InsertionPoint[0], 
                                entity.InsertionPoint[1]
                            ),
                            "layer": entity.Layer,
                            "type": entity.ObjectName
                        }
                        
                        # Add height if available
                        try:
                            text_data["height"] = entity.Height
                        except:
                            text_data["height"] = None

                        text_entities.append(text_data)
                except Exception as entity_error:
                    self._logger.warning(f"Skipped entity {i}: {str(entity_error)}")
                    continue

            return text_entities
        except Exception as e:
            self._logger.error(f"Error extracting text: {str(e)}")
            raise AutoCADConnectorException(f"Text extraction failed: {str(e)}")

    async def get_block_attributes(self) -> List[Dict[str, Any]]:
        """
        Extract block attributes from current drawing.
        Includes special handling for LT-specific block references.
        """
        attributes = []
        try:
            model_space = self.doc.ModelSpace
            for i in range(model_space.Count):
                try:
                    entity = model_space.Item(i)
                    if entity.ObjectName == "AcDbBlockReference":
                        block_data = {
                            "block_name": entity.EffectiveName,
                            "position": (
                                entity.InsertionPoint[0], 
                                entity.InsertionPoint[1]
                            ),
                            "layer": entity.Layer,
                            "attributes": {}
                        }

                        # Handle attributes if present
                        if entity.HasAttributes:
                            for j in range(entity.GetAttributes().Count):
                                try:
                                    attr = entity.GetAttributes().Item(j)
                                    block_data["attributes"][attr.TagString] = attr.TextString
                                except Exception as attr_error:
                                    self._logger.warning(
                                        f"Skipped attribute {j} in block {entity.EffectiveName}: "
                                        f"{str(attr_error)}"
                                    )
                        
                        attributes.append(block_data)
                except Exception as entity_error:
                    self._logger.warning(f"Skipped block {i}: {str(entity_error)}")
                    continue

            return attributes
        except Exception as e:
            self._logger.error(f"Error extracting block attributes: {str(e)}")
            raise AutoCADConnectorException(f"Block attribute extraction failed: {str(e)}")

    async def get_device_counts(self) -> List[Dict[str, Any]]:
        """
        Specialized method to extract device counts from drawings.
        Particularly useful for the floor plan drawings shown.
        """
        devices = []
        try:
            blocks = await self.get_block_attributes()
            for block in blocks:
                if "DEVICE" in block["block_name"].upper():
                    device_data = {
                        "position": block["position"],
                        "type": block["block_name"],
                        "count": None,
                        "circuit": None
                    }
                    
                    # Extract count and circuit information from attributes
                    attrs = block["attributes"]
                    for key, value in attrs.items():
                        if "COUNT" in key.upper():
                            device_data["count"] = value
                        elif "CIRCUIT" in key.upper():
                            device_data["circuit"] = value
                    
                    devices.append(device_data)
            
            return devices
        except Exception as e:
            self._logger.error(f"Error extracting device counts: {str(e)}")
            raise AutoCADConnectorException(f"Device count extraction failed: {str(e)}")

    async def close_drawing(self) -> None:
        """Close current drawing with LT-specific cleanup"""
        try:
            if self.doc:
                # Save any changes if needed
                # self.doc.Save()  # Uncomment if saving is required
                self.doc.Close()
                self._logger.info("Drawing closed successfully")
        except Exception as e:
            self._logger.error(f"Error closing drawing: {str(e)}")
            raise AutoCADConnectorException(f"Failed to close drawing: {str(e)}")

    async def disconnect(self) -> None:
        """Disconnect from AutoCAD LT"""
        try:
            if self.app:
                self.app.Quit()
                pythoncom.CoUninitialize()
                self._logger.info("Disconnected from AutoCAD LT")
        except Exception as e:
            self._logger.error(f"Error disconnecting from AutoCAD LT: {str(e)}")
            raise AutoCADConnectorException(f"Failed to disconnect: {str(e)}")

