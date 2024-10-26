from enum import Enum, auto
from dataclasses import dataclass
from typing import Dict, List, Optional

class RouterManufacturer(Enum):
    EVERTZ = "Evertz"
    ROSS = "Ross"

class RouterModel(Enum):
    # Evertz Models
    EQX = "EQX"
    EMR = "EMR"
    
    # Ross Models
    ULTRIX_FR1 = "Ultrix FR1"    # 36x36
    ULTRIX_FR2 = "Ultrix FR2"    # 72x72
    ULTRIX_FR5 = "Ultrix FR5"    # 160x160
    ULTRIX_FR12 = "Ultrix FR12"  # 288x288

@dataclass
class RouterCapabilities:
    """Router platform capabilities"""
    max_video_inputs: int
    max_video_outputs: int
    max_audio_inputs: int
    max_audio_outputs: int
    supports_12g: bool = False
    supports_ip: bool = False
    supports_fiber: bool = False
    multiviewer_capable: bool = False
    clean_switch_capable: bool = False
    frame_sync_capable: bool = False

class RouterSignalFormat(Enum):
    """Supported signal formats"""
    SDI_270M = "SD-SDI"
    SDI_1_5G = "HD-SDI"
    SDI_3G = "3G-SDI"
    SDI_12G = "12G-SDI"
    FIBER = "Fiber"
    IP_2110 = "SMPTE 2110"
    NDI = "NDI"

@dataclass
class RouterCard:
    """Router I/O card configuration"""
    manufacturer: RouterManufacturer
    model: str
    card_type: str
    port_count: int
    supported_formats: List[RouterSignalFormat]
    attributes: Dict[str, any] = None

class RouterPlatform:
    """Router platform configuration"""
    
    def __init__(self, 
                 manufacturer: RouterManufacturer,
                 model: RouterModel):
        self.manufacturer = manufacturer
        self.model = model
        self.capabilities = self._get_platform_capabilities()
        self.installed_cards: Dict[str, RouterCard] = {}

    def _get_platform_capabilities(self) -> RouterCapabilities:
        """Get platform capabilities based on manufacturer and model"""
        if self.manufacturer == RouterManufacturer.ROSS:
            # Based on Ross Ultrix specifications from ross.com
            if self.model == RouterModel.ULTRIX_FR1:
                return RouterCapabilities(
                    max_video_inputs=36,
                    max_video_outputs=36,
                    max_audio_inputs=768,
                    max_audio_outputs=768,
                    supports_12g=True,
                    supports_ip=True,
                    supports_fiber=True,
                    multiviewer_capable=True,
                    clean_switch_capable=True,
                    frame_sync_capable=True
                )
            elif self.model == RouterModel.ULTRIX_FR12:
                return RouterCapabilities(
                    max_video_inputs=288,
                    max_video_outputs=288,
                    max_audio_inputs=6144,
                    max_audio_outputs=6144,
                    supports_12g=True,
                    supports_ip=True,
                    supports_fiber=True,
                    multiviewer_capable=True,
                    clean_switch_capable=True,
                    frame_sync_capable=True
                )
        # Add other manufacturer/model capabilities
        return None
