from fastapi import APIRouter, Request
from app.service.wa import wa_contacts, msg_jid
from app.service.wamessage import msg_messages, view_combined_json
router = APIRouter()


@router.get("/get-wa-contacts")
async def get_wacontact_endpoint (request: Request):
    return wa_contacts()

@router.get("/get-wa-jid")
async def get_wacontact_endpoint (request: Request):
    return msg_jid()

@router.get("/wa-msg")
async def get_msgwa_endpoint (request: Request):
    return view_combined_json()

