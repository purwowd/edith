from app.service.browserhistory import get_browser_history
from fastapi import APIRouter, Request

router = APIRouter()

@router.get("/browser-history")
async def browser_history_endpoint (request: Request):
    return get_browser_history()