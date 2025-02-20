from app.service.call_logs import get_call_logs
from fastapi import APIRouter, Request

router = APIRouter()

@router.get("/call-logs")
async def CallLogs_endpoint (request: Request):
    return get_call_logs()