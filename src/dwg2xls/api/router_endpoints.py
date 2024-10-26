from fastapi import APIRouter, HTTPException
from typing import List, Dict
from ..core.broadcast.router_analysis import RouterAnalyzer, analyze_camera_chain, analyze_card_usage

router = APIRouter(prefix="/router", tags=["Router Analysis"])

@router.get("/camera-chain")
async def get_camera_chain():
    """Get camera chain analysis"""
    try:
        camera_sources = analyze_camera_chain()
        return {
            "status": "success",
            "camera_count": len(camera_sources),
            "cameras": [
                {
                    "name": cam.name,
                    "port": cam.port,
                    "card": cam.card
                }
                for cam in camera_sources
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/card-usage")
async def get_card_usage():
    """Get router card usage analysis"""
    try:
        usage = analyze_card_usage()
        return {
            "status": "success",
            "cards": {
                card_num: {
                    "total_ports": data["total"],
                    "signal_types": list(data["types"])
                }
                for card_num, data in usage.items()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
