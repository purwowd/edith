from fastapi import APIRouter, Request
from app.service.sms import sms
router = APIRouter()

@router.get("/sms")
async def sms_endpoint(request: Request):
    return sms()

