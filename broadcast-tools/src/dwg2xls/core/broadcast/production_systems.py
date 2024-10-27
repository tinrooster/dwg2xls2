from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set

class ProductionPlatform(Enum):
    ACUITY = "Ross Acuity"
    CARBONITE = "Ross Carbonite"
    ATEM = "BlackMagic ATEM"
    CONSTELLATION = "BlackMagic Constellation"

class MultiviewerPlatform(Enum):
    EVERTZ_VIP = "Evertz VIP"
    EVERTZ_EQX_MV = "Evertz EQX-MV"
    BMD_MULTIVIEW = "BlackMagic MultiView"
    BMD_SMARTVIEW = "BlackMagic SmartView"

@dataclass
class AcuityConfig:
    """Ross Acuity Production Switcher Configuration"""
    frame_type: str  # 4RU or 8RU
    control_panel: str  # 2ME, 3ME, 4ME
    me_count: int
    miniMe_count: int
    input_count: int
    output_count: int
    aux_buses: int
    custom_controls: int
    mnemonics: bool = True
    features: Dict[str, bool] = field(default_factory=lambda: {
        "ultrachrome": True,
        "media_stores": True,
        "clip_stores": True,
        "proc_amps": True
    })

@dataclass
class MultiviewerConfig:
    """Multiviewer Configuration"""
    platform: MultiviewerPlatform
    input_count: int
    output_count: int
    max_pips_per_output: int
    supported_layouts: List[str]
    features: Dict[str, bool]
    tally_support: bool = False
    audio_meters: bool = False
    ident_support: bool = False

class EvertzVIPMultiviewer:
    """Evertz VIP-X Multiviewer Platform"""
    
    def __init__(self, model: str):
        self.model = model
        self.config = self._get_model_config()
        self.layouts: Dict[str, Dict] = {}
        self.sources: Dict[int, str] = {}
        self.destinations: Dict[int, str] = {}

    def _get_model_config(self) -> MultiviewerConfig:
        configs = {
            "VIP-X16": MultiviewerConfig(
                platform=MultiviewerPlatform.EVERTZ_VIP,
                input_count=16,
                output_count=2,
                max_pips_per_output=16,
                supported_layouts=[
                    "1x1", "2x2", "3x3", "4x4", 
                    "3+7", "4+8", "1+7", "custom"
                ],
                features={
                    "uhd_support": True,
                    "hdr_support": True,
                    "audio_monitoring": True,
                    "closed_caption": True,
                    "timecode": True,
                    "clock": True,
                    "dynamic_umd": True
                },
                tally_support=True,
                audio_meters=True,
                ident_support=True
            ),
            # Add other VIP models...
        }
        return configs.get(self.model)

class BlackMagicMultiview:
    """BlackMagic MultiView Platform"""
    
    def __init__(self, model: str):
        self.model = model
        self.config = self._get_model_config()

    def _get_model_config(self) -> MultiviewerConfig:
        configs = {
            "MultiView 16": MultiviewerConfig(
                platform=MultiviewerPlatform.BMD_MULTIVIEW,
                input_count=16,
                output_count=2,  # HDMI and SDI
                max_pips_per_output=16,
                supported_layouts=[
                    "2x2", "3x3", "4x4", "2x8"
                ],
                features={
                    "uhd_support": True,
                    "audio_monitoring": True,
                    "labels": True,
                    "tally": True
                },
                tally_support=True,
                audio_meters=True,
                ident_support=True
            ),
            # Add other BlackMagic models...
        }
        return configs.get(self.model)
