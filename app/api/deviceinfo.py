from fastapi import APIRouter, Request
from app.service.deviceinfo import get_device_info

router = APIRouter()

@router.get("/device-info")
async def device_info_endpoint (request: Request):
    return get_device_info()