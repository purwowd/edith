# app/api/pullall.py

from fastapi import APIRouter, Request
from app.service.PullAll_service import pull_all_data, pull_all_data_rooted
router = APIRouter()

@router.get("/pull-all")
async def pull_all_endpoint(request: Request):
    return pull_all_data()

@router.get("/pull-all rooted")
async def pull_all_rooted_endpoint(request: Request):
    return pull_all_data_rooted()



